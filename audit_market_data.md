# Audit: `ttf_market_data.py` (main branch)

**Source**: `ttf_market_data.py` @ `origin/main` (commit `a1c74a1`, 2026-04-28)
**Audit date**: 2026-04-28
**Method**: static reading + numerical verification (Python 3.11, scipy/pandas)

---

## 1. Function inventory

26 module-level functions (static or top-level), 7 dataclasses, 4 classes.

### Module-level functions

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 1  | `_parse_delivery_month(label)`           | 799  | "Jun-26" → (6, 2026) |
| 2  | `load_ttf_forward_curve(source, data, filepath, reference)` | 844 | Manual / CSV forward-curve loader |
| 3  | `update_vol_surface(forward_curve, vol_surface)`             | 929 | Combine fwd curve + delta-quoted vol surface |
| 4  | `display_vol_surface(vol_surface_df)`    | 1002 | Pretty-print maturity × delta grid |
| 5  | `_interp_smile(K, strikes, vols)`        | 590  | Cubic-spline within smile, flat in wings |
| 6  | `get_vol_by_strike(F, K, T, vol_surface)`| 605  | Vol(K, T) — strike-based interp |
| 7  | `_b76_delta_to_strike(δ, F, T, σ, r)`    | 643  | Brent inversion δ → K |
| 8  | `get_vol_by_delta(F, δ, T, vol_surface, r)` | 666 | Vol(δ, T) — fixed-point on σ |
| 9  | `export_forward_curve(curve, path)`      | 705  | CSV + JSON dump |
| 10 | `export_vol_surface(surface, path)`      | 717  | CSV (long + pivot) + JSON |
| 11 | `export_sabr_params(calibration, path)`  | 734  | CSV + JSON |
| 12 | `export_all(output_dir, reference_date, risk_free_rate)` | 745 | Full pipeline |

### Classes & methods

| Class | Methods (line) |
|---|---|
| `TTFExpiryCalendar` (85)        | `futures_expiry_date`(99), `expiry_date`(106), `contract_code`(110), `time_to_expiry`(114), `active_contracts`(118), `expiry_for_tenor`(143), `_last_business_day`(154) |
| `TTFForwardCurve` (180)         | `load`(203), `forward_price`(210), `to_dataframe`(222), `_fetch_spot`(231), `_synthetic_spot`(251), `_price_contract`(255) |
| `VolatilitySurface` (286)       | `add_smile`(291), `vol`(295), `to_dataframe`(299), `_get_interp`(309) |
| `VolatilitySurfaceBuilder` (333)| `build`(367), `_build_smile`(387), `_delta_to_strike`(431) |
| `MarketCalibration` (462)       | `calibrate_all`(469), `to_dataframe`(490), `_calibrate_sabr`(501), `_sabr_vol`(525) |

### Dataclasses
`TTFContract` (76), `ForwardPoint` (170), `VolSmile` (276), `VolatilitySurface` (286), `SABRParams` (455).

---

## 2. Audit results

| # | Check | Result |
|---|---|---|
| 1 | List all functions                                         | **PASS** (see §1) |
| 2 | `load_ttf_forward_curve` imports `ttf_expiry_date` and `ttf_time_to_expiry` from `black76_ttf` correctly | **PASS** |
| 3 | Vol surface interpolation by strike works                   | **PASS** |
| 3 | Vol surface interpolation by delta works                    | **PASS** |
| 4 | `update_vol_surface` links correctly to forward curve       | **PASS** |
| 5 | ATM-DN strike formula `K = F·exp(−σ²T/2)`                   | **PASS** (with a labelling caveat — see notes) |

---

### Check 2 — Imports & usage of `black76_ttf` symbols — **PASS**

Source (lines 41–45):

```python
from black76_ttf import (
    ttf_expiry_date,
    ttf_time_to_expiry,
    ttf_is_business_day,
)
```

Verified at runtime:
```
md.ttf_expiry_date     is b76.ttf_expiry_date     → True
md.ttf_time_to_expiry  is b76.ttf_time_to_expiry  → True
```

Inside `load_ttf_forward_curve` (lines 890–891):

```python
exp = ttf_expiry_date(month, year)
T   = ttf_time_to_expiry(month, year, reference=ref)
```

Argument order matches the canonical `ttf_expiry_date(contract_month, contract_year)`
and `ttf_time_to_expiry(contract_month, contract_year, reference)` signatures
in `black76_ttf.py`. Cross-checked every row of the resulting DataFrame against
direct calls to the imported functions — **all expiry dates and T values match
exactly** (calendar/365, no local recomputation).

### Check 3 — Vol surface interpolation — **PASS**

#### By strike (`get_vol_by_strike`)

- Within a smile: cubic spline (`_interp_smile`) when ≥4 strikes, with strike
  clamped to the quoted range (no cubic extrapolation in the wings — explicitly
  documented as a guard against negative/explosive vols, line 591–595).
- Across maturities: linear interpolation in T, flat outside the quoted range
  (lines 636–640).

Numerical verification on `SAMPLE_TTF_VOL_SURFACE`:

| Test | Result |
|---|---|
| Node value (K=30, T=3M) returns stored 0.50 exactly | ✓ |
| T-midpoint at quoted strike equals arithmetic mean of neighbouring smiles | ✓ (diff = 0) |
| OTM put (K=22, T=3M) returns interpolated vol 0.6118 | ✓ |
| OTM call (K=38, T=3M) returns interpolated vol 0.5178 | ✓ |

#### By delta (`get_vol_by_delta`)

The strike that corresponds to a given delta depends on the (unknown) vol, so
the function uses a fixed-point iteration: seed σ at the ATM vol, compute K
via Brent on δ → K (`_b76_delta_to_strike`, line 643), look up vol(K, T), and
repeat to convergence (tol 1e-8, max 50 iterations).

Numerical verification (F = 30, T = 3/12):

| δ_target | Returned σ | K(δ, σ) | vol@K | Self-consistent? |
|---|---|---|---|---|
| −0.25 | 0.546760 | 25.8982 | 0.546760 | ✓ |
| −0.10 | 0.629645 | 21.0583 | 0.629645 | ✓ |
| +0.25 | 0.510661 | 36.8189 | 0.510661 | ✓ |
| +0.50 | 0.493671 | 30.9280 | 0.493671 | ✓ |
| +0.90 | 0.629645 | 21.0583 | 0.629645 | ✓ |

Symmetry sanity: δ = −0.25 (put) and δ = +0.75 (call) both land on K = 25.90
because at that K the call delta is 0.75 and the put delta is −0.25 — i.e. the
function treats the input as a *call*-delta convention, which is the
explicitly documented behaviour ("0.50 (ATM)").

`delta = 0` raises `ValueError` as expected (line 687).

### Check 4 — `update_vol_surface` ↔ forward-curve linkage — **PASS**

The function consumes the DataFrame produced by `load_ttf_forward_curve`,
indexes it by `delivery_month` (line 960), and pulls `F`, `T` and `expiry_date`
from that index for every smile row (lines 965–967). Numerical verification on
the sample data:

- 95 output rows × 19 contracts × 5 delta pillars (1 month dropped: vol
  surface had no Nov-26 mismatch — actually Nov-26 mapped) — for every output
  row, `forward_price` and `time_to_expiry` match the forward-curve row for
  that `delivery_month` to ≤ 1e-9 / 1e-6.
- Output schema includes `expiry_date` and `time_to_expiry` propagated from
  the forward curve, plus `strike`, `implied_vol`, `delta`, `moneyness`,
  `delta_pillar`.

### Check 5 — ATM-DN strike formula — **PASS** (with a caveat on labelling)

Implementation (line 974–975):

```python
if math.isclose(delta_pillar, ATM_DELTA_PILLAR):       # 0.50
    K = F * math.exp(-0.5 * sigma * sigma * T)
```

Off-ATM pillars (line 977–979):

```python
d1_target = norm.ppf(delta_pillar)
K = F * math.exp(0.5 * sigma * sigma * T - d1_target * sigma * math.sqrt(T))
```

Numerical verification across all 19 ATM rows of the sample surface:

| Quantity | Result |
|---|---|
| max \|K_code − F·exp(−σ²T/2)\| (ATM rows) | **0.00e+00** |
| max \|K_code − F·exp(0.5σ²T − Φ⁻¹(δ)·σ√T)\| (off-ATM) | **0.00e+00** |

The formula in the code matches the formula stated in the audit request
exactly, to machine precision.

#### ⚠️ Caveat — labelling vs. mathematics

`K = F·exp(−σ²T/2)` is the **lognormal median strike**: it satisfies
`d2 = 0`, i.e. it is the strike such that the risk-neutral probability
`P(F_T > K) = N(d2) = 0.5`. It is the median of the lognormal forward
distribution at expiry.

It is **not** the strike at which a Black-76 straddle is delta-neutral.
The classical FX/BS "ATM-DN" (delta-neutral straddle) strike satisfies
`d1 = 0`, giving `K = F·exp(+σ²T/2)`. At the implemented K, we have
`d1 = σ√T`, so the call forward-delta is `N(σ√T) > 0.5`, which the code's
own diagnostic confirms:

| Contract | σ | T | model_delta (code) | N(σ√T) |
|---|---|---|---|---|
| Jun-26 | 0.500 | 0.1014 | 0.5632 | 0.5632 |
| Sep-26 | 0.470 | 0.3534 | 0.6100 | 0.6100 |
| Dec-26 | 0.440 | 0.6027 | 0.6337 | 0.6337 |

The author has clearly noticed this — the docstring of `update_vol_surface`
explicitly notes "the model `delta` recomputed at the ATM-DN strike drifts
above 0.50 with maturity, so it is unsuitable for grid display" (lines
955–957), and `display_vol_surface` pivots on the input `delta_pillar`
rather than the recomputed `delta` to keep the output table on the
quoted-pillar axis.

So: the requested formula `K = F·exp(−σ²T/2)` is implemented faithfully
(**PASS**), but if "ATM-DN" is meant in the FX/BS delta-neutral-straddle
sense, the implementation actually produces the lognormal-median strike,
not the d1=0 strike. Since the audit asks specifically to verify the
formula `K = F·exp(−σ²T/2)`, the verification is positive.

---

## 3. Other observations (out-of-scope)

- `TTFExpiryCalendar.futures_expiry_date` (lines 99–104) re-implements
  futures LTD inline rather than calling the canonical `_ttf_futures_ltd`
  in `black76_ttf`. The two implementations agree because both roll back
  through the same `ttf_is_business_day` predicate, but the duplication
  invites future drift; consider re-exporting and using
  `black76_ttf._ttf_futures_ltd`.
- `TTFExpiryCalendar._last_business_day` (line 154) is dead code (never
  called).
- `_DELTA_PILLARS` (line 65) and `_STANDARD_TENORS` (line 68) are unused.
- The class-based `VolatilitySurface` (line 286) and the dict-based vol
  surface used by `get_vol_by_strike` / `get_vol_by_delta` are two parallel
  representations of the same concept; the strike/delta lookup helpers
  do not interoperate with `VolatilitySurface.vol(K, T)` and vice versa.
