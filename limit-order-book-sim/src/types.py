from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

    @property
    def opp(self) -> "Side":
        return Side.SELL if self == Side.BUY else Side.BUY


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    order_id: str
    side: Side
    qty: int                       # shares, integer
    order_type: OrderType
    price: Optional[int] = None    # integer ticks (e.g., cents). None for market orders.

    # runtime fields
    remaining: int = field(init=False)
    status: OrderStatus = field(init=False, default=OrderStatus.OPEN)

    def __post_init__(self) -> None:
        if self.qty <= 0:
            raise ValueError("qty must be > 0")
        self.remaining = self.qty
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("limit order requires price")
        if self.order_type == OrderType.MARKET and self.price is not None:
            raise ValueError("market order must not have price")


@dataclass(frozen=True)
class Trade:
    price: int
    qty: int
    taker_order_id: str
    maker_order_id: str


@dataclass(frozen=True)
class Cancel:
    order_id: str


@dataclass(frozen=True)
class Limit:
    order_id: str
    side: Side
    price: int
    qty: int


@dataclass(frozen=True)
class Market:
    order_id: str
    side: Side
    qty: int
