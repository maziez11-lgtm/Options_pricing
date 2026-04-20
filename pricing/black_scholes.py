"""Black-Scholes model for pricing European options."""

import math
from scipy.stats import norm


def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    return _d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European call option.

    Args:
        S: Current spot price
        K: Strike price
        T: Time to expiry in years
        r: Risk-free rate (annualised)
        sigma: Volatility (annualised)
    """
    if T <= 0:
        return max(S - K, 0.0)
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)


def put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European put option."""
    if T <= 0:
        return max(K - S, 0.0)
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def implied_volatility(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    tol: float = 1e-6,
    max_iter: int = 200,
) -> float:
    """Solve for implied volatility via Newton-Raphson iteration."""
    from pricing.greeks import vega as _vega

    sigma = 0.2  # initial guess
    price_fn = call_price if option_type == "call" else put_price

    for _ in range(max_iter):
        price = price_fn(S, K, T, r, sigma)
        v = _vega(S, K, T, r, sigma)
        diff = market_price - price
        if abs(diff) < tol:
            return sigma
        if v < 1e-10:
            break
        sigma += diff / v

    raise ValueError(
        f"Implied volatility did not converge for market_price={market_price}"
    )
