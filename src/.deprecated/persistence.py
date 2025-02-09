import logging
import os
import sqlite3


class Persistence:


    def __init__(self, database = "./.db/tading-bot.sqlite3.db"):
        self._db = database
        self._create_db_directory_if_not_exists()
        self._conn = None
        self._connect()
        self._ensure_tables_exist()
        self._disconnect()


    def _create_db_directory_if_not_exists(self):
        """Creates the database directory if it does not exist."""
        db_directory = os.path.dirname(self._db)
        if db_directory and not os.path.exists(db_directory):
            os.makedirs(db_directory, exist_ok=True)
            logging.debug("Created database directory " + db_directory)


    def _connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self._db)
            logging.debug("Conntected to database")


    def _disconnect(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logging.debug("Disconnected from database")
        else:
            logging.debug("Disconnect called but no connection was open")


    def _ensure_tables_exist(self):
        if not self._table_exists('instruments'):
            self._create_table_instruments()
            logging.debug("Created table instruments")
        if not self._table_exists('transactions'):
            self._create_table_transactions()
            logging.debug("Created table transactions")
        if not self._table_exists('instrument_daily_historical_data'):
            self._create_table_historical_data()
            logging.debug("Created table instrument_daily_historical_data")
        logging.debug("All tables exist")


    def _table_exists(self, table_name):
        if self._conn is None:
            self._connect()
        c = self._conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        return c.fetchone() is not None


    def _excecute_create_table_command(self, create_command):
        close_after_finish = False
        if self._conn is None:
            self._connect()
            close_after_finish = True
        cursor = self._conn.cursor()
        cursor.execute(create_command)
        self._conn.commit()
        if close_after_finish:
            self._disconnect()


    def _create_table_instruments(self):
        command = '''
                  CREATE TABLE IF NOT EXISTS instruments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    symbol TEXT UNIQUE,
                    wkn TEXT,
                    isin TEXT,
                    type TEXT,
                    last_updated DATETIME
                    )
                  '''
        self._excecute_create_table_command(command)


    def _create_table_transactions(self):
        command = '''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                price REAL,
                amount REAL,
                fee REAL,
                explanation TEXT
            )
        '''
        self._excecute_create_table_command(command)


    def _create_table_historical_data(self):
        command = '''
        CREATE TABLE IF NOT EXISTS instrument_daily_historical_data (
            id INTEGER PRIMARY KEY,
            instrument_id INTEGER,
            date DATETIME,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            dividends REAL,
            stock_splits REAL,
            FOREIGN KEY(instrument_id) REFERENCES instruments(id)
        )
        '''
        self._excecute_create_table_command(command)


    def save_historical_data(self, instrument_id, data):
        """
        Save historical data (a pandas DataFrame) into the database.

        :param instrument_id: The id of the instrument.
        :param data: A pandas DataFrame containing the historical data.
        """
        if data is False or data.empty:
            print("No data available to save.")
            return

        # Reset the DataFrame index so that the dates become a column.
        data_reset = data.reset_index()
        # Ensure the date column is named "Date"
        if "Date" not in data_reset.columns:
            data_reset.rename(columns={data_reset.columns[0]: "Date"}, inplace=True)

        # Prepare a list of records to be inserted.
        records = []
        for _, row in data_reset.iterrows():
            # Format the date to a string
            date_value = (
                row["Date"].strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(row["Date"], "strftime")
                else str(row["Date"])
            )
            records.append((
                instrument_id,
                date_value,
                row.get("Open", None),
                row.get("High", None),
                row.get("Low", None),
                row.get("Close", None),
                row.get("Volume", None),
                row.get("Dividends", None),
                row.get("Stock Splits", None),
            ))

        # Insert the data in bulk using executemany.
        self._connect()
        with self._conn:
            self._conn.executemany(
                """
                INSERT OR REPLACE INTO instrument_daily_historical_data
                (instrument_id, date, open, high, low, close, volume, dividends, stock_splits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                records
            )
        print("Historical data saved successfully.")