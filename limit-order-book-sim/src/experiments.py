from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Tuple

import numpy as np

from .simulator import SimConfig, run_simulation
from .metrics import summary_stats


def run_one(cfg: SimConfig) -> Dict[str, float]:
    mid, pnl, inv, cash, tagged_trades = run_simulation(cfg)
    stats = summary_stats(mid, pnl, inv, cash, tagged_trades)

    # Keep only numeric fields we care about
    return {
        "seed": float(cfg.seed),
        "final_pnl": float(stats["final_pnl"]),
        "max_drawdown": float(stats["max_drawdown"]),
        "sharpe": float(stats["sharpe"]),
        "mm_fills": float(stats["mm_fills"]),
        "avg_spread_capture_ticks": float(stats["avg_spread_capture_ticks"]),
        "avg_adverse_selection_ticks": float(stats["avg_adverse_selection_ticks"]),
        "end_inventory": float(stats["end_inventory"]),
    }


def monte_carlo(base_cfg: SimConfig, seeds: List[int]) -> Tuple[List[Dict[str, float]], Dict[str, float]]:
    rows: List[Dict[str, float]] = []

    for s in seeds:
        cfg = replace(base_cfg, seed=s)
        rows.append(run_one(cfg))

    # Aggregate
    def col(name: str) -> np.ndarray:
        return np.array([r[name] for r in rows], dtype=float)

    pnl = col("final_pnl")
    dd = col("max_drawdown")
    fills = col("mm_fills")
    spread = col("avg_spread_capture_ticks")
    adv = col("avg_adverse_selection_ticks")

    summary = {
        "n": float(len(rows)),
        "pnl_mean": float(pnl.mean()),
        "pnl_std": float(pnl.std(ddof=1)) if len(pnl) > 1 else 0.0,
        "pnl_p05": float(np.percentile(pnl, 5)),
        "pnl_p50": float(np.percentile(pnl, 50)),
        "pnl_p95": float(np.percentile(pnl, 95)),
        "dd_mean": float(dd.mean()),
        "fills_mean": float(fills.mean()),
        "spread_mean": float(spread.mean()),
        "adv_mean": float(adv.mean()),
    }
    return rows, summary


def grid_search(
    base_cfg: SimConfig,
    seeds: List[int],
    param_grid: List[Dict[str, float]],
) -> List[Dict[str, float]]:
    """
    param_grid items can include any SimConfig fields, e.g.:
      {"momentum_bias": 0.55, "prob_market_order": 0.30}
    """
    results: List[Dict[str, float]] = []

    for params in param_grid:
        cfg = replace(base_cfg, **params)
        rows, summ = monte_carlo(cfg, seeds)

        out = dict(params)
        out.update({
            "n": summ["n"],
            "pnl_mean": summ["pnl_mean"],
            "pnl_std": summ["pnl_std"],
            "pnl_p05": summ["pnl_p05"],
            "pnl_p50": summ["pnl_p50"],
            "pnl_p95": summ["pnl_p95"],
            "fills_mean": summ["fills_mean"],
            "spread_mean": summ["spread_mean"],
            "adv_mean": summ["adv_mean"],
            "dd_mean": summ["dd_mean"],
        })
        results.append(out)

    # Sort by mean PnL descending (research convenience)
    results.sort(key=lambda r: r["pnl_mean"], reverse=True)
    return results
