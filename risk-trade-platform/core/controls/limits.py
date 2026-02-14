from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class LimitDecision:
    status: str  # PASS | WARN | BLOCK
    reasons: List[str]


# Simple per-book limits (we'll move to DB/config later)
BOOK_LIMITS = {
    "RATES": {
        "max_trade_notional": 2_000_000,   # £2m per trade
        "max_book_dv01": 2_000.0,          # £2k per bp
    }
}


def evaluate_limits(
    book: str,
    trade_notional: float,
    trade_dv01: float,
    current_book_dv01: float,
) -> LimitDecision:
    limits = BOOK_LIMITS.get(book)
    if limits is None:
        # No config => warn, but allow (real teams vary; we’ll allow for now)
        return LimitDecision(status="WARN", reasons=["NO_LIMITS_CONFIGURED"])

    reasons: List[str] = []
    status = "PASS"

    if trade_notional > limits["max_trade_notional"]:
        reasons.append("LIM_TRADE_NOTIONAL_EXCEEDED")
        status = "BLOCK"

    projected = current_book_dv01 + trade_dv01
    if projected > limits["max_book_dv01"]:
        reasons.append("LIM_BOOK_DV01_EXCEEDED")
        status = "BLOCK"

    return LimitDecision(status=status, reasons=reasons)
