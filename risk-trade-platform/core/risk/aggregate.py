from typing import List
from core.risk.dv01 import calculate_bond_dv01


def portfolio_dv01(trades: List[dict]) -> dict:
    total_dv01 = 0.0
    total_notional = 0.0
    breakdown = []

    for trade in trades:
        risk = calculate_bond_dv01(
            symbol=trade["symbol"],
            quantity=trade["quantity"],
            price=trade["price"],
        )

        total_dv01 += risk.dv01
        total_notional += risk.notional

        breakdown.append(
            {
                "symbol": risk.symbol,
                "dv01": risk.dv01,
                "notional": risk.notional,
            }
        )

    return {
        "portfolio_notional": total_notional,
        "portfolio_dv01": total_dv01,
        "breakdown": breakdown,
    }
