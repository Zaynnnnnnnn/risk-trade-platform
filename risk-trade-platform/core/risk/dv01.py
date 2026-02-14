from dataclasses import dataclass


@dataclass
class BondRiskResult:
    symbol: str
    notional: float
    dv01: float


# Simple duration assumptions (hardcoded for now — later we externalise)
DURATION_MAP = {
    "UKT10Y": 8.5,
    "UKT5Y": 4.7,
    "UKT30Y": 18.0,
}


def calculate_bond_dv01(symbol: str, quantity: float, price: float) -> BondRiskResult:
    """
    Approx DV01 formula:
        DV01 = Notional × ModifiedDuration × 0.0001
    """

    if symbol not in DURATION_MAP:
        raise ValueError(f"No duration configured for {symbol}")

    notional = quantity * price / 100  # convert price quote to cash notional
    duration = DURATION_MAP[symbol]

    dv01 = notional * duration * 0.0001

    return BondRiskResult(symbol=symbol, notional=notional, dv01=dv01)
