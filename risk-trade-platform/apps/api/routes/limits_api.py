from __future__ import annotations

from fastapi import APIRouter

from core.controls.limits import BOOK_LIMITS

router = APIRouter()


@router.get("/limits")
def limits() -> dict:
    return BOOK_LIMITS
