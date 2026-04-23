"""TTF Natural Gas Options — Streamlit dashboard.

Tabs: Pricer, Structures, Vol Surface.

Run with:
    streamlit run dashboard_ttf.py

Requires:
    pip install streamlit pandas openpyxl plotly
    (plus the project's own deps: numpy, scipy, pandas, requests)
"""

from __future__ import annotations

import json
import math
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from black76_ttf import (
    b76_call, b76_put, b76_greeks,
    bach_call, bach_put, bach_greeks,
    b76_implied_vol, bach_implied_vol,
)
import structures_ttf as structs_mod


# ---------------------------------------------------------------------------
# Page configuration + dark theme
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="TTF Options Pricer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      /* Dark palette */
      html, body, [class*="css"] { color: #cbd5e1; }
      .stApp { background: #0a0a14; }
      section[data-testid="stSidebar"] { background: #0f0f1a; border-right: 1px solid #1e1e32; }

      /* Typography */
      h1, h2, h3 { color: #f1f5f9 !important; }
      h1 { border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }

      /* Metric cards */
      [data-testid="stMetric"] {
        background: #161625;
        border: 1px solid #2a2a42;
        padding: 12px 16px;
        border-radius: 10px;
      }
      [data-testid="stMetricLabel"] { color: #94a3b8 !important; }
      [data-testid="stMetricValue"] { color: #f1f5f9 !important; }

      /* Tab bar */
      .stTabs [data-baseweb="tab-list"] { gap: 4px; }
      .stTabs [data-baseweb="tab"] {
        background: #161625; border-radius: 8px 8px 0 0; color: #94a3b8;
        padding: 10px 20px;
      }
      .stTabs [aria-selected="true"] {
        background: #1e1e32 !important; color: #f1f5f9 !important;
        border-bottom: 2px solid #3b82f6 !important;
      }

      /* Tables */
      [data-testid="stDataFrame"] { background: #161625; border-radius: 8px; }

      /* Buttons */
      .stDownloadButton button {
        background: #1d4ed8; color: #f1f5f9; border: none;
        border-radius: 8px; padding: 8px 16px; font-weight: 600;
      }
      .stDownloadButton button:hover { background: #3b82f6; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    """Serialise a dict of DataFrames to an .xlsx byte stream."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return buf.getvalue()


def moneyness_label(F: float, K: float, option_type: str) -> str:
    if abs(F - K) / max(F, 1e-6) < 0.005:
        return "ATM"
    if option_type == "call":
        return "ITM" if F > K else "OTM"
    return "ITM" if F < K else "OTM"


# ---------------------------------------------------------------------------
# Sidebar — market inputs
# ---------------------------------------------------------------------------

st.sidebar.title("Market Inputs")

F = st.sidebar.number_input(
    "Forward F (EUR/MWh)",
    min_value=-20.0, max_value=250.0, value=30.0, step=0.5,
    help="TTF futures / forward price",
)
K = st.sidebar.number_input(
    "Strike K (EUR/MWh)",
    min_value=0.0, max_value=250.0, value=30.0, step=0.5,
)
T_days = st.sidebar.slider(
    "Maturity (calendar days)",
    min_value=1, max_value=1825, value=90, step=1,
    help="Time to expiry in calendar days (ACT/365)",
)
T = T_days / 365.0

r_pct = st.sidebar.slider(
    "Risk-free rate r (%)",
    min_value=0.0, max_value=10.0, value=2.0, step=0.05,
)
r = r_pct / 100.0

sigma_pct = st.sidebar.slider(
    "Lognormal vol σ (Black-76, %)",
    min_value=1.0, max_value=250.0, value=50.0, step=1.0,
)
sigma = sigma_pct / 100.0

sigma_n = st.sidebar.number_input(
    "Normal vol σₙ (Bachelier, EUR/MWh)",
    min_value=0.1, max_value=50.0, value=8.0, step=0.1,
    help="Used by Bachelier; typical rule-of-thumb σₙ ≈ F·σ for ATM",
)

option_type = st.sidebar.radio(
    "Option type", ["call", "put"], horizontal=True,
)

model = st.sidebar.selectbox(
    "Primary model",
    ["Black-76", "Bachelier"],
    help="Black-76 for F > ~5 EUR/MWh ; Bachelier when prices may go negative or very low",
)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("⚡ TTF Natural Gas Options — Pricer")
st.caption(
    f"Forward **{F:.2f} EUR/MWh** · Strike **{K:.2f} EUR/MWh** · "
    f"Maturity **{T_days} days** ({T:.4f} y) · "
    f"r **{r_pct:.2f} %** · σ **{sigma_pct:.0f} %** · σₙ **{sigma_n:.1f} EUR/MWh** · "
    f"**{option_type.upper()}** · {moneyness_label(F, K, option_type)}"
)


# ---------------------------------------------------------------------------
# Tabs (only Pricer for now)
# ---------------------------------------------------------------------------

tab_pricer, tab_structures, tab_vol = st.tabs(["Pricer", "Structures", "Vol Surface"])

with tab_pricer:

    # ─── Pricing both models ─────────────────────────────────────────────
    b76_call_px = b76_call(F, K, T, r, sigma)
    b76_put_px  = b76_put(F, K, T, r, sigma)
    bach_call_px = bach_call(F, K, T, r, sigma_n)
    bach_put_px  = bach_put(F, K, T, r, sigma_n)

    b76_call_greeks = b76_greeks(F, K, T, r, sigma, "call")
    b76_put_greeks  = b76_greeks(F, K, T, r, sigma, "put")
    bach_call_greeks = bach_greeks(F, K, T, r, sigma_n, "call")
    bach_put_greeks  = bach_greeks(F, K, T, r, sigma_n, "put")

    # Primary model selection
    if model == "Black-76":
        primary_call_px, primary_put_px = b76_call_px, b76_put_px
        primary_call_g, primary_put_g = b76_call_greeks, b76_put_greeks
        primary_tag = "Black-76"
    else:
        primary_call_px, primary_put_px = bach_call_px, bach_put_px
        primary_call_g, primary_put_g = bach_call_greeks, bach_put_greeks
        primary_tag = "Bachelier"

    # ─── Price cards ─────────────────────────────────────────────────────
    st.subheader(f"{primary_tag} — Prices")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Call price", f"{primary_call_px:.4f} EUR/MWh",
                help="Option premium for a call")
    col2.metric("Put price",  f"{primary_put_px:.4f} EUR/MWh",
                help="Option premium for a put")

    intrinsic_call = max(F - K, 0.0)
    intrinsic_put  = max(K - F, 0.0)
    col3.metric("Intrinsic (call)", f"{intrinsic_call:.4f}")
    col4.metric("Intrinsic (put)",  f"{intrinsic_put:.4f}")

    # ─── Greeks (selected option_type) ───────────────────────────────────
    st.subheader(f"{primary_tag} — Greeks ({option_type.upper()})")

    g = primary_call_g if option_type == "call" else primary_put_g
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Δ Delta", f"{g.delta:+.4f}")
    c2.metric("Γ Gamma", f"{g.gamma:.6f}")
    c3.metric("ν Vega",  f"{g.vega:.4f}",
              help="Per 1 unit (100 %) change in vol — divide by 100 for '1 vol-point'")
    c4.metric("Θ Theta/day", f"{g.theta:+.4f}")

    c5, c6, c7, _ = st.columns(4)
    c5.metric("ρ Rho", f"{g.rho:+.6f}",
              help="Per 1 pp change in rate")
    c6.metric("Vanna", f"{g.vanna:+.6f}",
              help="∂Δ/∂σ = ∂ν/∂F")
    c7.metric("Volga (vomma)", f"{g.volga:+.6f}",
              help="∂²V/∂σ² — vol convexity")

    # ─── Side-by-side comparison Black-76 vs Bachelier ───────────────────
    st.subheader("Black-76 vs Bachelier — Side-by-side comparison")

    comp_rows = []
    for side in ("call", "put"):
        g76  = b76_call_greeks if side == "call" else b76_put_greeks
        gbch = bach_call_greeks if side == "call" else bach_put_greeks
        px76 = b76_call_px if side == "call" else b76_put_px
        pxb  = bach_call_px if side == "call" else bach_put_px

        comp_rows.append({
            "Side": side.capitalize(),
            "Black-76 price (EUR/MWh)": round(px76, 6),
            "Bachelier price (EUR/MWh)": round(pxb, 6),
            "Δ B76": round(g76.delta, 6),
            "Δ Bachelier": round(gbch.delta, 6),
            "Γ B76": round(g76.gamma, 8),
            "Γ Bachelier": round(gbch.gamma, 8),
            "ν B76": round(g76.vega, 6),
            "ν Bachelier": round(gbch.vega, 6),
            "Θ/day B76": round(g76.theta, 6),
            "Θ/day Bachelier": round(gbch.theta, 6),
        })
    comparison_df = pd.DataFrame(comp_rows)
    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

    # Implied vol (round-trip sanity)
    with st.expander("Implied volatility round-trip (sanity check)"):
        try:
            iv_b76 = b76_implied_vol(
                b76_call_px if option_type == "call" else b76_put_px,
                F, K, T, r, option_type,
            )
            st.write(f"**Black-76 implied vol** from own {option_type} price: "
                     f"`{iv_b76*100:.4f} %`  (input σ = {sigma*100:.2f} %)")
        except Exception as e:
            st.warning(f"Black-76 IV solver: {e}")

        try:
            iv_bach = bach_implied_vol(
                bach_call_px if option_type == "call" else bach_put_px,
                F, K, T, r, option_type,
            )
            st.write(f"**Bachelier implied normal vol** from own {option_type} price: "
                     f"`{iv_bach:.4f} EUR/MWh`  (input σₙ = {sigma_n:.2f})")
        except Exception as e:
            st.warning(f"Bachelier IV solver: {e}")

    # ─── Put-call parity check ───────────────────────────────────────────
    with st.expander("Put-call parity check"):
        df = math.exp(-r * T)
        pcp_rhs = df * (F - K)
        pcp_b76 = b76_call_px - b76_put_px
        pcp_bach = bach_call_px - bach_put_px
        pc_df = pd.DataFrame({
            "Model": ["Black-76", "Bachelier"],
            "C − P": [round(pcp_b76, 8), round(pcp_bach, 8)],
            "e^(−rT)·(F − K)": [round(pcp_rhs, 8), round(pcp_rhs, 8)],
            "Error": [f"{abs(pcp_b76 - pcp_rhs):.2e}",
                      f"{abs(pcp_bach - pcp_rhs):.2e}"],
        })
        st.dataframe(pc_df, hide_index=True, use_container_width=True)

    # ─── Inputs summary DataFrame (for Excel export) ─────────────────────
    inputs_df = pd.DataFrame({
        "Parameter": ["Forward (EUR/MWh)", "Strike (EUR/MWh)",
                      "Maturity (days)", "Maturity (years)",
                      "Risk-free rate (%)", "σ Black-76 (%)",
                      "σₙ Bachelier (EUR/MWh)", "Option type",
                      "Primary model"],
        "Value":     [F, K, T_days, round(T, 6), r_pct, sigma_pct,
                      sigma_n, option_type, primary_tag],
    })

    # Full Greeks matrix for export
    greeks_rows = []
    for side in ("call", "put"):
        g76  = b76_call_greeks if side == "call" else b76_put_greeks
        gbch = bach_call_greeks if side == "call" else bach_put_greeks
        for label, (v76, vbch) in {
            "Delta": (g76.delta, gbch.delta),
            "Gamma": (g76.gamma, gbch.gamma),
            "Vega":  (g76.vega,  gbch.vega),
            "Theta/day": (g76.theta, gbch.theta),
            "Rho":   (g76.rho,   gbch.rho),
            "Vanna": (g76.vanna, gbch.vanna),
            "Volga": (g76.volga, gbch.volga),
        }.items():
            greeks_rows.append({
                "Side": side.capitalize(),
                "Greek": label,
                "Black-76": round(v76, 8),
                "Bachelier": round(vbch, 8),
            })
    greeks_df = pd.DataFrame(greeks_rows)

    # ─── Export to Excel ─────────────────────────────────────────────────
    st.divider()
    st.download_button(
        label="⬇ Export to Excel",
        data=excel_bytes({
            "Inputs": inputs_df,
            "Comparison": comparison_df,
            "Greeks (full)": greeks_df,
        }),
        file_name="ttf_pricer_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="export_pricer",
    )


# ---------------------------------------------------------------------------
# Tab 2 — Structures
# ---------------------------------------------------------------------------

_STRUCT_SPECS = {
    "Straddle":         {"strikes": ["K"]},
    "Strangle":         {"strikes": ["K_put", "K_call"]},
    "Bull call spread": {"strikes": ["K_lo", "K_hi"]},
    "Bear put spread":  {"strikes": ["K_lo", "K_hi"]},
    "Butterfly":        {"strikes": ["K_lo", "K_mid", "K_hi"]},
    "Condor":           {"strikes": ["K1", "K2", "K3", "K4"]},
    "Collar":           {"strikes": ["K_put", "K_call"]},
    "Risk reversal":    {"strikes": ["K_put", "K_call"]},
    "Calendar spread":  {"strikes": ["K"], "extra": ["T_near (days)", "T_far (days)"]},
    "Ratio spread":     {"strikes": ["K_lo", "K_hi"], "extra": ["Ratio (short qty)"]},
}


def _build_structure(
    name: str,
    F: float, T: float, r: float, sigma: float,
    ks: dict, extra: dict,
):
    """Dispatch to the right structures_ttf function with the right kwargs."""
    if name == "Straddle":
        return structs_mod.straddle(F, K=ks["K"], T=T, r=r, sigma=sigma)
    if name == "Strangle":
        return structs_mod.strangle(F, K_put=ks["K_put"], K_call=ks["K_call"],
                                    T=T, r=r, sigma=sigma)
    if name == "Bull call spread":
        return structs_mod.bull_call_spread(F, K_lo=ks["K_lo"], K_hi=ks["K_hi"],
                                            T=T, r=r, sigma=sigma)
    if name == "Bear put spread":
        return structs_mod.bear_put_spread(F, K_lo=ks["K_lo"], K_hi=ks["K_hi"],
                                           T=T, r=r, sigma=sigma)
    if name == "Butterfly":
        return structs_mod.butterfly(F, K_lo=ks["K_lo"], K_mid=ks["K_mid"],
                                     K_hi=ks["K_hi"], T=T, r=r, sigma=sigma)
    if name == "Condor":
        return structs_mod.condor(F, K1=ks["K1"], K2=ks["K2"],
                                  K3=ks["K3"], K4=ks["K4"],
                                  T=T, r=r, sigma=sigma)
    if name == "Collar":
        return structs_mod.collar(F, K_put=ks["K_put"], K_call=ks["K_call"],
                                  T=T, r=r, sigma=sigma)
    if name == "Risk reversal":
        return structs_mod.risk_reversal(F, K_put=ks["K_put"], K_call=ks["K_call"],
                                         T=T, r=r, sigma=sigma)
    if name == "Calendar spread":
        return structs_mod.calendar_spread(
            F, K=ks["K"],
            T_far=extra["T_far (days)"] / 365.0,
            T_near=extra["T_near (days)"] / 365.0,
            r=r, sigma=sigma,
        )
    if name == "Ratio spread":
        return structs_mod.ratio_spread(
            F, K_lo=ks["K_lo"], K_hi=ks["K_hi"],
            T=T, r=r, sigma=sigma,
            ratio=int(extra["Ratio (short qty)"]),
        )
    raise ValueError(f"Unknown structure: {name}")


with tab_structures:

    st.subheader("Structure selection")
    struct_name = st.selectbox(
        "Choose a structure",
        list(_STRUCT_SPECS.keys()),
        help="10 common multi-leg structures priced under Black-76",
    )

    spec = _STRUCT_SPECS[struct_name]

    # Dynamic strike inputs based on the selected structure
    st.markdown("**Strike inputs**")
    strike_cols = st.columns(max(len(spec["strikes"]), 2))
    ks: dict = {}
    # Provide sensible defaults around the forward F
    width = max(F * 0.10, 1.0)
    default_map = {
        "K":      F,
        "K_put":  F - width,
        "K_call": F + width,
        "K_lo":   F - width,
        "K_mid":  F,
        "K_hi":   F + width,
        "K1":     F - 2 * width,
        "K2":     F - width,
        "K3":     F + width,
        "K4":     F + 2 * width,
    }
    for i, kname in enumerate(spec["strikes"]):
        with strike_cols[i]:
            ks[kname] = st.number_input(
                kname,
                value=float(default_map.get(kname, F)),
                step=0.5, min_value=0.01, max_value=500.0,
                key=f"struct_{struct_name}_{kname}",
            )

    # Extra inputs (calendar, ratio)
    extra: dict = {}
    if "extra" in spec:
        st.markdown("**Additional inputs**")
        ex_cols = st.columns(len(spec["extra"]))
        defaults_extra = {
            "T_near (days)": 30,
            "T_far (days)":  180,
            "Ratio (short qty)": 2,
        }
        for j, ename in enumerate(spec["extra"]):
            with ex_cols[j]:
                if "Ratio" in ename:
                    extra[ename] = st.number_input(
                        ename, value=defaults_extra[ename],
                        step=1, min_value=1, max_value=10,
                        key=f"struct_{struct_name}_{ename}",
                    )
                else:
                    extra[ename] = st.number_input(
                        ename, value=defaults_extra[ename],
                        step=1, min_value=1, max_value=1825,
                        key=f"struct_{struct_name}_{ename}",
                    )

    # Reuse Forward, sigma, rate, T from the sidebar
    st.caption(
        f"Using sidebar values: F = **{F:.2f} EUR/MWh**, "
        f"σ = **{sigma_pct:.0f}%**, T = **{T_days} days**, r = **{r_pct:.2f}%**."
    )

    # Validate strikes (must be strictly increasing for multi-strike structures)
    validation_error = None
    if struct_name == "Strangle" and ks["K_put"] >= ks["K_call"]:
        validation_error = "K_put must be strictly less than K_call."
    elif struct_name in ("Bull call spread", "Bear put spread", "Ratio spread") \
            and ks["K_lo"] >= ks["K_hi"]:
        validation_error = "K_lo must be strictly less than K_hi."
    elif struct_name == "Butterfly" and not (ks["K_lo"] < ks["K_mid"] < ks["K_hi"]):
        validation_error = "Require K_lo < K_mid < K_hi."
    elif struct_name == "Condor" and not (ks["K1"] < ks["K2"] < ks["K3"] < ks["K4"]):
        validation_error = "Require K1 < K2 < K3 < K4."
    elif struct_name in ("Collar", "Risk reversal") and ks["K_put"] >= ks["K_call"]:
        validation_error = "K_put must be strictly less than K_call."
    elif struct_name == "Calendar spread" \
            and extra["T_far (days)"] <= extra["T_near (days)"]:
        validation_error = "T_far must be strictly greater than T_near."

    if validation_error:
        st.error(f"⚠ {validation_error}")
        st.stop()

    # Compute structure
    try:
        result = _build_structure(struct_name, F, T, r, sigma, ks, extra)
    except Exception as exc:
        st.error(f"Pricing error: {exc}")
        st.stop()

    # ─── Metrics row ─────────────────────────────────────────────────────
    st.subheader(f"{result.name} — Summary")

    m_cols = st.columns(5)
    premium_label = "Debit" if result.price >= 0 else "Credit"
    m_cols[0].metric(
        f"Net premium ({premium_label})",
        f"{result.price:+.4f} EUR/MWh",
    )
    if result.max_profit == math.inf:
        mp_txt = "∞"
    else:
        mp_txt = f"{result.max_profit:+.4f}"
    if result.max_loss == -math.inf:
        ml_txt = "−∞"
    else:
        ml_txt = f"{result.max_loss:+.4f}"
    m_cols[1].metric("Max profit", mp_txt)
    m_cols[2].metric("Max loss",   ml_txt)

    if result.breakevens:
        be_str = ", ".join(f"{b:.3f}" for b in result.breakevens)
    else:
        be_str = "—"
    m_cols[3].metric("Breakevens (EUR/MWh)", be_str)

    m_cols[4].metric("Number of legs", f"{len(result.legs)}")

    # ─── Net Greeks ─────────────────────────────────────────────────────
    g_cols = st.columns(4)
    g_cols[0].metric("Net Δ",       f"{result.delta:+.4f}")
    g_cols[1].metric("Net Γ",       f"{result.gamma:+.6f}")
    g_cols[2].metric("Net ν",       f"{result.vega:+.4f}")
    g_cols[3].metric("Net Θ/day",   f"{result.theta:+.4f}")

    # ─── Legs DataFrame ─────────────────────────────────────────────────
    st.subheader("Legs detail")
    legs_df = pd.DataFrame([
        {
            "#": i + 1,
            "Side": "Long" if leg.sign > 0 else "Short",
            "Type": leg.option_type,
            "Qty":  leg.qty,
            "Strike": round(leg.K, 4),
            "T (y)": round(leg.T, 4),
            "σ":    round(leg.sigma, 4),
            "Unit price": round(leg.unit_price, 6),
            "Unit Δ": round(leg.unit_delta, 6),
            "Unit Γ": round(leg.unit_gamma, 8),
            "Unit ν": round(leg.unit_vega, 6),
            "Unit Θ/day": round(leg.unit_theta, 6),
        }
        for i, leg in enumerate(result.legs)
    ])
    st.dataframe(legs_df, hide_index=True, use_container_width=True)

    # ─── P&L chart at expiry (Plotly) ───────────────────────────────────
    st.subheader("P&L at expiry")

    pnl_df = pd.DataFrame(result.pnl_at_expiry, columns=["F_T", "PnL"])

    fig = go.Figure()
    # Shade profit/loss regions
    fig.add_trace(go.Scatter(
        x=pnl_df["F_T"], y=pnl_df["PnL"],
        fill="tozeroy",
        fillcolor="rgba(34, 197, 94, 0.18)",  # green for profit
        line=dict(color="#22c55e", width=0),
        name="Profit",
        showlegend=False,
        hoverinfo="skip",
    ))
    # Main P&L curve
    fig.add_trace(go.Scatter(
        x=pnl_df["F_T"], y=pnl_df["PnL"],
        mode="lines",
        line=dict(color="#3b82f6", width=2.5),
        name="P&L",
        hovertemplate="F_T = %{x:.2f} EUR/MWh<br>P&L = %{y:+.4f}<extra></extra>",
    ))
    # Zero line
    fig.add_hline(y=0, line_color="#64748b", line_width=1, line_dash="dash")
    # Forward reference line
    fig.add_vline(
        x=F, line_color="#facc15", line_width=1, line_dash="dot",
        annotation_text=f"F = {F:.2f}",
        annotation_position="top",
        annotation_font_color="#facc15",
    )
    # Breakeven markers
    for be in result.breakevens:
        fig.add_vline(
            x=be, line_color="#f87171", line_width=1, line_dash="dot",
            annotation_text=f"BE {be:.2f}",
            annotation_position="bottom",
            annotation_font_color="#f87171",
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f0f1a",
        plot_bgcolor="#0f0f1a",
        font=dict(color="#cbd5e1", size=12),
        margin=dict(l=40, r=20, t=10, b=40),
        height=420,
        xaxis=dict(
            title="Forward at expiry F_T (EUR/MWh)",
            gridcolor="#1e1e32", zerolinecolor="#2a2a42",
        ),
        yaxis=dict(
            title="P&L (EUR/MWh)",
            gridcolor="#1e1e32", zerolinecolor="#2a2a42",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ─── Export to Excel ────────────────────────────────────────────────
    struct_summary_df = pd.DataFrame([{
        "Structure": result.name,
        "Net premium (EUR/MWh)": round(result.price, 6),
        "Net Δ": round(result.delta, 6),
        "Net Γ": round(result.gamma, 8),
        "Net ν": round(result.vega, 6),
        "Net Θ/day": round(result.theta, 6),
        "Max profit": (result.max_profit if result.max_profit != math.inf else "inf"),
        "Max loss":   (result.max_loss   if result.max_loss   != -math.inf else "-inf"),
        "Breakevens": ", ".join(f"{b:.4f}" for b in result.breakevens) or "—",
    }])
    pnl_export_df = pnl_df.rename(columns={"F_T": "F_T (EUR/MWh)",
                                           "PnL": "PnL (EUR/MWh)"})

    st.divider()
    st.download_button(
        label="⬇ Export to Excel",
        data=excel_bytes({
            "Summary": struct_summary_df,
            "Legs":    legs_df,
            "PnL at expiry": pnl_export_df,
        }),
        file_name=f"ttf_structure_{struct_name.lower().replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="export_structures",
    )


# ---------------------------------------------------------------------------
# Tab 3 — Vol Surface (3D)
# ---------------------------------------------------------------------------

_VOL_JSON_PATH = Path(__file__).parent / "ttf_output" / "ttf_vol_surface.json"


@st.cache_data(show_spinner=False)
def _load_precomputed_surface(path: str) -> dict | None:
    """Load the pre-computed vol surface JSON from ttf_output/.

    Returns a dict with keys 'reference_date' and 'surface' (list of
    {T, contract, F, strike, vol, model}) or None if the file is missing.
    """
    try:
        with open(path) as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@st.cache_data(show_spinner=True)
def _build_live_surface(
    reference_iso: str,
    atm_vol: float,
    _cache_key: int = 0,
) -> tuple[pd.DataFrame, str]:
    """Rebuild a fresh vol surface via ttf_market_data.

    Uses the default ATM vols but scales them so that the 3-month ATM
    lands on the sidebar's lognormal vol. Returns a long-format DataFrame
    and the reference date ISO string.
    """
    from datetime import date
    from ttf_market_data import TTFForwardCurve, VolatilitySurfaceBuilder

    ref = date.fromisoformat(reference_iso)
    fwd = TTFForwardCurve(ref).load()

    # Scale the built-in ATM vols so that the 3M pillar matches the sidebar sigma
    builder = VolatilitySurfaceBuilder(fwd, ref)
    base = dict(builder._ATM_VOLS)
    scale = atm_vol / base[3 / 12]
    atm_scaled = {t: v * scale for t, v in base.items()}

    surface = builder.build(atm_vols=atm_scaled)
    df = surface.to_dataframe()
    return df, str(ref)


def _surface_to_grid(df: pd.DataFrame) -> tuple[list[float], list[float], np.ndarray]:
    """Pivot the long-format surface DataFrame to (Ts, Ks, Z) for Plotly."""
    Ts = sorted(df["T"].unique())
    Ks = sorted(df["strike"].unique())
    Z = np.full((len(Ts), len(Ks)), np.nan)
    for i, t in enumerate(Ts):
        slice_ = df[df["T"] == t].set_index("strike")["vol"]
        for j, k in enumerate(Ks):
            if k in slice_.index:
                Z[i, j] = float(slice_.loc[k])
    # Fill NaNs by row-level linear interpolation on strike
    for i in range(len(Ts)):
        mask = ~np.isnan(Z[i])
        if mask.sum() >= 2:
            Z[i] = np.interp(Ks, np.array(Ks)[mask], Z[i][mask])
    return Ts, Ks, Z


with tab_vol:

    st.subheader("TTF implied-volatility surface (3D)")

    # Data-source selection
    precomp = _load_precomputed_surface(str(_VOL_JSON_PATH))

    source_options = []
    if precomp is not None:
        source_options.append("Pre-computed (ttf_output/ttf_vol_surface.json)")
    source_options.append("Live rebuild (ttf_market_data.VolatilitySurfaceBuilder)")

    col_src, col_info = st.columns([2, 3])
    with col_src:
        chosen_src = st.radio(
            "Data source",
            source_options,
            key="vol_src",
            help="The pre-computed file is what ttf_market_data.py last exported. "
                 "Live rebuild fetches a forward curve and constructs the surface.",
        )

    # Load the chosen surface into `df` + `ref_date_str`
    if chosen_src.startswith("Pre-computed"):
        df_surface = pd.DataFrame(precomp["surface"])
        ref_date_str = precomp["reference_date"]
    else:
        live_ref = st.session_state.get("vol_live_ref",
                                        pd.Timestamp.today().strftime("%Y-%m-%d"))
        with col_info:
            live_ref = st.text_input(
                "Reference date (YYYY-MM-DD)",
                value=live_ref,
                key="vol_live_ref",
            )
        try:
            df_surface, ref_date_str = _build_live_surface(live_ref, sigma)
        except Exception as exc:
            st.error(f"Live rebuild failed: {exc}")
            st.stop()

    with col_info:
        st.caption(
            f"Reference date : **{ref_date_str}** · "
            f"{len(df_surface['T'].unique())} maturities × "
            f"{len(df_surface['strike'].unique())} unique strikes · "
            f"{len(df_surface)} grid points"
        )

    # Strike-moneyness trim
    col_mony, col_maxT = st.columns(2)
    with col_mony:
        mony_range = st.slider(
            "Strike moneyness range K/F",
            min_value=0.3, max_value=3.0, value=(0.5, 1.8), step=0.05,
            key="vol_moneyness",
            help="Restrict the displayed strikes to this fraction of the forward.",
        )
    with col_maxT:
        max_T_years = st.slider(
            "Max maturity (years)",
            min_value=0.25, max_value=3.0, value=2.0, step=0.25,
            key="vol_maxT",
        )

    # Filter DataFrame
    def _in_moneyness(row) -> bool:
        try:
            ratio = row["strike"] / row["F"]
        except ZeroDivisionError:
            return False
        return mony_range[0] <= ratio <= mony_range[1]

    df_filt = df_surface[df_surface["T"] <= max_T_years].copy()
    df_filt = df_filt[df_filt.apply(_in_moneyness, axis=1)]

    if df_filt.empty:
        st.warning("No surface points in the selected range. Loosen the filters.")
        st.stop()

    Ts, Ks, Z = _surface_to_grid(df_filt)

    # Tenor labels for the y-axis
    def _tenor_label(t: float) -> str:
        if t < 1 / 12 + 0.001:     return "1M"
        if t < 2 / 12 + 0.001:     return "2M"
        if t < 3 / 12 + 0.001:     return "3M"
        if t < 6 / 12 + 0.001:     return "6M"
        if t < 9 / 12 + 0.001:     return "9M"
        if abs(t - 1.0) < 0.05:    return "1Y"
        if abs(t - 2.0) < 0.05:    return "2Y"
        return f"{t:.2f}y"

    tenor_labels = [_tenor_label(t) for t in Ts]

    # ─── 3D Surface plot ─────────────────────────────────────────────────
    surface_fig = go.Figure(data=[go.Surface(
        x=Ks,
        y=tenor_labels,
        z=Z * 100.0,   # show vol in %
        colorscale=[
            [0.00, "#1e3a5f"],
            [0.25, "#2563eb"],
            [0.50, "#7c3aed"],
            [0.75, "#db2777"],
            [1.00, "#ef4444"],
        ],
        contours={"z": {"show": True, "usecolormap": True,
                        "highlightcolor": "#ffffff",
                        "project": {"z": True}}},
        colorbar=dict(title="σ (%)", tickfont=dict(color="#cbd5e1")),
        hovertemplate=(
            "Strike: %{x:.2f} EUR/MWh<br>"
            "Tenor: %{y}<br>"
            "σ: %{z:.2f}%<extra></extra>"
        ),
        opacity=0.94,
    )])
    surface_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f0f1a",
        scene=dict(
            bgcolor="#0f0f1a",
            xaxis=dict(title="Strike (EUR/MWh)",
                       gridcolor="#2a2a42", color="#cbd5e1"),
            yaxis=dict(title="Tenor",
                       gridcolor="#2a2a42", color="#cbd5e1"),
            zaxis=dict(title="σ (%)",
                       gridcolor="#2a2a42", color="#cbd5e1"),
            camera=dict(eye=dict(x=1.7, y=-1.7, z=0.9)),
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=560,
    )
    st.plotly_chart(surface_fig, use_container_width=True)

    # ─── Smile cross-sections per tenor ─────────────────────────────────
    with st.expander("Smile cross-sections (per tenor)"):
        smile_fig = go.Figure()
        palette = ["#60a5fa", "#a78bfa", "#34d399", "#f87171",
                   "#facc15", "#fb923c", "#e879f9", "#2dd4bf"]
        for idx, t in enumerate(Ts):
            mask = df_filt["T"] == t
            sub = df_filt[mask].sort_values("strike")
            if len(sub) == 0:
                continue
            smile_fig.add_trace(go.Scatter(
                x=sub["strike"],
                y=sub["vol"] * 100.0,
                mode="lines+markers",
                name=tenor_labels[idx],
                line=dict(color=palette[idx % len(palette)], width=2),
                marker=dict(size=6),
                hovertemplate=(
                    f"{tenor_labels[idx]}<br>"
                    "K=%{x:.2f}<br>"
                    "σ=%{y:.2f}%<extra></extra>"
                ),
            ))
        smile_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f0f1a",
            plot_bgcolor="#0f0f1a",
            xaxis=dict(title="Strike (EUR/MWh)",
                       gridcolor="#1e1e32", color="#cbd5e1"),
            yaxis=dict(title="σ (%)",
                       gridcolor="#1e1e32", color="#cbd5e1"),
            legend=dict(font=dict(color="#cbd5e1")),
            margin=dict(l=10, r=10, t=10, b=40),
            height=380,
        )
        st.plotly_chart(smile_fig, use_container_width=True)

    # ─── Pivot table preview ────────────────────────────────────────────
    pivot_df = (
        df_filt.pivot_table(index="T", columns="strike", values="vol",
                            aggfunc="first")
        .sort_index(axis=0)
        .sort_index(axis=1)
    )
    pivot_df.index = [f"{t:.4f}" for t in pivot_df.index]
    pivot_df.index.name = "T (y)"

    with st.expander("Pivot table (T × strike)"):
        st.dataframe(
            pivot_df.style.format("{:.4f}"),
            use_container_width=True,
        )

    # ─── Export to Excel ─────────────────────────────────────────────────
    long_export = df_filt[["T", "contract", "F", "strike", "vol", "model"]].copy()
    long_export.columns = ["T (y)", "Contract", "F (EUR/MWh)",
                           "Strike (EUR/MWh)", "σ", "Model"]
    pivot_export = pivot_df.reset_index()

    meta_df = pd.DataFrame({
        "Field": ["Reference date", "Data source", "# tenors",
                  "# unique strikes", "# grid points",
                  "Strike moneyness min (K/F)", "Strike moneyness max (K/F)",
                  "Max maturity filter (y)"],
        "Value": [ref_date_str, chosen_src,
                  len(df_filt['T'].unique()),
                  len(df_filt['strike'].unique()),
                  len(df_filt),
                  mony_range[0], mony_range[1], max_T_years],
    })

    st.divider()
    st.download_button(
        label="⬇ Export to Excel",
        data=excel_bytes({
            "Meta":  meta_df,
            "Surface (long)": long_export,
            "Surface (pivot)": pivot_export,
        }),
        file_name="ttf_vol_surface_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="export_vol",
    )


st.sidebar.divider()
st.sidebar.caption(
    "Prices are indicative. Black-76 for F > ~5 EUR/MWh; "
    "Bachelier for low or negative prices. "
    "Uses `black76_ttf.py`, `structures_ttf.py`, `ttf_market_data.py`."
)
