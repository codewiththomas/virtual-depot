from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, CheckConstraint, func, Index
from sqlalchemy.orm import relationship
from .base_entity import Base

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey('instrument.id', ondelete="CASCADE"), nullable=False)
    depot_id = Column(Integer, ForeignKey('depot.id', ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, server_default=func.current_timestamp())
    trading_fee = Column(Float, nullable=False, default=1.0)
    price_per_unit = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    direction = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("price_per_unit >= 0", name="price_per_unit_non_negative"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("direction IN ('BUY', 'SELL')", name="direction_check"),
        Index('idx_transaction_date', 'date'),
        Index('idx_transaction_depot', 'depot_id'),
    )

    # Relationships back to Instrument and Depot
    instrument = relationship("Instrument", back_populates="transactions")
    depot = relationship("Depot", back_populates="transactions")
