from sqlalchemy import Column, BigInteger, Float, Integer, Boolean, String

from src.db.base import Base

class User(Base):
    __tablename__ = 'user'

    chat_id = Column(BigInteger, primary_key=True, unique=True)
    balance = Column(Float, default=0)

class Paylink(Base):
    __tablename__ = 'paylink'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    is_payed = Column(Boolean, nullable=False, default=False)
    amount = Column(Float, nullable=False)

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    asset = Column(String, nullable=False)
    network = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    address = Column(String, nullable=False)
    paylink_id = Column(Integer, nullable=False)
