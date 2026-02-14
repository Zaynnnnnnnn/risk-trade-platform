from src.matching_engine import MatchingEngine
from src.types import Cancel, Limit, Market, Side


def test_cancel_removes_order_from_matching():
    eng = MatchingEngine()
    eng.process(Limit(order_id="S1", side=Side.SELL, price=100, qty=5))
    eng.process(Cancel(order_id="S1"))

    trades = eng.process(Market(order_id="B1", side=Side.BUY, qty=3))
    assert trades == []
