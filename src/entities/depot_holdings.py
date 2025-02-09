from sqlalchemy import Column, Float, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base_entity import Base

class DepotHoldings(Base):
    __tablename__ = 'depot_holdings'

    depot_id = Column(Integer, ForeignKey('depot.id', ondelete="CASCADE"), primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instrument.id', ondelete="CASCADE"), primary_key=True)
    quantity = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_non_negative"),
    )

    # Relationships back to Depot and Instrument
    depot = relationship("Depot", back_populates="holdings")
    instrument = relationship("Instrument", back_populates="holdings")
