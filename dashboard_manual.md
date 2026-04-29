# Dashboard Manual — TTF Options Pricer

A practical guide to using `dashboard_jupyter.ipynb` for pricing TTF natural-gas
options and building option structures.

---

## SECTION 1 — Getting Started

### 1.1 Prerequisites

Install the following Python packages before opening the notebook. Python 3.10
or newer is recommended.

```bash
pip install numpy scipy pandas matplotlib ipywidgets plotly
```

| Package        | Why it is needed                                   |
| -------------- | -------------------------------------------------- |
| `numpy`        | Array maths used by the pricers and grids          |
| `scipy`        | Normal CDF/PDF and root finders for implied vol    |
| `pandas`       | Tabular display of inputs, prices and Greeks       |
| `matplotlib`   | Static P&L charts                                  |
| `ipywidgets`   | Interactive sliders, dropdowns and number boxes    |
| `plotly`       | Interactive P&L curves and the vol surface         |

If you use JupyterLab, also enable the widgets extension (modern Jupyter does
this automatically):

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

### 1.2 Opening `dashboard_jupyter.ipynb`

#### Option A — Classic Jupyter

1. Open a terminal in the project folder (`Options_pricing`).
2. Run:
   ```bash
   jupyter notebook dashboard_jupyter.ipynb
   ```
3. Your browser opens the notebook automatically.

#### Option B — JupyterLab

```bash
jupyter lab dashboard_jupyter.ipynb
```

#### Option C — VS Code

1. Install the **Python** and **Jupyter** extensions from the VS Code
   marketplace.
2. Open the project folder via *File → Open Folder*.
3. Click `dashboard_jupyter.ipynb` in the file explorer.
4. In the top-right corner of the notebook, select your Python interpreter
   (the one where you installed the prerequisites above).

### 1.3 Required files in the same folder

The notebook imports two local modules. They **must** sit next to the
notebook (same directory):

```
Options_pricing/
├── dashboard_jupyter.ipynb     ← the dashboard
├── black76_ttf.py              ← Black-76 & Bachelier pricers + Greeks
└── ttf_market_data.py          ← TTF contract calendar, market data helpers
```

If either file is missing or renamed, the first cell will fail with
`ModuleNotFoundError: No module named 'black76_ttf'` (or `ttf_market_data`).
Move them next to the notebook and re-run.

The `structures_ttf.py` module is also required for the **Structures** tab.
It must live in the same folder.

### 1.4 Running all cells

Once the notebook is open:

- **Classic Jupyter / Lab** — menu *Cell → Run All* (or *Run → Run All Cells*).
  Keyboard shortcut: `Esc` then `0 0` to restart and `Shift+Enter` repeatedly,
  or use *Kernel → Restart & Run All*.
- **VS Code** — click **Run All** at the top of the notebook, or press
  `Ctrl+Shift+P` and type *Notebook: Run All*.

After the last cell finishes, the dashboard appears inline: select a tab
(Pricer / Structures / Vol Surface) and start moving the sliders. Outputs
update live — no need to re-run cells.

---

## SECTION 2 — Pricer Tab

The Pricer tab values a single European option on a TTF future. It shows the
**Call price**, **Put price** and the full set of Greeks under both
**Black-76** and **Bachelier**.

### 2.1 Inputs explained — with example

We illustrate every input with the same running example:

> **Forward = 30 EUR/MWh, Strike = 32 EUR/MWh, Vol = 50 %, T = 30 days, r = 2 %.**

| Input             | Meaning                                                        | Example value |
| ----------------- | -------------------------------------------------------------- | ------------- |
| **Forward (F)**   | Quoted price today of the underlying TTF future, in EUR/MWh    | `30`          |
| **Strike (K)**    | Exercise price of the option, in EUR/MWh                       | `32`          |
| **Volatility σ**  | Black-76 lognormal volatility, expressed in **% per year**     | `50` (= 50 %) |
| **Maturity T**    | Time to option expiry. Enter **days** — the dashboard converts to years (`T_years = T_days / 365`) | `30` days |
| **Risk-free r**   | Continuously compounded discount rate, in **% per year**       | `2` (= 2 %)   |
| **Option type**   | `call` or `put`. Drives which Greeks block is displayed        | `call`        |
| **Model**         | Primary model: `Black-76` (lognormal) or `Bachelier` (normal)  | `Black-76`    |

Notes:

- Vol is entered in **percent**, not decimal: type `50`, not `0.50`.
- For the Bachelier model the input is a separate **normal** vol σₙ in
  **EUR/MWh per √year**, not a percentage.
- A 30-day option has `T = 30 / 365 ≈ 0.0822` year. Use 252 only if you have
  pre-agreed business-day conventions; the dashboard uses calendar days.

### 2.2 Black-76 vs Bachelier — when to use which

Both models price European options on **futures** with the same payoff at
expiry, but they assume different distributions for the forward.

| Model         | Underlying assumption        | Best for…                                                                                  |
| ------------- | ---------------------------- | ------------------------------------------------------------------------------------------ |
| **Black-76**  | Forward is **lognormal**     | Most natural-gas options, all "normal" market regimes where prices stay strictly positive. Industry standard for TTF. |
| **Bachelier** | Forward is **normal**        | Markets where prices can go to zero or negative (e.g. spreads, occasional power, calendar spread options), or when strikes are very far OTM and lognormal vol blows up. |

Practical rule of thumb:

- **Outright TTF options** → use **Black-76**.
- **TTF–HH spread or other spread/calendar options** → use **Bachelier**.
- **Sanity check** — for at-the-money short-dated options the two prices
  should agree to within a few cents; if they diverge wildly you have an
  input error (vol unit, T unit, wrong F or K).

### 2.3 Reading the output

#### Prices

| Field         | What it tells you                                             |
| ------------- | ------------------------------------------------------------- |
| **Call price**| Premium of a European call, in EUR/MWh, today                 |
| **Put price** | Premium of a European put, in EUR/MWh, today                  |
| Intrinsic     | `max(F − K, 0)` for calls, `max(K − F, 0)` for puts           |

Multiply by the contract size (e.g. **720 MWh** for a typical TTF monthly:
24 h × 30 days) to get the EUR premium of one lot.

#### Greeks

For the option type you selected, the dashboard prints:

| Greek           | Reads as                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------- |
| **Δ Delta**     | Change in option value for a **+1 EUR/MWh** move in the forward. Calls: 0 → +1. Puts: −1 → 0.     |
| **Γ Gamma**     | Change in delta per +1 EUR/MWh in F. Highest near ATM, decays with time.                          |
| **ν Vega**      | Change in option value per **+1.00 (= 100 %)** of vol. **Divide by 100** for a "per vol-point" sensitivity. |
| **Θ Theta/day** | Change in option value over **one calendar day** (already daily — no need to divide by 365).      |
| **ρ Rho**       | Change in option value per **+1 percentage point** of the risk-free rate.                         |
| **Vanna**       | `∂Δ/∂σ = ∂Vega/∂F`. Tells you how delta moves when vol moves.                                     |
| **Volga**       | `∂²V/∂σ²`. Vol convexity — useful for vol-of-vol risk on smile structures.                        |

A side-by-side table compares Black-76 and Bachelier for both call and put,
plus a put-call parity check (`C − P` vs `e^(−rT)·(F − K)`). The error column
should be ~`1e-12` — anything bigger means a bug.

### 2.4 Worked example — TTF Jun-26 call

Suppose today is 29 April 2026 and you want to price a **TTF Jun-26 30-day
call** struck at 32:

1. Pull the Jun-26 forward from your screen — say **F = 30 EUR/MWh**.
2. Strike **K = 32 EUR/MWh** (2 EUR OTM).
3. Implied vol from the broker for the Jun-26 ATM contract — say **50 %**.
4. Days to expiry — Jun-26 options expire on the last business day before the
   delivery month, ≈ **30 days** from today.
5. Risk-free rate — use **r = 2 %** (€STR-flat assumption).
6. Set option type = `call`, model = `Black-76`.

Run the dashboard. You should see (Black-76):

- **Call price ≈ 0.86 EUR/MWh**
- **Delta ≈ +0.36** (slightly OTM, less than 50 % delta)
- **Gamma ≈ 0.085**
- **Vega ≈ 0.034 / vol-point** (≈ 3.4 EUR/MWh per 100 % vol)
- **Theta ≈ −0.014 / day**

For one TTF Jun-26 lot (720 MWh): premium ≈ `0.86 × 720 ≈ 619 EUR`. If vol
moves +2 vol-points overnight, your option gains ≈ `0.034 × 2 × 720 ≈ 49 EUR`,
less ≈ `0.014 × 720 ≈ 10 EUR` of theta decay.

---

## SECTION 3 — Structures Tab

The Structures tab builds 10 standard option structures from individual
Black-76 legs. For each structure you get:

- a **leg-by-leg breakdown** (sign, qty, strike, type, unit price, Greeks),
- **net price** and **net Greeks**,
- a **payoff at expiry** chart with **break-evens** marked.

### 3.1 The 10 structures in plain words

We use **F = 30 EUR/MWh** and **σ = 50 %** in every example below, with
T = 30 days unless stated otherwise. Strikes are in EUR/MWh.

| # | Structure          | Plain-English description                                                                 | Default example legs                                  |
|---|--------------------|--------------------------------------------------------------------------------------------|-------------------------------------------------------|
| 1 | **Straddle**       | Buy call + buy put, **same strike**. Long volatility — pays if the market moves a lot in either direction. | Long 30 call + long 30 put                            |
| 2 | **Strangle**       | Buy OTM put + buy OTM call. Cheaper than a straddle; needs a bigger move to pay off.       | Long 28 put + long 32 call                            |
| 3 | **Bull call spread**| Buy a lower-strike call, sell a higher-strike call. Bullish, **capped** upside, **cheaper** than the call alone. | Long 30 call − short 32 call                          |
| 4 | **Bear put spread**| Buy a higher-strike put, sell a lower-strike put. Bearish, **capped** downside.            | Long 32 put − short 28 put                            |
| 5 | **Butterfly**      | Long–short–long around a centre strike (1×−2×+1× calls or puts). Bets that the price will **pin** the centre at expiry. | Long 28 call − 2× short 30 call + long 32 call        |
| 6 | **Condor**         | Like a butterfly but with **four** strikes — flat profit zone between the inner strikes.   | Long 26 / short 28 / short 32 / long 34 calls         |
| 7 | **Collar**         | On a long forward position: buy a put + sell a call. Caps both downside and upside; often **zero-cost**. | Long F + long 28 put − short 32 call                  |
| 8 | **Risk reversal**  | Sell a put, buy a call (or vice-versa). Synthetic long forward, sensitive to skew.         | Short 28 put + long 32 call                           |
| 9 | **Calendar spread**| Sell short-dated option, buy longer-dated option, **same strike**. Long vega, plays the term structure of vol. | Short 30 call (T = 30 d) + long 30 call (T = 90 d) |
| 10| **Ratio spread**   | Buy 1 ATM, sell N OTM (e.g. 1×2). Cheap or zero-cost upside but **unlimited** loss past the short strike. | Long 30 call − 2× short 32 call                       |

### 3.2 Reading the P&L-at-expiry chart

The chart plots **profit/loss in EUR/MWh as a function of the forward at
expiry F_T**, after netting the premium paid/received today.

How to read it:

- **Horizontal axis** — forward price at expiry, scanned over a wide range
  around the current F.
- **Vertical axis** — net P&L per MWh: `payoff(F_T) − net premium paid`
  (or `+ net premium received` for a short structure).
- **Zero line** — drawn for reference. Any crossing is a **break-even**.
- **Break-evens** — points where the curve crosses zero are listed below the
  chart. They tell you the prices the market needs to reach by expiry for the
  structure to start making money.
- **Max profit / max loss** — for capped structures (spreads, butterflies,
  condors) read them off the flat plateaus.
- The chart is **payoff at expiry only** — it ignores time value before
  expiry. Use the Greeks panel to understand intermediate behaviour.

### 3.3 Worked example — straddle on TTF Jun-26

Goal: bet that TTF Jun-26 will move sharply (in either direction) over the
next 30 days, e.g. ahead of a storage report.

Inputs:

- F = **30** EUR/MWh, σ = **50 %**, T = **30 days**, r = **2 %**.
- Structure = **Straddle**, strike **K = 30**.

Steps in the dashboard:

1. Open the **Structures** tab.
2. Select **Straddle** in the structure dropdown.
3. Set `K = 30`. Leave F, σ, T, r as above.
4. The leg table shows:
   - Long 1× **30 call**, unit price ≈ **1.71** EUR/MWh
   - Long 1× **30 put**,  unit price ≈ **1.71** EUR/MWh
   - **Net premium ≈ 3.42 EUR/MWh** (paid).
5. **Net Greeks**: Δ ≈ 0 (delta-neutral at inception), Γ large positive, Vega
   large positive, Θ negative (you bleed time value every day).
6. The **P&L-at-expiry** chart is a V-shape with the vertex at F_T = 30 and
   minimum value `−3.42` EUR/MWh (your max loss = premium paid).
7. **Break-evens** ≈ `30 ± 3.42` → `26.58` and `33.42` EUR/MWh.

Interpretation: you make money only if Jun-26 closes **below 26.58** or
**above 33.42** at expiry. Inside that band, you lose part of the premium;
exactly at 30 you lose the whole 3.42 EUR/MWh. For one lot (720 MWh) max
loss ≈ `3.42 × 720 ≈ 2 460 EUR`. Each EUR/MWh past a break-even adds 720 EUR
of profit.

If you instead expected only an **upside** move, switch to a **Bull call
spread** (long 30 call / short 32 call) — same view, much cheaper, with
capped profit at `K_hi − K_lo − net premium = 2 − net premium`.
