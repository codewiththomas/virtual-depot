from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from .base_entity import Base

class Depot(Base):
    __tablename__ = 'depot'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cash_balance = Column(Float, nullable=False, default=0)

    # Relationships to balances, holdings, and transactions
    balances = relationship("DepotBalance", back_populates="depot", cascade="all, delete-orphan")
    holdings = relationship("DepotHoldings", back_populates="depot", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="depot", cascade="all, delete-orphan")
