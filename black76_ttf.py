"""TTF natural gas options pricing — Black-76 & Bachelier models.

Conventions:
  - Underlying : TTF forward/futures price in EUR/MWh
  - Expiry     : T in years (e.g. 30 days → T = 30/365)
  - Rate       : risk-free EUR rate, annualised decimal (e.g. 3% → r = 0.03)
  - Vol        : lognormal decimal for Black-76 (e.g. 50% → sigma = 0.50)
                 normal EUR/MWh for Bachelier    (e.g. 8 EUR/MWh → sigma_n = 8.0)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta

from scipy.optimize import brentq
from scipy.stats import norm


# ---------------------------------------------------------------------------
# ICE TTF Natural Gas — Official futures (TFM) and options (TFO) expiry rules
# ---------------------------------------------------------------------------
# ICE product codes:
#   TFM  Dutch TTF Gas Futures
#   TFO  Dutch TTF Gas Options (Futures-Style Margin)
#
# TFM — futures expiry, verbatim:
#   "Trading will cease at the close of business two UK Business Days
#    prior to the first calendar day of the delivery month, quarter,
#    season, or calendar."
#
# TFO — option expiry, verbatim:
#   "Trading will cease when the intraday settlement price of the
#    underlying futures contract is set, five calendar days before
#    the start of the contract month. If that day is a non-business
#    day or non-UK business day, expiry will occur on the nearest
#    prior business day, except where that day is also the expiry
#    date of the underlying futures contract, in which case expiry
#    will occur on the preceding business day."
#
# Holiday calendar: UK public holidays only (England & Wales).


def _easter_sunday(year: int) -> date:
    """Gregorian Easter Sunday (Gauss's algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(114 + h + l - 7 * m, 31)
    return date(year, month, day + 1)


def _shift_off_weekend(d: date) -> date:
    """UK substitution: weekend holidays roll forward to the next weekday."""
    if d.weekday() == 5:        # Saturday → Monday
        return d + timedelta(days=2)
    if d.weekday() == 6:        # Sunday → Monday
        return d + timedelta(days=1)
    return d


def _first_monday(year: int, month: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(0 - first.weekday()) % 7)


def _last_monday(year: int, month: int) -> date:
    nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=last.weekday())


def _uk_holidays(year: int) -> frozenset[date]:
    """UK public holidays (England & Wales).

    Includes:
      - New Year's Day (1 Jan, weekend → next weekday)
      - Good Friday and Easter Monday
      - Early May bank holiday (1st Monday of May)
      - Spring bank holiday    (last Monday of May)
      - Summer bank holiday    (last Monday of August)
      - Christmas Day (25 Dec, weekend → next weekday)
      - Boxing Day    (26 Dec, weekend → next weekday, distinct from Christmas)
    """
    easter = _easter_sunday(year)
    christmas = _shift_off_weekend(date(year, 12, 25))
    boxing = _shift_off_weekend(date(year, 12, 26))
    if boxing == christmas:
        boxing = christmas + timedelta(days=1)
    return frozenset([
        _shift_off_weekend(date(year, 1, 1)),
        easter - timedelta(days=2),       # Good Friday
        easter + timedelta(days=1),       # Easter Monday
        _first_monday(year, 5),           # Early May bank holiday
        _last_monday(year, 5),            # Spring bank holiday
        _last_monday(year, 8),            # Summer bank holiday
        christmas,
        boxing,
    ])


def ttf_is_business_day(d: date) -> bool:
    """Return True if *d* is a UK business day.

    Excludes weekends and UK public holidays only.
    """
    if d.weekday() >= 5:
        return False
    return d not in _uk_holidays(d.year)


def _prev_uk_bd(d: date) -> date:
    """Roll *d* back to the nearest prior UK business day (inclusive)."""
    while not ttf_is_business_day(d):
        d -= timedelta(days=1)
    return d


def ttf_futures_expiry_date(delivery_month: int, delivery_year: int) -> date:
    """ICE TFM futures last trading day for the given delivery month / year.

    Implements the ICE TFM rule verbatim:

        Trading will cease at the close of business two UK Business Days
        prior to the first calendar day of the delivery month, quarter,
        season, or calendar.

    Parameters
    ----------
    delivery_month : 1–12 (e.g. 6 for Jun)
    delivery_year  : 4-digit year, e.g. 2026

    Returns
    -------
    :class:`datetime.date` — the futures last trading day.
    """
    if not (1 <= delivery_month <= 12):
        raise ValueError(f"delivery_month must be in 1..12, got {delivery_month}")

    d = date(delivery_year, delivery_month, 1)
    for _ in range(2):
        d = _prev_uk_bd(d - timedelta(days=1))
    return d


def ttf_expiry_date(contract_month: int, contract_year: int) -> date:
    """ICE TFO option expiry date for the given contract month / year.

    Implements the ICE TFO rule verbatim:

        Trading will cease when the intraday settlement price of the
        underlying futures contract is set, five calendar days before
        the start of the contract month. If that day is a non-business
        day or non-UK business day, expiry will occur on the nearest
        prior business day, except where that day is also the expiry
        date of the underlying futures contract, in which case expiry
        will occur on the preceding business day.

    Parameters
    ----------
    contract_month : 1–12 (the delivery month, e.g. 6 for Jun)
    contract_year  : 4-digit year, e.g. 2026

    Returns
    -------
    :class:`datetime.date` — the option last trading day.
    """
    if not (1 <= contract_month <= 12):
        raise ValueError(f"contract_month must be in 1..12, got {contract_month}")

    candidate = _prev_uk_bd(
        date(contract_year, contract_month, 1) - timedelta(days=5)
    )
    if candidate == ttf_futures_expiry_date(contract_month, contract_year):
        candidate = _prev_uk_bd(candidate - timedelta(days=1))
    return candidate


def ttf_time_to_expiry(
    contract_month: int,
    contract_year: int,
    reference: date | None = None,
) -> float:
    """Calendar-day time to ICE TFO expiry, divided by 365.

        t = (expiry_date - today).days / 365

    Calendar days only — no business-day adjustment, no day-count convention.
    """
    ref = reference or date.today()
    return (ttf_expiry_date(contract_month, contract_year) - ref).days / 365


_MONTH_CODES_ICE = "FGHJKMNQUVXZ"


def ttf_next_expiries(
    n: int = 6,
    reference: date | None = None,
) -> list[tuple[str, date]]:
    """Return the next *n* upcoming ICE TFO option expiries.

    Returns ``(contract_code, expiry_date)`` tuples in ascending order;
    codes follow ICE convention ``TTF<M><YY>``.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    ref = reference or date.today()
    out: list[tuple[str, date]] = []
    year, month = ref.year, ref.month

    while len(out) < n:
        exp = ttf_expiry_date(month, year)
        if exp > ref:
            code = f"TTF{_MONTH_CODES_ICE[month - 1]}{str(year)[-2:]}"
            out.append((code, exp))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return out


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

    # ── ICE TTF official expiry calendar (TFM futures + TFO options) ─────
    _MONTH_LABELS = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    print("\n=== ICE Dutch TTF — Official Expiry Calendar (TFM / TFO) ===")
    for yr in (2025, 2026):
        print(f"\n  {yr}")
        print(f"  {'Contract':<10}{'Futures LTD (TFM)':<22}{'Option Expiry (TFO)':<22}")
        print(f"  {'-' * 54}")
        for m in range(1, 13):
            fut = ttf_futures_expiry_date(m, yr)
            exp = ttf_expiry_date(m, yr)
            code = f"TTF{_MONTH_CODES_ICE[m - 1]}{str(yr)[-2:]}"
            print(
                f"  {code:<10}"
                f"{fut.strftime('%a %d %b %Y'):<22}"
                f"{exp.strftime('%a %d %b %Y'):<22}"
            )

    # Next 6 expiries from a reference date
    ref = date(2026, 4, 23)
    print(f"\n  Next 6 TFO expiries (reference = {ref}):")
    for code, exp in ttf_next_expiries(6, reference=ref):
        month = _MONTH_CODES_ICE.index(code[3]) + 1
        year = 2000 + int(code[-2:])
        T_opt = ttf_time_to_expiry(month, year, reference=ref)
        days = (exp - ref).days
        print(f"    {code}  expiry={exp}  T={T_opt:.4f} y  ({days} cal days)")
