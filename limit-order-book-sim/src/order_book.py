from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
from typing import Deque, Dict, Optional, Tuple

from .types import Order, OrderStatus, Side


@dataclass
class _Level:
    order_ids: Deque[str]


class OrderBook:
    """
    Simple limit order book with:
      - price levels storing FIFO queues of order_ids
      - lazy heaps to get best bid/ask quickly
    Prices are integer ticks (e.g., cents).
    """

    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}

        # price -> level
        self.bids: Dict[int, _Level] = {}
        self.asks: Dict[int, _Level] = {}

        # heaps of prices (lazy delete)
        self._bid_heap: list[int] = []   # store -price
        self._ask_heap: list[int] = []   # store +price

    def best_bid(self) -> Optional[int]:
        while self._bid_heap:
            p = -self._bid_heap[0]
            level = self.bids.get(p)
            if level and level.order_ids:
                return p
            heapq.heappop(self._bid_heap)
        return None

    def best_ask(self) -> Optional[int]:
        while self._ask_heap:
            p = self._ask_heap[0]
            level = self.asks.get(p)
            if level and level.order_ids:
                return p
            heapq.heappop(self._ask_heap)
        return None

    def add_limit(self, order: Order) -> None:
        if order.order_id in self.orders:
            raise ValueError("duplicate order_id")
        if order.price is None:
            raise ValueError("limit order must have price")

        self.orders[order.order_id] = order

        book = self.bids if order.side == Side.BUY else self.asks
        heap = self._bid_heap if order.side == Side.BUY else self._ask_heap

        if order.price not in book:
            book[order.price] = _Level(deque())
            heapq.heappush(heap, -order.price if order.side == Side.BUY else order.price)

        book[order.price].order_ids.append(order.order_id)

    def cancel(self, order_id: str) -> bool:
        """
        Marks an order as cancelled. We don't remove it from the deque immediately (lazy).
        Returns True if cancelled, False if not found/cannot cancel.
        """
        o = self.orders.get(order_id)
        if o is None:
            return False
        if o.status in {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}:
            return False

        o.remaining = 0
        o.status = OrderStatus.CANCELLED
        return True

    def _peek_next_order_id(self, side: Side, price: int) -> Optional[str]:
        book = self.bids if side == Side.BUY else self.asks
        level = book.get(price)
        if not level:
            return None

        # pop cancelled/filled orders lazily
        while level.order_ids:
            oid = level.order_ids[0]
            o = self.orders.get(oid)
            if o is None:
                level.order_ids.popleft()
                continue
            if o.status in {OrderStatus.CANCELLED, OrderStatus.FILLED} or o.remaining <= 0:
                level.order_ids.popleft()
                continue
            return oid

        return None

    def pop_next(self, side: Side, price: int) -> Optional[Order]:
        """
        Returns the next active order at price for that side (FIFO), without removing from orders dict.
        If the order becomes filled later, the queue will advance lazily.
        """
        oid = self._peek_next_order_id(side, price)
        if oid is None:
            return None
        return self.orders[oid]

    def book_state(self) -> Tuple[Optional[int], Optional[int]]:
        return self.best_bid(), self.best_ask()
