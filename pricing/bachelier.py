"""Bachelier (normal) model for options — used when TTF prices can go negative.

Uses normal (absolute) volatility sigma_n in EUR/MWh rather than a lognormal vol.
"""

import math
from scipy.stats import norm


def _d(F: float, K: float, T: float, sigma_n: float) -> float:
    """Standardised moneyness."""
    return (F - K) / (sigma_n * math.sqrt(T))


def call_price(F: float, K: float, T: float, r: float, sigma_n: float) -> float:
    """Price a European call under the Bachelier model.

    Args:
        F: Forward price (EUR/MWh) — may be negative
        K: Strike price (EUR/MWh)
        T: Time to expiry in years
        r: Risk-free discount rate (annualised)
        sigma_n: Normal (Bachelier) volatility in EUR/MWh
    """
    if T <= 0:
        return math.exp(-r * T) * max(F - K, 0.0)
    vol_sqrt_T = sigma_n * math.sqrt(T)
    d = (F - K) / vol_sqrt_T
    return math.exp(-r * T) * ((F - K) * norm.cdf(d) + vol_sqrt_T * norm.pdf(d))


def put_price(F: float, K: float, T: float, r: float, sigma_n: float) -> float:
    """Price a European put under the Bachelier model."""
    if T <= 0:
        return math.exp(-r * T) * max(K - F, 0.0)
    vol_sqrt_T = sigma_n * math.sqrt(T)
    d = (F - K) / vol_sqrt_T
    return math.exp(-r * T) * ((K - F) * norm.cdf(-d) + vol_sqrt_T * norm.pdf(d))


def price(
    F: float,
    K: float,
    T: float,
    r: float,
    sigma_n: float,
    option_type: str = "call",
) -> float:
    """Dispatch to call_price or put_price."""
    if option_type == "call":
        return call_price(F, K, T, r, sigma_n)
    if option_type == "put":
        return put_price(F, K, T, r, sigma_n)
    raise ValueError(f"Unknown option_type '{option_type}'. Use 'call' or 'put'.")
