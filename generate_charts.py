"""Generate the example chart images referenced from dashboard_manual.md.

Run from the project root:

    python generate_charts.py

All charts are written to ./charts/ (PNG, dark theme).
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3D projection)

import black76_ttf as b76
import structures_ttf as structs
import ttf_hh_spread as sp


plt.style.use("dark_background")

OUT_DIR = Path(__file__).parent / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Shared TTF Jun-26 parameters
F = 30.0
K_ATM = 30.0
SIGMA = 0.50
T_DAYS = 30
T = T_DAYS / 365.0
R = 0.02

CALL_COLOUR = "#3b82f6"   # blue
PUT_COLOUR = "#ef4444"    # red
ATM_COLOUR = "#9ca3af"    # grey
BE_COLOUR = "#facc15"     # yellow
POS_COLOUR = "#10b981"    # green
NEG_COLOUR = "#ef4444"    # red


def _save(fig: plt.Figure, name: str) -> None:
    path = OUT_DIR / name
    fig.savefig(path, dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# 1. Pricer chart — Call & Put prices vs strike
# ---------------------------------------------------------------------------

def chart_pricer() -> None:
    Ks = np.linspace(20.0, 40.0, 121)
    calls = np.array([b76.b76_call(F, K, T, R, SIGMA) for K in Ks])
    puts = np.array([b76.b76_put(F, K, T, R, SIGMA) for K in Ks])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(Ks, calls, color=CALL_COLOUR, lw=2.2, label="Black-76 Call")
    ax.plot(Ks, puts, color=PUT_COLOUR, lw=2.2, label="Black-76 Put")
    ax.axvline(F, color=ATM_COLOUR, ls="--", lw=1.0,
               label=f"ATM-DN strike (F = {F:.0f})")
    ax.set_xlabel("Strike (EUR/MWh)")
    ax.set_ylabel("Option price (EUR/MWh)")
    ax.set_title(
        "TTF Jun-26 — Black-76 Call & Put prices vs strike\n"
        f"F = {F:.0f} EUR/MWh,  σ = {SIGMA*100:.0f} %,  "
        f"T = {T_DAYS} days,  r = {R*100:.0f} %"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center")
    _save(fig, "pricer_example.png")


# ---------------------------------------------------------------------------
# 2. Greeks chart — Delta and Gamma vs strike
# ---------------------------------------------------------------------------

def chart_greeks() -> None:
    Ks = np.linspace(20.0, 40.0, 121)
    delta_call = np.array([b76.b76_greeks(F, K, T, R, SIGMA, "call").delta
                           for K in Ks])
    delta_put = np.array([b76.b76_greeks(F, K, T, R, SIGMA, "put").delta
                          for K in Ks])
    gamma = np.array([b76.b76_gamma(F, K, T, R, SIGMA) for K in Ks])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(Ks, delta_call, color=CALL_COLOUR, lw=2.2, label="Call Δ")
    ax1.plot(Ks, delta_put, color=PUT_COLOUR, lw=2.2, label="Put Δ")
    ax1.axhline(0.0, color="#6b7280", lw=0.6)
    ax1.axvline(F, color=ATM_COLOUR, ls="--", lw=1.0,
                label=f"ATM (F = {F:.0f})")
    ax1.set_ylabel("Delta")
    ax1.set_title(
        "TTF Jun-26 — Greeks vs strike\n"
        f"F = {F:.0f}, σ = {SIGMA*100:.0f} %, T = {T_DAYS} days, "
        f"r = {R*100:.0f} %"
    )
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="center right")

    ax2.plot(Ks, gamma, color=POS_COLOUR, lw=2.2, label="Gamma")
    ax2.axvline(F, color=ATM_COLOUR, ls="--", lw=1.0)
    ax2.set_xlabel("Strike (EUR/MWh)")
    ax2.set_ylabel("Gamma")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right")

    fig.tight_layout()
    _save(fig, "greeks_example.png")


# ---------------------------------------------------------------------------
# 3. Structures chart — Straddle P&L at expiry
# ---------------------------------------------------------------------------

def chart_straddle() -> None:
    res = structs.straddle(F, K=K_ATM, T=T, r=R, sigma=SIGMA)
    pnl = np.array(res.pnl_at_expiry)
    xs, ys = pnl[:, 0], pnl[:, 1]

    # Trim to the requested 20–40 window
    mask = (xs >= 20.0) & (xs <= 40.0)
    xs, ys = xs[mask], ys[mask]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(xs, ys, color=CALL_COLOUR, lw=2.2,
            label="Straddle P&L at expiry")
    ax.fill_between(xs, ys, 0, where=ys >= 0,
                    color=POS_COLOUR, alpha=0.20)
    ax.fill_between(xs, ys, 0, where=ys < 0,
                    color=NEG_COLOUR, alpha=0.20)
    ax.axhline(0.0, color="#9ca3af", lw=0.8)
    ax.axvline(F, color=ATM_COLOUR, ls="--", lw=0.9,
               label=f"F = K = {F:.0f}")

    y_top = float(ys.max())
    for be in res.breakevens:
        if 20.0 <= be <= 40.0:
            ax.axvline(be, color=BE_COLOUR, ls=":", lw=1.4)
            ax.text(be, y_top * 0.92, f"  BE {be:.2f}",
                    color=BE_COLOUR, fontsize=9, va="top")

    ax.set_xlabel("Spot price at expiry (EUR/MWh)")
    ax.set_ylabel("P&L (EUR/MWh)")
    ax.set_title(
        "Straddle on TTF Jun-26 — P&L at expiry\n"
        f"F = K = {F:.0f},  σ = {SIGMA*100:.0f} %,  "
        f"T = {T_DAYS} days  |  net premium = {res.price:.3f} EUR/MWh"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center")
    _save(fig, "straddle_example.png")


# ---------------------------------------------------------------------------
# 4. Vol Surface chart — TTF downside-skewed surface
# ---------------------------------------------------------------------------

def chart_vol_surface() -> None:
    # Pillar maturities: 1M, 3M, 6M, 12M
    Ts = np.array([1 / 12, 3 / 12, 6 / 12, 12 / 12])
    Ks = np.linspace(20.0, 40.0, 41)
    F0 = 30.0

    # ATM term-structure: ~50 % at 1M, ~45 % at 3M-6M, decaying toward 40 % at 12M+
    sigma_inf = 0.40
    delta_sigma = 0.12
    kappa = 1.5

    # Smile in log-moneyness m = ln(K/F)/sqrt(T): negative slope (downside skew)
    skew = -0.10
    wings = 0.10

    K_mesh, T_mesh = np.meshgrid(Ks, Ts)
    atm = sigma_inf + delta_sigma * np.exp(-kappa * T_mesh)
    m = np.log(K_mesh / F0) / np.sqrt(T_mesh)
    vol = atm + skew * m + wings * m**2
    vol = np.clip(vol, 0.20, 1.20)

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#0f0f1a")
    fig.patch.set_facecolor("#0f0f1a")

    surf = ax.plot_surface(
        K_mesh, T_mesh, vol * 100.0,
        cmap="viridis", edgecolor="none", alpha=0.95,
        rstride=1, cstride=1, antialiased=True,
    )

    # Tenor ticks
    ax.set_yticks(Ts)
    ax.set_yticklabels(["1M", "3M", "6M", "12M"])

    ax.set_xlabel("Strike (EUR/MWh)")
    ax.set_ylabel("Maturity")
    ax.set_zlabel("Implied vol σ (%)")
    ax.set_title(
        "TTF implied volatility surface — downside skew\n"
        "1M / 3M / 6M / 12M  |  F = 30 EUR/MWh"
    )
    cb = fig.colorbar(surf, shrink=0.6, aspect=15, pad=0.10)
    cb.set_label("σ (%)")
    ax.view_init(elev=24, azim=-58)
    _save(fig, "vol_surface_example.png")


# ---------------------------------------------------------------------------
# 5. TTF/HH Spread chart — call P&L at expiry
# ---------------------------------------------------------------------------

def chart_spread() -> None:
    F_ttf_eur = 30.0
    F_hh = 3.0
    fx = 1.08
    sigma_ttf = 0.50
    sigma_hh = 0.45
    rho = 0.6
    T_sp = 0.5
    r_usd = 0.04

    F_ttf_usd = sp.ttf_eur_to_usd(F_ttf_eur, fx)
    res = sp.spread_price(
        F_ttf_eur=F_ttf_eur, F_hh=F_hh, fx_eurusd=fx,
        T=T_sp, r_usd=r_usd,
        sigma_ttf=sigma_ttf, sigma_hh=sigma_hh, rho=rho,
        option_type="call",
    )
    premium = res.price  # USD/MMBtu

    # Vary F_TTF at expiry over a wide range; HH is held fixed (long spread call)
    F_ttf_usd_grid = np.linspace(F_ttf_usd * 0.30, F_ttf_usd * 1.80, 240)
    spread_T = F_ttf_usd_grid - F_hh
    payoff = np.maximum(spread_T, 0.0)
    pnl = payoff - premium
    breakeven = premium  # spread value where P&L = 0
    current_spread = F_ttf_usd - F_hh

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(spread_T, pnl, color=CALL_COLOUR, lw=2.2,
            label="Long call — P&L at expiry")
    ax.fill_between(spread_T, pnl, 0, where=pnl >= 0,
                    color=POS_COLOUR, alpha=0.20)
    ax.fill_between(spread_T, pnl, 0, where=pnl < 0,
                    color=NEG_COLOUR, alpha=0.20)

    ax.axhline(0.0, color="#9ca3af", lw=0.8)
    ax.axvline(0.0, color="#6b7280", ls=":", lw=0.8)
    ax.axvline(current_spread, color=ATM_COLOUR, ls="--", lw=0.9,
               label=f"Current spread = {current_spread:.2f}")
    ax.axvline(breakeven, color=BE_COLOUR, ls=":", lw=1.4,
               label=f"Breakeven = {breakeven:.2f}")

    ax.set_xlabel("Spread TTF − HH at expiry (USD/MMBtu)")
    ax.set_ylabel("P&L (USD/MMBtu)")
    ax.set_title(
        "TTF/HH spread call — P&L at expiry\n"
        f"TTF = {F_ttf_eur:.0f} EUR/MWh ({F_ttf_usd:.2f} USD/MMBtu),  "
        f"HH = {F_hh:.2f},  ρ = {rho:.1f},  T = 6 m  |  "
        f"premium = {premium:.2f} USD/MMBtu"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    _save(fig, "spread_example.png")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Generating charts in {OUT_DIR} …")
    chart_pricer()
    chart_greeks()
    chart_straddle()
    chart_vol_surface()
    chart_spread()
    print("Done.")


if __name__ == "__main__":
    main()
