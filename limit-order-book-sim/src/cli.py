from __future__ import annotations

import argparse

from .simulator import run_simulation, SimConfig
from .metrics import summary_stats
from .experiments import monte_carlo, grid_search


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mc", action="store_true", help="Run Monte Carlo across many seeds")
    p.add_argument("--grid", action="store_true", help="Run a small grid search (uses Monte Carlo)")
    p.add_argument("--n", type=int, default=20, help="Number of seeds for Monte Carlo")
    args = p.parse_args()

    base_cfg = SimConfig()

    # ---- GRID SEARCH ----
    if args.grid:
        seeds = list(range(1, args.n + 1))

        # Small, defensible grid (don’t overfit)
        param_grid = [
            {"momentum_bias": 0.55},
            {"momentum_bias": 0.60},
            {"momentum_bias": 0.65},
        ]

        results = grid_search(base_cfg, seeds, param_grid)

        print("\nGrid Search (sorted by mean PnL):")
        for r in results:
            print(
                f"momentum_bias={r['momentum_bias']:.2f} | "
                f"pnl_mean={r['pnl_mean']:.2f} | pnl_p05={r['pnl_p05']:.2f} | pnl_p95={r['pnl_p95']:.2f} | "
                f"fills_mean={r['fills_mean']:.1f} | spread_mean={r['spread_mean']:.2f} | adv_mean={r['adv_mean']:.2f} | "
                f"dd_mean={r['dd_mean']:.2f}"
            )
        return

    # ---- MONTE CARLO ----
    if args.mc:
        seeds = list(range(1, args.n + 1))
        rows, summ = monte_carlo(base_cfg, seeds)

        print("\nMonte Carlo Summary")
        print(f"Seeds: {int(summ['n'])}")
        print(f"PnL mean/std: {summ['pnl_mean']:.2f} / {summ['pnl_std']:.2f}")
        print(f"PnL p05/p50/p95: {summ['pnl_p05']:.2f} / {summ['pnl_p50']:.2f} / {summ['pnl_p95']:.2f}")
        print(f"Avg fills: {summ['fills_mean']:.1f}")
        print(f"Avg spread capture (ticks): {summ['spread_mean']:.2f}")
        print(f"Avg adverse selection (ticks): {summ['adv_mean']:.2f}")
        print(f"Avg max drawdown: {summ['dd_mean']:.2f}")

        # show worst/best 3 seeds quickly
        rows_sorted = sorted(rows, key=lambda r: r["final_pnl"])
        print("\nWorst 3 seeds:")
        for r in rows_sorted[:3]:
            print(f"seed={int(r['seed'])} pnl={r['final_pnl']:.2f} dd={r['max_drawdown']:.2f} fills={r['mm_fills']:.0f}")

        print("\nBest 3 seeds:")
        for r in rows_sorted[-3:][::-1]:
            print(f"seed={int(r['seed'])} pnl={r['final_pnl']:.2f} dd={r['max_drawdown']:.2f} fills={r['mm_fills']:.0f}")

        return

    # ---- SINGLE RUN (default) ----
    mid, pnl, inv, cash, tagged_trades = run_simulation(base_cfg)
    stats = summary_stats(mid, pnl, inv, cash, tagged_trades)

    print("\nSimulation complete")
    print(f"Trades executed: {stats['trades']}")
    print(f"Final PnL: {stats['final_pnl']:.2f}")
    print(f"Max Drawdown: {stats['max_drawdown']:.2f}")
    print(f"Sharpe (approx): {stats['sharpe']:.2f}")
    print(f"Max Inventory: {stats['max_inventory']}")
    print(f"Min Inventory: {stats['min_inventory']}")
    print(f"End Inventory: {stats['end_inventory']}")
    print(f"End Cash: {stats['end_cash']}")
    print(f"Mid start/end: {stats['mid_start']} -> {stats['mid_end']}")

    print("\nExecution quality (MM as maker only)")
    print(f"MM fills: {stats['mm_fills']} (bid={stats['bid_fills']}, ask={stats['ask_fills']})")
    print(f"Avg spread capture (ticks): {stats['avg_spread_capture_ticks']:.2f}")
    print(f"Avg adverse selection (ticks): {stats['avg_adverse_selection_ticks']:.2f}")


if __name__ == "__main__":
    main()
