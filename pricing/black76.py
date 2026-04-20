"""Black-76 model for European options on futures (TTF natural gas convention).

Underlying: TTF forward price in EUR/MWh.
"""

import math
from scipy.stats import norm


def _d1(F: float, K: float, T: float, sigma: float) -> float:
    return (math.log(F / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))


def _d2(F: float, K: float, T: float, sigma: float) -> float:
    return _d1(F, K, T, sigma) - sigma * math.sqrt(T)


def call_price(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European call on a TTF futures contract.

    Args:
        F: Forward / futures price (EUR/MWh)
        K: Strike price (EUR/MWh)
        T: Time to expiry in years
        r: Risk-free discount rate (annualised)
        sigma: Lognormal (Black) implied volatility
    """
    if T <= 0:
        return math.exp(-r * T) * max(F - K, 0.0)
    d1 = _d1(F, K, T, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    return math.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))


def put_price(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European put on a TTF futures contract."""
    if T <= 0:
        return math.exp(-r * T) * max(K - F, 0.0)
    d1 = _d1(F, K, T, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    return math.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def price(
    F: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
) -> float:
    """Dispatch to call_price or put_price."""
    if option_type == "call":
        return call_price(F, K, T, r, sigma)
    if option_type == "put":
        return put_price(F, K, T, r, sigma)
    raise ValueError(f"Unknown option_type '{option_type}'. Use 'call' or 'put'.")
