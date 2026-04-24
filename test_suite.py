"""Test suite for black76_ttf.py — PASS/FAIL report.

Covers:
  [1] Black-76 prices      Call/Put > 0 across the parameter grid
  [2] Bachelier prices     Call/Put > 0 across the parameter grid
  [3] Black-76 Greeks      call-put delta parity, gamma/vega >= 0,
                           vanna/volga finite
  [4] Bachelier Greeks     same battery as above
  [5] Put-Call Parity      C - P == exp(-rT) * (F - K)   (both models)
  [6] IV solver round-trip price -> solve -> sigma recovered
  [7] Expiry dates 2026    business day + before delivery month

Parameters
----------
Forward   : 30 EUR/MWh
Strikes   : 25, 28, 30, 32, 35
Vol B76   : 50 %   (sigma lognormal decimal)
Vol Bach  : 15 EUR/MWh  (= F * sigma_log, standard rule of thumb)
Maturites : 1 / 3 / 6 / 12 months (ACT/365)
Taux      : 2 %
"""

from __future__ import annotations

import math
from datetime import date

from black76_ttf import (
    b76_call, b76_put,
    b76_delta, b76_gamma, b76_vega, b76_vanna, b76_volga,
    bach_call, bach_put,
    bach_delta, bach_gamma, bach_vega, bach_vanna, bach_volga,
    b76_implied_vol, bach_implied_vol,
    ttf_expiry_date,
)

from structures_ttf import (
    straddle, strangle, bull_call_spread, bear_put_spread,
    butterfly, condor, collar, risk_reversal,
    calendar_spread, ratio_spread,
)

from ttf_hh_spread import (
    spread_price, margrabe_price, implied_correlation,
    ttf_eur_to_usd, _spread_vol,
)


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

F           = 30.0
STRIKES     = [25.0, 28.0, 30.0, 32.0, 35.0]
SIGMA_LOG   = 0.50
SIGMA_NORM  = 15.0                     # ~ F * SIGMA_LOG
MATURITIES  = {"1M": 1 / 12, "3M": 3 / 12, "6M": 6 / 12, "12M": 1.0}
R           = 0.02

TOL_PARITY  = 1e-8
TOL_IV_B76  = 1e-6
TOL_IV_BACH = 1e-4


# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

_results: list[tuple[str, bool, str]] = []


def record(name: str, passed: bool, msg: str = "") -> None:
    _results.append((name, passed, msg))
    tag = "PASS" if passed else "FAIL"
    detail = f"  -- {msg}" if msg else ""
    print(f"  [{tag}] {name}{detail}")


# ---------------------------------------------------------------------------
# [1] Black-76 prices
# ---------------------------------------------------------------------------

def test_b76_prices() -> None:
    for T_label, T in MATURITIES.items():
        for K in STRIKES:
            c = b76_call(F, K, T, R, SIGMA_LOG)
            p = b76_put(F, K, T, R, SIGMA_LOG)
            ok = c >= 0.0 and p >= 0.0 and math.isfinite(c) and math.isfinite(p)
            record(
                f"B76 price T={T_label} K={K:.0f}", ok,
                f"call={c:.6f} put={p:.6f}",
            )


# ---------------------------------------------------------------------------
# [2] Bachelier prices
# ---------------------------------------------------------------------------

def test_bach_prices() -> None:
    for T_label, T in MATURITIES.items():
        for K in STRIKES:
            c = bach_call(F, K, T, R, SIGMA_NORM)
            p = bach_put(F, K, T, R, SIGMA_NORM)
            ok = c >= 0.0 and p >= 0.0 and math.isfinite(c) and math.isfinite(p)
            record(
                f"Bach price T={T_label} K={K:.0f}", ok,
                f"call={c:.6f} put={p:.6f}",
            )


# ---------------------------------------------------------------------------
# [3] Black-76 Greeks
# ---------------------------------------------------------------------------

def test_b76_greeks() -> None:
    for T_label, T in MATURITIES.items():
        df = math.exp(-R * T)
        for K in STRIKES:
            d_c = b76_delta(F, K, T, R, SIGMA_LOG, "call")
            d_p = b76_delta(F, K, T, R, SIGMA_LOG, "put")
            g   = b76_gamma(F, K, T, R, SIGMA_LOG)
            v   = b76_vega(F, K, T, R, SIGMA_LOG)
            vn  = b76_vanna(F, K, T, R, SIGMA_LOG)
            vg  = b76_volga(F, K, T, R, SIGMA_LOG)

            parity = abs((d_c - d_p) - df)
            record(
                f"B76 delta parity T={T_label} K={K:.0f}", parity < TOL_PARITY,
                f"C-P={d_c - d_p:.8f} theo={df:.8f} diff={parity:.2e}",
            )
            record(
                f"B76 gamma/vega >= 0 T={T_label} K={K:.0f}",
                g >= 0.0 and v >= 0.0,
                f"gamma={g:.6f} vega={v:.6f}",
            )
            record(
                f"B76 vanna/volga finite T={T_label} K={K:.0f}",
                math.isfinite(vn) and math.isfinite(vg),
                f"vanna={vn:+.6f} volga={vg:+.6f}",
            )


# ---------------------------------------------------------------------------
# [4] Bachelier Greeks
# ---------------------------------------------------------------------------

def test_bach_greeks() -> None:
    for T_label, T in MATURITIES.items():
        df = math.exp(-R * T)
        for K in STRIKES:
            d_c = bach_delta(F, K, T, R, SIGMA_NORM, "call")
            d_p = bach_delta(F, K, T, R, SIGMA_NORM, "put")
            g   = bach_gamma(F, K, T, R, SIGMA_NORM)
            v   = bach_vega(F, K, T, R, SIGMA_NORM)
            vn  = bach_vanna(F, K, T, R, SIGMA_NORM)
            vg  = bach_volga(F, K, T, R, SIGMA_NORM)

            parity = abs((d_c - d_p) - df)
            record(
                f"Bach delta parity T={T_label} K={K:.0f}", parity < TOL_PARITY,
                f"C-P={d_c - d_p:.8f} theo={df:.8f} diff={parity:.2e}",
            )
            record(
                f"Bach gamma/vega >= 0 T={T_label} K={K:.0f}",
                g >= 0.0 and v >= 0.0,
                f"gamma={g:.6f} vega={v:.6f}",
            )
            record(
                f"Bach vanna/volga finite T={T_label} K={K:.0f}",
                math.isfinite(vn) and math.isfinite(vg),
                f"vanna={vn:+.6f} volga={vg:+.6f}",
            )


# ---------------------------------------------------------------------------
# [5] Put-Call Parity:  C - P == exp(-rT) * (F - K)
# ---------------------------------------------------------------------------

def test_put_call_parity() -> None:
    for T_label, T in MATURITIES.items():
        df = math.exp(-R * T)
        for K in STRIKES:
            theo = df * (F - K)

            c = b76_call(F, K, T, R, SIGMA_LOG)
            p = b76_put(F, K, T, R, SIGMA_LOG)
            diff = abs((c - p) - theo)
            record(
                f"PCP B76  T={T_label} K={K:.0f}", diff < TOL_PARITY,
                f"C-P={c - p:.8f} theo={theo:.8f} diff={diff:.2e}",
            )

            c2 = bach_call(F, K, T, R, SIGMA_NORM)
            p2 = bach_put(F, K, T, R, SIGMA_NORM)
            diff2 = abs((c2 - p2) - theo)
            record(
                f"PCP Bach T={T_label} K={K:.0f}", diff2 < TOL_PARITY,
                f"C-P={c2 - p2:.8f} theo={theo:.8f} diff={diff2:.2e}",
            )


# ---------------------------------------------------------------------------
# [6] Implied-vol round trip
# ---------------------------------------------------------------------------

def test_iv_round_trip() -> None:
    for T_label, T in MATURITIES.items():
        for K in STRIKES:
            # Black-76
            price_b76 = b76_call(F, K, T, R, SIGMA_LOG)
            try:
                iv = b76_implied_vol(price_b76, F, K, T, R, "call")
                diff = abs(iv - SIGMA_LOG)
                record(
                    f"IV B76  round-trip T={T_label} K={K:.0f}",
                    diff < TOL_IV_B76,
                    f"iv={iv:.8f} vs {SIGMA_LOG} diff={diff:.2e}",
                )
            except Exception as exc:
                record(
                    f"IV B76  round-trip T={T_label} K={K:.0f}", False,
                    f"solver error: {exc}",
                )

            # Bachelier
            price_bach = bach_call(F, K, T, R, SIGMA_NORM)
            try:
                iv_n = bach_implied_vol(price_bach, F, K, T, R, "call")
                diff_n = abs(iv_n - SIGMA_NORM)
                record(
                    f"IV Bach round-trip T={T_label} K={K:.0f}",
                    diff_n < TOL_IV_BACH,
                    f"iv_n={iv_n:.6f} vs {SIGMA_NORM} diff={diff_n:.2e}",
                )
            except Exception as exc:
                record(
                    f"IV Bach round-trip T={T_label} K={K:.0f}", False,
                    f"solver error: {exc}",
                )


# ---------------------------------------------------------------------------
# [7] Expiry dates Jan-Dec 2026
# ---------------------------------------------------------------------------

def test_expiries_2026() -> None:
    for month in range(1, 13):
        exp = ttf_expiry_date(month, 2026)
        is_business_day = exp.weekday() < 5
        before_delivery = exp < date(2026, month, 1)
        ok = is_business_day and before_delivery
        record(
            f"Expiry 2026-{month:02d}  ({exp.isoformat()}, {exp.strftime('%a')})",
            ok,
            f"business_day={is_business_day} before_delivery={before_delivery}",
        )


# ---------------------------------------------------------------------------
# [8] Structures — 10 multi-leg structures at F = 30
# ---------------------------------------------------------------------------

STRUCT_T = 3 / 12    # 3-month expiry for structures tests


def _validate_structure(tag: str, res) -> None:
    """Shared sanity checks for any StructureResult."""
    # Price: sum of leg net prices must match .price
    leg_sum = sum(l.net_price for l in res.legs)
    record(
        f"[{tag}] price == sum(legs)",
        math.isfinite(res.price) and abs(leg_sum - res.price) < 1e-10,
        f"price={res.price:+.6f}  sum_legs={leg_sum:+.6f}",
    )
    # Greeks all finite
    finite = all(
        math.isfinite(x) for x in (res.delta, res.gamma, res.vega, res.theta)
    )
    record(
        f"[{tag}] greeks finite",
        finite,
        f"delta={res.delta:+.4f} gamma={res.gamma:+.6f} "
        f"vega={res.vega:+.4f} theta={res.theta:+.4f}",
    )
    # P&L grid has the default 200 points and is ordered by F_T
    grid = res.pnl_at_expiry
    ordered = all(grid[i + 1][0] > grid[i][0] for i in range(len(grid) - 1))
    record(
        f"[{tag}] pnl grid shape+order",
        len(grid) == 200 and ordered,
        f"n={len(grid)} ordered={ordered}",
    )


def test_structures() -> None:
    cases = [
        ("Straddle",
         lambda: straddle(F, K=30.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Strangle",
         lambda: strangle(F, K_put=28.0, K_call=32.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Bull Call Spread",
         lambda: bull_call_spread(F, K_lo=29.0, K_hi=32.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Bear Put Spread",
         lambda: bear_put_spread(F, K_lo=28.0, K_hi=31.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Butterfly",
         lambda: butterfly(F, K_lo=27.0, K_mid=30.0, K_hi=33.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Condor",
         lambda: condor(F, K1=26.0, K2=29.0, K3=31.0, K4=34.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Collar",
         lambda: collar(F, K_put=28.0, K_call=32.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Risk Reversal",
         lambda: risk_reversal(F, K_put=28.0, K_call=32.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Calendar Spread",
         lambda: calendar_spread(F, K=30.0, T_far=0.5, T_near=STRUCT_T, r=R, sigma=SIGMA_LOG)),
        ("Ratio Spread 1x2",
         lambda: ratio_spread(F, K_lo=30.0, K_hi=33.0, T=STRUCT_T, r=R, sigma=SIGMA_LOG, ratio=2)),
    ]
    for tag, build in cases:
        try:
            res = build()
        except Exception as exc:
            record(f"[{tag}] build",    False, f"exception: {exc}")
            record(f"[{tag}] price == sum(legs)", False, "skipped (build failed)")
            record(f"[{tag}] greeks finite",       False, "skipped (build failed)")
            record(f"[{tag}] pnl grid shape+order", False, "skipped (build failed)")
            continue
        record(f"[{tag}] build", True, f"price={res.price:+.4f} EUR/MWh")
        _validate_structure(tag, res)


# ---------------------------------------------------------------------------
# [9] TTF / Henry Hub spread — ttf_hh_spread.py
# ---------------------------------------------------------------------------

SP_F_TTF_EUR = 30.0
SP_F_HH      = 3.0
SP_FX        = 1.08
SP_SIGMA_TTF = 0.50
SP_SIGMA_HH  = 0.40
SP_RHO       = 0.60
SP_T         = 0.50
SP_R_USD     = 0.04


def test_spread_pricing() -> None:
    try:
        res = spread_price(
            F_ttf_eur=SP_F_TTF_EUR, F_hh=SP_F_HH, fx_eurusd=SP_FX,
            T=SP_T, r_usd=SP_R_USD,
            sigma_ttf=SP_SIGMA_TTF, sigma_hh=SP_SIGMA_HH, rho=SP_RHO,
            option_type="call",
        )
    except Exception as exc:
        record("Spread pricing (call)", False, f"exception: {exc}")
        return

    record(
        "Spread price finite+positive",
        math.isfinite(res.price) and res.price > 0
        and math.isfinite(res.price_eur) and res.price_eur > 0,
        f"USD/MMBtu={res.price:.4f}  EUR/MWh={res.price_eur:.4f}",
    )

    # sigma_spread matches the analytic formula
    expected_sig = _spread_vol(SP_SIGMA_TTF, SP_SIGMA_HH, SP_RHO)
    record(
        "Spread sigma_spread formula",
        abs(res.sigma_spread - expected_sig) < 1e-12,
        f"got={res.sigma_spread:.8f} vs {expected_sig:.8f}",
    )

    g = res.greeks
    all_finite = all(math.isfinite(x) for x in (
        g.delta_ttf, g.delta_hh, g.gamma_ttf,
        g.vega_ttf, g.vega_hh, g.vega_rho, g.theta,
    ))
    record(
        "Spread greeks finite", all_finite,
        f"d_ttf={g.delta_ttf:+.4f} d_hh={g.delta_hh:+.4f} "
        f"vega_rho={g.vega_rho:+.4f}",
    )


def test_spread_parity() -> None:
    """Margrabe put-call parity in USD/MMBtu:  C - P = exp(-rT)*(F_ttf - F_hh)."""
    F_ttf_usd = ttf_eur_to_usd(SP_F_TTF_EUR, SP_FX)
    c = margrabe_price(F_ttf_usd, SP_F_HH, SP_T, SP_R_USD,
                       SP_SIGMA_TTF, SP_SIGMA_HH, SP_RHO, "call")
    p = margrabe_price(F_ttf_usd, SP_F_HH, SP_T, SP_R_USD,
                       SP_SIGMA_TTF, SP_SIGMA_HH, SP_RHO, "put")
    theo = math.exp(-SP_R_USD * SP_T) * (F_ttf_usd - SP_F_HH)
    diff = abs((c - p) - theo)
    record(
        "Spread put-call parity", diff < TOL_PARITY,
        f"C-P={c - p:.8f} theo={theo:.8f} diff={diff:.2e}",
    )


def test_spread_implied_correlation() -> None:
    """Price with known rho, solve implied_correlation, recover rho."""
    F_ttf_usd = ttf_eur_to_usd(SP_F_TTF_EUR, SP_FX)
    price = margrabe_price(F_ttf_usd, SP_F_HH, SP_T, SP_R_USD,
                           SP_SIGMA_TTF, SP_SIGMA_HH, SP_RHO, "call")
    try:
        rho_imp = implied_correlation(
            market_price=price,
            F_ttf=F_ttf_usd, F_hh=SP_F_HH,
            T=SP_T, r=SP_R_USD,
            sigma_ttf=SP_SIGMA_TTF, sigma_hh=SP_SIGMA_HH,
            option_type="call",
        )
        diff = abs(rho_imp - SP_RHO)
        record(
            "Spread implied correlation round-trip",
            diff < 1e-6,
            f"rho_imp={rho_imp:.8f} vs {SP_RHO} diff={diff:.2e}",
        )
    except Exception as exc:
        record("Spread implied correlation round-trip", False, f"solver error: {exc}")


# ---------------------------------------------------------------------------
# [10] Edge cases — extreme vol, deep ITM / OTM, 1-day maturity
# ---------------------------------------------------------------------------

def _edge_parity(label: str, K: float, T: float, sigma_log: float, sigma_norm: float) -> None:
    df   = math.exp(-R * T)
    theo = df * (F - K)

    try:
        c = b76_call(F, K, T, R, sigma_log)
        p = b76_put(F, K, T, R, sigma_log)
        finite = math.isfinite(c) and math.isfinite(p)
        record(
            f"Edge B76 finite+>=0 [{label}]",
            finite and c >= 0.0 and p >= 0.0,
            f"call={c:.6f} put={p:.6f}",
        )
        diff = abs((c - p) - theo)
        record(
            f"Edge B76 PCP [{label}]", diff < 1e-6,
            f"C-P={c - p:.6f} theo={theo:.6f} diff={diff:.2e}",
        )
    except Exception as exc:
        record(f"Edge B76 [{label}]", False, f"exception: {exc}")

    try:
        c2 = bach_call(F, K, T, R, sigma_norm)
        p2 = bach_put(F, K, T, R, sigma_norm)
        finite = math.isfinite(c2) and math.isfinite(p2)
        record(
            f"Edge Bach finite+>=0 [{label}]",
            finite and c2 >= 0.0 and p2 >= 0.0,
            f"call={c2:.6f} put={p2:.6f}",
        )
        diff2 = abs((c2 - p2) - theo)
        record(
            f"Edge Bach PCP [{label}]", diff2 < 1e-6,
            f"C-P={c2 - p2:.6f} theo={theo:.6f} diff={diff2:.2e}",
        )
    except Exception as exc:
        record(f"Edge Bach [{label}]", False, f"exception: {exc}")


def test_edge_cases() -> None:
    T_std = 3 / 12
    T_day = 1 / 365

    # Extreme vols — ATM strike, 3M
    _edge_parity("vol 1% ATM 3M",  K=30.0, T=T_std, sigma_log=0.01, sigma_norm=0.30)
    _edge_parity("vol 200% ATM 3M", K=30.0, T=T_std, sigma_log=2.00, sigma_norm=60.0)

    # Deep ITM / OTM — standard vol, 3M
    _edge_parity("deep ITM call K=5",   K=5.0,   T=T_std, sigma_log=SIGMA_LOG, sigma_norm=SIGMA_NORM)
    _edge_parity("deep OTM call K=100", K=100.0, T=T_std, sigma_log=SIGMA_LOG, sigma_norm=SIGMA_NORM)

    # 1-day maturity at ATM
    _edge_parity("maturity 1 day ATM", K=30.0, T=T_day, sigma_log=SIGMA_LOG, sigma_norm=SIGMA_NORM)

    # Greeks must still be finite at the extremes (ATM 3M, vol 1% and 200%)
    for label, sigma_log in (("vol 1% ATM 3M", 0.01), ("vol 200% ATM 3M", 2.00)):
        gs = (
            b76_delta(F, 30.0, T_std, R, sigma_log, "call"),
            b76_gamma(F, 30.0, T_std, R, sigma_log),
            b76_vega (F, 30.0, T_std, R, sigma_log),
            b76_vanna(F, 30.0, T_std, R, sigma_log),
            b76_volga(F, 30.0, T_std, R, sigma_log),
        )
        record(
            f"Edge B76 greeks finite [{label}]",
            all(math.isfinite(x) for x in gs),
            f"delta={gs[0]:+.4f} gamma={gs[1]:+.6f} vega={gs[2]:+.4f} "
            f"vanna={gs[3]:+.6f} volga={gs[4]:+.6f}",
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    bar = "=" * 72
    print(bar)
    print("  test_suite.py — black76_ttf.py")
    print(f"  F={F}  strikes={STRIKES}")
    print(f"  sigma_log={SIGMA_LOG}  sigma_norm={SIGMA_NORM}")
    print(f"  maturities={list(MATURITIES)}  r={R}")
    print(bar)

    sections = [
        ("[1] Black-76 prices",        test_b76_prices),
        ("[2] Bachelier prices",       test_bach_prices),
        ("[3] Black-76 Greeks",        test_b76_greeks),
        ("[4] Bachelier Greeks",       test_bach_greeks),
        ("[5] Put-Call Parity",        test_put_call_parity),
        ("[6] Implied Vol round-trip", test_iv_round_trip),
        ("[7] Expiry dates 2026",      test_expiries_2026),
        ("[8] Structures (10)",        test_structures),
        ("[9] TTF/HH spread: pricing", test_spread_pricing),
        ("[9] TTF/HH spread: parity",  test_spread_parity),
        ("[9] TTF/HH spread: implied correlation", test_spread_implied_correlation),
        ("[10] Edge cases",            test_edge_cases),
    ]
    for label, fn in sections:
        print(f"\n{label}")
        fn()

    total  = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok)
    failed = total - passed

    print("\n" + bar)
    print(f"  TOTAL: {total}   PASSED: {passed}   FAILED: {failed}")
    overall = "PASSED" if failed == 0 else "FAILED"
    print(f"  Overall: {overall}")
    print(bar)

    if failed:
        print("\nFailed tests:")
        for name, ok, msg in _results:
            if not ok:
                print(f"  - {name}: {msg}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
