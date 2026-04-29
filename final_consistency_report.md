# Final Consistency Report

**Date:** 2026-04-29
**Branch audited:** `claude/consistency-audit-expiry-UeIET` (= `main` + recent
expiry / market-data / dashboard work)
**Scope:** `black76_ttf.py`, `ttf_market_data.py`, `ttf_hh_spread.py`,
`structures_ttf.py`, `dashboard_jupyter.ipynb`, `dashboard_ttf.py`,
`test_suite.py`, `ttf_time.py`, `main.py`, `generate_charts.py`.

> Note: per the active development branch policy, this report is committed
> on `claude/consistency-audit-expiry-UeIET`. Merging this branch into `main`
> will land the file there.

---

## STEP 1 — Expiry dates cleanup

### 1.1 Inventory of expiry-related symbols in `black76_ttf.py`

Public API (intended to be the only public surface):

| Function | Line | Status |
|---|---|---|
| `ttf_futures_expiry_date(delivery_month, delivery_year)` | 126 | KEEP |
| `ttf_expiry_date(contract_month, contract_year)` | 153 | KEEP |
| `ttf_time_to_expiry(contract_month, contract_year, reference=None)` | 186 | KEEP |
| `ttf_is_business_day(d)` | 109 | KEEP |
| `ttf_next_expiries(n=6, reference=None)` | 204 | KEEP |

Private helpers (implementation detail of the calendar):

| Function | Line | Role |
|---|---|---|
| `_easter_sunday(year)` | 45 | Easter date for UK holiday set |
| `_shift_off_weekend(d)` | 60 | UK weekend → next-weekday substitution |
| `_first_monday(year, month)` | 69 | Used for early May bank holiday |
| `_last_monday(year, month)` | 74 | Used for spring/summer bank holidays |
| `_uk_holidays(year)` | 80 | UK bank holiday calendar |
| `_prev_uk_bd(d)` | 119 | Roll back to previous UK business day |

No legacy expiry helpers (`futures_expiry_from_delivery`,
`options_expiry_from_delivery`, `t_from_delivery`, `t_futures_from_delivery`,
`_ttf_futures_ltd`, `_ttf_holidays`, `_ttf_prev_bd`, `t_from_contract`)
remain in `black76_ttf.py`.

**Result: PASS** — exactly the five public functions requested are present;
private helpers are kept and prefixed with `_`.

> Caveat: a separate file `ttf_time.py` still defines the legacy expiry
> helpers (`futures_expiry_from_delivery`, `options_expiry_from_delivery`,
> `t_from_delivery`, `t_futures_from_delivery`). It is not imported anywhere
> in the repo (see Step 4) and is dead code.

### 1.2 TFM rule (futures): "two UK business days before delivery month"

`ttf_futures_expiry_date` (lines 126–150):

```python
d = date(delivery_year, delivery_month, 1)
for _ in range(2):
    d = _prev_uk_bd(d - timedelta(days=1))
return d
```

This iterates back **two UK business days** strictly before the 1st of the
delivery month, with the UK calendar (England & Wales bank holidays) used
for the business-day check.

**Result: PASS.**

### 1.3 TFO rule (options): "five calendar days before delivery month with UK BD adjustment"

`ttf_expiry_date` (lines 153–183):

```python
candidate = _prev_uk_bd(
    date(contract_year, contract_month, 1) - timedelta(days=5)
)
if candidate == ttf_futures_expiry_date(contract_month, contract_year):
    candidate = _prev_uk_bd(candidate - timedelta(days=1))
return candidate
```

Subtracts five **calendar** days from the 1st of the delivery month, rolls
back to the previous UK business day if needed, and steps back one more
business day if the candidate collides with the futures LTD.

**Result: PASS.**

### 1.4 `ttf_time_to_expiry` — calendar days / 365 only

```python
def ttf_time_to_expiry(contract_month, contract_year, reference=None):
    ref = reference or date.today()
    return (ttf_expiry_date(contract_month, contract_year) - ref).days / 365
```

No business-day adjustment, no day-count convention, no `+1` offset.

**Result: PASS.**

### 1.5 Printed calendar — Jan-Dec 2026

| Month | TFM (futures LTD) | TFO (option expiry) |
|---|---|---|
| Jan 2026 | Tue 30 Dec 2025 | Wed 24 Dec 2025 |
| Feb 2026 | Thu 29 Jan 2026 | Tue 27 Jan 2026 |
| Mar 2026 | Thu 26 Feb 2026 | Tue 24 Feb 2026 |
| Apr 2026 | Mon 30 Mar 2026 | Fri 27 Mar 2026 |
| May 2026 | Wed 29 Apr 2026 | Fri 24 Apr 2026 |
| Jun 2026 | Thu 28 May 2026 | Wed 27 May 2026 |
| Jul 2026 | Mon 29 Jun 2026 | Fri 26 Jun 2026 |
| Aug 2026 | Thu 30 Jul 2026 | Mon 27 Jul 2026 |
| Sep 2026 | Thu 27 Aug 2026 | Wed 26 Aug 2026 |
| Oct 2026 | Tue 29 Sep 2026 | Fri 25 Sep 2026 |
| Nov 2026 | Thu 29 Oct 2026 | Tue 27 Oct 2026 |
| Dec 2026 | Fri 27 Nov 2026 | Thu 26 Nov 2026 |

Spot-checks: Jan-26 TFO (Wed 24 Dec 2025) is correctly rolled back from
Sat 27 Dec 2025 → Fri 26 Dec (Boxing Day) → Thu 25 Dec (Christmas) →
Wed 24 Dec, then is also not the futures LTD (Tue 30 Dec). May-26 TFO is
Fri 24 Apr because the first roll back from Wed 27 Apr lands on the
TFM LTD Wed 29 Apr only after collision check; here `1 May - 5 cal days
= 26 Apr (Sun)` → Fri 24 Apr (Mon 27 Apr is the early-May bank holiday's
Monday in 2026? — Early May Monday is 4 May 2026, so Mon 27 Apr is a
business day. Inspection: candidate `26 Apr (Sun)` → `24 Apr (Fri)`,
which is not the TFM LTD `29 Apr`, so kept.) — values match the TFO rule.

**Result: PASS.**

---

## STEP 2 — Greeks consistency

Test parameters: `F = 30`, `K = 30`, `vol = 50%`, `T = 1`, `r = 2%`.

### 2.1 Theta `rate_term = +r * price` (Black-76 and Bachelier)

Current code in `b76_theta` (lines 354–367):

```python
if option_type == "call":
    rate_term = -r * df * (F * norm.cdf(d1) - K * norm.cdf(d2))
else:
    rate_term = -r * df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
return (decay + rate_term) / 365.0
```

This is **`-r * price`**, not `+r * price`. The same pattern is in
`bach_theta` (lines 455–466):

```python
price = bach_price(F, K, T, r, sigma_n, option_type)
rate_term = -r * price
return (decay + rate_term) / 365.0
```

The Black-76 European call theta (∂C/∂t, where t is "today" advancing) is
`+r·C - F·df·φ(d1)·σ/(2√T)`, i.e. the rate term should be **positive**
`+r·price`.

Numerical evidence at the test point:
- `decay term  = -2.842587`
- `rate_term (-r·price) = -0.116102`  → theta/day = **-0.008106**
- `rate_term (+r·price) = +0.116102`  → theta/day = **-0.007470**

Both yield a negative theta (because `decay` dominates), which is why the
sign error has not been visually obvious, but it is mathematically wrong
by `2·r·price/365`.

**Result: FAIL.** The "+r * price" theta fix is **not** applied — neither in
`b76_theta` nor in `bach_theta`. Both still use `-r * price`.

### 2.2 NameError fix — `_prev_uk_bd` in `__main__`

The `__main__` block (lines 664–720) references only the public API:
`b76_call`, `b76_put`, `b76_greeks`, `b76_implied_vol`,
`b76_delta_to_strike`, `bach_call`, `bach_implied_vol`,
`ttf_futures_expiry_date`, `ttf_expiry_date`, `ttf_time_to_expiry`,
`ttf_next_expiries`, `_MONTH_CODES_ICE`. There is **no reference** to
`_prev_uk_bd`. Running `python3 black76_ttf.py` produces no NameError.

**Result: PASS.**

### 2.3 Put-call parity: `C − P = e^(-rT)·(F − K)`

```
Call             = 5.805109
Put              = 5.805109
C − P            = 0.00000000
e^(-rT)·(F − K)  = 0.00000000   (F = K)
|diff|           = 0.00e+00
```

ATM (`F = K`) makes both sides zero; the parity identity holds exactly.

**Result: PASS.**

### 2.4 `Δ_call − Δ_put = e^(-rT)`

```
Delta_C            = 0.58685115
Delta_P            = -0.39334753
Delta_C − Delta_P  = 0.98019867
e^(-rT)            = 0.98019867
|diff|             = 0.00e+00
```

**Result: PASS.**

### 2.5 `Γ_call = Γ_put`

`b76_gamma` (lines 338–343) is symmetric in option type; numerical value
at the test point: `Γ = 0.02526744`. Call and put gammas agree by
construction in the closed-form formula.

**Result: PASS.**

### 2.6 Sanity values (test point)

```
Black-76: Call = 5.805109   Put = 5.805109
          Theta/day call = -0.008106   put = -0.008106    [WRONG sign on rate_term]
Bachelier: Call = 3.128342  Put = 3.128342
           Theta/day call = -0.004457  put = -0.004457    [WRONG sign on rate_term]
```

---

## STEP 3 — Module imports

### 3.1 `ttf_market_data.py`

```python
sys.path.insert(0, _HERE)               # line 38–39 — correct
from black76_ttf import (               # line 41
    ttf_futures_expiry_date,
    ttf_expiry_date,
    ttf_time_to_expiry,
    ttf_is_business_day,
)
```

`python3 -c "import ttf_market_data"` succeeds.

**Result: PASS.**

### 3.2 `ttf_hh_spread.py`

Top-level imports do not pull anything expiry-related from `black76_ttf`
(it uses only its own Margrabe code). However, line 263 has a deferred,
in-function import:

```python
if isinstance(T, str):
    from black76_ttf import t_from_contract     # line 263
    T_val = t_from_contract(T, reference)
```

`t_from_contract` **does not exist** in the cleaned `black76_ttf.py`.
Calling `spread_price(..., T="M+1", ...)` raises:

```
ImportError: cannot import name 't_from_contract' from 'black76_ttf'
```

The float branch (`T = 0.25` etc.) works fine.

**Result: FAIL** — the string-T contract-code path of `spread_price` is
broken. Either remove that branch (and require numeric `T`) or replace
with the new API, e.g. parse `"M+1"` → `(month, year)` and call
`ttf_time_to_expiry(month, year, reference)`.

### 3.3 `dashboard_jupyter.ipynb`

Cell 14 imports:

```python
from black76_ttf import (
    ttf_next_expiries, ttf_time_to_expiry,
    _ttf_futures_ltd, _MONTH_CODES_ICE,
)
```

`_ttf_futures_ltd` was removed in the recent expiry cleanup; the symbol
no longer exists. Running cell 14 raises:

```
ImportError: cannot import name '_ttf_futures_ltd' from 'black76_ttf'
```

`_MONTH_CODES_ICE` still exists. The other notebook cells
(`import black76_ttf as b76m`, `import structures_ttf as st`,
`import ttf_hh_spread as sp`, etc.) are syntactically fine **but** any
cell that imports `structures_ttf` will also fail (see 3.4).

The notebook does not set `sys.path` — it relies on Jupyter being launched
from the repo root, which is the documented convention.

**Result: FAIL** for cell 14 (uses removed symbol `_ttf_futures_ltd`)
and indirectly for any cell that imports `structures_ttf`.

### 3.4 `structures_ttf.py`

Top-level import (lines 33–36):

```python
from black76_ttf import (
    b76_price, b76_delta, b76_gamma, b76_vega, b76_theta,
    t_from_contract,
)
```

`t_from_contract` is gone. `import structures_ttf` raises:

```
ImportError: cannot import name 't_from_contract' from 'black76_ttf'
```

This is a **hard import failure at module load** — every consumer of
`structures_ttf` (notebook cell 5, `dashboard_ttf.py`, `test_suite.py`)
breaks. `structures_ttf.py` does not set `sys.path`; it relies on cwd.

**Result: FAIL.**

### 3.5 `dashboard_ttf.py`, `test_suite.py`

Their `from black76_ttf import (...)` blocks reference only existing
symbols and pass. Both transitively import `structures_ttf`, so they
break for the reason in 3.4.

`dashboard_ttf.py` sets `sys.path.append(...)` on line 24 — OK.
`test_suite.py` does not set `sys.path`, but it is run from the repo
root.

**Result: FAIL** (transitive, via `structures_ttf`).

### 3.6 `main.py`, `generate_charts.py`

`main.py` imports from a `pricing/` sub-package — unaffected by the
expiry refactor.
`generate_charts.py` does `import black76_ttf as b76` and uses only
public functions (`b76_call`, `b76_greeks`, etc.). Imports cleanly.

**Result: PASS.**

### 3.7 sys.path summary

| File | sys.path setup | OK? |
|---|---|---|
| `black76_ttf.py` | none needed (no sibling imports) | YES |
| `ttf_market_data.py` | `sys.path.insert(0, _HERE)` | YES |
| `ttf_hh_spread.py` | none | works because it's run from repo root |
| `structures_ttf.py` | none | works because it's run from repo root |
| `dashboard_ttf.py` | `sys.path.append(...)` | YES |
| `test_suite.py` | none | works because it's run from repo root |
| `dashboard_jupyter.ipynb` | none | relies on cwd |

No file is missing a `sys.path` line that would cause a path issue today;
all current import failures are due to symbol removals, not path setup.

---

## STEP 4 — Unused / duplicate functions

### 4.1 Wholly unused module

- **`ttf_time.py`** — defines a complete legacy expiry calendar
  (`futures_expiry_from_delivery`, `options_expiry_from_delivery`,
  `t_from_delivery`, `t_futures_from_delivery`, `_ttf_holidays`,
  `ttf_is_business_day`, etc.). **Not imported anywhere** in the repo
  (no `import ttf_time` / `from ttf_time` in any `.py` file or notebook
  cell). Recommend **delete** — its responsibilities are now owned by
  `black76_ttf.py`.

### 4.2 Duplicates / redundant local helpers

- **`ttf_market_data.py`** ships two parallel delta-to-strike inverters:
  `TTFExpiryCalendar._delta_to_strike` (line 429, instance method used
  internally in vol-surface building) and module-level
  `_b76_delta_to_strike` (line 640, used by `get_vol_by_delta`).
  Both re-implement what `black76_ttf.b76_delta_to_strike` already does.
  Recommend **collapse onto `black76_ttf.b76_delta_to_strike`** to
  eliminate three implementations of the same Brent solver.

### 4.3 Functions with no caller

`grep` of every `.py` file and notebook cell shows no callers for:

- `bach_delta_to_strike` (`black76_ttf.py:631`) — counterpart of
  `b76_delta_to_strike`, never used. Keep only if there is a planned
  Bachelier-quoted-delta workflow; otherwise **delete**.
- `bach_volga` (`black76_ttf.py:487`) — defined, exposed in
  `bach_greeks`, but `bach_greeks` itself has no caller outside
  `black76_ttf.py`'s `__main__`. Low-priority, low-cost; can keep.
- `bach_vanna`, `bach_rho` — same situation as `bach_volga`. Keep.

### 4.4 Functions referenced but missing (broken)

- `t_from_contract` (referenced by `structures_ttf.py:35` and
  `ttf_hh_spread.py:263`) — removed from `black76_ttf.py`, must either
  be reintroduced (e.g. parsing `"M+1"` style codes into a delivery
  month/year and delegating to `ttf_time_to_expiry`) or the call sites
  must be updated to take `(month, year)` directly.
- `_ttf_futures_ltd` (referenced by `dashboard_jupyter.ipynb` cell 14)
  — removed; replace with the public `ttf_futures_expiry_date`.

### 4.5 Recommended deletes

1. `ttf_time.py` — entire file (dead module).
2. `ttf_market_data.TTFExpiryCalendar._delta_to_strike` and
   `ttf_market_data._b76_delta_to_strike` — replace both call sites with
   `black76_ttf.b76_delta_to_strike`.
3. `bach_delta_to_strike` if no Bachelier delta-quote workflow exists.

---

## Summary table

| Check | Result |
|---|---|
| 1.1  Only the 5 public expiry functions remain in `black76_ttf.py` | **PASS** |
| 1.2  TFM rule = 2 UK business days before delivery month | **PASS** |
| 1.3  TFO rule = 5 calendar days before delivery month + UK BD roll | **PASS** |
| 1.4  `ttf_time_to_expiry` = calendar days / 365, nothing else | **PASS** |
| 1.5  Printed Jan-Dec 2026 calendar (TFM + TFO) | **PASS** |
| 2.1  Theta `rate_term = +r·price` in `b76_theta` and `bach_theta` | **FAIL** |
| 2.2  No `_prev_uk_bd` NameError in `__main__` | **PASS** |
| 2.3  Put-call parity `C − P = e^(-rT)(F − K)` | **PASS** |
| 2.4  `Δ_call − Δ_put = e^(-rT)` | **PASS** |
| 2.5  `Γ_call = Γ_put` | **PASS** |
| 3.1  `ttf_market_data.py` imports cleanly from `black76_ttf` | **PASS** |
| 3.2  `ttf_hh_spread.py` imports cleanly from `black76_ttf` | **FAIL** (`t_from_contract` missing) |
| 3.3  `dashboard_jupyter.ipynb` imports cleanly | **FAIL** (cell 14 uses removed `_ttf_futures_ltd`) |
| 3.4  `structures_ttf.py` imports cleanly | **FAIL** (`t_from_contract` missing) |
| 3.5  `sys.path` set correctly where needed | **PASS** |
| 4.1  No wholly unused modules | **FAIL** (`ttf_time.py` is dead) |
| 4.2  No duplicate implementations | **FAIL** (3× `delta_to_strike` solvers) |

## Actions required

1. **Fix `b76_theta` and `bach_theta`** rate-term sign:
   - `b76_theta`: replace the two-branch `rate_term = -r * df * (...)` with
     `rate_term = +r * b76_price(F, K, T, r, sigma, option_type)`.
   - `bach_theta`: change `rate_term = -r * price` to
     `rate_term = +r * price`.
2. **Restore or remove `t_from_contract`**. Either reintroduce it in
   `black76_ttf.py` (parse `"M+1"`/`"TTFM26"` into `(month, year)` and
   delegate to `ttf_time_to_expiry`) or update the two call sites
   (`structures_ttf.py:35,90` and `ttf_hh_spread.py:263–264`) to pass
   numeric `T` only and drop the string branch.
3. **Update notebook cell 14** to import `ttf_futures_expiry_date`
   instead of `_ttf_futures_ltd`.
4. **Delete `ttf_time.py`** (no callers anywhere).
5. **Consolidate the three delta-to-strike implementations** in
   `ttf_market_data.py` onto `black76_ttf.b76_delta_to_strike`.
