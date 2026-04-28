# Audit: `ttf_hh_spread.py` (main branch)

**Source**: `ttf_hh_spread.py` @ `origin/main` (commit `81a91b1`, 2026-04-21)
**Audit date**: 2026-04-28
**Method**: static reading + numerical verification (Python 3.11, scipy)

---

## 1. Function inventory

11 module-level functions and 2 dataclasses.

### Unit conversion

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 1 | `ttf_eur_to_usd(F_ttf_eur, fx_eurusd)`     | 52 | EUR/MWh → USD/MMBtu |
| 2 | `ttf_usd_to_eur(F_ttf_usd, fx_eurusd)`     | 57 | USD/MMBtu → EUR/MWh |
| 3 | `spread_usd_to_eur(spread_usd, fx_eurusd)` | 62 | Premium USD/MMBtu → EUR/MWh |

### Margrabe core

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 4 | `_spread_vol(σ1, σ2, ρ)`     | 109 | √(σ₁² + σ₂² − 2ρσ₁σ₂) |
| 5 | `_d1d2(F1, F2, T, σ_s)`      | 115 | (d1, d2) for Margrabe |
| 6 | `margrabe_price(...)`         | 121 | Exchange option premium (USD/MMBtu) |
| 7 | `margrabe_greeks(...)`        | 165 | All first-order Greeks (returns `SpreadGreeks`) |

### Top-level pricer

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 8 | `spread_price(F_ttf_eur, F_hh, fx, T, r_usd, σ_ttf, σ_hh, ρ, option_type, reference)` | 232 | TTF in EUR/MWh; T may be a `TTFM26`-style code |

### Solver / sensitivity / display

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 9  | `implied_correlation(market_price, F_ttf, F_hh, T, r, σ_ttf, σ_hh, option_type, ρ_lo, ρ_hi)` | 295 | Brent on ρ ∈ (−1, 1) |
| 10 | `rho_sensitivity(...)`     | 352 | Price vs ρ table |
| 11 | `vol_sensitivity(...)`     | 367 | ±5 vol / ±0.10 ρ stresses |
| 12 | `print_summary(res)`       | 390 | Formatted text dump |

### Dataclasses

`SpreadGreeks` (71): `delta_ttf, delta_hh, gamma_ttf, vega_ttf, vega_hh, vega_rho, theta`.
`SpreadResult`  (83): full pricing result + greeks.

---

## 2. Audit results

| # | Check | Result |
|---|---|---|
| 1 | List all functions | **PASS** (see §1) |
| 2 | EUR/MWh → USD/MMBtu (1 MWh = 3.412 MMBtu) | **PASS** |
| 3 | Margrabe model implementation | **PASS** |
| 4 | Greeks: Δ TTF, Δ HH, Vega TTF, Vega HH, Vega correlation | **PASS** |
| 5 | Implied correlation solver | **PASS** |
| 6 | Test with TTF = 30 EUR/MWh, HH = 3 USD/MMBtu, ρ = 0.6 | **PASS** |

---

### Check 2 — Unit conversion — **PASS**

```
MWH_TO_MMBTU = 3.412142   # exact conversion factor
F_ttf_usd = F_ttf_eur * fx_eurusd / MWH_TO_MMBTU
```

- The code uses **3.412142**; the audit prompt states **3.412**. The constant
  is the more precise value (NIST: 1 MWh = 3.412141633128… MMBtu). The
  3-digit value differs from the code by 1.4 × 10⁻⁴ (≈ 4 ppm), within
  rounding tolerance — the implementation is consistent with the standard
  energy-equivalence factor.
- Numerical checks (FX = 1.08):
  - `ttf_eur_to_usd(30, 1.08)` → **9.495502 USD/MMBtu**, matches manual
    `30·1.08/3.412142` to machine zero.
  - Round-trip `30 → ttf_eur_to_usd → ttf_usd_to_eur → 30` accurate to
    3.6 × 10⁻¹⁵.
  - `spread_usd_to_eur(1.0, 1.08)` → 3.159391 EUR/MWh = 1·3.412142/1.08 ✓

### Check 3 — Margrabe model — **PASS**

Implemented form (lines 149–162):
```
σ_s   = √(σ_TTF² + σ_HH² − 2ρ·σ_TTF·σ_HH)
d1    = [ln(F_ttf/F_hh) + ½σ_s²T] / (σ_s √T)
d2    = d1 − σ_s √T
Call  = e^{−rT}·[F_ttf · N(d1) − F_hh · N(d2)]
Put   = e^{−rT}·[F_hh · N(−d2) − F_ttf · N(−d1)]
```

This is the standard Black-76-style adaptation of Margrabe (1978) for
forwards, with USD discounting on both legs (both forwards quoted
USD/MMBtu after the EUR→USD conversion).

Numerical checks (TTF = 30 EUR/MWh, HH = 3 USD/MMBtu, FX = 1.08, σ_TTF = 0.60,
σ_HH = 0.50, ρ = 0.60, T = 180/365, r = 0.045):

| Quantity | Code | Independent Python | Δ |
|---|---|---|---|
| σ_spread | 0.50000000 | 0.50000000 | 0 |
| d1 | 3.457046 | 3.457046 | — |
| d2 | 3.105922 | 3.105922 | — |
| Call price | 6.35318943 | 6.35318943 | 0 |
| Put price  | 0.00024686 | 0.00024686 | 0 |
| C − P − e^{−rT}(F_TTF − F_HH) | — | — | −8.9e-16 |

Edge limits also correct:
- `ρ → +1`: σ_spread → 0.10, call → 6.353 ≈ `e^{−rT}·max(F_ttf−F_hh, 0)` (intrinsic).
- `ρ → −1`: σ_spread → 1.10, call → 6.467 (intrinsic + larger time value).

### Check 4 — Greeks — **PASS**

Analytic forms (lines 191–210):

```
Δ_TTF (call) = e^{−rT}·N(d1)
Δ_HH  (call) = −e^{−rT}·N(d2)
Γ_TTF        = e^{−rT}·φ(d1) / (F_TTF · σ_s · √T)
common       = e^{−rT}·F_TTF·φ(d1)·√T
Vega_TTF     = common · (σ_TTF − ρ·σ_HH) / σ_s
Vega_HH      = common · (σ_HH  − ρ·σ_TTF) / σ_s
Vega_ρ       = common · (−σ_TTF·σ_HH / σ_s)
```

Vega derivation is correct via chain rule on `σ_s² = σ_TTF² + σ_HH² −
2ρσ_TTFσ_HH`, giving
`∂σ_s/∂σ_TTF = (σ_TTF − ρσ_HH)/σ_s`,
`∂σ_s/∂σ_HH  = (σ_HH  − ρσ_TTF)/σ_s`,
`∂σ_s/∂ρ     = −σ_TTFσ_HH/σ_s`,
each multiplied by `∂C/∂σ_s = e^{−rT}·F_TTF·φ(d1)·√T`.

Verified against central-difference at the user's test case
(TTF = 30 EUR/MWh, HH = 3 USD/MMBtu, ρ = 0.6):

| Greek | Analytic | FD | Δ |
|---|---|---|---|
| Δ TTF | +0.977786 | +0.977786 | +5.7e-13 |
| Δ HH  | −0.977125 | −0.977125 | −5.2e-12 |
| Γ TTF | +0.000297 | +0.000297 | +1.6e-09 |
| Vega TTF | +0.003965 | +0.003965 | −3.4e-11 |
| Vega HH  | +0.001850 | +0.001850 | −1.3e-11 |
| Vega ρ   | −0.003965 | −0.003965 | −5.5e-11 |

Sign sanity:
- `Δ_TTF ∈ (0, e^{−rT}]` ✓ (0.978 ≤ df = 0.978)
- `Δ_HH  ∈ [−e^{−rT}, 0)` ✓
- `Vega_ρ < 0` for the call ✓ (higher ρ → lower spread vol → cheaper option)

Theta is computed by 1-day finite difference (line 213–215). At the deep-ITM
regime above, theta comes out **slightly positive** (+0.000774/day): for a
deeply ITM forward call with positive r, the increase in `e^{−rT}` as T → 0
can outweigh the loss of time-value, so the docstring's "negative for long
positions" remark is a typical-case statement, not a strict invariant.
This is correct behaviour, not a bug.

### Check 5 — Implied correlation — **PASS**

Brent's method on `ρ ∈ (rho_lo, rho_hi)` with `rho_lo = −0.9999`,
`rho_hi = +0.9999` (line 295). Bound checks rely on the Margrabe call/put
price being **monotonically decreasing in ρ** (because `σ_s` is decreasing
in ρ and vega_σ_s is positive); the same monotonicity holds for the put by
put-call parity (`∂P/∂ρ = ∂C/∂ρ`).

Numerical round-trip:

| Test | Generated price | Recovered ρ | Δ |
|---|---|---|---|
| ATM (F = 3.50, ρ_true = 0.30) | 0.623362 | 0.3000000000 | 5.7e-13 |
| Deep-ITM user case (ρ_true = 0.60) | 6.353189 | 0.6000000000 | 1.7e-12 |

The deep-ITM case is well-behaved despite being close to intrinsic
because the small time-value still depends monotonically on σ_s.

### Check 6 — User test: TTF = 30 EUR/MWh, HH = 3 USD/MMBtu, ρ = 0.6 — **PASS**

Full output of `spread_price(30.0, 3.0, fx_eurusd=1.08, T=180/365, r_usd=0.045,
sigma_ttf=0.60, sigma_hh=0.50, rho=0.60, "call")`:

| Quantity | Value |
|---|---|
| F_TTF_usd | 9.495502 USD/MMBtu (= 30·1.08/3.412142) |
| σ_spread | 0.500000 (= √(0.36 + 0.25 − 2·0.6·0.30)) |
| Call price (USD/MMBtu) | 6.353189 |
| Call price (EUR/MWh)   | 20.072208 |
| Δ TTF / Δ HH           | +0.9778 / −0.9771 |
| Vega TTF / Vega HH / Vega ρ | +0.0040 / +0.0019 / −0.0040 |

Observations:
- The call is **deep in-the-money** (forward spread = 6.495 USD/MMBtu vs
  σ_s √T ≈ 0.35), so price ≈ intrinsic = e^{−rT}·6.4955 = 6.353. The Δ_TTF
  ≈ Δ_HH ≈ ±df reflects this.
- The EUR/MWh premium check: `6.353189 × 3.412142 / 1.08 = 20.072208` ✓
- Put-call parity: `C − P = 6.353189 − 0.000247 = 6.352942 = e^{−rT}·(9.4955 − 3.0)` ✓

To exercise vol/correlation Greeks in a less-degenerate regime, the same
audit runs an ATM-equivalent (`F_TTF = F_HH = 3.50`, ρ = 0.30) — that test
recovers the seeded price and ρ to better than 1e-12.

---

## 3. Notes (out-of-scope)

- The conversion constant 3.412142 has 7 significant figures; if greater
  precision is desired the IUPAC value 3.4121416331… could be used, but
  this is well below typical price/FX uncertainty.
- `print_summary` uses non-ASCII characters (Δ, σ, ρ, ²); it depends on a
  UTF-8 console.
- `theta` is sign-noted in the docstring as "negative for long positions",
  but mathematically it can be positive for deep-ITM forwards under positive
  r (intrinsic discount-factor effect). Not a bug.
- For T as a contract code (e.g. `"TTFM26"`), the import of
  `t_from_contract` is local-scoped inside `spread_price` (line 263). This
  defers the dependency on `black76_ttf` until needed; numeric T paths
  do not require `black76_ttf` to be importable.
