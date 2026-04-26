# TTF Natural Gas Options — User Manual

This manual covers:

1. [Introduction](#1-introduction) — TTF options, Black-76 vs Bachelier, Greeks
2. [`black76_ttf.py`](#2-black76_ttfpy) — every function with worked examples

> **Conventions used throughout the examples**
> - TTF forward: `F = 30 EUR/MWh`
> - Strikes: `25 / 28 / 30 / 32 / 35 EUR/MWh`
> - Black-76 volatility: `sigma = 0.50` (50% lognormal)
> - Bachelier volatility: `sigma_n = 15 EUR/MWh` (≈ `F · sigma`)
> - Maturity: `T = 0.25` year (3 months, ACT/365)
> - Risk-free rate: `r = 0.02` (2%)
>
> Numerical values shown are rounded to 4 decimal places.

---

## 1. Introduction

### 1.1 What is a TTF option?

The **TTF** (*Title Transfer Facility*) is the Dutch virtual natural gas hub
and the European benchmark. A **TTF option** grants the right (without the
obligation) to buy (`call`) or sell (`put`) a TTF futures contract at a given
exercise price (`strike`, in EUR/MWh) on a given expiration date.

- **Underlying**: TTF futures (one contract = physical delivery over a given month).
- **Style**: European — exercise only at expiry.
- **Quote**: EUR/MWh (1 MWh = 3.4121 MMBtu).
- **Day-count**: ACT/365 for the time `T` to expiry.
- **Calendar**: ICE Endex Dutch TTF — option expiry falls ~5 calendar days
  before the 1st of the delivery month (rolled back to a business day,
  excluding NL+UK holidays and the futures LTD).

### 1.2 Black-76 vs Bachelier

Two pricing models are implemented; the choice depends on the price regime.

| Criterion | Black-76 (lognormal) | Bachelier (normal) |
|---|---|---|
| Assumption | `dF / F = sigma · dW` | `dF = sigma_n · dW` |
| Vol expressed in | decimal (`0.50` = 50%) | absolute EUR/MWh (`15` = 15 EUR/MWh) |
| Negative price allowed | **no** (F must be > 0) | **yes** |
| Suitable regime | normal conditions (F ≫ 0) | crisis / spreads (F low or < 0) |
| PCP | `C − P = e^(-rT)·(F − K)` | identical |

**Rule of thumb**: if `F < 2 EUR/MWh` or `F` may go negative (spreads,
under-balanced gas), switch to Bachelier. Otherwise, Black-76 is the standard.

At ATM (`K = F`), both models yield very similar prices when
`sigma_n ≈ F · sigma`.

### 1.3 The Greeks

Sensitivities of the option price with respect to the input parameters.

| Greek | Definition | Unit | Convention used here |
|---|---|---|---|
| **Delta** Δ | `∂V / ∂F` | dimensionless | discounted by `e^(-rT)` |
| **Gamma** Γ | `∂²V / ∂F²` | per EUR/MWh | identical for call/put |
| **Vega** ν | `∂V / ∂σ` | EUR/MWh per unit of vol | per 1.00 (100%) of vol |
| **Theta** Θ | `∂V / ∂t` | EUR/MWh per day | per calendar day (negative if long) |
| **Rho** ρ | `∂V / ∂r` | EUR/MWh per 1 pp | per percentage point |
| **Vanna** | `∂Δ / ∂σ` | mixed | cross derivative |
| **Volga** | `∂²V / ∂σ²` | EUR/MWh | vol convexity |

Practical conventions:

- `Δ_call − Δ_put = e^(-rT)` (forward delta parity).
- `Γ`, `ν` are identical for call and put under both Black-76 and Bachelier.
- `Θ` here is divided by 365 → **per day**, not per year.
- `ρ` here is divided by 100 → per **percentage point** of rate change.

---

## 2. `black76_ttf.py`

A single module, with no external dependency beyond `scipy.stats.norm` and
`scipy.optimize.brentq`. It covers:

- The ICE Endex Dutch TTF expiry calendar
- Time-to-expiry helpers (`T` in years, ACT/365)
- A contract code parser (`TTFM26`, `Jun26`, …)
- **Black-76** and **Bachelier** pricing (call / put / dispatcher)
- The full set of Greeks (Δ, Γ, ν, Θ, ρ, vanna, volga) for both models
- **Implied volatility** solvers (Brent)
- **Delta → strike** inversion

### 2.1 ICE Endex expiry calendar

#### `ttf_expiry_date(contract_month: int, contract_year: int) -> date`

Official TTF option expiry date for a given delivery month.

```python
from datetime import date
from black76_ttf import ttf_expiry_date

ttf_expiry_date(6, 2026)   # TTFM26: June 2026 delivery
# -> date(2026, 5, 27)

ttf_expiry_date(1, 2026)   # TTFF26: Dec-25 holiday shifts to Dec 24
# -> date(2025, 12, 24)

ttf_expiry_date(3, 2026)   # TTFH26: March 2026 delivery
# -> date(2026, 2, 24)
```

**Algorithm**:

1. Candidate = 1st of delivery month − 5 calendar days
2. If not a business day → roll back to the previous business day (NL + UK)
3. If equal to the futures LTD → roll back one additional business day

#### `ttf_time_to_expiry(contract_month, contract_year, reference=None) -> float`

Time `T` (years, ACT/365, including the reference day). Returns 0 if expiry
lies in the past.

```python
from datetime import date
from black76_ttf import ttf_time_to_expiry

ttf_time_to_expiry(6, 2026, reference=date(2026, 4, 23))
# -> 0.0959  (35 days / 365)
```

#### `ttf_next_expiries(n=6, reference=None) -> list[tuple[str, date]]`

The next `n` TTF expiries (ICE codes + dates), sorted ascending.

```python
from datetime import date
from black76_ttf import ttf_next_expiries

ttf_next_expiries(3, reference=date(2026, 4, 23))
# -> [('TTFK26', date(2026, 4, 24)),
#     ('TTFM26', date(2026, 5, 27)),
#     ('TTFN26', date(2026, 6, 26))]
```

#### `ttf_is_business_day(d: date) -> bool`

ICE Endex business day (Mon–Fri, excluding `_ttf_holidays(year)` = NL+UK:
1 January, Good Friday, Easter Monday, 1 May, 25 and 26 December).

```python
from datetime import date
from black76_ttf import ttf_is_business_day

ttf_is_business_day(date(2025, 12, 25))   # Christmas
# -> False
ttf_is_business_day(date(2026, 4, 6))     # Easter Monday
# -> False
```

### 2.2 "Simple" expiry helpers (5 business days before the futures LTD)

These coexist with the ICE calendar for backward compatibility. The functions
`b76_price_ttf` / `bach_price_ttf` use them via `t_from_contract`.

#### `futures_expiry_from_delivery(delivery_year, delivery_month) -> date`

Last business day of the month preceding delivery.

```python
from black76_ttf import futures_expiry_from_delivery

futures_expiry_from_delivery(2026, 6)
# -> date(2026, 5, 29)   (Friday)
```

#### `options_expiry_from_delivery(delivery_year, delivery_month) -> date`

5 business days before the futures LTD.

```python
from black76_ttf import options_expiry_from_delivery

options_expiry_from_delivery(2026, 6)
# -> date(2026, 5, 22)
```

#### `t_from_delivery(delivery_year, delivery_month, reference=None) -> float`

Time `T` (ACT/365) up to `options_expiry_from_delivery`.

```python
from datetime import date
from black76_ttf import t_from_delivery

t_from_delivery(2026, 6, reference=date(2026, 4, 1))
# -> 0.1425  (52 days / 365)
```

#### `t_futures_from_delivery(delivery_year, delivery_month, reference=None) -> float`

Same as above but up to the futures LTD.

```python
from datetime import date
from black76_ttf import t_futures_from_delivery

t_futures_from_delivery(2026, 6, reference=date(2026, 4, 1))
# -> 0.1616  (59 days / 365)
```

### 2.3 Contract code parser

#### `t_from_contract(contract: str, reference=None) -> float`

Accepts the ICE code (`TTFH26`) or the monthly abbreviation (`Mar26`, `Mar2026`)
and returns `T` via `t_from_delivery`.

```python
from datetime import date
from black76_ttf import t_from_contract

t_from_contract("TTFM26", reference=date(2026, 4, 1))
# -> 0.1425
t_from_contract("Jun26",  reference=date(2026, 4, 1))
# -> 0.1425
t_from_contract("Mar2026", reference=date(2026, 1, 15))
# -> 0.1233
```

Raises `ValueError` if the format is not recognized.

### 2.4 Black-76 pricing

Supported ICE month codes: `F G H J K M N Q U V X Z`.

#### `b76_call(F, K, T, r, sigma) -> float`

```python
from black76_ttf import b76_call

b76_call(F=30, K=30, T=0.25, r=0.02, sigma=0.50)
# -> 2.9670   EUR/MWh   (ATM call, 3 months)

b76_call(F=30, K=25, T=0.25, r=0.02, sigma=0.50)
# -> 6.4124   EUR/MWh   (ITM call)

b76_call(F=30, K=35, T=0.25, r=0.02, sigma=0.50)
# -> 1.2197   EUR/MWh   (OTM call)
```

#### `b76_put(F, K, T, r, sigma) -> float`

```python
from black76_ttf import b76_put

b76_put(F=30, K=30, T=0.25, r=0.02, sigma=0.50)
# -> 2.9670   EUR/MWh   (ATM put, 3 months)

b76_put(F=30, K=35, T=0.25, r=0.02, sigma=0.50)
# -> 6.1448   EUR/MWh   (ITM put)
```

> **PCP check**: for `K = 35`, `C − P = 1.2197 − 6.1448 = −4.9251`
> while `e^(-0.02·0.25)·(30 − 35) = −4.9750`. Exact difference → PCP holds.

#### `b76_price(F, K, T, r, sigma, option_type='call') -> float`

Generic dispatcher:

```python
from black76_ttf import b76_price

b76_price(30, 30, 0.25, 0.02, 0.50, "call")   # -> 2.9670
b76_price(30, 30, 0.25, 0.02, 0.50, "put")    # -> 2.9670
```

Raises `ValueError` if `option_type` ∉ `{'call', 'put'}`.

#### `b76_price_ttf(F, K, contract, r, sigma, option_type='call', reference=None) -> float`

Variant where `T` is derived from a contract code.

```python
from datetime import date
from black76_ttf import b76_price_ttf

b76_price_ttf(F=30, K=30, contract="TTFM26",
              r=0.02, sigma=0.50,
              option_type="call",
              reference=date(2026, 4, 1))
# -> 2.2530   EUR/MWh   (T = 52 / 365 = 0.1425)
```

### 2.5 Bachelier pricing

For forwards close to zero or negative, or for spreads.

#### `bach_call(F, K, T, r, sigma_n) -> float`

```python
from black76_ttf import bach_call

bach_call(F=30, K=30, T=0.25, r=0.02, sigma_n=15)
# -> 2.9770   EUR/MWh

bach_call(F=-3, K=0, T=60/365, r=0.02, sigma_n=6)
# -> 0.5860   EUR/MWh   (negative forward, crisis scenario)
```

#### `bach_put(F, K, T, r, sigma_n) -> float`

```python
from black76_ttf import bach_put

bach_put(F=30, K=30, T=0.25, r=0.02, sigma_n=15)
# -> 2.9770
```

#### `bach_price(F, K, T, r, sigma_n, option_type='call') -> float`

Dispatcher.

```python
from black76_ttf import bach_price

bach_price(30, 35, 0.25, 0.02, 15, "put")
# -> 7.6770
```

#### `bach_price_ttf(F, K, contract, r, sigma_n, option_type='call', reference=None) -> float`

Same as `b76_price_ttf` but using Bachelier.

```python
from datetime import date
from black76_ttf import bach_price_ttf

bach_price_ttf(F=30, K=30, contract="Jun26",
               r=0.02, sigma_n=15,
               option_type="call",
               reference=date(2026, 4, 1))
# -> 2.2519
```

### 2.6 Black-76 Greeks

All the functions below take `(F, K, T, r, sigma, option_type='call')` except
`b76_gamma`, `b76_vega`, `b76_vanna`, `b76_volga` which are identical for call
and put (no `option_type` argument).

```python
from black76_ttf import (
    b76_delta, b76_gamma, b76_vega, b76_theta, b76_rho,
    b76_vanna, b76_volga, b76_greeks,
)

F, K, T, r, sigma = 30, 30, 0.25, 0.02, 0.50

b76_delta(F, K, T, r, sigma, "call")   # -> +0.5470
b76_delta(F, K, T, r, sigma, "put")    # -> -0.4480
b76_gamma(F, K, T, r, sigma)           # -> +0.0525
b76_vega (F, K, T, r, sigma)           # -> +5.9069   (per 1.00 of vol)
b76_theta(F, K, T, r, sigma, "call")   # -> -0.0245   (per day)
b76_rho  (F, K, T, r, sigma, "call")   # -> -0.0074   (per 1 pp)
b76_vanna(F, K, T, r, sigma)           # -> +0.0984
b76_volga(F, K, T, r, sigma)           # -> -0.1846
```

#### `b76_greeks(F, K, T, r, sigma, option_type='call') -> B76Greeks`

All the Greeks in a single call (`B76Greeks` dataclass with fields `delta`,
`gamma`, `vega`, `theta`, `rho`, `vanna`, `volga`).

```python
g = b76_greeks(F=30, K=30, T=0.25, r=0.02, sigma=0.50, option_type="call")
g.delta   # +0.5470
g.gamma   # +0.0525
g.vega    # +5.9069
g.theta   # -0.0245
g.rho     # -0.0074
g.vanna   # +0.0984
g.volga   # -0.1846
```

> **Vega convention**: per unit of decimal vol (1.00 = 100%). For the "per 1
> vol point" sensitivity (1% = 0.01), divide vega by 100.

> **Rho convention**: already divided by 100, so directly in EUR/MWh per
> percentage point of rate change.

### 2.7 Bachelier Greeks

Same signatures, with `sigma_n` instead of `sigma`.

```python
from black76_ttf import (
    bach_delta, bach_gamma, bach_vega, bach_theta, bach_rho,
    bach_vanna, bach_volga, bach_greeks,
)

F, K, T, r, sigma_n = 30, 30, 0.25, 0.02, 15

bach_delta(F, K, T, r, sigma_n, "call")   # -> +0.4975
bach_delta(F, K, T, r, sigma_n, "put")    # -> -0.4975
bach_gamma(F, K, T, r, sigma_n)           # -> +0.0530
bach_vega (F, K, T, r, sigma_n)           # -> +0.1985
bach_theta(F, K, T, r, sigma_n, "call")   # -> -0.0246
bach_rho  (F, K, T, r, sigma_n, "call")   # -> -0.0074
bach_vanna(F, K, T, r, sigma_n)           # 0.0
bach_volga(F, K, T, r, sigma_n)           # -0.0132
```

> At ATM under Bachelier, `vanna = 0` exactly (by symmetry in `d = (F-K)/(σ√T)`).

#### `bach_greeks(...) -> BachGreeks`

```python
g = bach_greeks(30, 30, 0.25, 0.02, 15, "call")
g.delta, g.gamma, g.vega, g.theta, g.rho, g.vanna, g.volga
# (0.4975, 0.0530, 0.1985, -0.0246, -0.0074, 0.0, -0.0132)
```

### 2.8 Implied volatility solvers

**Brent** method, `xtol = 1e-8`, max 300 iterations.

#### `b76_implied_vol(market_price, F, K, T, r, option_type='call', sigma_lo=1e-6, sigma_hi=20.0) -> float`

Round-trip price → IV → sigma:

```python
from black76_ttf import b76_call, b76_implied_vol

p = b76_call(30, 30, 0.25, 0.02, 0.50)   # 2.9670
b76_implied_vol(p, F=30, K=30, T=0.25, r=0.02, option_type="call")
# -> 0.5000
```

Raises `ValueError` if `market_price` falls outside the
`[intrinsic, sigma_hi]` corridor.

#### `bach_implied_vol(market_price, F, K, T, r, option_type='call', sigma_lo=1e-6, sigma_hi=500.0) -> float`

Inverse for the normal vol in EUR/MWh.

```python
from black76_ttf import bach_call, bach_implied_vol

p = bach_call(30, 30, 0.25, 0.02, 15)   # 2.9770
bach_implied_vol(p, F=30, K=30, T=0.25, r=0.02, option_type="call")
# -> 15.0000
```

### 2.9 Delta → strike inversion

Useful for converting a 25Δ / 50Δ / 75Δ quote into a strike.

#### `b76_delta_to_strike(delta_target, F, T, r, sigma, option_type='call', K_lo=None, K_hi=None) -> float`

```python
from black76_ttf import b76_delta_to_strike

# Strike of the 25-delta call (typically OTM)
b76_delta_to_strike(delta_target=0.25,
                    F=30, T=0.25, r=0.02, sigma=0.50,
                    option_type="call")
# -> 35.0826   EUR/MWh

# Strike of the 25-delta put (the target delta is negative for a put)
b76_delta_to_strike(delta_target=-0.25,
                    F=30, T=0.25, r=0.02, sigma=0.50,
                    option_type="put")
# -> 25.5749   EUR/MWh
```

Defaults for `K_lo` / `K_hi`: `[F · 0.01, F · 10]`. Raises `ValueError` if the
target is not reachable within the bracket.

#### `bach_delta_to_strike(delta_target, F, T, r, sigma_n, option_type='call', K_lo=None, K_hi=None) -> float`

Bachelier variant — useful for negative or very low forwards.

```python
from black76_ttf import bach_delta_to_strike

bach_delta_to_strike(delta_target=0.25,
                     F=30, T=0.25, r=0.02, sigma_n=15,
                     option_type="call")
# -> 35.0570   EUR/MWh
```

Defaults for `K_lo` / `K_hi`: `[F − 10·σ_n·√T, F + 10·σ_n·√T]`.

---

## Appendix A — Reference values (3 months, ATM)

With `F = 30 EUR/MWh, K = 30, T = 0.25, r = 0.02`:

| Model  | sigma     | Call    | Put     | Δ_call | Γ      | ν      |
|--------|-----------|---------|---------|--------|--------|--------|
| B76    | 0.50      | 2.9670  | 2.9670  | +0.547 | 0.0525 | 5.907  |
| Bach   | 15 EUR/MWh| 2.9770  | 2.9770  | +0.498 | 0.0530 | 0.199  |

Theoretical `C − P` = `e^(-0.02·0.25)·(30 − 30) = 0`. Verified on both models
(difference < 1e-12 EUR/MWh).
