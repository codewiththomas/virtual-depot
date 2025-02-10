# /src/populate_instruments.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entities.instrument import Instrument
from entities.ticker_symbol import TickerSymbol

def populate_instruments():
    # Create an SQLite engine (change the URL if you use a different database)
    engine = create_engine('sqlite:///example.db', echo=True)

    # Create a configured Session class and a session instance
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # ---- Apple Inc. ----
        apple = Instrument(
            isin='US0378331005',
            wkn='865985',
            name='Apple Inc.',
            type='Stock'
        )
        apple.ticker_symbols.append(TickerSymbol(symbol='AAPL'))

        # ---- Alphabet Inc. (Google) ----
        google = Instrument(
            isin='US02079K3059',  # Alphabet ISIN (example value)
            wkn='A14Y6F',             # Optional
            name='Alphabet Inc.',
            type='Stock'
        )
        google.ticker_symbols.append(TickerSymbol(symbol='GOOGL'))

        # ---- ETF iShares Core MSCI World ETF ----
        etf_msci_world = Instrument(
            isin='IE00B4L5Y983',
            wkn='A0RPWH',
            name='iShares Core MSCI World ETF (Acc)',
            type='ETF'
        )
        # You can choose an appropriate ticker symbol for the ETF.
        etf_msci_world.ticker_symbols.append(TickerSymbol(symbol='URTH'))

        # ---- Bitcoin (BTC) ----
        btc = Instrument(
            isin=None,  # Cryptocurrencies typically do not have an ISIN
            wkn=None,   # Nor a WKN
            name='Bitcoin',
            type='Crypto'
        )
        btc.ticker_symbols.append(TickerSymbol(symbol='BTC'))

        # Add all instruments to the session
        session.add_all([apple, google, etf_msci_world, btc])

        # Commit the transaction to save the changes
        session.commit()
        print("Successfully added Apple, Google, ETF MSCI World, and BTC.")

    except Exception as e:
        session.rollback()
        print("An error occurred:", e)
    finally:
        session.close()

if __name__ == '__main__':
    populate_instruments()
