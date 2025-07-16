# SQLAlchemy models are now in database.py
# This file can be removed or used for Pydantic schemas for API validation

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class MarketCreate(BaseModel):
    question: str
    type: str = 'binary'
    status: str = 'active'
    liquidity_param: float = 100.0


class MarketResponse(BaseModel):
    id: int
    question: str
    type: str
    status: str
    created_at: datetime
    resolution_date: Optional[datetime] = None
    outcome: Optional[int] = None
    liquidity_param: float

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    user_id: str
    market_id: int
    outcome: int
    shares: float
    cost: float


class PositionResponse(BaseModel):
    id: int
    user_id: str
    market_id: int
    outcome: int
    shares: float
    cost: float
    timestamp: datetime

    class Config:
        from_attributes = True