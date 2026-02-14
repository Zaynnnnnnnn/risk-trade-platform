from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from infra.db.session import SessionLocal

router = APIRouter()


@router.get("/status")
def status() -> dict[str, str]:
    # basic DB ping
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    return {"api": "ok", "db": "ok"}
