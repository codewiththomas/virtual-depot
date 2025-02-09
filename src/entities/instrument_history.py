from sqlalchemy import Column, Integer, Date, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base_entity import Base

class InstrumentHistory(Base):
    __tablename__ = 'instrument_history'

    instrument_id = Column(Integer, ForeignKey('instrument.id', ondelete="CASCADE"), primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    dividend = Column(Float, nullable=False, default=0)
    split_factor = Column(Float, nullable=False, default=1.0)

    # Relationship back to Instrument
    instrument = relationship("Instrument", back_populates="histories")

    __table_args__ = (
        Index('idx_instrument_history_date', 'date'),
    )
