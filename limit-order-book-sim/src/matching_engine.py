from __future__ import annotations

from typing import List, Union

from .order_book import OrderBook
from .types import Cancel, Limit, Market, Order, OrderStatus, OrderType, Side, Trade


Event = Union[Limit, Market, Cancel]


class MatchingEngine:
    def __init__(self) -> None:
        self.book = OrderBook()

    def process(self, event: Event) -> List[Trade]:
        if isinstance(event, Cancel):
            self.book.cancel(event.order_id)
            return []

        if isinstance(event, Limit):
            order = Order(
                order_id=event.order_id,
                side=event.side,
                qty=event.qty,
                order_type=OrderType.LIMIT,
                price=event.price,
            )
            return self._execute(order)

        if isinstance(event, Market):
            order = Order(
                order_id=event.order_id,
                side=event.side,
                qty=event.qty,
                order_type=OrderType.MARKET,
                price=None,
            )
            return self._execute(order)

        raise TypeError("unknown event type")

    def _execute(self, taker: Order) -> List[Trade]:
        trades: List[Trade] = []

        # helper to get best price on opposite side
        def best_opp_price() -> int | None:
            return self.book.best_ask() if taker.side == Side.BUY else self.book.best_bid()

        while taker.remaining > 0:
            opp_price = best_opp_price()
            if opp_price is None:
                break

            # If taker is LIMIT, enforce price constraint
            if taker.order_type == OrderType.LIMIT:
                assert taker.price is not None
                if taker.side == Side.BUY and opp_price > taker.price:
                    break
                if taker.side == Side.SELL and opp_price < taker.price:
                    break

            maker_side = taker.side.opp
            maker = self.book.pop_next(maker_side, opp_price)
            if maker is None:
                # level empty (lazy cleanup); loop again
                continue

            # Execute at maker (resting) price (typical exchange behavior)
            exec_price = opp_price
            exec_qty = min(taker.remaining, maker.remaining)

            taker.remaining -= exec_qty
            maker.remaining -= exec_qty

            trades.append(
                Trade(
                    price=exec_price,
                    qty=exec_qty,
                    taker_order_id=taker.order_id,
                    maker_order_id=maker.order_id,
                )
            )

            # Update maker status
            if maker.remaining == 0:
                maker.status = OrderStatus.FILLED
            else:
                maker.status = OrderStatus.PARTIALLY_FILLED

            # Update taker status (for completeness)
            if taker.remaining == 0:
                taker.status = OrderStatus.FILLED
            else:
                taker.status = OrderStatus.PARTIALLY_FILLED

        # If LIMIT taker still has remaining, it becomes a resting order (maker)
        if taker.order_type == OrderType.LIMIT and taker.remaining > 0:
            # Resting order keeps original qty notion, but remaining is what matters for fills
            self.book.add_limit(taker)

        return trades
