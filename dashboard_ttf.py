"""TTF Natural Gas Options — Streamlit dashboard (Pricer tab only).

Run with:
    streamlit run dashboard_ttf.py

Requires:
    pip install streamlit pandas openpyxl
    (plus the project's own deps: numpy, scipy)
"""

from __future__ import annotations

import math
from io import BytesIO

import pandas as pd
import streamlit as st

from black76_ttf import (
    b76_call, b76_put, b76_greeks,
    bach_call, bach_put, bach_greeks,
    b76_implied_vol, bach_implied_vol,
)


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

tab_pricer, = st.tabs(["Pricer"])

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
    )


st.sidebar.divider()
st.sidebar.caption(
    "Prices are indicative. Black-76 for F > ~5 EUR/MWh; "
    "Bachelier for low or negative prices. "
    "Uses `black76_ttf.py`."
)
