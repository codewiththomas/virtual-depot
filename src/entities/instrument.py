from sqlalchemy import Column, Integer, String, CheckConstraint, Index, text
from sqlalchemy.orm import relationship
from .base_entity import Base

class Instrument(Base):
    __tablename__ = 'instrument'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String, nullable=True)  # For stocks & bonds, uniqueness is enforced via a partial index
    wkn = Column(String, nullable=True)   # For stocks & bonds, uniqueness is enforced via a partial index
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('Stock', 'Bond', 'Crypto', 'ETF', 'Other')", name='instrument_type_check'),
        # Partial (filtered) unique indexes for isin and wkn:
        Index('unique_isin', 'isin', unique=True, sqlite_where=text("type IN ('Stock','Bond')")),
        Index('unique_wkn', 'wkn', unique=True, sqlite_where=text("type IN ('Stock','Bond')")),
    )

    # Relationships
    ticker_symbols = relationship("TickerSymbol", back_populates="instrument", cascade="all, delete-orphan")
    histories = relationship("InstrumentHistory", back_populates="instrument", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="instrument", cascade="all, delete-orphan")
    holdings = relationship("DepotHoldings", back_populates="instrument", cascade="all, delete-orphan")
