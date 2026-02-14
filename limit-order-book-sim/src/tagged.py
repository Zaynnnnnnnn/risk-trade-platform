from dataclasses import dataclass


@dataclass(frozen=True)
class TaggedTrade:
    step: int
    mid: int
    price: int
    qty: int
    maker_order_id: str
    taker_order_id: str
    mm_side: str  # "BID", "ASK", or "NONE"
