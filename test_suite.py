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
        ("[1] Black-76 prices",       test_b76_prices),
        ("[2] Bachelier prices",      test_bach_prices),
        ("[3] Black-76 Greeks",       test_b76_greeks),
        ("[4] Bachelier Greeks",      test_bach_greeks),
        ("[5] Put-Call Parity",       test_put_call_parity),
        ("[6] Implied Vol round-trip", test_iv_round_trip),
        ("[7] Expiry dates 2026",     test_expiries_2026),
    ]
    for label, fn in sections:
        print(f"\n{label}")
        fn()

    total  = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok)
    failed = total - passed

    print("\n" + bar)
    print(f"  TOTAL: {total}   PASS: {passed}   FAIL: {failed}")
    print(bar)

    if failed:
        print("\nFailures:")
        for name, ok, msg in _results:
            if not ok:
                print(f"  - {name}: {msg}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
