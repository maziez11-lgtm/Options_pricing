# TTF Natural Gas Options Pricing

A Python library for pricing European options on TTF natural gas futures, with a React dashboard for interactive analysis.

## Overview

This library implements industry-standard models for energy derivatives:

- **Black-76** — lognormal model, the market standard for TTF options
- **Bachelier** — normal-distribution model for low or negative price environments
- **Monte Carlo** and **Binomial Tree** — for exotic/American options
- **SABR calibration** — fits the implied vol smile from market data
- ICE TFO (TTF Options) expiry calendar — official rule, UK business-day calendar

## Features

| Module | What It Provides |
|--------|-----------------|
| `black76_ttf.py` | Black-76 and Bachelier pricing, Greeks, implied vol, contract-code parsing |
| `ttf_market_data.py` | Forward curve, vol surface construction, SABR calibration, JSON/CSV export |
| `ttf_time.py` | Generic day-count helpers (Act/365, Act/360, Act/Act, Bus/252) — *not* the ICE TFO expiry calendar; use `black76_ttf.ttf_expiry_date` for that |
| `pricing/` | Core model implementations: Black-Scholes, Black-76, Bachelier, binomial tree, Monte Carlo, implied vol solvers |
| `dashboard/` | React + Vite frontend — interactive pricer, Greeks charts, 3D vol surface |

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd Options_pricing

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

`requirements.txt` covers `numpy`, `scipy`, `pandas`, and `requests`.

## Quick Start

```python
from black76_ttf import b76_call, b76_put, b76_greeks, b76_price_ttf

# Price a Jun-26 ATM call
call = b76_call(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50)
print(f"Call: {call:.2f} EUR/MWh")   # → 3.43 EUR/MWh

# Price by contract code — T is calculated automatically from the ICE expiry calendar
price = b76_price_ttf(F=35.0, K=35.0, contract="Jun26", r=0.03, sigma=0.50)

# Greeks
g = b76_greeks(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50, option_type="call")
print(f"Delta: {g.delta:.2f}  Vega: {g.vega:.2f}  Theta: {g.theta:.4f}/day")

# Load a TTF forward curve from a hand-typed dict and inspect it
from ttf_market_data import load_ttf_forward_curve
fc = load_ttf_forward_curve(
    source="manual",
    data={"Jun-26": 30.5, "Jul-26": 31.2, "Aug-26": 32.0},
)
# Or fc = load_ttf_forward_curve(source="csv", filepath="ttf_forwards.csv")
# Or fc = load_ttf_forward_curve()  # uses the bundled Jun-26→Dec-27 sample
```

Accepted contract formats: `"TTFM26"`, `"Jun26"`, `"Jun2026"`.

See **Manual Forward Curve & Vol Surface** below for the full forward-curve
loader and the delta-quoted vol-surface helpers.

## Module Overview

### `black76_ttf.py` — Core Pricing

The primary entry point for most use cases.

```python
from black76_ttf import (
    b76_call, b76_put, b76_price,       # Black-76 pricing
    b76_greeks, b76_implied_vol,         # Greeks and implied vol
    b76_price_ttf, bach_price_ttf,       # Pricing by contract code
    bach_call, bach_put, bach_greeks,    # Bachelier (normal vol)
    ttf_expiry_date, ttf_time_to_expiry, # ICE TFO expiry calendar
    ttf_is_business_day, ttf_next_expiries,
    t_from_contract,                     # Contract-name → T (calendar/365)
)
```

Use **Black-76** for normal market conditions (F > ~5 EUR/MWh). Use **Bachelier** when prices are near zero or negative, or when the market quotes normal vol in EUR/MWh.

### `ttf_market_data.py` — Market Data

Builds forward curves and vol surfaces from market data, with SABR calibration.
The class delegates the option-expiry calculation to
`black76_ttf.ttf_expiry_date` (ICE TFO rule, UK calendar) so dates stay in
sync with the rest of the project.

```python
from datetime import date
from ttf_market_data import TTFExpiryCalendar, VolatilitySurfaceBuilder, MarketCalibration

calendar = TTFExpiryCalendar(reference_date=date(2026, 4, 20))
calendar.expiry_date(2026, 6)            # date(2026, 5, 27)  — ICE TFO
calendar.futures_expiry_date(2026, 6)    # date(2026, 5, 29)  — last UK BD
```

### `pricing/` — Core Models

Lower-level implementations used by the TTF wrappers above.

```python
from pricing import black76_price, bachelier_price, binomial_price, mc_price
from pricing.greeks import b76_delta, b76_gamma, b76_vega
from pricing.implied_vol import b76_implied_vol_brent
```

## Vol Surface & Interpolation

### What is a vol surface?

A **volatility surface** is the set of implied vols quoted across strikes (the *smile*) and maturities (the *term structure*). For each (strike, maturity) point, the market quotes a Black-76 implied vol, and any option whose strike or expiry sits between quoted points needs a vol from interpolation.

For TTF options this matters because:

- Pricing a non-standard strike (e.g. 27.50 EUR/MWh) requires a vol that isn't directly quoted.
- Risk metrics (delta-bucketed Greeks, vega ladders, scenario P&L) need a continuous σ(K, T).
- Structured products (collars, calendar spreads, swaptions) reference vols at multiple points and break if the surface is inconsistent.

### Smile interpolation

Across strikes, `get_vol_by_strike(F, K, T, vol_surface)` uses a **natural cubic spline** between the quoted points, with **flat extrapolation** outside the wings. Across maturities, vols are interpolated linearly after the strike-level interpolation.

Why cubic spline:

- **Smooth** — C² continuity, so dσ/dK and d²σ/dK² are continuous (matters for vanna and volga).
- **Local** — interpolated values stay between neighbouring quotes, so adjacent points don't induce arbitrage at the smile level.
- **No parametric assumptions** — fits the quoted points exactly, unlike SABR or SVI which trade fit for stability.

Cubic *extrapolation* of vols is unstable (smile polynomials can swing into negative or explosive vols beyond the wings), so strikes outside the quoted range are clamped to the nearest wing vol.

### Delta-to-strike conversion

`get_vol_by_delta(F, delta, T, vol_surface, r)` converts a delta target (e.g. `0.25` for 25Δ call, `-0.25` for 25Δ put, `0.50` for ATM-equivalent) to a strike using **Black-76 delta inversion**:

```
delta_call = e^(-rT) · N(d1)
delta_put  = -e^(-rT) · N(-d1)
where d1 = [ln(F/K) + 0.5·σ²·T] / (σ·√T)
```

The strike consistent with a given delta depends on the unknown vol, so the routine runs a fixed-point iteration: seed with the ATM vol, invert delta → K at fixed σ via `brentq`, look up σ' = vol(K, T) from the surface, repeat until σ converges.

For ATM, the **delta-neutral straddle (ATM-DN)** convention is `K = F · exp(-σ²·T / 2)`, which is the strike where call and put deltas are equal in magnitude. This is the market-standard ATM definition for FX and energy options and is implicit in the iteration above when `delta = 0.50`.

### TTF surface characteristics

A typical TTF vol surface has:

- **Downside skew** — OTM puts trade at higher implied vols than OTM calls. The 25Δ put vol is typically ~3–5 vol points above the 25Δ call vol.
- **Term-structure decay** — short-dated vols are higher than long-dated vols. Sample levels in `SAMPLE_TTF_VOL_SURFACE`:

  | Tenor | ATM vol |
  |-------|---------|
  | 1M    | ~55%    |
  | 3M    | ~50%    |
  | 6M    | ~46%    |
  | 12M   | ~42%    |

The downside skew reflects an **asymmetric supply-disruption risk**: gas prices can spike sharply on cold weather, pipeline outages, or geopolitical events, while upside is bounded by demand destruction and storage capacity. Hedgers (utilities, industrials) systematically buy downside protection, pushing OTM put vols above OTM call vols.

### Limitations

- **No SABR or SVI parametrization.** Smile interpolation is purely numerical (cubic spline). For risk-neutral density extraction or extrapolation past the wings, use the SABR calibration in `MarketCalibration` instead.
- **No arbitrage-free constraints enforced.** Cubic splines do not guarantee monotonic call prices in K (no calendar arbitrage) or non-negative butterfly spreads. A pathological input surface can produce arbitrageable interpolated vols.
- **Wing extrapolation is flat.** Vols beyond the quoted strike range are clamped to the boundary value, which underestimates wing vols for far-OTM options. Quote a wider strike grid, or use SABR, if you need accurate tail pricing.
- **Linear in maturity, not in variance.** Term-structure interpolation is linear in σ rather than in σ²·T (total variance), which is acceptable for short tenor gaps but can introduce small calendar arbitrages over wide gaps.

```python
from ttf_market_data import (
    SAMPLE_TTF_VOL_SURFACE, get_vol_by_strike, get_vol_by_delta,
)

F, T, r = 30.0, 0.25, 0.03
sigma_K  = get_vol_by_strike(F, K=27.5, T=T, vol_surface=SAMPLE_TTF_VOL_SURFACE)
sigma_25p = get_vol_by_delta(F, delta=-0.25, T=T, vol_surface=SAMPLE_TTF_VOL_SURFACE, r=r)
```

## Manual Forward Curve & Vol Surface

`ttf_market_data.py` exposes a small set of helpers for working with a
hand-typed (or CSV-fed) forward curve, with the **ICE TFO** expiry calendar
imported directly from `black76_ttf` so the dates always match the official
contract rule.

### `load_ttf_forward_curve(source='manual', data=None, filepath=None, reference=None)`

Two input modes:

```python
from ttf_market_data import load_ttf_forward_curve

# 1. Manual — pass a {delivery_month: forward_price} dict
fc = load_ttf_forward_curve(
    source="manual",
    data={"Jun-26": 30.5, "Jul-26": 31.2, "Aug-26": 32.0},
)

# 2. CSV — a file with columns (delivery_month, forward_price)
fc = load_ttf_forward_curve(source="csv", filepath="ttf_forwards.csv")
```

Output columns: `delivery_month`, `expiry_date`, `time_to_expiry`,
`forward_price`. `expiry_date` comes from `ttf_expiry_date()` and
`time_to_expiry` from `ttf_time_to_expiry()` (calendar days / 365).

Calling `load_ttf_forward_curve()` with no arguments returns the bundled
sample curve `SAMPLE_TTF_FORWARD_CURVE` (Jun-26 → Dec-27, EUR/MWh, with a
realistic seasonal shape: winter peaks ≈ 35, summer troughs ≈ 28).

### `update_vol_surface(forward_curve, vol_surface)`

Joins a delta-quoted vol surface with the forward curve. For each
`(delivery_month, call-delta pillar, vol)` triple it computes:

- **Strike** — at the ATM pillar (Δ = 0.50), the delta-neutral rule
  `K_atm = F · exp(-σ²T / 2)`. At any other pillar, the Black-76 inversion
  `K = F · exp(0.5σ²T − Φ⁻¹(δ)·σ·√T)`.
- **Delta** — re-computed under Black-76 at that `(K, σ)` so the row is
  internally consistent.
- **Moneyness** — `K / F`.

```python
from ttf_market_data import update_vol_surface, SAMPLE_VOL_SURFACE
vs = update_vol_surface(fc, SAMPLE_VOL_SURFACE)
# columns: delivery_month, expiry_date, time_to_expiry, forward_price,
#          strike, implied_vol, delta, moneyness, delta_pillar
```

`SAMPLE_VOL_SURFACE` is a TTF-style downside-skew surface across the same
19 contracts: ATM ≈ 50% short term, ≈ 37% at ~1.5y, with a 10-Δ-call to
90-Δ-call wing spread of about 14 vol points (puts richer than calls).

### `display_vol_surface(vol_surface_df)`

Pretty-prints the surface as a clean maturity × delta grid. Vols are
formatted as percentages, the ATM column is suffixed with `(ATM)`, and the
function returns the formatted pivot for further export.

```text
TTF vol surface — rows: maturity, cols: call-delta pillar
ATM column is the delta-neutral strike (K = F·exp(−σ²T/2))

          Δ=0.10  Δ=0.25 Δ=0.50 (ATM)  Δ=0.75  Δ=0.90
Delivery
Jun-26     43.0%   47.0%        50.0%   53.0%   57.0%
Jul-26     42.0%   46.0%        49.0%   52.0%   56.0%
...
Dec-27     30.0%   34.0%        37.0%   40.0%   44.0%
```

## Dashboard

The interactive React dashboard visualises prices, Greeks, and vol surfaces.

```bash
cd dashboard
npm install
npm run dev
# Opens at http://localhost:5173
```

| Tab | Features |
|-----|----------|
| **Pricer** | Price a single call or put; view full Greeks |
| **Vol Surface** | 3D implied vol surface across strikes and tenors |
| **Greeks Chart** | Delta, Gamma, Vega vs strike for B76 and Bachelier side-by-side |
| **Comparison** | B76 vs Bachelier prices across the strike range |

Click **Export to Excel** in any tab to download a `.xlsx` file.

## Project Structure

```
Options_pricing/
├── black76_ttf.py        # TTF-specific Black-76 & Bachelier wrapper (main entry point)
├── ttf_market_data.py    # Forward curves, vol surfaces, SABR calibration
├── ttf_time.py           # Generic day-count helpers (Act/365, Act/360, Act/Act, Bus/252)
├── main.py               # Demo / entry-point script
├── pricing/              # Core model library
│   ├── black76.py        # Black-76 model
│   ├── bachelier.py      # Bachelier model
│   ├── black_scholes.py  # Black-Scholes model
│   ├── greeks.py         # Greeks for all three models (Δ, Γ, ν, Θ, ρ, Vanna, Volga)
│   ├── binomial_tree.py  # CRR binomial tree (American & European)
│   ├── implied_vol.py    # Brent's-method implied vol solvers
│   └── monte_carlo.py    # Monte Carlo pricing (plain vanilla & Asian)
├── dashboard/            # React + Vite frontend
├── ttf_output/           # Pre-computed JSON: forward_curve, vol_surface, SABR params
├── requirements.txt
└── user_manual.md        # Full user manual with worked examples and glossary
```

## Documentation

See **[user_manual.md](user_manual.md)** for:

- TTF options fundamentals (5-minute primer)
- Full API reference with parameter tables and code examples
- Greeks interpretation and hedging guidance
- Bachelier vs Black-76 model selection guide
- Implied vol, expiry calendar, and Bachelier normal-vol examples
- Glossary of 40+ options and energy-markets terms

## Expiry Calendar

TTF options follow the official **ICE TFO** (TTF Options) contract rule.
ICE product code: **TFO**.

> *Trading will cease when the intraday settlement price of the underlying
> futures contract is set, five calendar days before the start of the
> contract month. If that day is a non-business day or non-UK business day,
> expiry will occur on the nearest prior business day, except where that day
> is also the expiry date of the underlying futures contract, in which case
> expiry will occur on the preceding business day.*

The implementation uses a **UK business-day calendar** (England & Wales
public holidays only — New Year, Good Friday, Easter Monday, the early-May,
spring and summer bank holidays, Christmas Day, Boxing Day, with the
standard substitution to the next weekday when a fixed-date holiday falls
on a weekend).

Computed expiries for monthly contracts in 2026:

| Contract | Futures LTD | Option Expiry | Day |
|----------|-------------|---------------|-----|
| Jan-26 | 31 Dec 2025 | 24 Dec 2025 | Wed |
| Feb-26 | 30 Jan 2026 | 27 Jan 2026 | Tue |
| Mar-26 | 27 Feb 2026 | 24 Feb 2026 | Tue |
| Apr-26 | 31 Mar 2026 | 27 Mar 2026 | Fri |
| May-26 | 30 Apr 2026 | 24 Apr 2026 | Fri |
| Jun-26 | 29 May 2026 | 27 May 2026 | Wed |
| Jul-26 | 30 Jun 2026 | 26 Jun 2026 | Fri |
| Aug-26 | 31 Jul 2026 | 27 Jul 2026 | Mon |
| Sep-26 | 28 Aug 2026 | 27 Aug 2026 | Thu |
| Oct-26 | 30 Sep 2026 | 25 Sep 2026 | Fri |
| Nov-26 | 30 Oct 2026 | 27 Oct 2026 | Tue |
| Dec-26 | 30 Nov 2026 | 26 Nov 2026 | Thu |

`ttf_expiry_date()`, `ttf_time_to_expiry()`, `ttf_next_expiries()`,
`t_from_contract()` and `b76_price_ttf()` all use this calendar.

## Requirements

- Python 3.9+
- numpy, scipy, pandas, requests
- Node.js 18+ (dashboard only)
