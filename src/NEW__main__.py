import sqlite3
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- DataManager Class ---

class DataManager:
    """
    Handles downloading asset data from Yahoo Finance and storing it in a SQLite database.
    Uses incremental updates: on each run for a given asset, it downloads data only for the requested period.
    """
    def __init__(self, db_name='trading_bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_data (
                id INTEGER PRIMARY KEY,
                asset TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(asset, date)
            )
        ''')
        self.conn.commit()

    def update_asset_data(self, asset, start_date, end_date):
        """
        Downloads data from Yahoo Finance between start_date and end_date (YYYY-MM-DD strings)
        and saves it into the database.
        """
        try:
            data = yf.download(asset, start=start_date, end=end_date, progress=False)
        except Exception as e:
            print(f"Error downloading data for {asset}: {e}")
            return

        # If no data was returned (e.g. non-trading day) skip updating.
        if data.empty:
            return

        # Reset index so that the date becomes a column.
        data.reset_index(inplace=True)
        cursor = self.conn.cursor()
        for _, row in data.iterrows():
            try:
                # Explicitly convert to a Timestamp in case row['Date'] is not already one.
                date_str = pd.Timestamp(row['Date']).strftime("%Y-%m-%d")
                cursor.execute('''
                    INSERT OR IGNORE INTO asset_data (asset, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (asset, date_str,
                      row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
            except Exception as e:
                print(f"Error inserting data for {asset} on {row['Date']}: {e}")
        self.conn.commit()

    def get_asset_data(self, asset, start_date, end_date):
        """
        Retrieves asset data from the database between start_date and end_date (YYYY-MM-DD strings)
        and returns a DataFrame.
        """
        query = '''
            SELECT date, open, high, low, close, volume FROM asset_data
            WHERE asset = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        '''
        df = pd.read_sql_query(query, self.conn, params=(asset, start_date, end_date), parse_dates=['date'])
        return df

# --- IndicatorCalculator, Portfolio, Strategy remain unchanged ---

class IndicatorCalculator:
    """
    Contains static methods to compute technical indicators.
    """

    @staticmethod
    def SMA(series, window):
        return series.rolling(window=window).mean()

    @staticmethod
    def RSI(series, window=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(window=window).mean()
        loss = -delta.clip(upper=0).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def BollingerBands(series, window=20, num_std=2):
        sma = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        upper_band = sma + num_std * std
        lower_band = sma - num_std * std
        return sma, upper_band, lower_band

    @staticmethod
    def MACD(series, fast=12, slow=26, signal=9):
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def OBV(close, volume):
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=close.index)


class Portfolio:
    """
    Represents the virtual portfolio (depot) of the bot.
    Keeps track of cash, asset holdings, and trade history.
    """
    def __init__(self, starting_balance):
        self.starting_balance = starting_balance
        self.cash = starting_balance
        self.holdings = {}  # asset -> quantity held
        self.trade_cost = 1.0  # each trade costs 1 EUR
        self.trade_history = []  # log of executed trades

    def buy(self, asset, price, quantity, date):
        total_cost = price * quantity + self.trade_cost
        if self.cash >= total_cost:
            self.cash -= total_cost
            self.holdings[asset] = self.holdings.get(asset, 0) + quantity
            self.trade_history.append({
                'date': date,
                'asset': asset,
                'action': 'BUY',
                'price': price,
                'quantity': quantity
            })
            print(f"[{date}] Bought {quantity} of {asset} at {price:.2f} EUR (cost {total_cost:.2f} EUR)")
        else:
            print(f"[{date}] Not enough cash to buy {asset}.")

    def sell(self, asset, price, quantity, date):
        if self.holdings.get(asset, 0) >= quantity:
            self.holdings[asset] -= quantity
            total_gain = price * quantity - self.trade_cost
            self.cash += total_gain
            self.trade_history.append({
                'date': date,
                'asset': asset,
                'action': 'SELL',
                'price': price,
                'quantity': quantity
            })
            print(f"[{date}] Sold {quantity} of {asset} at {price:.2f} EUR (gain {total_gain:.2f} EUR)")
        else:
            print(f"[{date}] Not enough holdings to sell {asset}.")

    def evaluate(self, current_prices):
        """
        Returns the current portfolio value by summing cash and current value of all holdings.
        current_prices: dict mapping asset -> current price.
        """
        total = self.cash
        for asset, quantity in self.holdings.items():
            total += current_prices.get(asset, 0) * quantity
        return total


class Strategy:
    """
    Implements the trading strategy.
    For demonstration purposes the strategy here is:
      - If the RSI is below 30: BUY 10 shares.
      - If the RSI is above 70 and we hold the asset: SELL all shares.
    """
    def __init__(self):
        self.buy_quantity = 10

    def decide_trades(self, asset_data, portfolio, current_date):
        decisions = []
        for asset, df in asset_data.items():
            if df.empty or len(df) < 15:
                continue  # not enough data to compute indicators

            # Calculate RSI on the closing price.
            df = df.copy()
            df['RSI'] = IndicatorCalculator.RSI(df['close'])
            latest_rsi = df['RSI'].iloc[-1]
            latest_price = df['close'].iloc[-1]

            # Simple rules: buy when RSI < 30, sell when RSI > 70.
            if latest_rsi < 30:
                decisions.append({
                    'asset': asset,
                    'action': 'BUY',
                    'quantity': self.buy_quantity,
                    'price': latest_price
                })
            elif latest_rsi > 70 and portfolio.holdings.get(asset, 0) > 0:
                decisions.append({
                    'asset': asset,
                    'action': 'SELL',
                    'quantity': portfolio.holdings.get(asset, 0),
                    'price': latest_price
                })
        return decisions


class TradingBot:
    """
    The main trading bot class that orchestrates data updates, indicator calculations,
    decision making, and execution of trades over a simulation period.
    """
    def __init__(self, starting_balance, assets, start_date, end_date):
        self.portfolio = Portfolio(starting_balance)
        self.assets = assets  # list of asset tickers
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.data_manager = DataManager()
        self.strategy = Strategy()
        self.dates = pd.date_range(start=self.start_date, end=self.end_date, freq='D')

    def run(self):
        """
        Runs the simulation day-by-day. For each day, the bot:
          - Updates the data for each asset.
          - Computes technical indicators.
          - Decides on trades.
          - Executes the trades.
          - Evaluates the portfolio.
        """
        for current_date in self.dates:
            date_str = current_date.strftime("%Y-%m-%d")
            print(f"\n=== Trading Date: {date_str} ===")
            asset_data = {}

            # Update data and retrieve history up to the current date for each asset.
            for asset in self.assets:
                # Download data for the current day.
                next_date_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
                self.data_manager.update_asset_data(asset, date_str, next_date_str)
                # Retrieve all data from the start of the simulation until today.
                df = self.data_manager.get_asset_data(asset,
                                                      self.start_date.strftime("%Y-%m-%d"),
                                                      date_str)
                asset_data[asset] = df

            # Decide trades based on the current data and strategy.
            decisions = self.strategy.decide_trades(asset_data, self.portfolio, current_date)

            # Execute decisions.
            for decision in decisions:
                asset = decision['asset']
                action = decision['action']
                quantity = decision['quantity']
                price = decision['price']
                if action == 'BUY':
                    self.portfolio.buy(asset, price, quantity, date_str)
                elif action == 'SELL':
                    self.portfolio.sell(asset, price, quantity, date_str)

            # Evaluate the portfolio.
            current_prices = {}
            for asset in self.assets:
                df = asset_data[asset]
                if not df.empty:
                    current_prices[asset] = df['close'].iloc[-1]
                else:
                    current_prices[asset] = 0
            portfolio_value = self.portfolio.evaluate(current_prices)
            print(f"Portfolio value on {date_str}: {portfolio_value:.2f} EUR")

            # TODO: (Optional) Check risk constraints (e.g. 30-day depot condition).


if __name__ == '__main__':
    # Example configuration:
    starting_balance = 10000  # starting with 10,000 EUR
    assets = ['AAPL', 'GOOGL']  # tradeable assets (tickers)
    start_date = '2025-01-01'
    end_date = '2025-02-01'  # simulation period

    bot = TradingBot(starting_balance, assets, start_date, end_date)
    bot.run()
