from sqlalchemy import Column, Float, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base_entity import Base

class DepotBalance(Base):
    __tablename__ = 'depot_balance'

    depot_id = Column(Integer, ForeignKey('depot.id', ondelete="CASCADE"), primary_key=True)
    currency = Column(String(3), nullable=False)  # ISO currency code
    cash_balance = Column(Float, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("LENGTH(currency) = 3", name="currency_length_check"),
    )

    # Relationship back to Depot
    depot = relationship("Depot", back_populates="balances")
