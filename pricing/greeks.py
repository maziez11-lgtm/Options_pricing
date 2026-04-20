"""Greeks for Black-76 and Bachelier models.

Black-76 Greeks use lognormal vol (sigma).
Bachelier Greeks use normal vol (sigma_n) in EUR/MWh.

Greeks covered: Delta, Gamma, Vega, Theta, Rho, Vanna, Volga (Vomma).
"""

import math
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Black-76 Greeks
# ---------------------------------------------------------------------------

def _b76_d1_d2(
    F: float, K: float, T: float, sigma: float
) -> tuple[float, float]:
    d1 = (math.log(F / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    return d1, d1 - sigma * math.sqrt(T)


def b76_delta(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """Black-76 delta w.r.t. forward price F."""
    if T <= 0:
        return math.exp(-r * T) * (1.0 if option_type == "call" and F > K else 0.0)
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    df = math.exp(-r * T)
    if option_type == "call":
        return df * norm.cdf(d1)
    return df * (norm.cdf(d1) - 1.0)


def b76_gamma(
    F: float, K: float, T: float, r: float, sigma: float
) -> float:
    """Black-76 gamma (same for call and put)."""
    if T <= 0:
        return 0.0
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    return math.exp(-r * T) * norm.pdf(d1) / (F * sigma * math.sqrt(T))


def b76_vega(
    F: float, K: float, T: float, r: float, sigma: float
) -> float:
    """Black-76 vega — sensitivity to lognormal vol (per 1-unit change in sigma)."""
    if T <= 0:
        return 0.0
    d1, _ = _b76_d1_d2(F, K, T, sigma)
    return math.exp(-r * T) * F * norm.pdf(d1) * math.sqrt(T)


def b76_vanna(
    F: float, K: float, T: float, r: float, sigma: float
) -> float:
    """Black-76 vanna — d(delta)/d(sigma) = d(vega)/dF."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    return -math.exp(-r * T) * norm.pdf(d1) * d2 / sigma


def b76_volga(
    F: float, K: float, T: float, r: float, sigma: float
) -> float:
    """Black-76 volga (vomma) — d²(price)/d(sigma)²."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    vega = b76_vega(F, K, T, r, sigma)
    return vega * d1 * d2 / sigma


def b76_theta(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """Black-76 theta (per calendar day)."""
    if T <= 0:
        return 0.0
    d1, d2 = _b76_d1_d2(F, K, T, sigma)
    df = math.exp(-r * T)
    term1 = -(F * df * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    if option_type == "call":
        theta = term1 - r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        theta = term1 - r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
    return theta / 365.0


def b76_rho(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """Black-76 rho — dV/dr per 1 percentage-point change (÷100 convention)."""
    if T <= 0:
        return 0.0
    from pricing.black76 import price as b76_price
    return -T * b76_price(F, K, T, r, sigma, option_type) / 100.0


def b76_greeks(
    F: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> dict[str, float]:
    """Return all Black-76 greeks as a dict."""
    return {
        "delta": b76_delta(F, K, T, r, sigma, option_type),
        "gamma": b76_gamma(F, K, T, r, sigma),
        "vega": b76_vega(F, K, T, r, sigma),
        "theta": b76_theta(F, K, T, r, sigma, option_type),
        "rho": b76_rho(F, K, T, r, sigma, option_type),
        "vanna": b76_vanna(F, K, T, r, sigma),
        "volga": b76_volga(F, K, T, r, sigma),
    }


# ---------------------------------------------------------------------------
# Bachelier Greeks
# ---------------------------------------------------------------------------

def _bach_d(F: float, K: float, T: float, sigma_n: float) -> float:
    return (F - K) / (sigma_n * math.sqrt(T))


def bach_delta(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Bachelier delta w.r.t. forward price F."""
    if T <= 0:
        return math.exp(-r * T) * (1.0 if option_type == "call" and F > K else 0.0)
    d = _bach_d(F, K, T, sigma_n)
    df = math.exp(-r * T)
    if option_type == "call":
        return df * norm.cdf(d)
    return df * (norm.cdf(d) - 1.0)


def bach_gamma(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    """Bachelier gamma."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return math.exp(-r * T) * norm.pdf(d) / (sigma_n * math.sqrt(T))


def bach_vega(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    """Bachelier vega — sensitivity to normal vol (per 1 EUR/MWh change in sigma_n)."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    return math.exp(-r * T) * norm.pdf(d) * math.sqrt(T)


def bach_vanna(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    """Bachelier vanna — d(delta)/d(sigma_n)."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    df = math.exp(-r * T)
    return -df * norm.pdf(d) * d / sigma_n


def bach_volga(
    F: float, K: float, T: float, r: float, sigma_n: float
) -> float:
    """Bachelier volga — d²(price)/d(sigma_n)²."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    vega = bach_vega(F, K, T, r, sigma_n)
    return vega * (d**2 - 1.0) / sigma_n


def bach_theta(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Bachelier theta — dV/dt per calendar day."""
    if T <= 0:
        return 0.0
    d = _bach_d(F, K, T, sigma_n)
    df = math.exp(-r * T)
    from pricing.bachelier import price as bach_price
    decay = -df * sigma_n * norm.pdf(d) / (2.0 * math.sqrt(T))
    return (decay - r * bach_price(F, K, T, r, sigma_n, option_type)) / 365.0


def bach_rho(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> float:
    """Bachelier rho — dV/dr per 1 percentage-point change (÷100 convention)."""
    if T <= 0:
        return 0.0
    from pricing.bachelier import price as bach_price
    return -T * bach_price(F, K, T, r, sigma_n, option_type) / 100.0


def bach_greeks(
    F: float, K: float, T: float, r: float, sigma_n: float, option_type: str = "call"
) -> dict[str, float]:
    """Return all Bachelier greeks as a dict."""
    return {
        "delta": bach_delta(F, K, T, r, sigma_n, option_type),
        "gamma": bach_gamma(F, K, T, r, sigma_n),
        "vega": bach_vega(F, K, T, r, sigma_n),
        "theta": bach_theta(F, K, T, r, sigma_n, option_type),
        "rho": bach_rho(F, K, T, r, sigma_n, option_type),
        "vanna": bach_vanna(F, K, T, r, sigma_n),
        "volga": bach_volga(F, K, T, r, sigma_n),
    }


# ---------------------------------------------------------------------------
# Black-Scholes Greeks (for equities / non-futures use-cases)
# ---------------------------------------------------------------------------

def _bs_d1_d2(
    S: float, K: float, T: float, r: float, sigma: float
) -> tuple[float, float]:
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return d1, d1 - sigma * math.sqrt(T)


def delta(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    if T <= 0:
        return 1.0 if option_type == "call" and S > K else 0.0
    d1, _ = _bs_d1_d2(S, K, T, r, sigma)
    return norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1.0


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    if T <= 0:
        return 0.0
    d1, _ = _bs_d1_d2(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * math.sqrt(T))


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    if T <= 0:
        return 0.0
    d1, _ = _bs_d1_d2(S, K, T, r, sigma)
    return S * norm.pdf(d1) * math.sqrt(T)


def theta(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    if T <= 0:
        return 0.0
    d1, d2 = _bs_d1_d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    if option_type == "call":
        return (term1 - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365.0
    return (term1 + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365.0


def rho(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    if T <= 0:
        return 0.0
    _, d2 = _bs_d1_d2(S, K, T, r, sigma)
    if option_type == "call":
        return K * T * math.exp(-r * T) * norm.cdf(d2) / 100.0
    return -K * T * math.exp(-r * T) * norm.cdf(-d2) / 100.0
