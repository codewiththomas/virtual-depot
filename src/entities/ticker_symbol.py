from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base_entity import Base

class TickerSymbol(Base):
    __tablename__ = 'ticker_symbol'

    symbol = Column(String, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instrument.id', ondelete="CASCADE"), nullable=False)

    # Relationship back to Instrument
    instrument = relationship("Instrument", back_populates="ticker_symbols")
