from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Wallet(Base):
    __tablename__ = 'wallets'
    
    wallet_uid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    balance = Column(Numeric(precision=15, scale=2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship with transactions
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wallet(wallet_uid='{self.wallet_uid}', username='{self.username}', balance={self.balance})>"


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_uid = Column(String(36), ForeignKey('wallets.wallet_uid'), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'top_up' or 'payment'
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with wallet
    wallet = relationship("Wallet", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id='{self.id}', wallet_uid='{self.wallet_uid}', amount={self.amount}, type='{self.transaction_type}')>"
