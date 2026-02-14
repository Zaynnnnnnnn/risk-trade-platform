from src.matching_engine import MatchingEngine
from src.types import Limit, Market, Side


def test_limit_cross_executes_at_resting_price():
    eng = MatchingEngine()

    # resting sell at 101
    trades = eng.process(Limit(order_id="S1", side=Side.SELL, price=101, qty=10))
    assert trades == []

    # aggressive buy limit at 105 crosses -> should execute at 101 (resting)
    trades = eng.process(Limit(order_id="B1", side=Side.BUY, price=105, qty=4))
    assert len(trades) == 1
    assert trades[0].price == 101
    assert trades[0].qty == 4


def test_market_order_consumes_liquidity():
    eng = MatchingEngine()
    eng.process(Limit(order_id="S1", side=Side.SELL, price=101, qty=5))
    eng.process(Limit(order_id="S2", side=Side.SELL, price=102, qty=5))

    trades = eng.process(Market(order_id="B1", side=Side.BUY, qty=7))
    assert sum(t.qty for t in trades) == 7
    assert trades[0].price == 101  # first fills best ask
