import logging
from datetime import datetime as dt
from instrument import Instrument

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    #depot = Persistence()

    apple = Instrument(1, "865985", "US0378331005", "Apple", ["APPL", "APC"], "stock", dt.now())
    apple.save_historical_data()
