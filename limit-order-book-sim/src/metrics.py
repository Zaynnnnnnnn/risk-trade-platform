import numpy as np


def compute_drawdown(series):
    peak = -float("inf")
    max_dd = 0.0
    for x in series:
        peak = max(peak, x)
        dd = x - peak
        max_dd = min(max_dd, dd)
    return float(max_dd)


def compute_sharpe(series):
    returns = np.diff(series)
    if len(returns) < 2:
        return 0.0
    mean = float(np.mean(returns))
    std = float(np.std(returns))
    if std == 0.0:
        return 0.0
    return (mean / std) * np.sqrt(252)


def mm_execution_metrics(tagged_trades, horizon_steps=20):
    # step->mid map for future mid lookup
    step_to_mid = {}
    for tr in tagged_trades:
        step_to_mid[tr.step] = tr.mid

    bid_caps = []
    ask_caps = []
    adv = []

    for tr in tagged_trades:
        if tr.mm_side == "NONE":
            continue

        # spread capture vs mid at fill time
        if tr.mm_side == "BID":
            bid_caps.append(tr.mid - tr.price)
        else:  # ASK
            ask_caps.append(tr.price - tr.mid)

        future_mid = step_to_mid.get(tr.step + horizon_steps, tr.mid)

        # adverse selection proxy
        if tr.mm_side == "BID":
            adv.append(future_mid - tr.price)
        else:
            adv.append(tr.price - future_mid)

    def safe_mean(x):
        return float(np.mean(x)) if x else 0.0

    return {
        "mm_fills": len(bid_caps) + len(ask_caps),
        "bid_fills": len(bid_caps),
        "ask_fills": len(ask_caps),
        "avg_spread_capture_ticks": safe_mean(bid_caps + ask_caps),
        "avg_adverse_selection_ticks": safe_mean(adv),
    }


def summary_stats(mid, pnl, inv, cash, tagged_trades):
    stats = {
        "trades": len(tagged_trades),
        "final_pnl": pnl[-1] if pnl else 0.0,
        "max_drawdown": compute_drawdown(pnl) if pnl else 0.0,
        "sharpe": compute_sharpe(pnl) if pnl else 0.0,
        "max_inventory": max(inv) if inv else 0,
        "min_inventory": min(inv) if inv else 0,
        "end_inventory": inv[-1] if inv else 0,
        "end_cash": cash[-1] if cash else 0,
        "mid_start": mid[0] if mid else None,
        "mid_end": mid[-1] if mid else None,
    }

    stats.update(mm_execution_metrics(tagged_trades))
    return stats
