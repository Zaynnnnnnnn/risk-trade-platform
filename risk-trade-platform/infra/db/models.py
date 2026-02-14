from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    book = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)  # store JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class RiskRun(Base):
    __tablename__ = "risk_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book = Column(String, nullable=False)
    report = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    key = Column(String, primary_key=True)
    response = Column(Text, nullable=False)  # store JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
