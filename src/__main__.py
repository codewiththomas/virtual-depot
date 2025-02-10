import logging

import yfinance as yf
from datetime import datetime as dt, timedelta
# from instrument import Instrument

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entities.base_entity import Base
from entities.instrument import Instrument
from entities.ticker_symbol import TickerSymbol
from entities.instrument_history import InstrumentHistory
from entities.depot import Depot
from entities.depot_balance import DepotBalance
from entities.depot_holdings import DepotHoldings
from entities.transaction import Transaction

def update_stock_data():
    engine = create_engine('sqlite:///.db/tading-bot.sqlite3.db', echo=False)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        # Step 1: Get all instruments from the database
        instruments = session.query(Instrument).all()

        for instrument in instruments:
            for ticker in instrument.ticker_symbols:
            # Step 2: Get the max date for each instrument
                max_date = session.query(InstrumentHistory).filter(InstrumentHistory.instrument_id == instrument.id).order_by(InstrumentHistory.date.desc()).first()
                if max_date:
                    max_date = max_date.date + timedelta(days=1)
                else:
                    max_date = dt(1970, 1, 1)
                logging.info(f"Max date for {instrument.name}: {max_date}")

                # Step 3: Get the historical data for each instrument, starting from the max date until today
                data = yf.download(ticker.symbol, start=max_date)

                # Step 4: Save the (new) historical data to the database
                for date, row in data.iterrows():
                    history = InstrumentHistory(
                        instrument_id=instrument.id,
                        date=date,
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=row['Volume'].item(),
                        dividend=0,
                        split_factor=0
                    )
                    session.add(history)
                session.commit()


def init_db():
    engine = create_engine('sqlite:///.db/tading-bot.sqlite3.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        microsoft = Instrument(
            isin='US5949181045',
            wkn='870747',
            name='Microsoft Corporation',
            type='Stock'
        )
        msft_ticker = TickerSymbol(
            symbol='MSFT'
        )
        microsoft.ticker_symbols.append(msft_ticker)
        session.add(microsoft)
        session.commit()


def main():
    logging.basicConfig(level=logging.INFO)

    # Create an SQLite engine (change the URL for other DBs)
    init_db()
    update_stock_data()

    logging.info("Database tables created")

if __name__ == "__main__":

    main()
    # apple = Instrument(1, "865985", "US0378331005", "Apple", ["APPL", "APC"], "stock", dt.now())
    # apple.save_historical_data()
