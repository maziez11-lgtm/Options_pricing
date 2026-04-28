# Final Audit Report — Options_pricing

**Compiled**: 2026-04-28
**Scope**: Consolidation of all per-module audits performed on `origin/main`.
**Sources**:
- `audit_inventory.md` (repository-wide file inventory)
- `audit_black76.md` (`black76_ttf.py`)
- `audit_market_data.md` (`ttf_market_data.py`)
- `audit_spread.md` (`ttf_hh_spread.py`)
- `audit_structures.md` (`structures_ttf.py`)

> **Missing input**: the requested `audit_docs.md` is not present in any
> branch of the repository (verified via `git log --all`). No documentation
> audit was produced upstream, so this report cannot summarise one.

---

## 1. Summary of PASS / FAIL across all audits

### 1.1 `audit_inventory.md` — Repository inventory

This is a structural listing (23 branches, per-file commit dates). It carries
no PASS/FAIL checks of its own. Used here only to confirm the perimeter of the
audited code: `main` tip is `df73cc6` (2026-04-28), 59 tracked files.

### 1.2 `audit_black76.md` — `black76_ttf.py`

| # | Check | Result |
|---|---|---|
| 1 | List all functions (44 functions, 2 dataclasses) | **PASS** |
| 2 | No duplicate / conflicting expiry-date functions | **PASS** |
| 3 | Only valid expiry definition is the ICE TFO one | **PASS** |
| 4 | `ttf_time_to_expiry` uses calendar days / 365 | **PASS** |
| 5 | Put-call parity holds numerically (≤ 4e-15) | **PASS** |
| 6 | Greeks mathematically consistent | **FAIL** (theta sign error, both Black-76 and Bachelier) |

### 1.3 `audit_market_data.md` — `ttf_market_data.py`

| # | Check | Result |
|---|---|---|
| 1 | List all functions (26 functions, 7 dataclasses, 4 classes) | **PASS** |
| 2 | Imports of `ttf_expiry_date` / `ttf_time_to_expiry` from `black76_ttf` | **PASS** |
| 3a | Vol surface interpolation by strike | **PASS** |
| 3b | Vol surface interpolation by delta | **PASS** |
| 4 | `update_vol_surface` linkage to forward curve | **PASS** |
| 5 | ATM-DN strike formula `K = F·exp(−σ²T/2)` | **PASS** (with labelling caveat) |

### 1.4 `audit_spread.md` — `ttf_hh_spread.py`

| # | Check | Result |
|---|---|---|
| 1 | List all functions (12 functions, 2 dataclasses) | **PASS** |
| 2 | EUR/MWh ↔ USD/MMBtu conversion (factor 3.412142) | **PASS** |
| 3 | Margrabe model implementation | **PASS** |
| 4 | Greeks: Δ TTF, Δ HH, Vega TTF, Vega HH, Vega ρ | **PASS** |
| 5 | Implied-correlation Brent solver | **PASS** |
| 6 | Test case TTF=30, HH=3, ρ=0.6 | **PASS** |

### 1.5 `audit_structures.md` — `structures_ttf.py`

| # | Check | Result |
|---|---|---|
| 1 | List all 10 structures | **PASS** |
| 2 | Net Greeks consistent (sum-of-legs + FD price bump) | **PASS** (Δ, Γ, Vega) — Θ inherits black76 sign error |
| 3 | Breakeven points correct (analytical + grid) | **PASS** |
| 4 | Test each structure at F=30, σ=0.5, T=1 | **PASS** |

### 1.6 Aggregate scoreboard

| Module | Checks | PASS | FAIL |
|---|---:|---:|---:|
| `black76_ttf.py` | 6 | 5 | 1 |
| `ttf_market_data.py` | 6 | 6 | 0 |
| `ttf_hh_spread.py` | 6 | 6 | 0 |
| `structures_ttf.py` | 4 | 4 | 0 (Θ flagged as inherited defect) |
| **Total** | **22** | **21** | **1** |

---

## 2. Bugs found

### B1 — Theta sign error in `b76_theta` (`black76_ttf.py`, lines 426–433) — **HIGH**

The rate term is computed as `−r·price` for both call and put, whereas the
correct Black-76 theta carries `+r·price`. The defect produces a per-day
error of exactly `2·r·price / 365`.

Numerical evidence (F = K = 35, T = 90/365, r = 0.03, σ = 0.50):
- Analytic Θ/day = −0.019253
- Finite-difference Θ/day = −0.018689
- Discrepancy = 5.6 × 10⁻⁴/day (matches `2·0.03·3.432/365`).

All other 7 Greek classes (Delta, Gamma, Vega, Rho, Vanna, Volga) match the
finite-difference reference to ≤ 1 × 10⁻⁸.

### B2 — Same sign error in `bach_theta` (`black76_ttf.py`, line 531) — **HIGH**

Mirrors B1: `rate_term = -r * price`. Bachelier Θ/day analytic = −0.008869
vs FD = −0.008610 (error ≈ 2.6 × 10⁻⁴/day). All other Bachelier Greeks pass
to ≤ 1 × 10⁻⁷.

### B3 — Theta defect propagates to every structure in `structures_ttf.py` — **HIGH (inherited)**

Each of the 10 structures sums per-leg Black-76 thetas. Aggregation is
correct, but each leg carries the B1 error, so every reported net theta is
biased by `2·r·net_premium / 365`. Most affected: pure-time structures (e.g.
calendar spread). Self-fixing once B1 is fixed.

### B4 — `NameError` in `black76_ttf.py` `__main__` demo (line 772) — **LOW**

The demo block calls `_ttf_prev_bd(delivery - timedelta(days=5))`, but the
function defined in the module is `_prev_uk_bd`. Running
`python black76_ttf.py` directly raises `NameError`. Library import paths
are unaffected.

---

## 3. Code quality / design observations (not strict bugs)

These were flagged as "out-of-scope" by the per-module audits but are listed
here for completeness; none cause incorrect numerical output today.

### O1 — `TTFExpiryCalendar.futures_expiry_date` duplicates `_ttf_futures_ltd`
(`ttf_market_data.py`, lines 99–104). Both implementations agree because
they share the same `ttf_is_business_day` predicate, but the duplication
invites future drift. Recommend re-exporting `black76_ttf._ttf_futures_ltd`.

### O2 — Dead code: `TTFExpiryCalendar._last_business_day`
(`ttf_market_data.py`, line 154) is never called.

### O3 — Unused module-level constants
`_DELTA_PILLARS` (line 65) and `_STANDARD_TENORS` (line 68) in
`ttf_market_data.py` are unreferenced.

### O4 — Two parallel vol-surface representations in `ttf_market_data.py`
The class-based `VolatilitySurface` (line 286) and the dict-based vol
surface used by `get_vol_by_strike` / `get_vol_by_delta` do not interoperate.
A consumer using one cannot feed the other without rebuilding.

### O5 — "ATM-DN" labelling caveat (`ttf_market_data.py`, line 974)
The implemented strike `K = F·exp(−σ²T/2)` is the **lognormal-median**
strike (`d2 = 0`), not the FX/BS delta-neutral-straddle strike (`d1 = 0`).
The author already documents this in `update_vol_surface`'s docstring and
keeps `display_vol_surface` pivoted on the input pillar. Numerics are
correct under the formula stated in the audit prompt.

### O6 — `condor` `max_profit` formula assumes symmetric strikes
(`structures_ttf.py`). Declared as `(K2 − K1) − debit`; for asymmetric
condors the true plateau is `min(K2 − K1, K4 − K3) − debit`. Symmetric test
cases pass exactly.

### O7 — `print_summary` non-ASCII glyphs (`ttf_hh_spread.py`)
Uses Δ, σ, ρ, ²; requires a UTF-8 console.

### O8 — Documentation audit not performed
No `audit_docs.md` exists in any branch. The user manual / README cannot be
declared PASS or FAIL until that audit is produced.

---

## 4. List of fixes needed

### Required (correctness)

| ID | File | Lines | Fix |
|---|---|---|---|
| F1 | `black76_ttf.py` | 426–433 (`b76_theta`) | Change `rate_term = -r * df * (...)` → `rate_term = +r * df * (...)` (i.e. `+r·C` for calls, `+r·P` for puts). Equivalently, `rate_term = +r * price`. |
| F2 | `black76_ttf.py` | 531 (`bach_theta`) | Change `rate_term = -r * price` → `rate_term = +r * price`. |
| F3 | tests | — | Update any test that pins the buggy theta values. The numerical FD theta of the price function is the authoritative reference. |
| F4 | `black76_ttf.py` | 772 (`__main__` demo) | Replace `_ttf_prev_bd` with `_prev_uk_bd` (the actual function name in the module). |

### Recommended (hygiene, behaviour-preserving)

| ID | File | Fix |
|---|---|---|
| F5 | `ttf_market_data.py` | Have `TTFExpiryCalendar.futures_expiry_date` delegate to `black76_ttf._ttf_futures_ltd` instead of re-implementing it (kills O1). |
| F6 | `ttf_market_data.py` | Remove unused `_last_business_day`, `_DELTA_PILLARS`, `_STANDARD_TENORS` (O2, O3). |
| F7 | `ttf_market_data.py` | Either unify the two vol-surface representations or document that they are intentionally separate (O4). |
| F8 | `ttf_market_data.py` | Rename or re-document the "ATM" pillar so the lognormal-median nature of `K = F·exp(−σ²T/2)` is unambiguous (O5). |
| F9 | `structures_ttf.py` | Generalise `condor.max_profit` to `min(K2−K1, K4−K3) − debit` (O6). |
| F10 | — | Produce the missing `audit_docs.md` so the documentation set (`README.md`, `user_manual.md`, `user_manual.html`, `user_manual.pdf`, `file_structure.md`) is covered (O8). |

---

## 5. Overall project status

**Status: AMBER — production-blocking bug in theta only.**

- **Numerical core (pricing, parity, IV, Greeks ex-theta, Margrabe, structures aggregation):** all PASS at machine precision. The Black-76, Bachelier and Margrabe pricers, the implied-vol and implied-correlation solvers, the ICE TFO calendar, the calendar/365 time-to-expiry, the unit conversion (3.412142 MWh→MMBtu), the strike- and delta-based vol-surface interpolators, and all 10 multi-leg structures (premium, Δ, Γ, Vega, breakevens, max P/L) are mathematically correct.
- **Single correctness defect:** B1/B2 — theta has the wrong sign on the rate term in both `b76_theta` and `bach_theta`. Per-day error is `2·r·price / 365`. The defect is small in absolute terms but inverts the rate contribution; deep-ITM forwards and any P&L decomposition that splits decay vs. discount are visibly affected. B3 follows automatically and is fixed by fixing B1.
- **One trivial bug:** B4 (NameError) only affects the standalone `__main__` demo, not library users.
- **Hygiene findings (O1–O7):** non-blocking. They invite drift but produce correct numbers today.
- **Coverage gap:** O8 — no documentation audit was produced, so the user manual / README / file_structure markdown have not been independently verified. Recommend producing `audit_docs.md` before declaring full release readiness.

Once F1–F4 land (and the corresponding tests are refreshed), the project
clears all 22 audit checks and can move to GREEN. F5–F10 are recommended
follow-ups, not blockers.
