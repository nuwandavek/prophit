from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from contextlib import contextmanager
from ..constants import (
    DATABASE_URL, 
    DEFAULT_LIQUIDITY_PARAM, 
    DEFAULT_MARKET_TYPE, 
    DEFAULT_MARKET_STATUS
)

Base = declarative_base()

class Market(Base):
    __tablename__ = 'markets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    type = Column(String, default=DEFAULT_MARKET_TYPE, nullable=False)
    status = Column(String, default=DEFAULT_MARKET_STATUS, nullable=False)
    created_at = Column(DateTime, default=func.now())
    resolution_date = Column(DateTime)
    outcome = Column(Integer)
    liquidity_param = Column(Float, default=DEFAULT_LIQUIDITY_PARAM)
    
    # Relationship to positions
    positions = relationship("Position", back_populates="market")


class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    outcome = Column(Integer, nullable=False)
    shares = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationship to market
    market = relationship("Market", back_populates="positions")


# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Get database session with context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()