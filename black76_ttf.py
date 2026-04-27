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
import re

from scipy.optimize import brentq
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Expiry calendar (self-contained, no external dependencies)
# ---------------------------------------------------------------------------

def _is_business_day(d: date) -> bool:
    return d.weekday() < 5


def _prev_business_day(d: date) -> date:
    while not _is_business_day(d):
        d -= timedelta(days=1)
    return d


def _subtract_business_days(d: date, n: int) -> date:
    while n > 0:
        d -= timedelta(days=1)
        if _is_business_day(d):
            n -= 1
    return d


def futures_expiry_from_delivery(delivery_year: int, delivery_month: int) -> date:
    """Last business day of the month before the delivery month (futures LTD)."""
    last_of_prev = date(delivery_year, delivery_month, 1) - timedelta(days=1)
    return _prev_business_day(last_of_prev)


def options_expiry_from_delivery(delivery_year: int, delivery_month: int) -> date:
    """5 business days before the futures LTD (ICE/EEX TTF options convention)."""
    return _subtract_business_days(
        futures_expiry_from_delivery(delivery_year, delivery_month), 5
    )


def t_from_delivery(
    delivery_year: int,
    delivery_month: int,
    reference: date | None = None,
) -> float:
    """ACT/365 time to TTF options expiry for a given delivery month."""
    ref = reference or date.today()
    exp = options_expiry_from_delivery(delivery_year, delivery_month)
    return max((exp - ref).days + 1, 0) / 365.0


def t_futures_from_delivery(
    delivery_year: int,
    delivery_month: int,
    reference: date | None = None,
) -> float:
    """ACT/365 time to TTF futures expiry for a given delivery month."""
    ref = reference or date.today()
    exp = futures_expiry_from_delivery(delivery_year, delivery_month)
    return max((exp - ref).days + 1, 0) / 365.0


# ---------------------------------------------------------------------------
# ICE Endex Dutch TTF Natural Gas — Official expiry calendar
# ---------------------------------------------------------------------------
# Rules (ICE Endex Dutch TTF Natural Gas Options):
#   - European-style options settling into ICE Endex TTF futures
#   - Expiry candidate = 5 calendar days BEFORE the 1st calendar day
#     of the delivery month
#   - If the candidate is not a business day, roll back to the previous
#     business day
#   - If that rolled-back business day coincides with the last trading
#     day of the underlying future, roll back one more business day
#   - Holiday calendar = intersection of NL + UK bank holidays relevant
#     to ICE Endex (New Year, Good Friday, Easter Monday, Labour Day,
#     Christmas, Boxing Day)
#
# NB: this is INDEPENDENT from `options_expiry_from_delivery` above,
# which uses a simpler "5 business days before futures LTD" convention.
# The two functions deliberately coexist: existing pricing code that
# imports `options_expiry_from_delivery` keeps its behaviour; new code
# using the ICE Endex rule should call `ttf_expiry_date` instead.


def _easter_sunday(year: int) -> date:
    """Gregorian Easter Sunday via Gauss's algorithm."""
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


def _ttf_holidays(year: int) -> frozenset[date]:
    """NL + UK bank holidays observed by ICE Endex for TTF trading.

    Conservative intersection — covers the six fixed closures that both
    Dutch and UK markets share:
        Jan 1  New Year's Day
        GF-2   Good Friday   (Easter Sunday − 2)
        EM+1   Easter Monday (Easter Sunday + 1)
        May 1  Labour Day (NL) — also covers early-May UK bank holiday
        Dec 25 Christmas Day
        Dec 26 Boxing Day / 2nd Christmas Day
    """
    easter = _easter_sunday(year)
    return frozenset([
        date(year, 1, 1),
        easter - timedelta(days=2),   # Good Friday
        easter + timedelta(days=1),   # Easter Monday
        date(year, 5, 1),             # Labour Day (NL)
        date(year, 12, 25),
        date(year, 12, 26),
    ])


def ttf_is_business_day(d: date) -> bool:
    """Return True if *d* is a trading day on ICE Endex.

    A TTF business day is Mon–Fri excluding the NL + UK bank holidays
    listed in :func:`_ttf_holidays`.
    """
    if d.weekday() >= 5:     # Saturday=5, Sunday=6
        return False
    return d not in _ttf_holidays(d.year)


def _ttf_prev_bd(d: date) -> date:
    """Roll *d* back to the previous ICE Endex business day (inclusive)."""
    while not ttf_is_business_day(d):
        d -= timedelta(days=1)
    return d


def _ttf_futures_ltd(contract_year: int, contract_month: int) -> date:
    """ICE Endex TTF futures last trading day.

    = last ICE Endex business day of the month *before* the delivery month.
    Respects the NL+UK holiday calendar (so e.g. a LTD falling on Good
    Friday is rolled back).
    """
    first_of_delivery = date(contract_year, contract_month, 1)
    last_of_prev_month = first_of_delivery - timedelta(days=1)
    return _ttf_prev_bd(last_of_prev_month)


def ttf_expiry_date(contract_month: int, contract_year: int) -> date:
    """Official ICE Endex Dutch TTF option expiry date.

    Parameters
    ----------
    contract_month : 1–12 (the delivery month, e.g. 6 for Jun)
    contract_year  : 4-digit year, e.g. 2026

    Returns
    -------
    :class:`datetime.date` — the last trading day of the option.

    Algorithm
    ---------
    1. Candidate = 1st of delivery month − 5 calendar days
    2. If the candidate is not a business day → previous business day
    3. If that business day equals the futures LTD → step back one more
       business day

    Examples
    --------
    >>> ttf_expiry_date(6, 2026)   # Jun-26
    datetime.date(2026, 5, 27)
    >>> ttf_expiry_date(1, 2026)   # Jan-26 — Dec-25 holidays bite
    datetime.date(2025, 12, 24)
    """
    if not (1 <= contract_month <= 12):
        raise ValueError(f"contract_month must be in 1..12, got {contract_month}")

    delivery_first = date(contract_year, contract_month, 1)
    candidate = delivery_first - timedelta(days=5)
    candidate = _ttf_prev_bd(candidate)

    futures_ltd = _ttf_futures_ltd(contract_year, contract_month)
    if candidate == futures_ltd:
        candidate = _ttf_prev_bd(candidate - timedelta(days=1))
    return candidate


def ttf_time_to_expiry(
    contract_month: int,
    contract_year: int,
    reference: date | None = None,
) -> float:
    """Raw calendar-day time to TTF option expiry, divided by 365.

    t = (expiry_date - today).days / 365

    No business-day adjustment, no holiday removal, no day-count convention.

    Parameters
    ----------
    contract_month : 1–12 (the delivery month)
    contract_year  : 4-digit year
    reference      : valuation date (default: today)
    """
    ref = reference or date.today()
    exp = ttf_expiry_date(contract_month, contract_year)
    return (exp - ref).days / 365


_MONTH_CODES_ICE = "FGHJKMNQUVXZ"


def ttf_next_expiries(
    n: int = 6,
    reference: date | None = None,
) -> list[tuple[str, date]]:
    """Return the next *n* upcoming ICE Endex TTF option expiries.

    Parameters
    ----------
    n          : number of consecutive monthly contracts to return
    reference  : valuation date (default: today)

    Returns
    -------
    list of (contract_code, expiry_date) tuples, ordered ascending.
    Contract codes follow ICE convention: ``TTF<M><YY>``.

    Example
    -------
    >>> ttf_next_expiries(3, reference=date(2026, 4, 23))
    [('TTFK26', date(2026, 4, 24)),
     ('TTFM26', date(2026, 5, 27)),
     ('TTFN26', date(2026, 6, 26))]
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
# Contract-name parser
# ---------------------------------------------------------------------------

_MONTH_FROM_CODE = {
    "F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
    "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12,
}
_MONTH_FROM_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_ICE_RE   = re.compile(r"^TTF([FGHJKMNQUVXZ])(\d{2})$", re.IGNORECASE)
_ABBR_RE  = re.compile(r"^([A-Za-z]{3})-?(\d{2,4})$")


def t_from_contract(contract: str, reference: date | None = None) -> float:
    """Return ACT/365 T (today included) for a TTF contract name.

    Accepted formats
    ----------------
    "TTFH26"   ICE/EEX code  (delivery month = March 2026)
    "Mar26"    3-letter month abbreviation + 2-digit year
    "Mar2026"  3-letter month abbreviation + 4-digit year
    """
    m = _ICE_RE.match(contract.strip())
    if m:
        month = _MONTH_FROM_CODE[m.group(1).upper()]
        year  = 2000 + int(m.group(2))
        return t_from_delivery(year, month, reference)

    m = _ABBR_RE.match(contract.strip())
    if m:
        abbr = m.group(1).lower()
        yr   = int(m.group(2))
        year = yr if yr > 100 else 2000 + yr
        month = _MONTH_FROM_ABBR.get(abbr)
        if month:
            return t_from_delivery(year, month, reference)

    raise ValueError(
        f"Cannot parse contract '{contract}'. "
        "Use ICE code ('TTFH26') or month abbreviation ('Mar26')."
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


def b76_price_ttf(
    F: float,
    K: float,
    contract: str,
    r: float,
    sigma: float,
    option_type: str = "call",
    reference: date | None = None,
) -> float:
    """Black-76 price where T is derived from a TTF contract name.

    Parameters
    ----------
    contract : ICE code or month abbreviation, e.g. "TTFH26" or "Mar26"
    reference : valuation date (default: today)

    Example
    -------
    >>> b76_price_ttf(35.0, 35.0, "TTFM26", r=0.03, sigma=0.50)
    >>> b76_price_ttf(35.0, 32.0, "Jun26",  r=0.03, sigma=0.45, option_type="put")
    """
    T = t_from_contract(contract, reference)
    return b76_price(F, K, T, r, sigma, option_type)


def bach_price_ttf(
    F: float,
    K: float,
    contract: str,
    r: float,
    sigma_n: float,
    option_type: str = "call",
    reference: date | None = None,
) -> float:
    """Bachelier price where T is derived from a TTF contract name.

    Parameters
    ----------
    contract : ICE code or month abbreviation, e.g. "TTFH26" or "Mar26"
    reference : valuation date (default: today)
    """
    T = t_from_contract(contract, reference)
    return bach_price(F, K, T, r, sigma_n, option_type)


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

    # ── ICE Endex official expiry calendar ───────────────────────────────
    _MONTH_LABELS = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    print("\n=== ICE Endex Dutch TTF — Official Expiry Calendar ===")
    for yr in (2025, 2026):
        print(f"\n  {yr}")
        print(f"  {'Contract':<10}{'Delivery':<12}{'Candidate':<14}{'Expiry':<12}  Futures LTD")
        print(f"  {'-' * 64}")
        for m in range(1, 13):
            exp = ttf_expiry_date(m, yr)
            fut = _ttf_futures_ltd(yr, m)
            delivery = date(yr, m, 1)
            candidate = _ttf_prev_bd(delivery - timedelta(days=5))
            code = f"TTF{_MONTH_CODES_ICE[m-1]}{str(yr)[-2:]}"
            holiday_flag = " *" if candidate != (delivery - timedelta(days=5)) else "  "
            print(
                f"  {code:<10}{_MONTH_LABELS[m-1]}-{str(yr)[-2:]:<8}"
                f"{str(candidate):<12}{holiday_flag}{str(exp):<12}  {fut}"
            )
        print("  (* = candidate adjusted back due to weekend/holiday)")

    # Next 6 expiries from a reference date
    ref = date(2026, 4, 23)
    print(f"\n  Next 6 expiries (reference = {ref}):")
    for code, exp in ttf_next_expiries(6, reference=ref):
        T_opt = ttf_time_to_expiry(
            int({_MONTH_CODES_ICE[i]: i + 1 for i in range(12)}[code[3]]),
            2000 + int(code[-2:]),
            reference=ref,
        )
        days = (exp - ref).days + 1
        print(f"    {code}  expiry={exp}  T={T_opt:.4f} y  ({days} cal days)")
