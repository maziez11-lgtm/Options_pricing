"""TTF natural gas options pricing — Black-76 & Bachelier models.

Conventions:
  - Underlying : TTF forward/futures price in EUR/MWh
  - Expiry     : T in years (e.g. 30 days → T = 30/365)
  - Rate       : risk-free EUR rate, annualised decimal (e.g. 3% → r = 0.03)
  - Vol        : lognormal decimal for Black-76 (e.g. 50% → sigma = 0.50)
                 normal EUR/MWh for Bachelier    (e.g. 8 EUR/MWh → sigma_n = 8.0)

T helpers (re-exported for convenience):
  from black76_ttf import time_to_maturity, maturity_breakdown, t_from_delivery
"""

from __future__ import annotations

import math
import sys
import os
from dataclasses import dataclass

# Ensure the directory containing this file is on sys.path so that ttf_time
# can be found regardless of the working directory the caller uses.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scipy.optimize import brentq
from scipy.stats import norm

from ttf_time import (   # noqa: F401  — re-export for one-stop import
    time_to_maturity,
    time_to_maturity_multi,
    maturity_breakdown,
    expiry_from_delivery,
    options_expiry_from_delivery,
    futures_expiry_from_delivery,
    t_from_delivery,
    t_futures_from_delivery,
    subtract_business_days,
    parse_date,
    DayCount,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _df(r: float, T: float) -> float:
    return math.exp(-r * T)


# ── Black-76 ─────────────────────────────────────────────────────────────────

def _b76_d1(F: float, K: float, T: float, sigma: float) -> float:
    return (math.log(F / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))


def _b76_d1_d2(F: float, K: float, T: float, sigma: float) -> tuple[float, float]:
    d1 = _b76_d1(F, K, T, sigma)
    return d1, d1 - sigma * math.sqrt(T)


# ── Bachelier ─────────────────────────────────────────────────────────────────

def _bach_d(F: float, K: float, T: float, sigma_n: float) -> float:
    return (F - K) / (sigma_n * math.sqrt(T))


# ---------------------------------------------------------------------------
# Black-76 pricing
# ---------------------------------------------------------------------------

def b76_call(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-76 call price on a TTF futures contract (EUR/MWh)."""
    if T <= 0:
        return _df(r, T) * max(F - K, 0.0)
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    return _df(r, T) * (F * norm.cdf(d1) - K * norm.cdf(d2))


def b76_put(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-76 put price on a TTF futures contract (EUR/MWh)."""
    if T <= 0:
        return _df(r, T) * max(K - F, 0.0)
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    return _df(r, T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def b76_price(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """Dispatch to b76_call / b76_put."""
    ot = option_type.lower()
    if ot == "call":
        return b76_call(F, K, T, r, sigma)
    if ot == "put":
        return b76_put(F, K, T, r, sigma)
    raise ValueError(f"option_type must be 'call' or 'put', got '{option_type}'")


# ---------------------------------------------------------------------------
# Bachelier pricing (for negative or near-zero TTF prices)
# ---------------------------------------------------------------------------

def bach_call(F: float, K: float, T: float, r: float, sigma_n: float) -> float:
    """Bachelier call price — supports negative forward prices (EUR/MWh)."""
    if T <= 0:
        return _df(r, T) * max(F - K, 0.0)
    vol_sqrt_T = sigma_n * math.sqrt(T)
    d = (F - K) / vol_sqrt_T
    return _df(r, T) * ((F - K) * norm.cdf(d) + vol_sqrt_T * norm.pdf(d))


def bach_put(F: float, K: float, T: float, r: float, sigma_n: float) -> float:
    """Bachelier put price — supports negative forward prices (EUR/MWh)."""
    if T <= 0:
        return _df(r, T) * max(K - F, 0.0)
    vol_sqrt_T = sigma_n * math.sqrt(T)
    d = (F - K) / vol_sqrt_T
    return _df(r, T) * ((K - F) * norm.cdf(-d) + vol_sqrt_T * norm.pdf(d))


def bach_price(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Dispatch to bach_call / bach_put."""
    ot = option_type.lower()
    if ot == "call":
        return bach_call(F, K, T, r, sigma_n)
    if ot == "put":
        return bach_put(F, K, T, r, sigma_n)
    raise ValueError(f"option_type must be 'call' or 'put', got '{option_type}'")


# ---------------------------------------------------------------------------
# Black-76 Greeks
# ---------------------------------------------------------------------------

def b76_delta(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """dV/dF (forward delta, discounted)."""
    if T <= 0:
        return _df(r, T) if (option_type == "call" and F > K) else 0.0
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    df = _df(r, T)
    return df * norm.cdf(d1) if option_type == "call" else df * (norm.cdf(d1) - 1.0)


def b76_gamma(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """d²V/dF² (same for call and put)."""
    if T <= 0:
        return 0.0
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    return _df(r, T) * norm.pdf(d1) / (F * sigma * math.sqrt(T))


def b76_vega(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """dV/d(sigma) — sensitivity per unit change in lognormal vol."""
    if T <= 0:
        return 0.0
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    return _df(r, T) * F * norm.pdf(d1) * math.sqrt(T)


def b76_theta(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """dV/dt per calendar day (time decay, negative for long positions)."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    df = _df(r, T)
    decay = -(F * df * norm.pdf(d1) * sigma) / (2.0 * math.sqrt(T))
    if option_type == "call":
        rate_term = -r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        rate_term = -r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
    return (decay + rate_term) / 365.0


def b76_rho(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """dV/dr per 1 percentage-point change in rate (÷100 convention)."""
    if T <= 0:
        return 0.0
    price = b76_price(F, K, T, r, sigma, option_type)
    return -T * price / 100.0


def b76_vanna(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """d(delta)/d(sigma) = d(vega)/dF — mixed partial."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    return -_df(r, T) * norm.pdf(d1) * d2 / sigma


def b76_volga(F: float, K: float, T: float, r: float, sigma: float) -> float:
    """d²V/d(sigma)² (vomma) — vol convexity."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    return b76_vega(F, K, T, r, sigma) * d1 * d2 / sigma


@dataclass
class B76Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    vanna: float
    volga: float


def b76_greeks(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> B76Greeks:
    """Compute all Black-76 Greeks in one call."""
    return B76Greeks(
        delta=b76_delta(F, K, T, r, sigma, option_type),
        gamma=b76_gamma(F, K, T, r, sigma),
        vega=b76_vega(F, K, T, r, sigma),
        theta=b76_theta(F, K, T, r, sigma, option_type),
        rho=b76_rho(F, K, T, r, sigma, option_type),
        vanna=b76_vanna(F, K, T, r, sigma),
        volga=b76_volga(F, K, T, r, sigma),
    )


# ---------------------------------------------------------------------------
# Bachelier Greeks
# ---------------------------------------------------------------------------

def bach_delta(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    if T <= 0:
        return _df(r, T) if (option_type == "call" and F > K) else 0.0
    d = _bach_d(F, K, T, sigma_n)
    df = _df(r, T)
    return df * norm.cdf(d) if option_type == "call" else df * (norm.cdf(d) - 1.0)


def bach_gamma(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return _df(r, T) * norm.pdf(d) / (sigma_n * math.sqrt(T))


def bach_vega(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    """dV/d(sigma_n) in EUR/MWh per EUR/MWh of vol."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return _df(r, T) * norm.pdf(d) * math.sqrt(T)


def bach_theta(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Bachelier theta per calendar day."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    df = _df(r, T)
    decay = -df * sigma_n * norm.pdf(d) / (2.0 * math.sqrt(T))
    price = bach_price(F, K, T, r, sigma_n, option_type)
    rate_term = -r * price
    return (decay + rate_term) / 365.0


def bach_rho(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Bachelier rho per 1 pp change in rate."""
    if T <= 0:
        return 0.0
    return -T * bach_price(F, K, T, r, sigma_n, option_type) / 100.0


def bach_vanna(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return -_df(r, T) * norm.pdf(d) * d / sigma_n


def bach_volga(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return bach_vega(F, K, T, r, sigma_n) * (d**2 - 1.0) / sigma_n


@dataclass
class BachGreeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    vanna: float
    volga: float


def bach_greeks(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> BachGreeks:
    """Compute all Bachelier Greeks in one call."""
    return BachGreeks(
        delta=bach_delta(F, K, T, r, sigma_n, option_type),
        gamma=bach_gamma(F, K, T, r, sigma_n),
        vega=bach_vega(F, K, T, r, sigma_n),
        theta=bach_theta(F, K, T, r, sigma_n, option_type),
        rho=bach_rho(F, K, T, r, sigma_n, option_type),
        vanna=bach_vanna(F, K, T, r, sigma_n),
        volga=bach_volga(F, K, T, r, sigma_n),
    )


# ---------------------------------------------------------------------------
# Implied volatility solvers (Brent's method)
# ---------------------------------------------------------------------------

_BRENT_XTOL = 1e-8
_BRENT_MAXITER = 300


def b76_implied_vol(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    sigma_lo: float = 1e-6,
    sigma_hi: float = 20.0,
) -> float:
    """Implied lognormal vol for a Black-76 option via Brent's method.

    Returns:
        sigma (dimensionless decimal, e.g. 0.50 for 50%)
    Raises:
        ValueError if no solution found in [sigma_lo, sigma_hi].
    """
    def f(s: float) -> float:
        return b76_price(F, K, T, r, s, option_type) - market_price

    if f(sigma_lo) * f(sigma_hi) > 0:
        raise ValueError(
            f"Could not bracket implied vol in [{sigma_lo}, {sigma_hi}]. "
            "Check that market_price is above intrinsic value."
        )
    return brentq(f, sigma_lo, sigma_hi, xtol=_BRENT_XTOL, maxiter=_BRENT_MAXITER)


def bach_implied_vol(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    sigma_lo: float = 1e-6,
    sigma_hi: float = 500.0,
) -> float:
    """Implied normal vol for a Bachelier option via Brent's method.

    Returns:
        sigma_n in EUR/MWh
    Raises:
        ValueError if no solution found in [sigma_lo, sigma_hi].
    """
    def f(s: float) -> float:
        return bach_price(F, K, T, r, s, option_type) - market_price

    if f(sigma_lo) * f(sigma_hi) > 0:
        raise ValueError(
            f"Could not bracket implied normal vol in [{sigma_lo}, {sigma_hi}]. "
            "Check inputs."
        )
    return brentq(f, sigma_lo, sigma_hi, xtol=_BRENT_XTOL, maxiter=_BRENT_MAXITER)


# ---------------------------------------------------------------------------
# Delta-to-strike inversion
# ---------------------------------------------------------------------------

def b76_delta_to_strike(
    delta_target: float,
    F: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    K_lo: float | None = None,
    K_hi: float | None = None,
) -> float:
    """Find the strike K such that Black-76 delta equals delta_target.

    Typical TTF use: convert 25Δ / 50Δ / 75Δ quotes to strikes.

    Args:
        delta_target: Target delta (e.g. 0.25, 0.50, -0.25 for puts)
        F: Forward price (EUR/MWh)
        T: Time to expiry in years
        r: Risk-free rate
        sigma: Lognormal vol
        option_type: 'call' or 'put'
        K_lo / K_hi: Optional bracketing strikes (defaults to 1% and 10× of F)

    Returns:
        Strike K in EUR/MWh.
    """
    if K_lo is None:
        K_lo = max(F * 0.01, 0.01)
    if K_hi is None:
        K_hi = F * 10.0

    def f(K: float) -> float:
        return b76_delta(F, K, T, r, sigma, option_type) - delta_target

    if f(K_lo) * f(K_hi) > 0:
        raise ValueError(
            f"Could not bracket K for delta={delta_target} in [{K_lo:.2f}, {K_hi:.2f}]."
        )
    return brentq(f, K_lo, K_hi, xtol=1e-6, maxiter=_BRENT_MAXITER)


def bach_delta_to_strike(
    delta_target: float,
    F: float,
    T: float,
    r: float,
    sigma_n: float,
    option_type: str = "call",
    K_lo: float | None = None,
    K_hi: float | None = None,
) -> float:
    """Find the strike K such that Bachelier delta equals delta_target.

    Useful when forward prices are negative (e.g. crisis scenarios).
    """
    if K_lo is None:
        K_lo = F - 10 * sigma_n * math.sqrt(T)
    if K_hi is None:
        K_hi = F + 10 * sigma_n * math.sqrt(T)

    def f(K: float) -> float:
        return bach_delta(F, K, T, r, sigma_n, option_type) - delta_target

    if f(K_lo) * f(K_hi) > 0:
        raise ValueError(
            f"Could not bracket K for delta={delta_target} in [{K_lo:.2f}, {K_hi:.2f}]."
        )
    return brentq(f, K_lo, K_hi, xtol=1e-6, maxiter=_BRENT_MAXITER)


# ---------------------------------------------------------------------------
# Quick sanity check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # TTF example: front-month, ATM, 3-month expiry
    F, K, T, r, sigma = 35.0, 35.0, 90 / 365, 0.03, 0.50

    call = b76_call(F, K, T, r, sigma)
    put = b76_put(F, K, T, r, sigma)
    print("=== Black-76 (TTF, EUR/MWh) ===")
    print(f"  Call : {call:.4f}  Put : {put:.4f}")

    g = b76_greeks(F, K, T, r, sigma, "call")
    print(f"  Delta={g.delta:.4f}  Gamma={g.gamma:.6f}  Vega={g.vega:.4f}")
    print(f"  Theta={g.theta:.4f}/day  Vanna={g.vanna:.6f}  Volga={g.volga:.6f}")

    iv = b76_implied_vol(call, F, K, T, r, "call")
    print(f"  IV (Brent): {iv:.6f}  (input sigma={sigma})")

    k25 = b76_delta_to_strike(0.25, F, T, r, sigma, "call")
    print(f"  25Δ call strike: {k25:.4f} EUR/MWh")

    # Bachelier — negative price scenario
    F2, K2, T2, sigma_n = -3.0, 0.0, 60 / 365, 6.0
    call2 = bach_call(F2, K2, T2, r, sigma_n)
    iv2 = bach_implied_vol(call2, F2, K2, T2, r, "call")
    print("\n=== Bachelier (negative price, EUR/MWh) ===")
    print(f"  Call : {call2:.4f}")
    print(f"  IV (Brent): {iv2:.6f}  (input sigma_n={sigma_n})")
