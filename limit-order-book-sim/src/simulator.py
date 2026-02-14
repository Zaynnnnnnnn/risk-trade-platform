from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple

from .matching_engine import MatchingEngine
from .types import Limit, Market, Side
from .strategies.market_maker import MarketMaker, MMConfig
from .tagged import TaggedTrade


@dataclass
class SimConfig:
    seed: int = 42
    steps: int = 5_000
    start_mid: int = 10_000

    # order flow
    limit_qty: int = 10
    market_qty: int = 5
    prob_market_order: float = 0.30

    # mid dynamics
    prob_mid_move: float = 0.20
    mid_move_ticks: int = 1

    # external liquidity placement
    ext_limit_min_offset: int = 8
    ext_limit_max_offset: int = 20

    # toxic flow
    momentum_bias: float = 0.60

    # volatility model (CHANGED)
    vol_window: int = 50
    vol_k: float = 3.0            # was 2.0
    base_spread_floor: int = 3    # was 2

    # alpha (CHANGED)
    alpha_strength: int = 2       # was 1


def run_simulation(cfg: SimConfig) -> Tuple[List[int], List[float], List[int], List[int], List[TaggedTrade]]:
    random.seed(cfg.seed)

    eng = MatchingEngine()

    mm = MarketMaker(
        eng,
        MMConfig(
            base_spread=4,        # will be overwritten dynamically each step
            inventory_skew=0.6,
            order_size=5,
            max_inventory=200,
            refresh_ticks=2,
        ),
    )

    mid = cfg.start_mid

    mid_series: List[int] = []
    pnl_series: List[float] = []
    inv_series: List[int] = []
    cash_series: List[int] = []
    tagged_trades: List[TaggedTrade] = []

    recent_mid_changes: List[int] = []

    for t in range(cfg.steps):
        prev_mid = mid

        # --- mid random walk ---
        if random.random() < cfg.prob_mid_move:
            mid += random.choice([-cfg.mid_move_ticks, cfg.mid_move_ticks])

        mid_change = mid - prev_mid

        # --- rolling volatility estimate ---
        recent_mid_changes.append(mid_change)
        if len(recent_mid_changes) > cfg.vol_window:
            recent_mid_changes.pop(0)

        if len(recent_mid_changes) > 1:
            vol = sum(abs(x) for x in recent_mid_changes) / len(recent_mid_changes)
        else:
            vol = 0.0

        dynamic_spread = cfg.base_spread_floor + int(cfg.vol_k * vol)
        mm.cfg.base_spread = max(cfg.base_spread_floor, dynamic_spread)

        # --- short-term mean reversion alpha ---
        alpha_bias = 0
        if len(recent_mid_changes) >= 3:
            last_moves = recent_mid_changes[-3:]
            if all(x > 0 for x in last_moves):
                alpha_bias = -cfg.alpha_strength
            elif all(x < 0 for x in last_moves):
                alpha_bias = cfg.alpha_strength

        adjusted_mid = mid + alpha_bias

        # --- MM quotes ---
        mm.step(t, adjusted_mid)

        oid = f"ext_{t}"

        # --- external order flow ---
        if random.random() < cfg.prob_market_order:
            if mid_change > 0:
                side = Side.BUY if random.random() < cfg.momentum_bias else Side.SELL
            elif mid_change < 0:
                side = Side.SELL if random.random() < cfg.momentum_bias else Side.BUY
            else:
                side = random.choice([Side.BUY, Side.SELL])

            new_trades = eng.process(Market(order_id=oid, side=side, qty=cfg.market_qty))

        else:
            side = random.choice([Side.BUY, Side.SELL])
            offset = random.randint(cfg.ext_limit_min_offset, cfg.ext_limit_max_offset)
            price = mid - offset if side == Side.BUY else mid + offset
            new_trades = eng.process(Limit(order_id=oid, side=side, price=price, qty=cfg.limit_qty))

        # --- tag and update MM ---
        for tr in new_trades:
            if tr.maker_order_id.startswith("mm_bid_"):
                mm_side = "BID"
            elif tr.maker_order_id.startswith("mm_ask_"):
                mm_side = "ASK"
            else:
                mm_side = "NONE"

            tagged_trades.append(
                TaggedTrade(
                    step=t,
                    mid=mid,
                    price=tr.price,
                    qty=tr.qty,
                    maker_order_id=tr.maker_order_id,
                    taker_order_id=tr.taker_order_id,
                    mm_side=mm_side,
                )
            )

            mm.on_trade(tr)

        mid_series.append(mid)
        inv_series.append(mm.inventory)
        cash_series.append(mm.cash)
        pnl_series.append(mm.mark_to_market(mid))

    # --- flatten inventory at end ---
    if mm.inventory != 0:
        side = Side.SELL if mm.inventory > 0 else Side.BUY
        qty = abs(mm.inventory)
        _ = eng.process(Market(order_id="mm_flatten", side=side, qty=qty))

        # record final state
        mid_series.append(mid)
        inv_series.append(mm.inventory)
        cash_series.append(mm.cash)
        pnl_series.append(mm.mark_to_market(mid))

    return mid_series, pnl_series, inv_series, cash_series, tagged_trades
