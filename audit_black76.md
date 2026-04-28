# Audit: `black76_ttf.py` (main branch)

**Source**: `black76_ttf.py` @ `origin/main` (commit `a87f8ff`, 2026-04-28)
**Audit date**: 2026-04-28
**Method**: static reading + numerical verification (Python 3.11, scipy)

> Scope note: This audit covers `black76_ttf.py` only. The repository also
> contains `pricing/black76.py`, which was **not** evaluated.

---

## 1. Function inventory

44 module-level functions and 2 dataclasses.

### ICE TFO calendar (lines 40–204)

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 1  | `_easter_sunday(year)`               | 40  | Gauss's Easter algorithm |
| 2  | `_shift_off_weekend(d)`              | 55  | UK weekend → next weekday substitution |
| 3  | `_first_monday(year, month)`         | 64  | First Monday of a month |
| 4  | `_last_monday(year, month)`          | 69  | Last Monday of a month |
| 5  | `_uk_holidays(year)`                 | 75  | UK (E&W) public holidays for a given year |
| 6  | `ttf_is_business_day(d)`             | 104 | UK business-day predicate |
| 7  | `_prev_uk_bd(d)`                     | 114 | Roll back to nearest prior UK business day |
| 8  | `_ttf_futures_ltd(year, month)`      | 121 | TTF futures last trading day |
| 9  | `ttf_expiry_date(month, year)`       | 128 | **ICE TFO option expiry** |
| 10 | `ttf_time_to_expiry(month, year, reference)` | 161 | Calendar-day T (years) |
| 11 | `ttf_next_expiries(n, reference)`    | 179 | Next *n* upcoming expiries |

### Contract parser

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 12 | `t_from_contract(contract, reference)` | 223 | Parse `TTFH26` / `Mar26` → T |

### Internal helpers

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 13 | `_df(r, T)`              | 257 | exp(−rT) discount factor |
| 14 | `_b76_d1(F,K,T,σ)`       | 263 | Black-76 d1 |
| 15 | `_b76_d1_d2(F,K,T,σ)`    | 267 | Black-76 (d1, d2) |
| 16 | `_bach_d(F,K,T,σₙ)`      | 274 | Bachelier d |

### Pricing

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 17 | `b76_call`           | 282 | Black-76 call |
| 18 | `b76_put`            | 290 | Black-76 put |
| 19 | `b76_price`          | 298 | Dispatcher |
| 20 | `b76_price_ttf`      | 310 | Price by TTF contract name |
| 21 | `bach_price_ttf`     | 335 | Bachelier price by TTF contract name |
| 22 | `bach_call`          | 359 | Bachelier call |
| 23 | `bach_put`           | 368 | Bachelier put |
| 24 | `bach_price`         | 377 | Dispatcher |

### Greeks (Black-76)

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 25 | `b76_delta`  | 393 | ∂V/∂F |
| 26 | `b76_gamma`  | 404 | ∂²V/∂F² |
| 27 | `b76_vega`   | 412 | ∂V/∂σ |
| 28 | `b76_theta`  | 420 | ∂V/∂t per day |
| 29 | `b76_rho`    | 436 | ∂V/∂r per 1pp |
| 30 | `b76_vanna`  | 446 | ∂²V/∂F∂σ |
| 31 | `b76_volga`  | 454 | ∂²V/∂σ² |
| 32 | `b76_greeks` | 473 | Bundle, returns `B76Greeks` (dataclass @ 462) |

### Greeks (Bachelier)

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 33 | `bach_delta`  | 492 |
| 34 | `bach_gamma`  | 502 |
| 35 | `bach_vega`   | 511 |
| 36 | `bach_theta`  | 521 |
| 37 | `bach_rho`    | 535 |
| 38 | `bach_vanna`  | 544 |
| 39 | `bach_volga`  | 553 |
| 40 | `bach_greeks` | 573 | Bundle, returns `BachGreeks` (dataclass @ 562) |

### Solvers

| # | Symbol | Line | Purpose |
|---|---|---|---|
| 41 | `b76_implied_vol`     | 596 | Brent on Black-76 |
| 42 | `bach_implied_vol`    | 624 | Brent on Bachelier |
| 43 | `b76_delta_to_strike` | 656 | Brent on δ→K (Black-76) |
| 44 | `bach_delta_to_strike`| 697 | Brent on δ→K (Bachelier) |

---

## 2. Audit results

| # | Check | Result |
|---|---|---|
| 1 | List all functions                                         | **PASS** (see §1) |
| 2 | No duplicate / conflicting expiry-date functions           | **PASS** |
| 3 | Only valid expiry definition is the ICE TFO one            | **PASS** |
| 4 | `ttf_time_to_expiry` uses calendar days / 365 only         | **PASS** |
| 5 | Put-call parity holds numerically                          | **PASS** |
| 6 | Greeks mathematically consistent                           | **FAIL** (theta sign error, both models) |

---

### Check 2 — Duplicate / conflicting expiry functions — **PASS**

There is exactly **one** option-expiry function in the file: `ttf_expiry_date`
(line 128). The only other date-producing helper, `_ttf_futures_ltd` (line 121),
returns the **futures** last-trading-day and is used solely as the tiebreaker
required by the ICE TFO rule. No alternative or legacy expiry rule (e.g.
"5 business days before futures LTD") exists in the file.

### Check 3 — ICE TFO rule — **PASS**

The implementation in `ttf_expiry_date` (lines 153–158) matches the ICE TFO
specification verbatim:

```python
candidate = date(contract_year, contract_month, 1) - timedelta(days=5)   # 5 calendar days
candidate = _prev_uk_bd(candidate)                                       # nearest prior UK BD
if candidate == _ttf_futures_ltd(contract_year, contract_month):
    candidate = _prev_uk_bd(candidate - timedelta(days=1))               # futures-LTD tiebreak
```

UK-only holiday calendar (`_uk_holidays`, lines 75–101): New Year, Good
Friday, Easter Monday, Early May, Spring & Summer bank holidays,
Christmas, Boxing Day — with weekend-substitution and Christmas/Boxing
collision handling. No TARGET / Euronext / Endex calendar is mixed in.

Verified all 24 contract months in 2025–2026:
- Every expiry is a UK business day.
- No expiry collides with the futures LTD.
- Every expiry is at least 5 calendar days before the start of the delivery month
  (more when rolled back through weekends/holidays).

Sample (full table produced during audit):

| Contract | Delivery | 5-cd-back | Expiry | Futures LTD |
|---|---|---|---|---|
| 2025-01 | 2025-01-01 | 2024-12-27 | 2024-12-27 | 2024-12-31 |
| 2025-05 | 2025-05-01 | 2025-04-26 | 2025-04-25 | 2025-04-30 |
| 2025-08 | 2025-08-01 | 2025-07-27 | 2025-07-25 | 2025-07-31 |
| 2026-01 | 2026-01-01 | 2025-12-27 | 2025-12-24 | 2025-12-31 |
| 2026-05 | 2026-05-01 | 2026-04-26 | 2026-04-24 | 2026-04-30 |
| 2026-10 | 2026-10-01 | 2026-09-26 | 2026-09-25 | 2026-09-30 |

### Check 4 — `ttf_time_to_expiry` is calendar/365 — **PASS**

Body of the function (line 173):

```python
return (ttf_expiry_date(contract_month, contract_year) - ref).days / 365
```

- `(date − date).days` is a calendar-day count.
- Divisor is the literal `365` (no leap-year adjustment, no business-day count,
  no `ACT/360`, etc.).
- Numerical check: with `ref = 2026-01-01`, expiry of TTF Apr-26 is `2026-03-27`,
  giving T = 85/365 = 0.2328767123… — exact match.

### Check 5 — Put-call parity — **PASS**

Identity tested: `C − P = exp(−rT)·(F − K)` for `F = 35`, `T = 90/365`,
`r = 0.03`.

Black-76 (σ = 0.50), strikes 20, 25, 30, 35, 40, 45, 50:
max |residual| = **3.55 × 10⁻¹⁵** (machine precision).

Bachelier (σₙ = 8.0), same strikes:
max |residual| = **1.78 × 10⁻¹⁵** (machine precision).

Implied-vol round-trip also exact to ~1e-11 (Black-76) and machine zero
(Bachelier).

### Check 6 — Greeks mathematical consistency — **FAIL**

Method: analytic vs central-difference of the price function (Black-76 ATM,
F = K = 35, T = 90/365, r = 0.03, σ = 0.50).

| Greek | Analytic | Finite-diff | Δ | Verdict |
|---|---|---|---|---|
| Delta (call)  | +0.545349 | +0.545349 | −2.5e-11 | **PASS** |
| Delta (put)   | −0.447281 | −0.447281 | +1.7e-11 | **PASS** |
| Gamma         | +0.045221 | +0.045221 | +6.9e-09 | **PASS** |
| Vega          | +6.829578 | +6.829578 | −2.9e-11 | **PASS** |
| Rho (per 1pp) | −0.008463 | −0.008463 | +2.5e-12 | **PASS** |
| Vanna         | +0.097565 | +0.097565 | +1.2e-12 | **PASS** |
| Volga         | −0.210501 | −0.210501 | +5.2e-11 | **PASS** |
| **Theta/day (call)** | **−0.019253** | **−0.018689** | **−5.6e-04** | **FAIL** |
| **Theta/day (put)**  | **−0.019253** | **−0.018689** | **−5.6e-04** | **FAIL** |

Cross-check: `Δ_call − Δ_put = 0.992630 = exp(−rT)` ✓ (delta parity).

Bachelier shows the **same** theta defect: analytic −0.008869/day vs FD
−0.008610/day, Δ ≈ −2.6e-04/day. Other Bachelier Greeks pass to ≤1e-7.

#### Root cause — sign error on the rate term

Standard Black-76 theta (Hull, Haug, Wikipedia):

```
Θ_call = −F·e^{−rT}·φ(d₁)·σ / (2√T)  +  r·C
Θ_put  = −F·e^{−rT}·φ(d₁)·σ / (2√T)  +  r·P
```

The implementation (lines 426–433) computes:

```python
decay = -(F * df * norm.pdf(d1) * sigma) / (2.0 * math.sqrt(T))   # OK
if option_type == "call":
    rate_term = -r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))   # = -r·C  ← wrong sign
else:
    rate_term = -r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1)) # = -r·P  ← wrong sign
return (decay + rate_term) / 365.0
```

The discrepancy is exactly `2·r·price / 365` per day, which matches the
observed residual (2·0.03·3.432/365 ≈ 5.64e-4). The same pattern appears in
`bach_theta` (line 531: `rate_term = -r * price`).

Recommended fix: change the sign of `rate_term` in `b76_theta` and
`bach_theta`. Numerical FD theta from the price function is the reference;
any tests that pinned the buggy values should be updated.

---

## 3. Other findings (out-of-scope, but worth noting)

- **NameError in `__main__` demo, line 772**: the script's demo block calls
  `_ttf_prev_bd(delivery - timedelta(days=5))`, but the function defined in
  the file is `_prev_uk_bd`. Running `python black76_ttf.py` will raise
  `NameError`. The production library code paths are unaffected.

- The file is otherwise self-consistent: PCP, IV round-trip, delta parity,
  and 6 of 7 Greek classes match the price function to numerical precision.
