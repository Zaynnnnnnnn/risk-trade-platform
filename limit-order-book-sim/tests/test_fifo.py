from src.matching_engine import MatchingEngine
from src.types import Limit, Market, Side


def test_fifo_at_same_price_level():
    eng = MatchingEngine()
    # two sells at same price
    eng.process(Limit(order_id="S1", side=Side.SELL, price=100, qty=3))
    eng.process(Limit(order_id="S2", side=Side.SELL, price=100, qty=3))

    trades = eng.process(Market(order_id="B1", side=Side.BUY, qty=4))
    assert len(trades) == 2
    assert trades[0].maker_order_id == "S1"
    assert trades[0].qty == 3
    assert trades[1].maker_order_id == "S2"
    assert trades[1].qty == 1
