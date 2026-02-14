from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from ..types import Limit, Cancel, Side
from ..matching_engine import MatchingEngine


@dataclass
class MMConfig:
    base_spread: int = 2           # ticks from mid
    inventory_skew: float = 0.2    # how aggressively to skew quotes
    order_size: int = 10
    max_inventory: int = 200
    refresh_ticks: int = 2         # refresh quotes if mid moves this much


class MarketMaker:
    """
    Inventory-aware market maker.

    Maintains one bid and one ask.
    Refreshes quotes when mid moves enough that current quotes are stale.
    """

    def __init__(self, engine: MatchingEngine, cfg: MMConfig):
        self.engine = engine
        self.cfg = cfg

        self.inventory = 0
        self.cash = 0

        self.bid_id: Optional[str] = None
        self.ask_id: Optional[str] = None
        self.bid_price: Optional[int] = None
        self.ask_price: Optional[int] = None

    def mark_to_market(self, mid: int) -> float:
        return self.cash + self.inventory * mid

    def on_trade(self, trade) -> None:
        if trade.maker_order_id == self.bid_id:
            self.inventory += trade.qty
            self.cash -= trade.qty * trade.price
            # bid got hit -> we should replace it later
            self.bid_id = None
            self.bid_price = None

        elif trade.maker_order_id == self.ask_id:
            self.inventory -= trade.qty
            self.cash += trade.qty * trade.price
            # ask got hit -> replace later
            self.ask_id = None
            self.ask_price = None

    def quote_prices(self, mid: int) -> Tuple[int, int]:
        skew = int(self.inventory * self.cfg.inventory_skew)

        bid = mid - self.cfg.base_spread - skew
        ask = mid + self.cfg.base_spread - skew

        if bid >= ask:
            ask = bid + 1

        return bid, ask

    def _quotes_stale(self, mid: int) -> bool:
        if self.bid_price is None or self.ask_price is None:
            return True
        # if mid moved away, refresh
        if abs((mid - self.bid_price) - self.cfg.base_spread) >= self.cfg.refresh_ticks:
            return True
        if abs((self.ask_price - mid) - self.cfg.base_spread) >= self.cfg.refresh_ticks:
            return True
        return False

    def step(self, t: int, mid: int):
        disable_bid = self.inventory >= self.cfg.max_inventory
        disable_ask = self.inventory <= -self.cfg.max_inventory

        # refresh rule
        if self._quotes_stale(mid):
            if self.bid_id is not None:
                self.engine.process(Cancel(self.bid_id))
                self.bid_id = None
                self.bid_price = None
            if self.ask_id is not None:
                self.engine.process(Cancel(self.ask_id))
                self.ask_id = None
                self.ask_price = None

        bid_price, ask_price = self.quote_prices(mid)

        if not disable_bid and self.bid_id is None:
            self.bid_id = f"mm_bid_{t}"
            self.bid_price = bid_price
            self.engine.process(Limit(self.bid_id, Side.BUY, bid_price, self.cfg.order_size))

        if not disable_ask and self.ask_id is None:
            self.ask_id = f"mm_ask_{t}"
            self.ask_price = ask_price
            self.engine.process(Limit(self.ask_id, Side.SELL, ask_price, self.cfg.order_size))
