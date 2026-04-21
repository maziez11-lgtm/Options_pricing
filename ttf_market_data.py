"""TTF Natural Gas Market Data Module.

Covers:
  - TTF expiry calendar (ICE/EEX conventions)
  - Forward curve fetching via Yahoo Finance (requests) with synthetic fallback
  - Volatility surface construction (strikes × maturities)
  - SABR-style market calibration
  - CSV / JSON export for downstream pricing modules

TTF conventions:
  - Underlying : ICE TTF Natural Gas front-month futures, EUR/MWh
  - Expiry     : last business day of the month *before* the delivery month
  - Vol        : lognormal (Black-76) for positive prices,
                 normal (Bachelier) when F ≤ 0 or near zero (< 2 EUR/MWh)
  - Rate       : EUR risk-free rate (ESTER / EURIBOR proxy), annualised decimal
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import requests
from scipy.interpolate import RectBivariateSpline, interp1d
from scipy.optimize import minimize, brentq
from scipy.stats import norm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# ICE TTF front-month Yahoo Finance ticker
_YF_TTF_TICKER = "TTF=F"
_YF_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
_YF_HEADERS = {"User-Agent": "Mozilla/5.0"}

# Delivery months available on ICE (all 12)
_MONTH_CODES = {
    1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
    7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z",
}

# Delta pillars for vol surface (call deltas)
_DELTA_PILLARS = [0.10, 0.25, 0.50, 0.75, 0.90]

# Standard tenors in years
_STANDARD_TENORS = [1 / 12, 2 / 12, 3 / 12, 6 / 12, 9 / 12, 1.0, 2.0]


# ---------------------------------------------------------------------------
# 1. TTF Expiry Calendar
# ---------------------------------------------------------------------------

@dataclass
class TTFContract:
    delivery_month: int
    delivery_year: int
    expiry_date: date         # options expiry (5 bd before futures expiry)
    futures_expiry_date: date # futures last trading day
    contract_code: str
    T: float                  # time to options expiry in years (Act/365)


class TTFExpiryCalendar:
    """TTF option and futures expiry dates following ICE/EEX conventions.

    Futures expiry : last business day of the month preceding delivery.
    Options expiry : 5 business days before the futures expiry.
    """

    def __init__(self, reference_date: Optional[date] = None) -> None:
        self.reference_date = reference_date or date.today()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Internal business-day helpers (self-contained, no external deps)
    # ------------------------------------------------------------------

    @staticmethod
    def _is_bd(d: date) -> bool:
        return d.weekday() < 5

    @staticmethod
    def _prev_bd(d: date) -> date:
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        return d

    @staticmethod
    def _subtract_bd(d: date, n: int) -> date:
        while n > 0:
            d -= timedelta(days=1)
            if d.weekday() < 5:
                n -= 1
        return d

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def futures_expiry_date(self, delivery_year: int, delivery_month: int) -> date:
        """TTF futures last trading day: last business day of month before delivery."""
        last_of_prev = date(delivery_year, delivery_month, 1) - timedelta(days=1)
        return self._prev_bd(last_of_prev)

    def expiry_date(self, delivery_year: int, delivery_month: int) -> date:
        """TTF options expiry: 5 business days before the futures expiry."""
        return self._subtract_bd(self.futures_expiry_date(delivery_year, delivery_month), 5)

    def contract_code(self, delivery_year: int, delivery_month: int) -> str:
        """Return ICE-style code, e.g. 'TTFH26' for March 2026."""
        return f"TTF{_MONTH_CODES[delivery_month]}{str(delivery_year)[-2:]}"

    def time_to_expiry(self, expiry: date) -> float:
        """Act/365 Fixed from reference_date to expiry."""
        return max((expiry - self.reference_date).days / 365.0, 0.0)

    def active_contracts(self, n: int = 12) -> list[TTFContract]:
        """Return the next *n* monthly TTF contracts."""
        contracts: list[TTFContract] = []
        ref = self.reference_date
        year, month = ref.year, ref.month

        while len(contracts) < n:
            month += 1
            if month > 12:
                month = 1
                year += 1
            expiry = self.expiry_date(year, month)
            if expiry > ref:
                contracts.append(
                    TTFContract(
                        delivery_month=month,
                        delivery_year=year,
                        expiry_date=expiry,
                        futures_expiry_date=self.futures_expiry_date(year, month),
                        contract_code=self.contract_code(year, month),
                        T=self.time_to_expiry(expiry),
                    )
                )
        return contracts

    def expiry_for_tenor(self, tenor_years: float) -> date:
        """Nearest contract expiry to a given tenor (in years)."""
        target = self.reference_date + timedelta(days=int(tenor_years * 365))
        contracts = self.active_contracts(n=36)
        return min(contracts, key=lambda c: abs((c.expiry_date - target).days)).expiry_date

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _last_business_day(year: int, month: int) -> date:
        """Last Mon-Fri of the given month."""
        if month == 12:
            last = date(year, month, 31)
        else:
            last = date(year, month + 1, 1) - timedelta(days=1)
        while last.weekday() >= 5:  # Sat=5, Sun=6
            last -= timedelta(days=1)
        return last


# ---------------------------------------------------------------------------
# 2. Forward Curve
# ---------------------------------------------------------------------------

@dataclass
class ForwardPoint:
    contract_code: str
    delivery_month: int
    delivery_year: int
    expiry_date: date
    T: float
    forward_price: float  # EUR/MWh
    source: str


class TTFForwardCurve:
    """Fetch and interpolate TTF forward prices.

    Primary source : Yahoo Finance (requests-based, no yfinance dependency).
    Fallback       : Synthetic curve from a base spot price and shape.
    """

    def __init__(
        self,
        reference_date: Optional[date] = None,
        risk_free_rate: float = 0.03,
        timeout: int = 10,
    ) -> None:
        self.reference_date = reference_date or date.today()
        self.risk_free_rate = risk_free_rate
        self.timeout = timeout
        self.calendar = TTFExpiryCalendar(self.reference_date)
        self._points: list[ForwardPoint] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, contracts: Optional[list[TTFContract]] = None) -> "TTFForwardCurve":
        """Fetch prices for *contracts* (default: next 12 monthly contracts)."""
        contracts = contracts or self.calendar.active_contracts(n=12)
        spot, source = self._fetch_spot()
        self._points = [self._price_contract(c, spot, source) for c in contracts]
        return self

    def forward_price(self, T: float) -> float:
        """Linearly interpolate forward price for a given tenor T (years)."""
        if not self._points:
            raise RuntimeError("Call .load() first.")
        ts = np.array([p.T for p in self._points])
        fs = np.array([p.forward_price for p in self._points])
        if T <= ts[0]:
            return float(fs[0])
        if T >= ts[-1]:
            return float(fs[-1])
        return float(np.interp(T, ts, fs))

    def to_dataframe(self) -> pd.DataFrame:
        if not self._points:
            raise RuntimeError("Call .load() first.")
        return pd.DataFrame([asdict(p) for p in self._points])

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_spot(self) -> tuple[float, str]:
        """Fetch latest TTF front-month price from Yahoo Finance.

        Returns (price, source) where source is 'yahoo_finance' or 'synthetic'.
        """
        try:
            url = _YF_BASE_URL.format(ticker=_YF_TTF_TICKER)
            resp = requests.get(
                url, headers=_YF_HEADERS, timeout=self.timeout, params={"range": "1d", "interval": "1d"}
            )
            resp.raise_for_status()
            data = resp.json()
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            logger.info("Yahoo Finance TTF spot: %.4f EUR/MWh", price)
            return float(price), "yahoo_finance"
        except Exception as exc:
            logger.warning("Yahoo Finance fetch failed (%s). Using synthetic curve.", exc)
            return self._synthetic_spot(), "synthetic"

    @staticmethod
    def _synthetic_spot() -> float:
        """Representative TTF spot price when live feed is unavailable."""
        return 35.0  # EUR/MWh (typical mid-range)

    def _price_contract(self, c: TTFContract, spot: float, source: str) -> ForwardPoint:
        """Price a single contract using cost-of-carry (gas storage proxy)."""
        carry = self.risk_free_rate
        seasonal = 0.03 * math.sin(2 * math.pi * (c.delivery_month - 1) / 12)  # winter premium
        fwd = spot * math.exp((carry + seasonal) * c.T)
        return ForwardPoint(
            contract_code=c.contract_code,
            delivery_month=c.delivery_month,
            delivery_year=c.delivery_year,
            expiry_date=c.expiry_date,
            T=c.T,
            forward_price=round(fwd, 4),
            source=source,
        )


# ---------------------------------------------------------------------------
# 3. Volatility Surface
# ---------------------------------------------------------------------------

@dataclass
class VolSmile:
    T: float
    contract_code: str
    F: float                        # forward price at this tenor
    strikes: list[float]
    vols: list[float]               # Black-76 lognormal vols
    model: str = "black76"          # 'black76' or 'bachelier'


@dataclass
class VolatilitySurface:
    reference_date: date
    smiles: list[VolSmile] = field(default_factory=list)
    _interp: Optional[RectBivariateSpline] = field(default=None, init=False, repr=False)

    def add_smile(self, smile: VolSmile) -> None:
        self.smiles.append(smile)
        self._interp = None  # invalidate cache

    def vol(self, K: float, T: float) -> float:
        """Bilinear interpolation for vol at (K, T)."""
        return float(self._get_interp()(T, K))

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for s in self.smiles:
            for k, v in zip(s.strikes, s.vols):
                rows.append(
                    {"T": s.T, "contract": s.contract_code, "F": s.F,
                     "strike": k, "vol": v, "model": s.model}
                )
        return pd.DataFrame(rows)

    def _get_interp(self) -> RectBivariateSpline:
        if self._interp is not None:
            return self._interp
        if not self.smiles:
            raise RuntimeError("VolatilitySurface has no smiles — call add_smile() first.")
        df = self.to_dataframe()
        Ts = sorted(df["T"].unique())
        Ks = sorted(df["strike"].unique())
        grid = np.zeros((len(Ts), len(Ks)))
        for i, t in enumerate(Ts):
            row = df[df["T"] == t].set_index("strike")["vol"]
            for j, k in enumerate(Ks):
                grid[i, j] = row.get(k, np.nan)
        # fill NaN by row interpolation
        for i in range(len(Ts)):
            mask = ~np.isnan(grid[i])
            if mask.sum() >= 2:
                f = interp1d(np.array(Ks)[mask], grid[i][mask],
                             kind="linear", fill_value="extrapolate")
                grid[i] = f(Ks)
        self._interp = RectBivariateSpline(Ts, Ks, grid, kx=1, ky=1)
        return self._interp


class VolatilitySurfaceBuilder:
    """Build a TTF vol surface from ATM vol + parametric smile.

    When live option quotes are unavailable (no public free feed for TTF
    options), the surface is constructed from:
      - ATM vol estimates per tenor (empirically typical TTF levels)
      - Symmetric risk-reversal / butterfly parametrisation
    """

    # Typical TTF ATM vols by tenor (illustrative market levels)
    _ATM_VOLS = {
        1 / 12: 0.65,
        2 / 12: 0.58,
        3 / 12: 0.52,
        6 / 12: 0.46,
        9 / 12: 0.42,
        1.0:    0.40,
        2.0:    0.38,
    }
    # Risk-reversal (25D): negative → put vol > call vol (TTF downside skew typical)
    _RR25 = {T: -0.03 for T in _ATM_VOLS}
    # Butterfly (25D): smile convexity
    _BF25 = {T: 0.015 for T in _ATM_VOLS}

    def __init__(
        self,
        forward_curve: TTFForwardCurve,
        reference_date: Optional[date] = None,
        n_strikes: int = 9,
    ) -> None:
        self.forward_curve = forward_curve
        self.reference_date = reference_date or date.today()
        self.n_strikes = n_strikes

    def build(
        self,
        atm_vols: Optional[dict[float, float]] = None,
        rr25: Optional[dict[float, float]] = None,
        bf25: Optional[dict[float, float]] = None,
    ) -> VolatilitySurface:
        """Construct the full surface."""
        atm_vols = atm_vols or self._ATM_VOLS
        rr25 = rr25 or self._RR25
        bf25 = bf25 or self._BF25

        surface = VolatilitySurface(reference_date=self.reference_date)
        for T, atm in atm_vols.items():
            F = self.forward_curve.forward_price(T)
            rr = rr25.get(T, 0.0)
            bf = bf25.get(T, 0.0)
            smile = self._build_smile(T, F, atm, rr, bf)
            surface.add_smile(smile)
        return surface

    def _build_smile(
        self, T: float, F: float, atm: float, rr25: float, bf25: float
    ) -> VolSmile:
        """Parameterise smile from ATM, 25D RR and 25D BF.

        25D call vol = ATM + 0.5*RR + BF
        25D put vol  = ATM - 0.5*RR + BF
        """
        model = "bachelier" if F < 2.0 else "black76"
        call25_vol = atm + 0.5 * rr25 + bf25
        put25_vol = atm - 0.5 * rr25 + bf25

        # Convert 25D vols → strikes via delta inversion
        k25c = self._delta_to_strike(0.25, F, T, call25_vol)
        k25p = self._delta_to_strike(-0.25, F, T, put25_vol)

        # Build a symmetric strike grid from 10D to 90D
        k10c = self._delta_to_strike(0.10, F, T, atm * 1.05)
        k10p = self._delta_to_strike(-0.10, F, T, atm * 1.05)

        raw_strikes = sorted({k10p, k25p, F * 0.90, k25p * 1.05,
                               F, k25c * 0.95, F * 1.10, k25c, k10c})
        # Interpolate vols across strikes (cubic in log-strike space)
        ref_strikes = [k10p, k25p, F, k25c, k10c]
        ref_vols = [
            put25_vol * 1.04,
            put25_vol,
            atm,
            call25_vol,
            call25_vol * 1.04,
        ]
        log_ref = np.log(np.array(ref_strikes) / F)
        log_grid = np.log(np.array(raw_strikes) / F)
        interp_vols = np.interp(log_grid, log_ref, ref_vols)

        return VolSmile(
            T=T,
            contract_code=self.forward_curve.calendar.expiry_for_tenor(T).strftime("%b%y"),
            F=round(F, 4),
            strikes=[round(k, 4) for k in raw_strikes],
            vols=[round(float(v), 6) for v in interp_vols],
            model=model,
        )

    @staticmethod
    def _delta_to_strike(delta: float, F: float, T: float, sigma: float) -> float:
        """Black-76 delta-to-strike inversion via Brent (r=0 for forward delta)."""
        sign = 1 if delta > 0 else -1

        def f(K: float) -> float:
            if K <= 0:
                return -abs(delta)
            d1 = (math.log(F / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
            d_model = norm.cdf(sign * d1) * sign
            return d_model - abs(delta)

        lo, hi = F * 0.01, F * 10.0
        try:
            return brentq(f, lo, hi, xtol=1e-4)
        except ValueError:
            return F * (1.0 - delta * 0.5)


# ---------------------------------------------------------------------------
# 4. Market Calibration
# ---------------------------------------------------------------------------

@dataclass
class SABRParams:
    alpha: float   # initial vol level
    beta: float    # CEV exponent (0 = normal, 1 = lognormal)
    rho: float     # vol-spot correlation
    nu: float      # vol-of-vol


class MarketCalibration:
    """Calibrate SABR parameters to the observed vol smile for each tenor."""

    def __init__(self, surface: VolatilitySurface) -> None:
        self.surface = surface
        self.results: dict[float, SABRParams] = {}

    def calibrate_all(self) -> "MarketCalibration":
        """Calibrate SABR for every Black-76 smile in the surface.

        Bachelier smiles (model='bachelier', i.e. F < 2 EUR/MWh) use the
        normal-vol SABR which is not implemented here — they are skipped.
        """
        for smile in self.surface.smiles:
            if smile.model == "bachelier":
                logger.warning(
                    "Skipping SABR calibration for T=%.4f: "
                    "Bachelier smile (F=%.4f) requires normal-vol SABR.",
                    smile.T, smile.F,
                )
                continue
            try:
                params = self._calibrate_sabr(smile)
                self.results[smile.T] = params
            except Exception as exc:
                logger.warning("SABR calibration failed for T=%.4f: %s", smile.T, exc)
        return self

    def to_dataframe(self) -> pd.DataFrame:
        rows = [
            {"T": T, "alpha": p.alpha, "beta": p.beta, "rho": p.rho, "nu": p.nu}
            for T, p in sorted(self.results.items())
        ]
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _calibrate_sabr(self, smile: VolSmile) -> SABRParams:
        F, T = smile.F, smile.T
        strikes = np.array(smile.strikes)
        market_vols = np.array(smile.vols)

        beta = 0.5  # fixed — typical for energy markets

        def objective(params: np.ndarray) -> float:
            alpha, rho, nu = params
            if alpha <= 0 or nu <= 0 or abs(rho) >= 1:
                return 1e6
            model_vols = np.array([
                self._sabr_vol(F, K, T, alpha, beta, rho, nu) for K in strikes
            ])
            return float(np.sum((model_vols - market_vols) ** 2))

        x0 = [market_vols.mean(), -0.2, 0.4]
        bounds = [(1e-4, 5.0), (-0.999, 0.999), (1e-4, 5.0)]
        res = minimize(objective, x0, bounds=bounds, method="L-BFGS-B",
                       options={"ftol": 1e-12, "gtol": 1e-8, "maxiter": 500})
        alpha, rho, nu = res.x
        return SABRParams(alpha=round(alpha, 6), beta=beta,
                          rho=round(rho, 6), nu=round(nu, 6))

    @staticmethod
    def _sabr_vol(
        F: float, K: float, T: float,
        alpha: float, beta: float, rho: float, nu: float
    ) -> float:
        """Hagan et al. (2002) SABR implied vol approximation."""
        if abs(F - K) < 1e-8:
            # ATM: chi(z)/z → 1 as F→K, so the correction term drops out entirely.
            # Correct formula: sigma_ATM = alpha / F^(1-beta) * (1 + term2*T)
            FK_mid = F ** (1 - beta)
            term2 = (
                (1 - beta) ** 2 / 24 * alpha**2 / FK_mid**2
                + rho * beta * nu * alpha / (4 * FK_mid)
                + (2 - 3 * rho**2) / 24 * nu**2
            )
            return alpha / FK_mid * (1 + term2 * T)

        log_FK = math.log(F / K)
        FK_mid = (F * K) ** ((1 - beta) / 2)
        z = nu / alpha * FK_mid * log_FK
        chi = math.log(
            (math.sqrt(1 - 2 * rho * z + z**2) + z - rho) / (1 - rho)
        )
        x_chi = z / chi if abs(chi) > 1e-10 else 1.0
        num = alpha
        denom_main = FK_mid * (
            1
            + (1 - beta) ** 2 / 24 * log_FK**2
            + (1 - beta) ** 4 / 1920 * log_FK**4
        )
        term2 = (
            (1 - beta) ** 2 / 24 * alpha**2 / FK_mid**2
            + rho * beta * nu * alpha / (4 * FK_mid)
            + (2 - 3 * rho**2) / 24 * nu**2
        )
        return num / denom_main * x_chi * (1 + term2 * T)


# ---------------------------------------------------------------------------
# 5. Export utilities
# ---------------------------------------------------------------------------

def export_forward_curve(curve: TTFForwardCurve, path: str) -> None:
    """Export forward curve to CSV and JSON (path without extension)."""
    df = curve.to_dataframe()
    df["expiry_date"] = df["expiry_date"].astype(str)

    df.to_csv(f"{path}.csv", index=False)
    records = json.loads(df.to_json(orient="records", date_format="iso"))
    with open(f"{path}.json", "w") as fh:
        json.dump({"reference_date": str(curve.reference_date), "curve": records}, fh, indent=2)
    logger.info("Forward curve exported to %s.csv / %s.json", path, path)


def export_vol_surface(surface: VolatilitySurface, path: str) -> None:
    """Export vol surface (long format) to CSV and JSON."""
    df = surface.to_dataframe()

    df.to_csv(f"{path}.csv", index=False)
    pivot = df.pivot_table(index="T", columns="strike", values="vol", aggfunc="first")
    pivot.to_csv(f"{path}_pivot.csv")

    records = json.loads(df.to_json(orient="records"))
    with open(f"{path}.json", "w") as fh:
        json.dump(
            {"reference_date": str(surface.reference_date), "surface": records},
            fh, indent=2,
        )
    logger.info("Vol surface exported to %s.csv / %s.json", path, path)


def export_sabr_params(calibration: MarketCalibration, path: str) -> None:
    """Export SABR calibrated parameters to CSV and JSON."""
    df = calibration.to_dataframe()

    df.to_csv(f"{path}.csv", index=False)
    records = json.loads(df.to_json(orient="records"))
    with open(f"{path}.json", "w") as fh:
        json.dump({"sabr_params": records}, fh, indent=2)
    logger.info("SABR params exported to %s.csv / %s.json", path, path)


def export_all(
    output_dir: str = ".",
    reference_date: Optional[date] = None,
    risk_free_rate: float = 0.03,
) -> dict[str, pd.DataFrame]:
    """Run the full pipeline and export everything to *output_dir*.

    Returns a dict with keys 'forward_curve', 'vol_surface', 'sabr_params'.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    ref = reference_date or date.today()
    calendar = TTFExpiryCalendar(ref)
    contracts = calendar.active_contracts(n=12)

    # 1. Forward curve
    fwd_curve = TTFForwardCurve(ref, risk_free_rate).load(contracts)
    export_forward_curve(fwd_curve, os.path.join(output_dir, "ttf_forward_curve"))

    # 2. Vol surface
    builder = VolatilitySurfaceBuilder(fwd_curve, ref)
    surface = builder.build()
    export_vol_surface(surface, os.path.join(output_dir, "ttf_vol_surface"))

    # 3. SABR calibration
    calibration = MarketCalibration(surface).calibrate_all()
    export_sabr_params(calibration, os.path.join(output_dir, "ttf_sabr_params"))

    return {
        "forward_curve": fwd_curve.to_dataframe(),
        "vol_surface": surface.to_dataframe(),
        "sabr_params": calibration.to_dataframe(),
    }


# ---------------------------------------------------------------------------
# CLI / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    ref = date(2026, 4, 20)
    cal = TTFExpiryCalendar(ref)

    print("=== TTF Active Contracts ===")
    for c in cal.active_contracts(n=6):
        print(f"  {c.contract_code}  expiry={c.expiry_date}  T={c.T:.4f}y")

    print("\n=== Forward Curve ===")
    fwd = TTFForwardCurve(ref, risk_free_rate=0.03).load()
    df_fwd = fwd.to_dataframe()
    print(df_fwd[["contract_code", "expiry_date", "T", "forward_price", "source"]].to_string(index=False))

    print("\n=== Volatility Surface (first smile) ===")
    builder = VolatilitySurfaceBuilder(fwd, ref)
    surface = builder.build()
    df_vol = surface.to_dataframe()
    first_T = df_vol["T"].min()
    print(df_vol[df_vol["T"] == first_T][["T", "F", "strike", "vol", "model"]].to_string(index=False))

    print("\n=== SABR Calibration ===")
    calib = MarketCalibration(surface).calibrate_all()
    print(calib.to_dataframe().to_string(index=False))

    print("\n=== Exporting to ./ttf_output/ ===")
    export_all(output_dir="ttf_output", reference_date=ref)
    print("Done.")
