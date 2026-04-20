"""Implied volatility solvers using Brent's method.

Supports Black-76 (lognormal vol) and Bachelier (normal vol) models.
"""

from __future__ import annotations

from scipy.optimize import brentq

from pricing import black76, bachelier


_BRENT_XTOL = 1e-8
_BRENT_MAXITER = 200


def _bracket(
    price_fn,
    market_price: float,
    sigma_lo: float = 1e-6,
    sigma_hi: float = 20.0,
) -> tuple[float, float]:
    """Verify the bracket [sigma_lo, sigma_hi] straddles market_price.

    Raises ValueError if no bracket can be found.
    """
    if price_fn(sigma_lo) > market_price:
        raise ValueError(
            "market_price is below the intrinsic value; "
            "check inputs or use the other model."
        )
    if price_fn(sigma_hi) < market_price:
        raise ValueError(
            f"market_price exceeds model price at sigma={sigma_hi}; "
            "increase sigma_hi or check inputs."
        )
    return sigma_lo, sigma_hi


def black76_iv(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    sigma_lo: float = 1e-6,
    sigma_hi: float = 20.0,
) -> float:
    """Implied lognormal volatility for a Black-76 option via Brent's method.

    Args:
        market_price: Observed option price (EUR/MWh)
        F: Forward price (EUR/MWh)
        K: Strike price (EUR/MWh)
        T: Time to expiry in years
        r: Risk-free rate (annualised)
        option_type: 'call' or 'put'
        sigma_lo: Lower bound for vol search
        sigma_hi: Upper bound for vol search

    Returns:
        Implied lognormal volatility
    """
    def objective(sigma: float) -> float:
        return black76.price(F, K, T, r, sigma, option_type) - market_price

    lo, hi = _bracket(lambda s: black76.price(F, K, T, r, s, option_type), market_price, sigma_lo, sigma_hi)
    return brentq(objective, lo, hi, xtol=_BRENT_XTOL, maxiter=_BRENT_MAXITER)


def bachelier_iv(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    sigma_lo: float = 1e-6,
    sigma_hi: float = 500.0,
) -> float:
    """Implied normal (Bachelier) volatility in EUR/MWh via Brent's method.

    Args:
        market_price: Observed option price (EUR/MWh)
        F: Forward price (EUR/MWh) — may be negative
        K: Strike price (EUR/MWh)
        T: Time to expiry in years
        r: Risk-free rate (annualised)
        option_type: 'call' or 'put'
        sigma_lo: Lower bound for normal vol search (EUR/MWh)
        sigma_hi: Upper bound for normal vol search (EUR/MWh)

    Returns:
        Implied normal volatility in EUR/MWh
    """
    def objective(sigma_n: float) -> float:
        return bachelier.price(F, K, T, r, sigma_n, option_type) - market_price

    lo, hi = _bracket(lambda s: bachelier.price(F, K, T, r, s, option_type), market_price, sigma_lo, sigma_hi)
    return brentq(objective, lo, hi, xtol=_BRENT_XTOL, maxiter=_BRENT_MAXITER)


def solve(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    model: str = "black76",
) -> float:
    """Unified implied vol entry point.

    Args:
        model: 'black76' (lognormal) or 'bachelier' (normal, for negative prices)
    """
    if model == "black76":
        return black76_iv(market_price, F, K, T, r, option_type)
    if model == "bachelier":
        return bachelier_iv(market_price, F, K, T, r, option_type)
    raise ValueError(f"Unknown model '{model}'. Use 'black76' or 'bachelier'.")
