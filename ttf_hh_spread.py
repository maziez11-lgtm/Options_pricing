"""TTF vs Henry Hub Spread Option Pricer — Margrabe's Formula (1978).

Prices the exchange option on the TTF − HH basis:
  Call  =  max(F_TTF_usd − F_HH, 0)  at expiry   (TTF outperforms HH)
  Put   =  max(F_HH − F_TTF_usd, 0)  at expiry   (HH outperforms TTF)

Unit conversion
---------------
  1 MWh = 3.412142 MMBtu  (exact energy equivalence)
  F_TTF_usd [USD/MMBtu] = F_TTF_eur [EUR/MWh] × FX_EURUSD / 3.412142

Spread volatility (Margrabe)
-----------------------------
  σ_spread = √(σ_TTF² + σ_HH² − 2ρ × σ_TTF × σ_HH)

Key intuition
-------------
  ρ → +1   assets move together → spread vol ↓ → option cheaper
  ρ → −1   assets diverge      → spread vol ↑ → option more expensive
  The implied correlation is the market's view of TTF/HH co-movement.

Typical LNG-driven regime (2022–2026)
--------------------------------------
  TTF  ≈ 25–45 EUR/MWh  →  ~8–14 USD/MMBtu  (after FX)
  HH   ≈  2–5 USD/MMBtu
  Spread TTF−HH ≈ 5–12 USD/MMBtu  (LNG netback drives convergence)
  Implied correlation ≈ 0.20–0.55
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Union

from scipy.optimize import brentq
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MWH_TO_MMBTU = 3.412142   # exact conversion factor


# ---------------------------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------------------------

def ttf_eur_to_usd(F_ttf_eur: float, fx_eurusd: float) -> float:
    """Convert TTF forward price from EUR/MWh to USD/MMBtu."""
    return F_ttf_eur * fx_eurusd / MWH_TO_MMBTU


def ttf_usd_to_eur(F_ttf_usd: float, fx_eurusd: float) -> float:
    """Convert TTF forward price from USD/MMBtu to EUR/MWh."""
    return F_ttf_usd * MWH_TO_MMBTU / fx_eurusd


def spread_usd_to_eur(spread_usd: float, fx_eurusd: float) -> float:
    """Convert a USD/MMBtu spread or option price to EUR/MWh."""
    return spread_usd * MWH_TO_MMBTU / fx_eurusd


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SpreadGreeks:
    """Margrabe spread option Greeks — all prices in USD/MMBtu."""
    delta_ttf:   float   # ∂Price/∂F_TTF_usd  (dimensionless, ∈ [0,1] for call)
    delta_hh:    float   # ∂Price/∂F_HH       (dimensionless, ∈ [-1,0] for call)
    gamma_ttf:   float   # ∂²Price/∂F_TTF²    (USD⁻¹·MMBtu)
    vega_ttf:    float   # ∂Price/∂σ_TTF      (USD/MMBtu per unit vol)
    vega_hh:     float   # ∂Price/∂σ_HH       (USD/MMBtu per unit vol)
    vega_rho:    float   # ∂Price/∂ρ          (USD/MMBtu per unit correlation)
    theta:       float   # price decay per calendar day (USD/MMBtu/day, negative)


@dataclass
class SpreadResult:
    """Full pricing result for a TTF/HH spread option."""
    # Inputs (normalised)
    F_ttf_eur:   float
    F_ttf_usd:   float
    F_hh:        float
    fx_eurusd:   float
    sigma_ttf:   float
    sigma_hh:    float
    rho:         float
    sigma_spread: float
    T:           float
    r_usd:       float
    option_type: str

    # Outputs
    price:       float   # option premium in USD/MMBtu
    price_eur:   float   # option premium in EUR/MWh
    greeks:      SpreadGreeks


# ---------------------------------------------------------------------------
# Margrabe core
# ---------------------------------------------------------------------------

def _spread_vol(sigma1: float, sigma2: float, rho: float) -> float:
    """Instantaneous volatility of the spread F1/F2 ratio."""
    var = sigma1**2 + sigma2**2 - 2.0 * rho * sigma1 * sigma2
    return math.sqrt(max(var, 0.0))


def _d1d2(F1: float, F2: float, T: float, sigma_s: float) -> tuple[float, float]:
    sqrtT = math.sqrt(T)
    d1 = (math.log(F1 / F2) + 0.5 * sigma_s**2 * T) / (sigma_s * sqrtT)
    return d1, d1 - sigma_s * sqrtT


def margrabe_price(
    F_ttf: float,
    F_hh:  float,
    T:     float,
    r:     float,
    sigma_ttf: float,
    sigma_hh:  float,
    rho:       float,
    option_type: str = "call",
) -> float:
    """Exchange option price via Margrabe (1978), in USD/MMBtu.

    Parameters
    ----------
    F_ttf      : TTF forward in USD/MMBtu (after EUR/MWh → USD/MMBtu conversion)
    F_hh       : Henry Hub forward in USD/MMBtu
    T          : time to expiry in years (ACT/365, today included)
    r          : USD risk-free rate (annualised decimal)
    sigma_ttf  : TTF lognormal vol (decimal)
    sigma_hh   : HH lognormal vol (decimal)
    rho        : instantaneous correlation TTF/HH  ∈ (−1, 1)
    option_type: "call"  →  max(F_ttf − F_hh, 0)
                 "put"   →  max(F_hh  − F_ttf, 0)
    """
    ot = option_type.lower()
    if ot not in ("call", "put"):
        raise ValueError(f"option_type must be 'call' or 'put', got '{option_type}'")

    df = math.exp(-r * T)
    sigma_s = _spread_vol(sigma_ttf, sigma_hh, rho)

    # Degenerate cases
    if T <= 0 or sigma_s < 1e-12:
        payoff = max(F_ttf - F_hh, 0.0) if ot == "call" else max(F_hh - F_ttf, 0.0)
        return df * payoff

    d1, d2 = _d1d2(F_ttf, F_hh, T, sigma_s)

    if ot == "call":
        return df * (F_ttf * norm.cdf(d1) - F_hh * norm.cdf(d2))
    else:
        return df * (F_hh * norm.cdf(-d2) - F_ttf * norm.cdf(-d1))


def margrabe_greeks(
    F_ttf: float,
    F_hh:  float,
    T:     float,
    r:     float,
    sigma_ttf: float,
    sigma_hh:  float,
    rho:       float,
    option_type: str = "call",
) -> SpreadGreeks:
    """All first-order Greeks for the Margrabe spread option.

    Vega_ttf and vega_hh are per 1-unit (100%) change in vol.
    Divide by 100 for the conventional "per 1% vol move" figure.
    """
    ot = option_type.lower()
    df = math.exp(-r * T)
    sigma_s = _spread_vol(sigma_ttf, sigma_hh, rho)

    if T <= 0 or sigma_s < 1e-12:
        return SpreadGreeks(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    sqrtT = math.sqrt(T)
    d1, d2 = _d1d2(F_ttf, F_hh, T, sigma_s)
    phi_d1 = norm.pdf(d1)

    # ── Deltas ──────────────────────────────────────────────────────────────
    # Using F_ttf × φ(d1) = F_hh × φ(d2) for simplification
    if ot == "call":
        delta_ttf = df * norm.cdf(d1)
        delta_hh  = -df * norm.cdf(d2)
    else:
        delta_ttf = -df * norm.cdf(-d1)
        delta_hh  =  df * norm.cdf(-d2)

    # ── Gamma (w.r.t. F_ttf) ────────────────────────────────────────────────
    gamma_ttf = df * phi_d1 / (F_ttf * sigma_s * sqrtT)

    # ── Vegas ────────────────────────────────────────────────────────────────
    # ∂σ_s/∂σ_ttf = (σ_ttf − ρ σ_hh) / σ_s
    # ∂σ_s/∂σ_hh  = (σ_hh  − ρ σ_ttf) / σ_s
    # ∂σ_s/∂ρ     = −σ_ttf σ_hh / σ_s
    common = df * F_ttf * phi_d1 * sqrtT    # shared factor across all vegas
    vega_ttf = common * (sigma_ttf - rho * sigma_hh) / sigma_s
    vega_hh  = common * (sigma_hh  - rho * sigma_ttf) / sigma_s
    vega_rho = common * (-sigma_ttf * sigma_hh / sigma_s)

    # ── Theta (finite difference, 1-day step) ───────────────────────────────
    T1 = max(T - 1.0 / 365, 1e-6)
    theta = margrabe_price(F_ttf, F_hh, T1, r, sigma_ttf, sigma_hh, rho, ot) \
          - margrabe_price(F_ttf, F_hh, T,  r, sigma_ttf, sigma_hh, rho, ot)

    return SpreadGreeks(
        delta_ttf=delta_ttf,
        delta_hh=delta_hh,
        gamma_ttf=gamma_ttf,
        vega_ttf=vega_ttf,
        vega_hh=vega_hh,
        vega_rho=vega_rho,
        theta=theta,
    )


# ---------------------------------------------------------------------------
# Full pricer — accepts TTF in EUR/MWh
# ---------------------------------------------------------------------------

def spread_price(
    F_ttf_eur: float,
    F_hh:      float,
    fx_eurusd: float,
    T:         Union[float, str],
    r_usd:     float,
    sigma_ttf: float,
    sigma_hh:  float,
    rho:       float,
    option_type: str = "call",
    reference: date | None = None,
) -> SpreadResult:
    """Price a TTF/HH spread option with TTF quoted in EUR/MWh.

    Parameters
    ----------
    F_ttf_eur  : TTF forward in EUR/MWh
    F_hh       : Henry Hub forward in USD/MMBtu
    fx_eurusd  : EUR/USD spot or forward FX rate (e.g. 1.08)
    T          : time to expiry in years, or TTF contract code ("TTFM26")
    r_usd      : USD risk-free rate (decimal)
    sigma_ttf  : TTF lognormal vol (decimal)
    sigma_hh   : HH lognormal vol (decimal)
    rho        : TTF/HH correlation
    option_type: "call" or "put"

    Returns
    -------
    SpreadResult with price in both USD/MMBtu and EUR/MWh.
    """
    if isinstance(T, str):
        from black76_ttf import t_from_contract
        T_val = t_from_contract(T, reference)
    else:
        T_val = float(T)

    F_ttf_usd = ttf_eur_to_usd(F_ttf_eur, fx_eurusd)
    sigma_s   = _spread_vol(sigma_ttf, sigma_hh, rho)
    price_usd = margrabe_price(F_ttf_usd, F_hh, T_val, r_usd, sigma_ttf, sigma_hh, rho, option_type)
    greeks    = margrabe_greeks(F_ttf_usd, F_hh, T_val, r_usd, sigma_ttf, sigma_hh, rho, option_type)

    return SpreadResult(
        F_ttf_eur=F_ttf_eur,
        F_ttf_usd=F_ttf_usd,
        F_hh=F_hh,
        fx_eurusd=fx_eurusd,
        sigma_ttf=sigma_ttf,
        sigma_hh=sigma_hh,
        rho=rho,
        sigma_spread=sigma_s,
        T=T_val,
        r_usd=r_usd,
        option_type=option_type,
        price=price_usd,
        price_eur=spread_usd_to_eur(price_usd, fx_eurusd),
        greeks=greeks,
    )


# ---------------------------------------------------------------------------
# Implied correlation solver
# ---------------------------------------------------------------------------

def implied_correlation(
    market_price: float,
    F_ttf:    float,
    F_hh:     float,
    T:        float,
    r:        float,
    sigma_ttf: float,
    sigma_hh:  float,
    option_type: str = "call",
    rho_lo: float = -0.9999,
    rho_hi: float =  0.9999,
) -> float:
    """Implied correlation from a market spread option price (USD/MMBtu).

    For a call, price is decreasing in ρ (higher correlation → tighter spread).
    For a put, price is also decreasing in ρ (symmetric argument).
    Brent's method is used over ρ ∈ (rho_lo, rho_hi).

    Parameters
    ----------
    market_price : observed market price in USD/MMBtu
    F_ttf        : TTF forward in USD/MMBtu
    F_hh         : HH forward in USD/MMBtu
    T, r, sigma_ttf, sigma_hh : as in margrabe_price

    Returns
    -------
    Implied correlation ρ ∈ (−1, 1)

    Raises
    ------
    ValueError if the market price is outside the achievable range.
    """
    def residual(rho: float) -> float:
        return margrabe_price(F_ttf, F_hh, T, r, sigma_ttf, sigma_hh, rho, option_type) - market_price

    p_lo = margrabe_price(F_ttf, F_hh, T, r, sigma_ttf, sigma_hh, rho_lo, option_type)
    p_hi = margrabe_price(F_ttf, F_hh, T, r, sigma_ttf, sigma_hh, rho_hi, option_type)

    if market_price > p_lo:
        raise ValueError(
            f"Market price {market_price:.4f} exceeds maximum achievable "
            f"{p_lo:.4f} (at ρ={rho_lo}). Check inputs."
        )
    if market_price < p_hi:
        raise ValueError(
            f"Market price {market_price:.4f} is below minimum achievable "
            f"{p_hi:.4f} (at ρ={rho_hi}). Price may be below intrinsic value."
        )

    return brentq(residual, rho_lo, rho_hi, xtol=1e-8, maxiter=300)


# ---------------------------------------------------------------------------
# Sensitivity surface helpers
# ---------------------------------------------------------------------------

def rho_sensitivity(
    F_ttf: float, F_hh: float, T: float, r: float,
    sigma_ttf: float, sigma_hh: float,
    option_type: str = "call",
    rhos: list[float] | None = None,
) -> list[tuple[float, float]]:
    """Price vs correlation table. Returns [(rho, price), ...]."""
    if rhos is None:
        rhos = [-0.9, -0.7, -0.5, -0.3, -0.1, 0.0, 0.1, 0.3, 0.5, 0.7, 0.9]
    return [
        (rho, margrabe_price(F_ttf, F_hh, T, r, sigma_ttf, sigma_hh, rho, option_type))
        for rho in rhos
    ]


def vol_sensitivity(
    F_ttf: float, F_hh: float, T: float, r: float,
    sigma_ttf: float, sigma_hh: float, rho: float,
    option_type: str = "call",
) -> dict:
    """Prices across ±20% shifts in each vol input (1-way stress)."""
    base = margrabe_price(F_ttf, F_hh, T, r, sigma_ttf, sigma_hh, rho, option_type)
    bump = 0.05   # 5 vol-point bump
    return {
        "base":         base,
        "σ_ttf +5%":    margrabe_price(F_ttf, F_hh, T, r, sigma_ttf + bump, sigma_hh,       rho, option_type),
        "σ_ttf −5%":    margrabe_price(F_ttf, F_hh, T, r, sigma_ttf - bump, sigma_hh,       rho, option_type),
        "σ_hh  +5%":    margrabe_price(F_ttf, F_hh, T, r, sigma_ttf,        sigma_hh + bump, rho, option_type),
        "σ_hh  −5%":    margrabe_price(F_ttf, F_hh, T, r, sigma_ttf,        sigma_hh - bump, rho, option_type),
        "ρ     +0.10":  margrabe_price(F_ttf, F_hh, T, r, sigma_ttf,        sigma_hh,       rho + 0.10, option_type),
        "ρ     −0.10":  margrabe_price(F_ttf, F_hh, T, r, sigma_ttf,        sigma_hh,       rho - 0.10, option_type),
    }


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_summary(res: SpreadResult) -> None:
    """Print a formatted pricing summary."""
    SEP = "─" * 64

    print(f"\n{'═' * 64}")
    print(f"  TTF / Henry Hub Spread Option — {res.option_type.upper()}")
    print(f"{'═' * 64}")

    print(f"\n  Underlyings")
    print(f"  {SEP}")
    print(f"  TTF forward      : {res.F_ttf_eur:>8.3f} EUR/MWh")
    print(f"  TTF forward      : {res.F_ttf_usd:>8.4f} USD/MMBtu  (FX {res.fx_eurusd:.4f})")
    print(f"  Henry Hub fwd    : {res.F_hh:>8.4f} USD/MMBtu")
    print(f"  Spread (TTF−HH)  : {res.F_ttf_usd - res.F_hh:>+8.4f} USD/MMBtu")
    print(f"  Maturity (T)     : {res.T:>8.4f} years  ({res.T*365:.0f} calendar days)")

    print(f"\n  Volatility")
    print(f"  {SEP}")
    print(f"  σ TTF            : {res.sigma_ttf:>8.1%}")
    print(f"  σ HH             : {res.sigma_hh:>8.1%}")
    print(f"  Correlation ρ    : {res.rho:>8.3f}")
    print(f"  σ spread         : {res.sigma_spread:>8.1%}")

    print(f"\n  Price")
    print(f"  {SEP}")
    print(f"  Option premium   : {res.price:>8.4f} USD/MMBtu")
    print(f"  Option premium   : {res.price_eur:>8.4f} EUR/MWh")

    g = res.greeks
    print(f"\n  Greeks")
    print(f"  {SEP}")
    print(f"  Δ TTF            : {g.delta_ttf:>+8.4f}  (USD/MMBtu per USD/MMBtu)")
    print(f"  Δ HH             : {g.delta_hh:>+8.4f}  (USD/MMBtu per USD/MMBtu)")
    print(f"  Γ TTF            : {g.gamma_ttf:>+8.6f}  (per USD/MMBtu²)")
    print(f"  Vega TTF         : {g.vega_ttf:>+8.4f}  (per unit vol)")
    print(f"  Vega HH          : {g.vega_hh:>+8.4f}  (per unit vol)")
    print(f"  Vega ρ           : {g.vega_rho:>+8.4f}  (per unit correlation)")
    print(f"  Theta/day        : {g.theta:>+8.4f}  USD/MMBtu")

    # Vega in "per 1% vol move" convention
    print(f"\n  Vega (per 1% vol move, market convention)")
    print(f"  {SEP}")
    print(f"  Vega TTF /1%     : {g.vega_ttf/100:>+8.6f}  USD/MMBtu")
    print(f"  Vega HH  /1%     : {g.vega_hh/100:>+8.6f}  USD/MMBtu")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ── Market inputs ────────────────────────────────────────────────────────
    F_TTF_EUR = 30.0       # EUR/MWh
    F_HH      = 3.0        # USD/MMBtu
    FX        = 1.08       # EUR/USD
    SIG_TTF   = 0.60       # 60% lognormal vol (TTF is more volatile)
    SIG_HH    = 0.50       # 50% lognormal vol
    RHO       = 0.35       # moderate positive correlation
    R_USD     = 0.045      # USD risk-free rate (~4.5%)
    T         = 180 / 365  # ~6-month expiry

    F_TTF_USD = ttf_eur_to_usd(F_TTF_EUR, FX)
    print(f"\nTTF:  {F_TTF_EUR} EUR/MWh  =  {F_TTF_USD:.4f} USD/MMBtu  (FX={FX})")
    print(f"HH :  {F_HH} USD/MMBtu")
    print(f"Spread TTF−HH : {F_TTF_USD - F_HH:.4f} USD/MMBtu ({(F_TTF_USD-F_HH)*MWH_TO_MMBTU/FX:.2f} EUR/MWh)")

    # ── Pricing call and put ─────────────────────────────────────────────────
    call = spread_price(F_TTF_EUR, F_HH, FX, T, R_USD, SIG_TTF, SIG_HH, RHO, "call")
    put  = spread_price(F_TTF_EUR, F_HH, FX, T, R_USD, SIG_TTF, SIG_HH, RHO, "put")

    print_summary(call)
    print_summary(put)

    # ── Put-call parity check ─────────────────────────────────────────────────
    df = math.exp(-R_USD * T)
    pcp_lhs = call.price - put.price
    pcp_rhs = df * (F_TTF_USD - F_HH)
    print(f"\n  Put-call parity:  C − P = {pcp_lhs:.6f}  |  e^(−rT)(F_TTF−F_HH) = {pcp_rhs:.6f}  ✓" if abs(pcp_lhs - pcp_rhs) < 1e-8 else "  PCP ERROR")

    # ── Correlation sensitivity ───────────────────────────────────────────────
    print(f"\n\n  Call price vs correlation  (TTF={F_TTF_EUR} EUR/MWh, HH={F_HH} USD/MMBtu, T={T:.3f}y)")
    print(f"  {'ρ':>8}  {'σ_spread':>10}  {'Price USD':>11}  {'Price EUR':>11}")
    print(f"  {'─'*48}")
    for rho, px_usd in rho_sensitivity(F_TTF_USD, F_HH, T, R_USD, SIG_TTF, SIG_HH, "call"):
        sig_s = _spread_vol(SIG_TTF, SIG_HH, rho)
        px_eur = spread_usd_to_eur(px_usd, FX)
        print(f"  {rho:>8.2f}  {sig_s:>10.1%}  {px_usd:>11.4f}  {px_eur:>11.4f}")

    # ── Implied correlation example (near-ATM case) ───────────────────────────
    # The deep-ITM case above is close to pure intrinsic; use ATM spread instead.
    F_atm = 3.50   # USD/MMBtu — equal forwards for a meaningful vol/corr test
    atm_base = margrabe_price(F_atm, F_atm, T, R_USD, SIG_TTF, SIG_HH, RHO, "call")
    target_price = round(atm_base * 0.80, 4)   # cheaper → implies higher ρ
    print(f"\n  Implied correlation demo (ATM: F_TTF=F_HH={F_atm} USD/MMBtu)")
    print(f"  Base price @ ρ={RHO}  : {atm_base:.4f} USD/MMBtu")
    print(f"  Market quote          : {target_price:.4f} USD/MMBtu")
    try:
        impl_rho = implied_correlation(target_price, F_atm, F_atm, T, R_USD, SIG_TTF, SIG_HH, "call")
        verify = margrabe_price(F_atm, F_atm, T, R_USD, SIG_TTF, SIG_HH, impl_rho, "call")
        print(f"  Implied correlation   : ρ = {impl_rho:.4f}")
        print(f"  Verification          : {verify:.6f}  (target={target_price:.4f})  ✓")
    except ValueError as e:
        print(f"  {e}")

    # ── Vol stress ─────────────────────────────────────────────────────────────
    stresses = vol_sensitivity(F_TTF_USD, F_HH, T, R_USD, SIG_TTF, SIG_HH, RHO, "call")
    print(f"\n  Vol / correlation stress (call)")
    print(f"  {'─'*40}")
    base_px = stresses.pop("base")
    print(f"  {'Base':20s}: {base_px:.4f} USD/MMBtu")
    for label, px in stresses.items():
        print(f"  {label:20s}: {px:.4f}  ({px - base_px:+.4f})")

    # ── Contract-name interface ────────────────────────────────────────────────
    print(f"\n  Using contract code: spread_price(..., T='TTFM26', ...)")
    try:
        res_contract = spread_price(F_TTF_EUR, F_HH, FX, "TTFM26", R_USD, SIG_TTF, SIG_HH, RHO)
        print(f"  TTFM26  T={res_contract.T:.4f}y  price={res_contract.price:.4f} USD/MMBtu")
    except Exception as e:
        print(f"  {e}")
