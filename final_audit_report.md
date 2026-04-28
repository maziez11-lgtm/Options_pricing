# Final Audit Report — `maziez11-lgtm/Options_pricing`

**Branch audited**: `main` (commit tip `df73cc6` at audit start;
work performed against the actual files on `main`)
**Audit date**: 2026-04-28
**Underlying reports**: `audit_inventory.md`, `audit_black76.md`,
`audit_market_data.md`, `audit_spread.md`, `audit_structures.md`,
`audit_docs.md` (all on the audit branch).

---

## 1. PASS / FAIL summary

### `audit_inventory.md` — Repository inventory

| Check | Result |
|---|---|
| All branches enumerated (23 remote branches) | **PASS** |
| Every file × every branch listed with last-commit date | **PASS** |

### `audit_black76.md` — `black76_ttf.py`

| # | Check | Result |
|---|---|---|
| 1 | List all functions (44 + 2 dataclasses)                | **PASS** |
| 2 | No duplicate / conflicting expiry-date functions       | **PASS** |
| 3 | Only valid expiry definition is the ICE TFO one        | **PASS** |
| 4 | `ttf_time_to_expiry` uses calendar days / 365 only     | **PASS** |
| 5 | Put-call parity holds numerically                      | **PASS** (≤ 3.6e-15) |
| 6 | Greeks mathematically consistent                       | **FAIL** (theta sign error) |

### `audit_market_data.md` — `ttf_market_data.py`

| # | Check | Result |
|---|---|---|
| 1 | Function inventory (12 + 5 classes + 5 dataclasses)    | **PASS** |
| 2 | `load_ttf_forward_curve` uses imported `ttf_expiry_date` / `ttf_time_to_expiry` correctly | **PASS** |
| 3 | Vol-surface interpolation by strike                    | **PASS** |
| 4 | Vol-surface interpolation by delta                     | **PASS** |
| 5 | `update_vol_surface` links to forward curve            | **PASS** |
| 6 | ATM-DN strike formula `K = F · exp(−σ²T/2)`            | **PASS** (formula matches; convention caveat — see §3) |

### `audit_spread.md` — `ttf_hh_spread.py`

| # | Check | Result |
|---|---|---|
| 1 | Function inventory (12 + 2 dataclasses)                | **PASS** |
| 2 | EUR/MWh ↔ USD/MMBtu conversion (1 MWh = 3.412142 MMBtu) | **PASS** |
| 3 | Margrabe model                                         | **PASS** (PCP at 8.9e-16) |
| 4 | Greeks: Δ TTF, Δ HH, Vega TTF, Vega HH, Vega ρ         | **PASS** (≤ 1e-9 vs FD) |
| 5 | Implied-correlation solver                             | **PASS** (≤ 1.7e-12 round-trip) |
| 6 | Test at TTF = 30 EUR/MWh, HH = 3 USD/MMBtu, ρ = 0.6    | **PASS** |

### `audit_structures.md` — `structures_ttf.py`

| # | Check | Result |
|---|---|---|
| 1 | List all 10 structures                                 | **PASS** |
| 2 | Net Greeks consistent (sum-of-legs and FD-of-premium) | **PASS** (≤ 1e-12 / ≤ 1e-9) |
| 3 | Breakevens correct (analytical and grid)               | **PASS** |
| 4 | Test each structure at F = 30, σ = 0.5, T = 1          | **PASS** |

### `audit_docs.md` — Documentation

| # | Check | Result |
|---|---|---|
| 1 | `user_manual.md` complete (6 parts + glossary)         | **PASS** (glossary = Part 6) |
| 2 | `user_manual.html` matches `user_manual.md`            | **PASS** |
| 3 | `README.md` up to date with all modules                | **FAIL** (5 modules missing) |
| 4 | ICE TFO expiry definition correct everywhere           | **PASS** |
| 5 | Everything in English only                             | **PASS** for content, **1 French filename** |

### Aggregate

| Category | Total | PASS | FAIL |
|---|---:|---:|---:|
| Repository inventory             | 2   | 2   | 0 |
| `black76_ttf.py`                 | 6   | 5   | 1 |
| `ttf_market_data.py`             | 6   | 6   | 0 |
| `ttf_hh_spread.py`               | 6   | 6   | 0 |
| `structures_ttf.py`              | 4   | 4   | 0 |
| Documentation                    | 5   | 4   | 1 |
| **Total**                        | **29** | **27** | **2** |

**Pass rate**: 27 / 29 = **93 %**.

---

## 2. Bugs found

### Bug 1 (HIGH) — `b76_theta` rate-term sign error

**File / lines**: `black76_ttf.py`, lines 426–433.

The Black-76 theta is implemented as

```python
decay = -(F * df * norm.pdf(d1) * sigma) / (2.0 * math.sqrt(T))
if option_type == "call":
    rate_term = -r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))   # = -r·C
else:
    rate_term = -r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1)) # = -r·P
return (decay + rate_term) / 365.0
```

The standard Black-76 theta (Hull, Haug, Wikipedia) is

```
Θ = -F·e^{-rT}·φ(d₁)·σ / (2√T)  +  r·V          where V = C or P
```

The implemented `rate_term` has the **wrong sign**. The error is exactly
`2·r·V / 365` per day. At the standard test point
(F = K = 35, T = 90/365, r = 0.03, σ = 0.50):

| Quantity | Analytic (code) | Finite difference (truth) | Δ |
|---|---|---|---|
| Theta call (per day) | −0.019253 | −0.018689 | −5.6e-04 |
| Theta put  (per day) | −0.019253 | −0.018689 | −5.6e-04 |

Severity: every Black-76 theta returned by the library is biased.

### Bug 2 (HIGH) — `bach_theta` rate-term sign error (same defect)

**File / lines**: `black76_ttf.py`, lines 521–532.

```python
decay = -df * sigma_n * norm.pdf(d) / (2.0 * math.sqrt(T))
price = bach_price(F, K, T, r, sigma_n, option_type)
rate_term = -r * price                                  # ← wrong sign
return (decay + rate_term) / 365.0
```

Same correction needed: the rate term should be `+r * price`. Verified
numerically: analytic theta −0.008869/day vs FD reference −0.008610/day,
Δ ≈ −2.6e-04/day = `2·r·P/365`.

### Bug 3 (LOW) — NameError in `black76_ttf.py` `__main__` block

**File / lines**: `black76_ttf.py`, line 772.

```python
candidate = _ttf_prev_bd(delivery - timedelta(days=5))
```

The function defined in the file is `_prev_uk_bd`, not `_ttf_prev_bd`.
Running `python black76_ttf.py` raises `NameError`. The library imports
are unaffected — this is dead/demo code only.

### Bug 4 (HIGH-by-propagation) — `structures_ttf.py` net theta is biased

All 10 structures aggregate per-leg theta from the buggy `b76_theta`.
The aggregation itself is correct (verified at ≤ 1e-12), so
**fixing Bug 1 automatically fixes every structure**. No structure-level
code change is required.

### Documentation gap (MEDIUM) — `README.md` missing modules

`README.md` does not mention the following modules that exist on `main`:

| Missing module | What it is |
|---|---|
| `structures_ttf.py`        | 10 multi-leg structure pricer |
| `ttf_hh_spread.py`         | TTF/Henry Hub spread (Margrabe) |
| `dashboard_ttf.py`         | Top-level dashboard script |
| `dashboard_jupyter.ipynb`  | Jupyter dashboard |
| `test_suite.py`            | Test suite |

### Hygiene — French filename

`dashboard/Initialisation dossier` is the only non-English item in the
project (filename only; not content).

### Lower-priority observations (non-bugs)

- `TTFExpiryCalendar.futures_expiry_date` (`ttf_market_data.py:99–104`)
  re-implements futures-LTD inline rather than reusing
  `black76_ttf._ttf_futures_ltd`. Both produce the same result today,
  but the duplication invites drift.
- `TTFExpiryCalendar._last_business_day`, `_DELTA_PILLARS`,
  `_STANDARD_TENORS` are dead code / unused.
- `condor.max_profit` declares `(K2 − K1) − debit`; for asymmetric
  condors the plateau is `min(K2 − K1, K4 − K3) − debit`. With the
  symmetric defaults the formula is exact.
- `update_vol_surface` labels `K = F · exp(−σ²T / 2)` "ATM-DN", but
  this is the **lognormal-median strike** (`d2 = 0`), not the
  delta-neutral straddle strike (`d1 = 0`, which would be
  `F · exp(+σ²T / 2)`). The implementation matches its own
  documentation; the docstring already acknowledges that the model
  delta drifts above 0.50 with maturity.

---

## 3. Fixes needed (priority order)

### P1 — Math correctness (1-line fixes)

1. **`black76_ttf.py:430`** — Black-76 theta rate term, call branch:
   ```python
   rate_term = -r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))
   ```
   change to
   ```python
   rate_term =  r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))
   ```

2. **`black76_ttf.py:432`** — Black-76 theta rate term, put branch:
   ```python
   rate_term = -r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
   ```
   change to
   ```python
   rate_term =  r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
   ```

3. **`black76_ttf.py:531`** — Bachelier theta rate term:
   ```python
   rate_term = -r * price
   ```
   change to
   ```python
   rate_term =  r * price
   ```

4. **`black76_ttf.py:772`** (demo only) — fix the typo:
   ```python
   candidate = _ttf_prev_bd(delivery - timedelta(days=5))
   ```
   change to
   ```python
   candidate = _prev_uk_bd(delivery - timedelta(days=5))
   ```

After P1 the entire test suite (PCP, FD-of-premium for Greeks, structure
nets, finite-difference theta) is expected to pass to numerical
precision. No structure-level edits are needed; structures will inherit
the corrected theta from the primitives.

### P2 — Documentation

5. **`README.md`** — add `structures_ttf.py` and `ttf_hh_spread.py` to
   the *Features* module table; add `structures_ttf.py`,
   `ttf_hh_spread.py`, `dashboard_ttf.py`, `dashboard_jupyter.ipynb`,
   `test_suite.py` to the *Project Structure* tree. Add a Quick-Start
   one-liner for each.

6. **`user_manual.md`** — promote `structures_ttf.py` from a single
   subsection inside Part 5 to a dedicated module Part with its 10
   structures, breakevens, and Greeks. Optional: short subsections on
   `pricing/`, `ttf_time.py`, `dashboard_ttf.py`, `main.py`,
   `test_suite.py` if they are intended to be public-facing.

### P3 — Hygiene

7. Rename or remove `dashboard/Initialisation dossier` (French
   filename, no content).
8. Replace the inline futures-LTD computation in
   `TTFExpiryCalendar.futures_expiry_date` with a call to
   `black76_ttf._ttf_futures_ltd` (avoid duplication).
9. Delete dead code: `TTFExpiryCalendar._last_business_day`,
   `_DELTA_PILLARS`, `_STANDARD_TENORS` in `ttf_market_data.py`.
10. Generalise `condor.max_profit` to
    `min(K2 − K1, K4 − K3) − debit`.

---

## 4. Overall project status

The codebase is **mathematically sound and well-tested**, with one
isolated sign defect that propagates through the public API:

- **Single-leg pricing** (`black76_ttf.py`): correct Black-76 and
  Bachelier prices, correct Greeks for δ / Γ / vega / ρ / vanna /
  volga, correct put-call parity to machine precision, correct ICE
  TFO expiry calendar (verbatim implementation), correct calendar/365
  time-to-expiry. **Theta is biased** by `2·r·V / 365`/day for both
  models — the only outright bug.
- **Market data** (`ttf_market_data.py`): forward-curve loader,
  vol-surface interpolation by strike and by delta, and the surface
  ↔ forward-curve linkage all behave as documented; imports from
  `black76_ttf` are correct.
- **Spread option** (`ttf_hh_spread.py`): Margrabe pricing, Greeks,
  PCP, and implied correlation all reproduce hand-computed values to
  machine precision; unit conversions are exact.
- **Structures** (`structures_ttf.py`): all 10 structures present,
  net Greeks consistent two ways, breakevens match analytical
  formulas, max-profit / max-loss declared correctly. Theta inherits
  Bug 1.
- **Documentation**: ICE TFO rule consistent everywhere; manual
  (Markdown ↔ HTML) is complete and consistent; README needs to be
  brought up to date with five modules added since the last revision.

**Severity stack**:
- 0 critical defects.
- 3 math-correctness bugs all in the same `theta` sign convention
  (one-line each) — high priority, but localised.
- 1 demo-only NameError in `black76_ttf.py`'s `__main__`.
- 1 documentation gap in `README.md` (5 modules) and one stale French
  filename.

**Verdict**: **READY FOR PRODUCTION USE** for pricing, Greeks (other
than theta), implied vol, implied correlation, and structure pricing.
Theta consumers should hold pending the P1 fixes. Total estimated
effort to clear every P1+P2 item: **under one hour** of edits, plus
the standard test pass.
