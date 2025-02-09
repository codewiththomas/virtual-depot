PRAGMA foreign_keys = ON;

-- Table: instrument
CREATE TABLE instrument (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isin TEXT UNIQUE,  -- Unique only for stocks & bonds (handled by partial index)
    wkn TEXT UNIQUE,   -- Same as ISIN
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('Stock', 'Bond', 'Crypto', 'ETF', 'Other')) NOT NULL
);

-- Indexes to enforce uniqueness only for stocks & bonds
CREATE UNIQUE INDEX IF NOT EXISTS unique_isin
ON instrument (isin) WHERE type IN ('Stock', 'Bond');

CREATE UNIQUE INDEX IF NOT EXISTS unique_wkn
ON instrument (wkn) WHERE type IN ('Stock', 'Bond');

-- Table: ticker_symbol
CREATE TABLE ticker_symbol (
    symbol TEXT PRIMARY KEY,
    instrument_id INTEGER NOT NULL,
    FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
);

-- Table: instrument_history
CREATE TABLE instrument_history (
    instrument_id INTEGER NOT NULL,
    date DATE NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    dividend REAL DEFAULT 0,
    split_factor REAL DEFAULT 1.0,
    PRIMARY KEY (instrument_id, date),
    FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
);

-- Table: depot
CREATE TABLE depot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cash_balance REAL NOT NULL DEFAULT 0
);

-- Table: depot_balance (optional, for multi-currency cash tracking)
CREATE TABLE depot_balance (
    depot_id INTEGER NOT NULL,
    currency TEXT CHECK (LENGTH(currency) = 3) NOT NULL,  -- ISO currency codes
    cash_balance REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (depot_id, currency),
    FOREIGN KEY (depot_id) REFERENCES depot(id) ON DELETE CASCADE
);

-- Table: depot_holdings (optional, for tracking current asset quantities)
CREATE TABLE depot_holdings (
    depot_id INTEGER NOT NULL,
    instrument_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK(quantity >= 0),
    PRIMARY KEY (depot_id, instrument_id),
    FOREIGN KEY (depot_id) REFERENCES depot(id) ON DELETE CASCADE,
    FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE
);

-- Table: transaction
CREATE TABLE transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id INTEGER NOT NULL,
    depot_id INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    trading_fee REAL NOT NULL DEFAULT 1.0,  -- Each trade costs 1 EUR
    price_per_unit REAL NOT NULL CHECK(price_per_unit >= 0),
    quantity REAL NOT NULL CHECK(quantity > 0),
    direction TEXT CHECK(direction IN ('BUY', 'SELL')) NOT NULL,
    FOREIGN KEY (instrument_id) REFERENCES instrument(id) ON DELETE CASCADE,
    FOREIGN KEY (depot_id) REFERENCES depot(id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_instrument_history_date ON instrument_history (date);
CREATE INDEX idx_transaction_date ON transaction (date);
CREATE INDEX idx_transaction_depot ON transaction (depot_id);

