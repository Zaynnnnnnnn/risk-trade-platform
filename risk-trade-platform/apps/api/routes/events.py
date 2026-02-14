from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from sqlalchemy.orm import Session

from infra.db.models import Event
from infra.db.session import SessionLocal

router = APIRouter()


def get_db() -> Session:
    return SessionLocal()


@router.get("/")
def list_events(limit: int = 50) -> list[dict[str, Any]]:
    """
    Returns most recent events (audit trail).
    """

    db = get_db()

    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "payload": json.loads(e.payload),
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
