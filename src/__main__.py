import logging
from persistence import Persistence
from instrument import Instrument

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    #depot = Persistence()

    msft = Instrument(1, "Apple", "APPL", "865985", "US0378331005", "stock", "2021-01-01 00:00:00")
    msft = Instrument(2, "Apple", "APC", "865985", "US0378331005", "stock", "2021-01-01 00:00:00")
    msft = Instrument(3, "Microsoft", "Google", "stock", "2021-01-01 00:00:00")
    msft = Instrument(4, "Microsoft", "MSFT", "stock", "2021-01-01 00:00:00")
    msft.save_historical_data()
