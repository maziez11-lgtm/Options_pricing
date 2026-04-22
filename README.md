# TTF Natural Gas Options Pricing

A Python library for pricing European options on TTF natural gas futures, with a React dashboard for interactive analysis.

## Overview

This library implements industry-standard models for energy derivatives:

- **Black-76** — lognormal model, the market standard for TTF options
- **Bachelier** — normal-distribution model for low or negative price environments
- **Monte Carlo** and **Binomial Tree** — for exotic/American options
- **SABR calibration** — fits the implied vol smile from market data
- TTF-specific expiry calendar following ICE/EEX conventions (options expire 5 business days before futures LTD)

## Features

| Module | What It Provides |
|--------|-----------------|
| `black76_ttf.py` | Black-76 and Bachelier pricing, Greeks, implied vol, contract-code parsing |
| `ttf_market_data.py` | Forward curve, vol surface construction, SABR calibration, JSON/CSV export |
| `ttf_time.py` | Time-to-maturity utilities, day-count conventions, TARGET2 holiday calendar |
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
```

Accepted contract formats: `"TTFM26"`, `"Jun26"`, `"Jun2026"`.

## Module Overview

### `black76_ttf.py` — Core Pricing

The primary entry point for most use cases.

```python
from black76_ttf import (
    b76_call, b76_put, b76_price,       # Black-76 pricing
    b76_greeks, b76_implied_vol,         # Greeks and implied vol
    b76_price_ttf, bach_price_ttf,       # Pricing by contract code
    bach_call, bach_put, bach_greeks,    # Bachelier (normal vol)
    options_expiry_from_delivery,        # Expiry calendar
    t_from_contract, t_from_delivery,    # Time-to-maturity
)
```

Use **Black-76** for normal market conditions (F > ~5 EUR/MWh). Use **Bachelier** when prices are near zero or negative, or when the market quotes normal vol in EUR/MWh.

### `ttf_market_data.py` — Market Data

Builds forward curves and vol surfaces from market data, with SABR calibration.

```python
from ttf_market_data import TTFExpiryCalendar, VolatilitySurface, calibrate_sabr

calendar = TTFExpiryCalendar()
expiry = calendar.options_expiry(2026, 6)   # 2026-05-22
```

### `ttf_time.py` — Time Utilities

Day-count conventions and business-day helpers for precise T calculations.

```python
from ttf_time import ttf_time_to_expiry, DayCountConvention

T = ttf_time_to_expiry("TTFM26", convention=DayCountConvention.ACT365)
```

### `pricing/` — Core Models

Lower-level implementations used by the TTF wrappers above.

```python
from pricing import black76_price, bachelier_price, binomial_price, mc_price
from pricing.greeks import b76_delta, b76_gamma, b76_vega
from pricing.implied_vol import b76_implied_vol_brent
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
├── ttf_time.py           # Day-count conventions, TARGET2 calendar, T calculations
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

TTF options follow ICE/EEX conventions:

| Contract | Futures LTD | Options Expiry |
|----------|------------|----------------|
| Jun-26 | 29 May 2026 | 22 May 2026 |
| Jul-26 | 30 Jun 2026 | 23 Jun 2026 |

Options expire **5 business days before** the futures last trading day. `t_from_contract()` and `b76_price_ttf()` use this calendar automatically.

## Requirements

- Python 3.9+
- numpy, scipy, pandas, requests
- Node.js 18+ (dashboard only)
