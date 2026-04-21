# TTF Natural Gas Options — User Manual

> Written for gas traders and analysts familiar with TTF markets, but new to options pricing.

---

## Table of Contents

1. [What Is a TTF Option?](#1-what-is-a-ttf-option)
2. [Key Concepts in 5 Minutes](#2-key-concepts-in-5-minutes)
3. [Quick Start](#3-quick-start)
4. [Module 1 — Black-76 & Bachelier Pricing (`black76_ttf.py`)](#4-module-1--black-76--bachelier-pricing)
5. [Module 2 — Option Structures (`structures_ttf.py`)](#5-module-2--option-structures)
6. [Module 3 — TTF/HH Spread Option (`ttf_hh_spread.py`)](#6-module-3--ttfhh-spread-option)
7. [The Dashboard](#7-the-dashboard)
8. [Glossary](#8-glossary)

---

## 1. What Is a TTF Option?

**TTF** (Title Transfer Facility) is the main European natural gas benchmark, traded on ICE and EEX. Prices are quoted in **EUR/MWh**, and the standard contract is a monthly futures (delivery of 1 MW of gas continuously for the entire delivery month).

A **TTF option** gives you the *right, but not the obligation*, to buy or sell TTF gas at a pre-agreed price on a specific date.

### Call vs Put — The Simple Version

| Option | You get the right to… | Profits when… |
|--------|----------------------|---------------|
| **Call** | **Buy** gas at the strike price | Gas price **rises** above the strike |
| **Put** | **Sell** gas at the strike price | Gas price **falls** below the strike |

**Concrete example:**  
You buy a **Jun-26 Call, strike €35/MWh**. If TTF for June-26 delivery is trading at €42/MWh at expiry, you can still buy at €35 — a gain of **€7/MWh**. If it's at €28/MWh, the option expires worthless (you simply don't exercise it). The most you lose is the **premium** you paid upfront.

### TTF Options Expiry Convention (ICE/EEX)

- **Futures expiry**: last business day of the month *before* delivery.
- **Options expiry**: **5 business days before** the futures expiry.

Example for June-26 delivery:
- Futures last trading day: **29 May 2026**
- Options last trading day: **22 May 2026**

---

## 2. Key Concepts in 5 Minutes

### The 5 Inputs to Any Option Price

| Parameter | Symbol | What It Means | Typical TTF Value |
|-----------|--------|---------------|-------------------|
| Forward price | F | Current TTF futures price | €30–45 / MWh |
| Strike price | K | The fixed exercise price | Near F (ATM) |
| Time to expiry | T | Years until option expires | 0.08 – 2.0 y |
| Risk-free rate | r | EUR overnight rate (€STR) | 2–4% |
| Implied volatility | σ | Market's forecast of price movement | 40–80% |

### Volatility — The Most Important Input

Volatility (σ) measures how much the market *expects* gas prices to move. It is expressed as an annualised percentage:

- **σ = 50%** means the market expects TTF to move roughly ±50% over the next year.
- Higher σ → more expensive options (both calls and puts).
- You *cannot* observe σ directly; it is **implied** from market option prices.

### The Greeks — Sensitivity at a Glance

| Greek | What It Tells You | Practical Use |
|-------|------------------|---------------|
| **Delta (Δ)** | €-change in option value per €1 move in forward | Hedge ratio: delta = 0.50 means hedge half your position |
| **Gamma (Γ)** | How fast delta changes | High gamma → option reacts non-linearly to price moves |
| **Vega (ν)** | €-change per 1% increase in implied vol | Risk to vol moves; positive for long options |
| **Theta (Θ)** | Daily time decay (€/day, always negative for buyers) | Cost of holding an option overnight |
| **Rho (ρ)** | Sensitivity to interest rate changes | Small effect on short-dated TTF options |

---

## 3. Quick Start

### Requirements

```bash
pip install scipy numpy pandas requests
```

### Your First Calculation

```python
from black76_ttf import b76_call, b76_put, b76_greeks

F     = 35.0   # EUR/MWh — TTF Jun-26 forward
K     = 35.0   # EUR/MWh — at-the-money strike
T     = 0.25   # years   — ~3 months to expiry
r     = 0.03   # 3% EUR risk-free rate
sigma = 0.50   # 50% implied volatility

call = b76_call(F, K, T, r, sigma)
put  = b76_put(F, K, T, r, sigma)

print(f"Call: {call:.2f} EUR/MWh")   # → 3.43 EUR/MWh
print(f"Put:  {put:.2f} EUR/MWh")    # → 3.17 EUR/MWh

g = b76_greeks(F, K, T, r, sigma, "call")
print(f"Delta: {g.delta:.2f}, Vega: {g.vega:.2f}, Theta: {g.theta:.4f}/day")
```

### Using Contract Codes

```python
from black76_ttf import b76_price_ttf

# Automatically calculates T from the ICE contract code
price = b76_price_ttf(F=35.0, K=35.0, contract="TTFM26", r=0.03, sigma=0.50)
price = b76_price_ttf(F=35.0, K=35.0, contract="Jun26",  r=0.03, sigma=0.50)
```

Accepted contract formats: `"TTFM26"`, `"Jun26"`, `"Jun2026"`.

---

## 4. Module 1 — Black-76 & Bachelier Pricing

**File:** `black76_ttf.py`

### 4.1 Which Model to Use?

| Situation | Use |
|-----------|-----|
| Normal market conditions (F > ~5 EUR/MWh) | **Black-76** (lognormal vol) |
| Low or negative prices (crisis/glut scenarios) | **Bachelier** (normal vol) |
| Market quotes are in "EUR/MWh vol" rather than "%" | **Bachelier** |

### 4.2 Black-76 Pricing

The **Black-76 model** is the industry standard for options on energy futures. It assumes forward prices follow a lognormal distribution.

#### Core Functions

```python
from black76_ttf import b76_call, b76_put, b76_price

# Vanilla call and put
call = b76_call(F=35.0, K=33.0, T=0.5, r=0.03, sigma=0.45)
put  = b76_put( F=35.0, K=37.0, T=0.5, r=0.03, sigma=0.48)

# Generic function (call or put)
price = b76_price(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50, option_type="call")
```

#### Parameters

| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| `F` | float | EUR/MWh | TTF forward price |
| `K` | float | EUR/MWh | Strike price |
| `T` | float | years | Time to expiry (today included) |
| `r` | float | decimal | Risk-free rate (0.03 = 3%) |
| `sigma` | float | decimal | Lognormal implied vol (0.50 = 50%) |
| `option_type` | str | — | `"call"` or `"put"` |

#### Pricing with Contract Name

```python
from black76_ttf import b76_price_ttf, bach_price_ttf
from datetime import date

# T calculated automatically (options expiry, today included)
price = b76_price_ttf(
    F=35.0, K=35.0,
    contract="TTFM26",     # or "Jun26", "Jun2026"
    r=0.03, sigma=0.50,
    option_type="call",
    reference=date(2026, 4, 21)   # optional, defaults to today
)
```

### 4.3 Greeks

```python
from black76_ttf import b76_greeks, B76Greeks

g = b76_greeks(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50, option_type="call")

print(f"Delta : {g.delta:.4f}")   # fraction of forward movement
print(f"Gamma : {g.gamma:.6f}")   # delta change per EUR/MWh
print(f"Vega  : {g.vega:.4f}")    # EUR/MWh per 1-unit (100%) vol change
print(f"Theta : {g.theta:.4f}")   # EUR/MWh per calendar day
print(f"Vanna : {g.vanna:.6f}")   # mixed delta/vol sensitivity
print(f"Volga : {g.volga:.6f}")   # vol convexity
```

**Interpreting delta for hedging:**

| Delta | Position Description |
|-------|---------------------|
| 0.50 | At-the-money (ATM) call |
| 0.25 | 25-delta call — moderately OTM |
| 0.10 | 10-delta call — deep OTM, "wing" |
| −0.50 | ATM put |

### 4.4 Implied Volatility

```python
from black76_ttf import b76_implied_vol

# You observe the market price of an option and solve for σ
market_price = 3.50   # EUR/MWh

iv = b76_implied_vol(
    market_price=market_price,
    F=35.0, K=35.0, T=0.25, r=0.03,
    option_type="call"
)
print(f"Implied vol: {iv:.1%}")   # e.g. 51.3%
```

Raises `ValueError` if the price is below intrinsic value or outside the solvable range.

### 4.5 Bachelier Model (Normal Vol)

Used when TTF prices approach zero or go negative (rare but possible during supply gluts).

```python
from black76_ttf import bach_call, bach_put, bach_greeks, bach_implied_vol

# Normal vol is in EUR/MWh (absolute), NOT a percentage
sigma_n = 8.0   # 8 EUR/MWh annual normal vol

call = bach_call(F=5.0, K=5.0, T=0.25, r=0.03, sigma_n=sigma_n)
iv_n = bach_implied_vol(market_price=1.20, F=5.0, K=5.0, T=0.25, r=0.03)
```

### 4.6 Expiry Calendar

```python
from black76_ttf import options_expiry_from_delivery, futures_expiry_from_delivery
from black76_ttf import t_from_delivery, t_from_contract

# Expiry dates
opt_exp = options_expiry_from_delivery(2026, 6)   # → 2026-05-22
fut_exp = futures_expiry_from_delivery(2026, 6)   # → 2026-05-29

# Time to expiry in years (ACT/365, today included)
T = t_from_delivery(2026, 6)
T = t_from_contract("TTFM26")
T = t_from_contract("Jun26")
```

---

## 5. Module 2 — Option Structures

**File:** `structures_ttf.py`

Each structure combines two or more options to express a specific market view while managing cost and risk.

### Common Return Type

Every function returns a `StructureResult` with:

```python
result.price        # net premium paid (+) or received (−) in EUR/MWh
result.delta        # net delta
result.gamma        # net gamma
result.vega         # net vega
result.theta        # net theta per day
result.breakevens   # list of breakeven prices at expiry
result.max_profit   # maximum gain (math.inf if unlimited)
result.max_loss     # maximum loss (negative, −math.inf if unlimited)
result.pnl_at_expiry  # list of (F_T, pnl) tuples for plotting
```

---

### Structure 1 — Straddle

**View:** "I don't know which way gas will move, but I expect a big move."  
**Cost:** High (two premiums)  

```python
from structures_ttf import straddle

s = straddle(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~6.86 EUR/MWh
# Breakevens:  28.14 and 41.86 EUR/MWh
# Max profit:  unlimited
# Max loss:    −6.86 EUR/MWh (if F_T = K at expiry)
```

**P&L at expiry:** profit = |F_T − K| − premium

---

### Structure 2 — Strangle

**View:** "I expect a big move but want to spend less than a straddle."  
**Cost:** Lower than straddle (OTM options cheaper)

```python
from structures_ttf import strangle

s = strangle(F=35.0, K_put=32.0, K_call=38.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~4.29 EUR/MWh
# Profit zone: F_T < 27.71 or F_T > 42.29 EUR/MWh
```

You can pass per-leg vols to reflect the market smile:
```python
s = strangle(F=35.0, K_put=32.0, K_call=38.0, T=0.25, r=0.03, sigma=0.50,
             sigma_put=0.55, sigma_call=0.45)
```

---

### Structure 3 — Bull Call Spread

**View:** "I'm bullish, but I want to reduce the cost of my call."  
**Cost:** Low (partial debit)

```python
from structures_ttf import bull_call_spread

s = bull_call_spread(F=35.0, K_lo=34.0, K_hi=38.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~1.62 EUR/MWh  (vs ~3.90 for naked call)
# Max profit:  2.38 EUR/MWh at F_T ≥ 38
# Max loss:    −1.62 EUR/MWh at F_T ≤ 34
# Breakeven:   35.62 EUR/MWh
```

**Trade-off:** You cap your profit at K_hi in exchange for a lower premium.

---

### Structure 4 — Bear Put Spread

**View:** "I'm bearish, but I want to reduce the cost of my put."  
**Cost:** Low (partial debit)

```python
from structures_ttf import bear_put_spread

s = bear_put_spread(F=35.0, K_lo=32.0, K_hi=36.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~1.99 EUR/MWh
# Max profit:  2.01 EUR/MWh at F_T ≤ 32
# Max loss:    −1.99 EUR/MWh at F_T ≥ 36
```

---

### Structure 5 — Butterfly

**View:** "I expect gas to stay close to current levels — low volatility."  
**Cost:** Very low (small net debit)

```python
from structures_ttf import butterfly

s = butterfly(F=35.0, K_lo=31.0, K_mid=35.0, K_hi=39.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~0.71 EUR/MWh
# Max profit:  3.29 EUR/MWh at F_T = 35 (the middle strike)
# Max loss:    −0.71 EUR/MWh if F_T ≤ 31 or F_T ≥ 39
```

**Analogy:** You're selling a straddle but buying protection at the wings.

---

### Structure 6 — Condor

**View:** "I expect gas to trade in a range — wider than butterfly."  
**Cost:** Slightly higher than butterfly

```python
from structures_ttf import condor

s = condor(F=35.0, K1=30.0, K2=33.0, K3=37.0, K4=40.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: ~0.93 EUR/MWh
# Max profit:  2.07 EUR/MWh when 33 ≤ F_T ≤ 37
# Max loss:    −0.93 EUR/MWh if F_T ≤ 30 or F_T ≥ 40
```

---

### Structure 7 — Collar

**View:** "I'm long physical gas or a futures contract and want to hedge downside cheaply."  
**Cost:** Often near zero (put premium ≈ call premium received)

```python
from structures_ttf import collar

s = collar(F=35.0, K_put=32.0, K_call=38.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: −0.28 EUR/MWh  (slight CREDIT)
# Protects below 32 EUR/MWh
# Gives up upside above 38 EUR/MWh
```

> **Important:** The `collar()` function prices the options overlay only. Add your futures P&L `(F_T − F_entry)` to get the total hedged position P&L.

---

### Structure 8 — Risk Reversal

**View:** "I'm directionally bullish and want upside exposure, partly funded by selling downside."  
**Cost:** Near zero or small debit/credit depending on the vol skew

```python
from structures_ttf import risk_reversal

s = risk_reversal(F=35.0, K_put=32.0, K_call=38.0, T=0.25, r=0.03, sigma=0.50)
# Net premium: +0.28 EUR/MWh  (small debit)
# Profits from upside moves above 38
# Loses from downside moves below 32
# Max profit / loss: unlimited on both sides
```

---

### Structure 9 — Calendar Spread

**View:** "I think near-term vol is too high relative to longer-dated vol — buy long-dated, sell short-dated."  
**Cost:** Small debit (far option costs more than near option)

```python
from structures_ttf import calendar_spread

s = calendar_spread(
    F=35.0, K=35.0,
    T_far=180/365, T_near=90/365,
    r=0.03, sigma=0.50
)
# Net premium: ~1.37 EUR/MWh
# P&L at near expiry depends on remaining time value of far option
# Max profit near K at the near-term expiry date
```

You can also pass contract codes:
```python
s = calendar_spread(F=35.0, K=35.0, T_far="TTFU26", T_near="TTFM26", r=0.03, sigma=0.50)
```

---

### Structure 10 — Ratio Spread

**View:** "I'm mildly bullish and want a cheap or zero-cost structure."  
**Caution:** Unlimited loss if price rallies far above the short strike.

```python
from structures_ttf import ratio_spread

s = ratio_spread(F=35.0, K_lo=35.0, K_hi=38.0, T=0.25, r=0.03, sigma=0.50, ratio=2)
# Net premium: −1.14 EUR/MWh  (CREDIT received)
# Max profit:  4.14 EUR/MWh at F_T = 38
# Max loss:    unlimited if F_T >> 38  (you are short 2 calls vs long 1)
```

### Displaying Results

```python
from structures_ttf import straddle, print_summary

s = straddle(F=35.0, K=35.0, T=0.25, r=0.03, sigma=0.50)
print_summary(s)

# Plotting P&L at expiry
import matplotlib.pyplot as plt
prices = [pt[0] for pt in s.pnl_at_expiry]
pnls   = [pt[1] for pt in s.pnl_at_expiry]
plt.plot(prices, pnls)
plt.axhline(0, color='gray', linestyle='--')
plt.xlabel("TTF at Expiry (EUR/MWh)")
plt.ylabel("P&L (EUR/MWh)")
plt.title("Straddle P&L at Expiry")
plt.show()
```

---

## 6. Module 3 — TTF/HH Spread Option

**File:** `ttf_hh_spread.py`

### 6.1 The TTF / Henry Hub Basis

**Henry Hub (HH)** is the North American natural gas benchmark, quoted in **USD/MMBtu**.

The TTF/HH basis measures the cost of shipping LNG from the US to Europe. When TTF is much higher than HH (converted to the same unit), it is profitable to export LNG from the US to Europe, and LNG tankers flow accordingly — compressing the spread over time.

**Unit conversion:**
```
1 MWh = 3.412 MMBtu

TTF (USD/MMBtu) = TTF (EUR/MWh) × EUR/USD rate ÷ 3.412
```

Example: TTF = 30 EUR/MWh, EUR/USD = 1.08  
→ TTF = 30 × 1.08 ÷ 3.412 = **9.50 USD/MMBtu**  
→ Spread TTF − HH = 9.50 − 3.00 = **6.50 USD/MMBtu** (LNG arbitrage window open)

### 6.2 Margrabe's Model

The spread option is priced using **Margrabe's formula** (1978), which values the option to exchange one asset for another:

- **Call:** max(F_TTF_usd − F_HH, 0) — benefits if TTF stays above HH
- **Put:**  max(F_HH − F_TTF_usd, 0) — benefits if HH closes the gap with TTF

The key parameter is the **spread volatility**:
```
σ_spread = √(σ_TTF² + σ_HH² − 2ρ × σ_TTF × σ_HH)
```

Where **ρ** is the correlation between TTF and HH price movements.

### 6.3 Pricing a Spread Option

```python
from ttf_hh_spread import spread_price, print_summary

result = spread_price(
    F_ttf_eur = 30.0,    # TTF forward in EUR/MWh
    F_hh      = 3.0,     # HH forward in USD/MMBtu
    fx_eurusd = 1.08,    # EUR/USD rate
    T         = 0.5,     # years to expiry
    r_usd     = 0.045,   # USD risk-free rate
    sigma_ttf = 0.60,    # TTF vol (60%)
    sigma_hh  = 0.50,    # HH vol (50%)
    rho       = 0.35,    # TTF/HH correlation
    option_type = "call"
)

print(f"Premium: {result.price:.4f} USD/MMBtu")
print(f"Premium: {result.price_eur:.4f} EUR/MWh")
print_summary(result)
```

### 6.4 Reading the Greeks

| Greek | Meaning | Typical Value |
|-------|---------|---------------|
| **Δ_TTF** | Change in option value per $1/MMBtu move in TTF | 0 to +1 (call) |
| **Δ_HH** | Change in option value per $1/MMBtu move in HH | −1 to 0 (call) |
| **Vega_TTF** | Sensitivity to TTF vol | Positive for long spread |
| **Vega_HH** | Sensitivity to HH vol | Positive for long spread |
| **Vega_ρ** | Sensitivity to correlation | **Negative** — higher correlation = cheaper spread option |

> **Key insight:** If TTF and HH move perfectly together (ρ = 1), the spread never changes and the option is worth almost nothing. Lower correlation → more spread volatility → more expensive option.

### 6.5 Implied Correlation

The implied correlation is the correlation ρ that, given observed vols, matches a market spread option price. It is the market's view of how linked the two markets are.

```python
from ttf_hh_spread import implied_correlation, ttf_eur_to_usd

F_ttf_usd = ttf_eur_to_usd(30.0, fx_eurusd=1.08)   # 9.50 USD/MMBtu

rho = implied_correlation(
    market_price = 0.48,    # observed market price in USD/MMBtu
    F_ttf        = F_ttf_usd,
    F_hh         = 3.50,
    T            = 0.5,
    r            = 0.045,
    sigma_ttf    = 0.60,
    sigma_hh     = 0.50,
    option_type  = "call"
)
print(f"Implied correlation: {rho:.3f}")
```

### 6.6 Correlation Sensitivity Table

```python
from ttf_hh_spread import rho_sensitivity, ttf_eur_to_usd

F_ttf_usd = ttf_eur_to_usd(30.0, 1.08)

table = rho_sensitivity(F_ttf_usd, F_hh=3.0, T=0.5, r=0.045,
                        sigma_ttf=0.60, sigma_hh=0.50)
for rho, price in table:
    print(f"  ρ = {rho:+.1f}  →  {price:.4f} USD/MMBtu")
```

---

## 7. The Dashboard

The React dashboard is located in the `/dashboard` folder.

### Start the Development Server

```bash
cd dashboard
npm install
npm run dev
# Opens at http://localhost:5173
```

### Features

| Tab | What It Does |
|-----|-------------|
| **Pricer** | Price a single call or put, view full Greeks |
| **Vol Surface** | 3D implied vol surface across strikes and tenors |
| **Greeks Chart** | Delta, Gamma, Vega vs strike for Black-76 and Bachelier |
| **Comparison** | Side-by-side B76 vs Bachelier prices across strikes |

### Excel Export

Click **Export to Excel** in any tab to download a `.xlsx` file with prices and Greeks.

---

## 8. Glossary

| Term | Definition |
|------|-----------|
| **ATM (At the Money)** | Option whose strike equals the current forward price |
| **Bachelier model** | Normal-distribution option pricing model — handles negative prices |
| **Basis** | Price difference between two related markets (e.g. TTF − HH) |
| **Black-76** | Lognormal option pricing model for futures, standard in energy markets |
| **Call option** | Right to buy the underlying at the strike price |
| **Delta (Δ)** | Rate of change of option price with respect to the forward price |
| **Expiry / Expiration** | Date on which the option can last be exercised |
| **Forward price (F)** | Price agreed today for delivery at a future date |
| **Gamma (Γ)** | Rate of change of delta; acceleration of option value |
| **Greeks** | Collective name for option price sensitivities (Δ, Γ, ν, Θ, ρ) |
| **Henry Hub (HH)** | US natural gas benchmark at the Henry Hub, Louisiana; USD/MMBtu |
| **Implied volatility** | The vol that, plugged into the pricing model, reproduces the market price |
| **Intrinsic value** | max(F − K, 0) for a call; the in-the-money amount |
| **ITM (In the Money)** | Call with F > K; put with K > F — has positive intrinsic value |
| **LNG** | Liquefied Natural Gas — enables TTF/HH arbitrage via shipping |
| **Lognormal** | Statistical distribution used in Black-76; prices can't go negative |
| **Margrabe model** | Prices the option to exchange one asset for another (spread option) |
| **MMBtu** | Million British Thermal Units — US energy unit (1 MWh = 3.412 MMBtu) |
| **MWh** | Megawatt-hour — European energy unit for gas pricing |
| **Normal distribution** | Bell-curve distribution used in Bachelier model |
| **OTM (Out of the Money)** | Call with F < K; put with K > F — zero intrinsic value |
| **Premium** | Price paid to buy an option (upfront, non-refundable) |
| **Put option** | Right to sell the underlying at the strike price |
| **Put-call parity** | Mathematical relationship: C − P = e^(−rT)(F − K) |
| **Rho (ρ)** | Sensitivity of option price to interest rate changes |
| **Risk Reversal** | Long call + short put (or vice versa); directional structure |
| **Spread option** | Option on the difference between two asset prices |
| **Strike (K)** | The fixed price at which the option can be exercised |
| **Theta (Θ)** | Time decay — option value lost per calendar day |
| **Time value** | Option premium above intrinsic value; reflects uncertainty |
| **TTF** | Title Transfer Facility — European gas hub (Netherlands) |
| **Vega (ν)** | Sensitivity of option price to a change in implied volatility |
| **Vol surface** | Grid of implied vols across strikes and maturities |
| **Volatility (σ)** | Annualised measure of price uncertainty; key driver of option price |

---

*Generated for the TTF Options Pricing project. All prices in EUR/MWh unless stated.*
