import pandas as pd

def calculate_sma(series: pd.Series, window: int):
    return series.rolling(window=window).mean()

def calculate_rsi(series: pd.Series, period: int = 14):
    """
    Berechnet den RSI (Relative Strength Index) auf Basis von Kursen.
    """
    delta = series.diff()
    gains = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    losses = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gains / losses
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std_dev: float = 2.0):
    sma = calculate_sma(series, window)
    std_dev = series.rolling(window=window).std()
    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)
    return sma, upper_band, lower_band
