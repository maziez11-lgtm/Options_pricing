# Audit: 10 Option Structures (main branch)

**Source**: `structures_ttf.py` @ `origin/main` (commit `c898843`, 2026-04-21).
The audit prompt referenced "structures in `black76_ttf.py`" — the
structures actually live in **`structures_ttf.py`**; `black76_ttf.py`
contains only single-leg pricing primitives. `structures_ttf.py` imports
`b76_price`, `b76_delta`, `b76_gamma`, `b76_vega`, `b76_theta`,
`t_from_contract` from `black76_ttf` (lines 33–36).

**Audit date**: 2026-04-28
**Method**: static reading + numerical verification at the requested
test point F = 30, σ = 0.50, T = 1, r = 0.03, all 10 structures.

---

## 1. Structure inventory

All 10 structures (matching the docstring at lines 12–24) are exposed as
top-level functions and return a `StructureResult` dataclass containing net
premium, net Greeks (Δ, Γ, Vega, Θ/day), the (F_T, P&L) grid, breakevens,
max-profit and max-loss.

| # | Name | Function | Line | Legs |
|---|---|---|---|---|
| 1  | Straddle           | `straddle(F, K, T, r, σ)`                                | 173 | +1 call(K), +1 put(K) |
| 2  | Strangle           | `strangle(F, K_put, K_call, T, r, σ)`                    | 199 | +1 put(K_put), +1 call(K_call) |
| 3  | Bull Call Spread   | `bull_call_spread(F, K_lo, K_hi, T, r, σ)`               | 231 | +1 call(K_lo), −1 call(K_hi) |
| 4  | Bear Put Spread    | `bear_put_spread(F, K_lo, K_hi, T, r, σ)`                | 266 | +1 put(K_hi), −1 put(K_lo) |
| 5  | Butterfly          | `butterfly(F, K_lo, K_mid, K_hi, T, r, σ)`               | 301 | +1 call(K_lo), −2 call(K_mid), +1 call(K_hi) |
| 6  | Condor             | `condor(F, K1, K2, K3, K4, T, r, σ)`                     | 337 | +1, −1, −1, +1 calls @ K1..K4 |
| 7  | Collar             | `collar(F, K_put, K_call, T, r, σ)`                      | 373 | +1 put(K_put), −1 call(K_call) |
| 8  | Risk Reversal      | `risk_reversal(F, K_put, K_call, T, r, σ)`               | 409 | +1 call(K_call), −1 put(K_put) |
| 9  | Calendar Spread    | `calendar_spread(F, K, T_far, T_near, r, σ)`             | 442 | +1 call(K, T_far), −1 call(K, T_near) |
| 10 | Ratio Spread       | `ratio_spread(F, K_lo, K_hi, T, r, σ, ratio=2)`          | 485 | +1 call(K_lo), −N call(K_hi) |

Supporting machinery: `Leg` dataclass (line 43) with `sign × qty × unit_X`
properties for net price/Greeks; `_make_leg` (94), `_payoff` (108),
`_price_grid` (112, ±3σ√T window or ≥45 % of F), `_expiry_pnl` (120),
`_breakevens` (133, linear interp on sign changes), `_build` (146).

---

## 2. Audit results

| # | Check | Result |
|---|---|---|
| 1 | List all 10 structures | **PASS** (see §1) |
| 2 | Net Greeks consistent for each structure | **PASS** |
| 3 | Breakeven points correct | **PASS** |
| 4 | Test each structure at F = 30, σ = 0.50, T = 1 | **PASS** |

### Test-point summary (F = 30, σ = 0.50, T = 1, r = 0.03)

Strikes chosen to span a representative range around F = 30:

```
straddle          K = 30
strangle          K_put = 27,  K_call = 33
bull_call_spread  K_lo = 29,   K_hi = 33
bear_put_spread   K_lo = 27,   K_hi = 31
butterfly         K_lo = 26,   K_mid = 30,  K_hi = 34
condor            K1 = 25, K2 = 28, K3 = 32, K4 = 35
collar            K_put = 27,  K_call = 33
risk_reversal     K_put = 27,  K_call = 33
calendar_spread   K = 30, T_far = 1.5, T_near = 1.0
ratio_spread      K_lo = 30, K_hi = 33, ratio = 2
```

| Structure | Premium | Δ | Γ | Vega | Θ/day | Breakevens |
|---|---:|---:|---:|---:|---:|---|
| Straddle           | +11.4947 | +0.1916 | +0.050032 | +22.514 | −0.0164 | 18.505, 41.495 |
| Strangle           |  +8.8084 | +0.1952 | +0.048976 | +22.039 | −0.0158 | 18.192, 41.808 |
| Bull Call Spread   |  +1.4635 | +0.0980 | −0.001226 |  −0.552 | +0.0003 | 30.463 |
| Bear Put Spread    |  +2.2182 | −0.1013 | +0.002164 |  +0.974 | −0.0008 | 28.782 |
| Butterfly          |  +0.4001 | +0.0064 | −0.001868 |  −0.840 | +0.0005 | 26.400, 33.600 |
| Condor             |  +0.5249 | +0.0080 | −0.002427 |  −1.092 | +0.0007 | 25.525, 34.475 |
| Collar             |  −0.5635 | −0.8212 | −0.002553 |  −1.149 | +0.0008 | 33.563 |
| Risk Reversal      |  +0.5635 | +0.8212 | +0.002553 |  +1.149 | −0.0008 | 33.563 |
| Calendar Spread    |  +1.1512 | +0.0120 | −0.005207 |  +2.114 | +0.0015 | 22.871, 40.610 |
| Ratio Spread (1×2) |  −3.6246 | −0.4354 | −0.026513 | −11.931 | +0.0085 | 39.625 |

Sign sanity:
- Long-vol structures (1, 2, 9): Vega > 0, Γ > 0 (1, 2) ✓
- Short-vol structures (5, 6): Vega < 0, Γ < 0 ✓
- Calendar (long far / short near): net Vega > 0 ✓
- Risk reversal vs collar: equal and opposite (greeks negate exactly) ✓
- Bull call spread bullish (Δ > 0), bear put spread bearish (Δ < 0) ✓

### Check 2 — Net-Greek consistency — **PASS**

Two independent verifications for each structure:

**(a) Sum-of-legs invariant.** For every structure,
`net_X == Σ_legs (sign × qty × unit_X)` for X ∈ {price, Δ, Γ, Vega, Θ}.
All 10 structures pass to ≤ 1e-12. This is by construction in `_build`,
but the test confirms the data flow.

**(b) Net Greek vs. central difference of total premium.** The structure
function is recomputed at bumped F or σ; `(price(+h) − price(−h))/(2h)`
must equal the reported analytic net Δ / Vega.

| Structure | Δ analytic | Δ FD | Δ err | Vega analytic | Vega FD | Vega err |
|---|---:|---:|---:|---:|---:|---:|
| Straddle           | +0.191578 | +0.191578 | 4.1e-10 | +22.5144 | +22.5144 | −3.2e-10 |
| Strangle           | +0.195230 | +0.195230 | 4.1e-10 | +22.0391 | +22.0391 | +2.7e-10 |
| Bull Call Spread   | +0.098022 | +0.098022 | 6.3e-11 |  −0.5515 |  −0.5515 | −1.5e-10 |
| Bear Put Spread    | −0.101259 | −0.101259 | −5.3e-11 |  +0.9737 |  +0.9737 | −1.8e-10 |
| Butterfly          | +0.006354 | +0.006354 | −9.9e-12 |  −0.8405 |  −0.8405 | +1.0e-09 |
| Condor             | +0.008005 | +0.008005 | −2.0e-11 |  −1.0922 |  −1.0922 | +4.3e-10 |
| Collar             | −0.821166 | −0.821166 | 8.9e-11 |  −1.1491 |  −1.1491 | −4.4e-13 |
| Risk Reversal      | +0.821166 | +0.821166 | −8.9e-11 |  +1.1491 |  +1.1491 | +4.4e-13 |
| Calendar Spread    | +0.011963 | +0.011963 | −4.0e-11 |  +2.1142 |  +2.1142 | +1.6e-10 |
| Ratio Spread       | −0.435385 | −0.435385 | −1.1e-10 | −11.9310 | −11.9310 | −4.3e-10 |

> Caveat on Θ. Theta is summed correctly across legs, but the per-leg
> theta inherits the sign-error in `b76_theta` documented in
> `audit_black76.md`. Net theta values shown above are therefore
> internally consistent (delta-error ≈ 2·r·premium / 365) but slightly
> off the true ∂P/∂t for any structure with non-zero net premium. Pure
> calendar-only structures (calendar spread at ATM with equal σ) are
> the most affected because theta is the dominant Greek there.

### Check 3 — Breakeven points — **PASS**

Two cross-checks for each structure:

**(a) P&L at the reported BE prices.** Linearly interpolating the
P&L grid (200 points, ±3σ√T window) at each breakeven returns ≈ 0:

| Structure | P&L at BE (interp) |
|---|---|
| Straddle           | +1.0e-5 / +1.0e-5 |
| Strangle           | −5.0e-5 / −5.0e-5 |
| Bull Call Spread   | −0.0e+0 |
| Bear Put Spread    | −0.0e+0 |
| Butterfly          | +3.0e-5 / +3.0e-5 |
| Condor             | +5.0e-5 / +5.0e-5 |
| Collar             | +4.0e-5 |
| Risk Reversal      | −4.0e-5 |
| Calendar Spread    | +1.0e-5 / −1.0e-5 |
| Ratio Spread       | +4.0e-5 |

Residuals are at the level of the grid resolution
(`(hi-lo)/199 ≈ 0.13` × the local slope of P&L), confirming the linear
interpolation in `_breakevens` is correct.

**(b) Analytical formulas (single source of truth).**

| Structure | Formula | Code result |
|---|---|---|
| Straddle           | `K ± premium`           = 30 ± 11.4947     | 18.5053, 41.4947 ✓ |
| Strangle           | `K_put − P`, `K_call + P` = 18.1916, 41.8084 | 18.1916, 41.8084 ✓ |
| Bull Call Spread   | `K_lo + debit` = 29 + 1.4635 = 30.4635       | 30.4635 ✓ |
| Bear Put Spread    | `K_hi − debit` = 31 − 2.2182 = 28.7818       | 28.7818 ✓ |
| Butterfly          | `K_lo + debit`, `K_hi − debit` = 26.4001, 33.5999 | 26.4001, 33.5999 ✓ |
| Condor             | `K1 + debit`, `K4 − debit` = 25.5249, 34.4751 | 25.5249, 34.4751 ✓ |
| Collar / RR        | Crosses zero at `K_call ± credit` = 33.5635 | 33.5635 ✓ |

Calendar spread has no closed-form BE (it depends on residual time-value
of the far option), so it is checked only by the grid intercept.

### Check 4 — Per-structure test at F = 30, σ = 0.5, T = 1 — **PASS**

All 10 structures executed without error. Every structure:
- returns finite, plausible premium and net Greeks,
- produces breakevens that lie on the P&L curve (zero crossings),
- declares max-profit / max-loss matching the analytical formula in the
  bounded cases.

Bounded structures have declared `max_profit` exactly matching the
formula `(width − debit)`:

| Structure | Width | Debit | (Width − Debit) | Declared max_profit |
|---|---:|---:|---:|---:|
| Bull Call Spread | 4.0  | 1.4635 | 2.5365 | 2.5365 |
| Bear Put Spread  | 4.0  | 2.2182 | 1.7818 | 1.7818 |
| Butterfly        | 4.0  | 0.4001 | 3.5999 | 3.5999 |
| Condor           | 3.0  | 0.5249 | 2.4751 | 2.4751 |

For butterfly and ratio_spread, the *grid scan* peaks slightly below
`max_profit` because the 200-point grid does not land exactly on the
optimal F_T (= K_mid for butterfly, = K_hi for ratio); the analytical
declaration is still correct.

Unbounded structures correctly declare `±math.inf`:
- Straddle, Strangle, Risk Reversal: `max_profit = inf`
- Risk Reversal, Collar, Ratio Spread (ratio>1): `max_loss = -inf`

---

## 3. Other observations (out-of-scope)

- **Naming**: the audit prompt placed the structures in `black76_ttf.py`;
  they actually live in `structures_ttf.py`. The pricing primitives are
  imported from `black76_ttf`.
- **Theta inheritance**: `b76_theta` has a sign error on the rate term
  (see `audit_black76.md`). All 10 structures report theta consistent
  with the per-leg theta they import, so the aggregation is correct, but
  theta values are biased by `2·r·premium / 365` per day. Fixing the
  underlying primitive automatically fixes every structure.
- **`_price_grid`**: the ±3σ√T window can be narrow at high σ × T (here
  ±45 EUR/MWh around F = 30), wide enough to bracket all observed BEs
  in this audit; for very long-dated or high-vol cases the floor of
  0.45 × F prevents the grid collapsing.
- **`condor` `max_profit`**: declared as `(K2 − K1) − debit`. This is
  correct only when K2 − K1 ≤ K4 − K3; for asymmetric condors the
  payoff plateau is `min(K2 − K1, K4 − K3)`. With the symmetric test
  inputs (3-wide on both sides) the formula is exact.
- **Calendar spread P&L assumption**: P&L is evaluated at the near
  expiry assuming the far option retains its time value at the same σ.
  The same-σ assumption ignores any vol term-structure or smile re-mark;
  this is documented (lines 451–454).
