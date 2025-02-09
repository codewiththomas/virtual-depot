import logging
# from datetime import datetime as dt
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

    logging.info("Database tables created")

if __name__ == "__main__":

    main()
    # apple = Instrument(1, "865985", "US0378331005", "Apple", ["APPL", "APC"], "stock", dt.now())
    # apple.save_historical_data()
