"""TTF Natural Gas Options — Multi-Leg Structure Pricer.

All structures use Black-76 (lognormal vol, options on TTF futures).
Prices in EUR/MWh, vol in decimal (0.50 = 50%), T in years (ACT/365).

Each function returns a StructureResult with:
  - Net premium (positive = debit paid, negative = credit received)
  - Net Greeks (delta, gamma, vega, theta)
  - P&L at expiry across a price grid
  - Breakeven prices

Structures
----------
1.  straddle         long call + long put (same strike)
2.  strangle         long OTM call + long OTM put (different strikes)
3.  bull_call_spread long call K_lo + short call K_hi
4.  bear_put_spread  long put K_hi + short put K_lo
5.  butterfly        long call K_lo + short 2x call K_mid + long call K_hi
6.  condor           long call K1 + short call K2 + short call K3 + long call K4
7.  collar           long put K_put + short call K_call  (options overlay only)
8.  risk_reversal    long call K_call + short put K_put
9.  calendar_spread  long call T_far + short call T_near (same strike, same sigma)
10. ratio_spread     long 1x call K_lo + short N calls K_hi  (default N=2)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Union

from black76_ttf import (
    b76_price, b76_delta, b76_gamma, b76_vega, b76_theta,
    t_from_contract,
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Leg:
    option_type: str   # "call" or "put"
    K: float
    T: float
    sign: int          # +1 long, -1 short
    qty: int           # absolute quantity (e.g. 2 for ratio short leg)
    sigma: float
    unit_price: float
    unit_delta: float
    unit_gamma: float
    unit_vega: float
    unit_theta: float

    @property
    def net_price(self) -> float:  return self.sign * self.qty * self.unit_price
    @property
    def net_delta(self) -> float:  return self.sign * self.qty * self.unit_delta
    @property
    def net_gamma(self) -> float:  return self.sign * self.qty * self.unit_gamma
    @property
    def net_vega(self) -> float:   return self.sign * self.qty * self.unit_vega
    @property
    def net_theta(self) -> float:  return self.sign * self.qty * self.unit_theta


@dataclass
class StructureResult:
    name: str
    legs: list[Leg]
    price: float                             # net premium (+ debit / - credit)
    delta: float
    gamma: float
    vega: float
    theta: float
    pnl_at_expiry: list[tuple[float, float]] # (F_T, pnl) grid
    breakevens: list[float]
    max_profit: float                        # math.inf if unlimited
    max_loss: float                          # -math.inf if unlimited


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_T(t_or_contract: Union[float, str], reference: date | None = None) -> float:
    if isinstance(t_or_contract, str):
        return t_from_contract(t_or_contract, reference)
    return float(t_or_contract)


def _make_leg(
    option_type: str, K: float, T: float, sign: int, qty: int,
    sigma: float, F: float, r: float,
) -> Leg:
    return Leg(
        option_type=option_type, K=K, T=T, sign=sign, qty=qty, sigma=sigma,
        unit_price=b76_price(F, K, T, r, sigma, option_type),
        unit_delta=b76_delta(F, K, T, r, sigma, option_type),
        unit_gamma=b76_gamma(F, K, T, r, sigma),
        unit_vega=b76_vega(F, K, T, r, sigma),
        unit_theta=b76_theta(F, K, T, r, sigma, option_type),
    )


def _payoff(option_type: str, K: float, F_T: float) -> float:
    return max(F_T - K, 0.0) if option_type == "call" else max(K - F_T, 0.0)


def _price_grid(F: float, sigma: float, T: float, n: int = 200) -> list[float]:
    """Sensible ±3σ price range centred on F."""
    width = max(3.0 * sigma * math.sqrt(max(T, 1 / 365)) * F, 0.45 * F)
    lo = max(F - width, 0.01)
    hi = F + width
    return [lo + i * (hi - lo) / (n - 1) for i in range(n)]


def _expiry_pnl(
    legs: list[Leg], net_price: float, grid: list[float]
) -> list[tuple[float, float]]:
    out = []
    for F_T in grid:
        payoff = sum(
            leg.sign * leg.qty * _payoff(leg.option_type, leg.K, F_T)
            for leg in legs
        )
        out.append((F_T, payoff - net_price))
    return out


def _breakevens(pnl_curve: list[tuple[float, float]]) -> list[float]:
    bks: list[float] = []
    for i in range(len(pnl_curve) - 1):
        F0, p0 = pnl_curve[i]
        F1, p1 = pnl_curve[i + 1]
        if p0 * p1 < 0:
            alpha = -p0 / (p1 - p0)
            bks.append(round(F0 + alpha * (F1 - F0), 4))
        elif abs(p0) < 1e-6:
            bks.append(round(F0, 4))
    return sorted(set(bks))


def _build(
    name: str,
    legs: list[Leg],
    pnl_curve: list[tuple[float, float]],
    max_profit: float | None = None,
    max_loss: float | None = None,
) -> StructureResult:
    pnls = [p for _, p in pnl_curve]
    return StructureResult(
        name=name,
        legs=legs,
        price=sum(l.net_price for l in legs),
        delta=sum(l.net_delta for l in legs),
        gamma=sum(l.net_gamma for l in legs),
        vega=sum(l.net_vega for l in legs),
        theta=sum(l.net_theta for l in legs),
        pnl_at_expiry=pnl_curve,
        breakevens=_breakevens(pnl_curve),
        max_profit=max_profit if max_profit is not None else max(pnls),
        max_loss=max_loss if max_loss is not None else min(pnls),
    )


# ---------------------------------------------------------------------------
# 1. Straddle — long call + long put, same strike
# ---------------------------------------------------------------------------

def straddle(
    F: float, K: float, T: Union[float, str], r: float, sigma: float,
    *,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Long ATM call + long ATM put.

    Profits when the forward moves significantly in either direction.
    Max loss = net premium paid, at expiry with F_T = K.
    """
    T_ = _resolve_T(T, reference)
    legs = [
        _make_leg("call", K, T_, +1, 1, sigma, F, r),
        _make_leg("put",  K, T_, +1, 1, sigma, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = [(F_T, abs(F_T - K) - net_price) for F_T in grid]
    return _build("Straddle", legs, pnl, max_profit=math.inf, max_loss=min(p for _, p in pnl))


# ---------------------------------------------------------------------------
# 2. Strangle — long OTM call + long OTM put
# ---------------------------------------------------------------------------

def strangle(
    F: float, K_put: float, K_call: float, T: Union[float, str], r: float, sigma: float,
    *,
    sigma_put: float | None = None,
    sigma_call: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Long OTM put (K_put < F) + long OTM call (K_call > F).

    Cheaper than straddle but needs a larger move to profit.
    Max loss = net premium, in the range K_put ≤ F_T ≤ K_call.
    """
    if K_put >= K_call:
        raise ValueError("K_put must be < K_call")
    T_ = _resolve_T(T, reference)
    sp = sigma_put  or sigma
    sc = sigma_call or sigma
    legs = [
        _make_leg("put",  K_put,  T_, +1, 1, sp, F, r),
        _make_leg("call", K_call, T_, +1, 1, sc, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    return _build("Strangle", legs, pnl, max_profit=math.inf, max_loss=min(p for _, p in pnl))


# ---------------------------------------------------------------------------
# 3. Bull Call Spread — long call K_lo + short call K_hi
# ---------------------------------------------------------------------------

def bull_call_spread(
    F: float, K_lo: float, K_hi: float, T: Union[float, str], r: float, sigma: float,
    *,
    sigma_lo: float | None = None,
    sigma_hi: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Bullish debit spread: profits when F_T rises above K_lo.

    Max profit = (K_hi - K_lo) - debit, at F_T ≥ K_hi.
    Max loss   = debit paid, at F_T ≤ K_lo.
    Breakeven  ≈ K_lo + debit.
    """
    if K_lo >= K_hi:
        raise ValueError("K_lo must be < K_hi")
    T_ = _resolve_T(T, reference)
    sl = sigma_lo or sigma
    sh = sigma_hi or sigma
    legs = [
        _make_leg("call", K_lo, T_, +1, 1, sl, F, r),
        _make_leg("call", K_hi, T_, -1, 1, sh, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    max_profit = (K_hi - K_lo) - net_price
    max_loss   = -net_price
    return _build("Bull Call Spread", legs, pnl, max_profit, max_loss)


# ---------------------------------------------------------------------------
# 4. Bear Put Spread — long put K_hi + short put K_lo
# ---------------------------------------------------------------------------

def bear_put_spread(
    F: float, K_lo: float, K_hi: float, T: Union[float, str], r: float, sigma: float,
    *,
    sigma_lo: float | None = None,
    sigma_hi: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Bearish debit spread: profits when F_T falls below K_hi.

    Max profit = (K_hi - K_lo) - debit, at F_T ≤ K_lo.
    Max loss   = debit paid, at F_T ≥ K_hi.
    Breakeven  ≈ K_hi - debit.
    """
    if K_lo >= K_hi:
        raise ValueError("K_lo must be < K_hi")
    T_ = _resolve_T(T, reference)
    sl = sigma_lo or sigma
    sh = sigma_hi or sigma
    legs = [
        _make_leg("put", K_hi, T_, +1, 1, sh, F, r),
        _make_leg("put", K_lo, T_, -1, 1, sl, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    max_profit = (K_hi - K_lo) - net_price
    max_loss   = -net_price
    return _build("Bear Put Spread", legs, pnl, max_profit, max_loss)


# ---------------------------------------------------------------------------
# 5. Butterfly — long K_lo + short 2x K_mid + long K_hi (calls)
# ---------------------------------------------------------------------------

def butterfly(
    F: float,
    K_lo: float, K_mid: float, K_hi: float,
    T: Union[float, str], r: float, sigma: float,
    *,
    sigma_lo: float | None = None,
    sigma_mid: float | None = None,
    sigma_hi: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Symmetric butterfly (calls): profits if F_T ≈ K_mid at expiry.

    Max profit ≈ (K_mid - K_lo) - debit, at F_T = K_mid.
    Max loss   = debit, at F_T ≤ K_lo or F_T ≥ K_hi.
    """
    if not (K_lo < K_mid < K_hi):
        raise ValueError("Require K_lo < K_mid < K_hi")
    T_ = _resolve_T(T, reference)
    legs = [
        _make_leg("call", K_lo,  T_, +1, 1, sigma_lo  or sigma, F, r),
        _make_leg("call", K_mid, T_, -1, 2, sigma_mid or sigma, F, r),
        _make_leg("call", K_hi,  T_, +1, 1, sigma_hi  or sigma, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    max_profit = (K_mid - K_lo) - net_price
    max_loss   = -net_price
    return _build("Butterfly", legs, pnl, max_profit, max_loss)


# ---------------------------------------------------------------------------
# 6. Condor — long K1 + short K2 + short K3 + long K4 (calls)
# ---------------------------------------------------------------------------

def condor(
    F: float,
    K1: float, K2: float, K3: float, K4: float,
    T: Union[float, str], r: float, sigma: float,
    *,
    sigmas: tuple[float, float, float, float] | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Call condor: wider profit zone than butterfly, smaller max profit.

    Max profit = (K2 - K1) - debit, when K2 ≤ F_T ≤ K3.
    Max loss   = debit, at F_T ≤ K1 or F_T ≥ K4.
    """
    if not (K1 < K2 < K3 < K4):
        raise ValueError("Require K1 < K2 < K3 < K4")
    T_ = _resolve_T(T, reference)
    s1, s2, s3, s4 = sigmas if sigmas else (sigma, sigma, sigma, sigma)
    legs = [
        _make_leg("call", K1, T_, +1, 1, s1, F, r),
        _make_leg("call", K2, T_, -1, 1, s2, F, r),
        _make_leg("call", K3, T_, -1, 1, s3, F, r),
        _make_leg("call", K4, T_, +1, 1, s4, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    max_profit = (K2 - K1) - net_price
    max_loss   = -net_price
    return _build("Condor", legs, pnl, max_profit, max_loss)


# ---------------------------------------------------------------------------
# 7. Collar — long put K_put + short call K_call (options overlay)
# ---------------------------------------------------------------------------

def collar(
    F: float, K_put: float, K_call: float, T: Union[float, str], r: float, sigma: float,
    *,
    sigma_put: float | None = None,
    sigma_call: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Options overlay for a long futures position.

    Long put (floor) + short call (cap). The net premium is often near zero
    (zero-cost collar). P&L shown for the options overlay alone — add your
    futures P&L (F_T - F_entry) to get total hedged P&L.

    Max profit on overlay = K_put - net_premium (if F_T → 0, put deep ITM).
    Max loss on overlay   = unlimited (short call has no cap on upside).
    """
    if K_put >= K_call:
        raise ValueError("K_put must be < K_call")
    T_ = _resolve_T(T, reference)
    sp = sigma_put  or sigma
    sc = sigma_call or sigma
    legs = [
        _make_leg("put",  K_put,  T_, +1, 1, sp, F, r),
        _make_leg("call", K_call, T_, -1, 1, sc, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    return _build("Collar", legs, pnl, max_profit=max(p for _, p in pnl), max_loss=-math.inf)


# ---------------------------------------------------------------------------
# 8. Risk Reversal — long call K_call + short put K_put
# ---------------------------------------------------------------------------

def risk_reversal(
    F: float, K_put: float, K_call: float, T: Union[float, str], r: float, sigma: float,
    *,
    sigma_put: float | None = None,
    sigma_call: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Directionally bullish: profits from upside, loses on downside.

    Net premium is often small (near zero-cost if skew is symmetric).
    Max profit = unlimited (long call).
    Max loss   = unlimited downside (short put).
    """
    if K_put >= K_call:
        raise ValueError("K_put must be < K_call")
    T_ = _resolve_T(T, reference)
    sp = sigma_put  or sigma
    sc = sigma_call or sigma
    legs = [
        _make_leg("call", K_call, T_, +1, 1, sc, F, r),
        _make_leg("put",  K_put,  T_, -1, 1, sp, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    return _build("Risk Reversal", legs, pnl, max_profit=math.inf, max_loss=-math.inf)


# ---------------------------------------------------------------------------
# 9. Calendar Spread — long far-dated call + short near-dated call
# ---------------------------------------------------------------------------

def calendar_spread(
    F: float, K: float,
    T_far: Union[float, str], T_near: Union[float, str],
    r: float, sigma: float,
    *,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Long vol in the far tenor, short vol in the near tenor (same strike).

    P&L is evaluated at the near-term expiry, assuming the far option retains
    its remaining time value (T_far − T_near) at the same sigma.

    Profits when implied vol rises or when the near option decays faster.
    Max profit occurs near K at near-term expiry (maximum time-value capture).
    Max loss ≈ net debit paid.
    """
    T_far_  = _resolve_T(T_far,  reference)
    T_near_ = _resolve_T(T_near, reference)
    if T_far_ <= T_near_:
        raise ValueError("T_far must be > T_near")

    legs = [
        _make_leg("call", K, T_far_,  +1, 1, sigma, F, r),
        _make_leg("call", K, T_near_, -1, 1, sigma, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    T_remaining = T_far_ - T_near_

    grid = _price_grid(F, sigma, T_near_, n_points)
    pnl: list[tuple[float, float]] = []
    for F_T in grid:
        far_val  = b76_price(F_T, K, T_remaining, r, sigma, "call")
        near_val = _payoff("call", K, F_T)          # near option expired
        pnl.append((F_T, far_val - near_val - net_price))

    return _build("Calendar Spread", legs, pnl)


# ---------------------------------------------------------------------------
# 10. Ratio Spread — long 1 call K_lo + short N calls K_hi
# ---------------------------------------------------------------------------

def ratio_spread(
    F: float, K_lo: float, K_hi: float, T: Union[float, str], r: float, sigma: float,
    *,
    ratio: int = 2,
    sigma_lo: float | None = None,
    sigma_hi: float | None = None,
    reference: date | None = None,
    n_points: int = 200,
) -> StructureResult:
    """Long 1 call at K_lo, short `ratio` calls at K_hi.

    Often structured for zero or small net credit.
    Max profit ≈ (K_hi - K_lo) - net_premium, at F_T = K_hi.
    Max loss on upside = unlimited when ratio > 1  (as F_T → ∞).
    Max loss on downside = net_premium if debit, 0 if credit.
    """
    if K_lo >= K_hi:
        raise ValueError("K_lo must be < K_hi")
    if ratio < 1:
        raise ValueError("ratio must be ≥ 1")
    T_ = _resolve_T(T, reference)
    sl = sigma_lo or sigma
    sh = sigma_hi or sigma
    legs = [
        _make_leg("call", K_lo, T_, +1,     1, sl, F, r),
        _make_leg("call", K_hi, T_, -1, ratio, sh, F, r),
    ]
    net_price = sum(l.net_price for l in legs)
    grid = _price_grid(F, sigma, T_, n_points)
    pnl = _expiry_pnl(legs, net_price, grid)
    max_profit = (K_hi - K_lo) - net_price
    max_loss   = -net_price if net_price > 0 else 0.0
    return _build(
        f"Ratio Spread (1x{ratio})", legs, pnl,
        max_profit=max_profit,
        max_loss=-math.inf if ratio > 1 else max_loss,
    )


# ---------------------------------------------------------------------------
# Display helper
# ---------------------------------------------------------------------------

def print_summary(result: StructureResult) -> None:
    """Print a formatted summary of the structure."""
    SEP = "─" * 62
    print(f"\n{'═' * 62}")
    print(f"  {result.name}")
    print(f"{'═' * 62}")

    premium_label = "debit" if result.price >= 0 else "credit"
    print(f"  Net premium   : {result.price:+.4f} EUR/MWh  ({premium_label})")
    print(f"  Net delta     : {result.delta:+.4f}")
    print(f"  Net gamma     : {result.gamma:+.6f}")
    print(f"  Net vega      : {result.vega:+.4f}")
    print(f"  Net theta/day : {result.theta:+.4f}")

    if result.breakevens:
        be_str = "  ".join(f"{b:.3f}" for b in result.breakevens)
        print(f"  Breakevens    : {be_str}")
    else:
        print(f"  Breakevens    : none in price range")

    mp = f"{result.max_profit:.4f}" if result.max_profit != math.inf  else "∞  (unlimited)"
    ml = f"{result.max_loss:.4f}"   if result.max_loss   != -math.inf else "-∞ (unlimited)"
    print(f"  Max profit    : {mp}")
    print(f"  Max loss      : {ml}")

    print(f"\n  Legs:")
    print(f"  {'#':<3} {'side':<6} {'type':<5} {'qty':<4} {'K':>8}  {'T':>7}  {'σ':>6}  {'price':>8}")
    print(f"  {SEP}")
    for i, leg in enumerate(result.legs, 1):
        side = "long " if leg.sign > 0 else "short"
        print(
            f"  {i:<3} {side:<6} {leg.option_type:<5} {leg.qty:<4} "
            f"{leg.K:>8.3f}  {leg.T:>7.4f}  {leg.sigma:>6.1%}  {leg.unit_price:>8.4f}"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from datetime import date as _d

    F    = 35.0          # TTF forward EUR/MWh
    r    = 0.03          # risk-free rate
    sig  = 0.50          # 50% lognormal vol
    T    = 90 / 365      # ~3-month expiry

    structures = [
        straddle(F, K=35.0, T=T, r=r, sigma=sig),
        strangle(F, K_put=32.0, K_call=38.0, T=T, r=r, sigma=sig),
        bull_call_spread(F, K_lo=34.0, K_hi=38.0, T=T, r=r, sigma=sig),
        bear_put_spread(F, K_lo=32.0, K_hi=36.0, T=T, r=r, sigma=sig),
        butterfly(F, K_lo=31.0, K_mid=35.0, K_hi=39.0, T=T, r=r, sigma=sig),
        condor(F, K1=30.0, K2=33.0, K3=37.0, K4=40.0, T=T, r=r, sigma=sig),
        collar(F, K_put=32.0, K_call=38.0, T=T, r=r, sigma=sig),
        risk_reversal(F, K_put=32.0, K_call=38.0, T=T, r=r, sigma=sig),
        calendar_spread(F, K=35.0, T_far=180/365, T_near=90/365, r=r, sigma=sig),
        ratio_spread(F, K_lo=35.0, K_hi=38.0, T=T, r=r, sigma=sig, ratio=2),
    ]

    for s in structures:
        print_summary(s)
