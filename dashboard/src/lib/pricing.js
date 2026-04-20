/**
 * TTF Natural Gas Options Pricing Engine
 * Black-76 (lognormal) and Bachelier (normal) models
 * All prices in EUR/MWh, vol in decimal, T in years
 */

// ---------------------------------------------------------------------------
// Normal distribution helpers
// ---------------------------------------------------------------------------

function erf(x) {
  const a1 =  0.254829592, a2 = -0.284496736, a3 =  1.421413741;
  const a4 = -1.453152027, a5 =  1.061405429, p  =  0.3275911;
  const sign = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1.0 / (1.0 + p * x);
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

export function normCDF(x) {
  return 0.5 * (1 + erf(x / Math.SQRT2));
}

export function normPDF(x) {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

// ---------------------------------------------------------------------------
// Black-76 model (lognormal vol, options on futures)
// ---------------------------------------------------------------------------

function b76_d1d2(F, K, T, sigma) {
  const d1 = (Math.log(F / K) + 0.5 * sigma * sigma * T) / (sigma * Math.sqrt(T));
  return { d1, d2: d1 - sigma * Math.sqrt(T) };
}

export function b76Price(F, K, T, r, sigma, type = 'call') {
  if (T <= 0) return Math.exp(-r * T) * Math.max(type === 'call' ? F - K : K - F, 0);
  const df = Math.exp(-r * T);
  const { d1, d2 } = b76_d1d2(F, K, T, sigma);
  if (type === 'call') return df * (F * normCDF(d1) - K * normCDF(d2));
  return df * (K * normCDF(-d2) - F * normCDF(-d1));
}

export function b76Greeks(F, K, T, r, sigma, type = 'call') {
  if (T <= 0) return { delta: 0, gamma: 0, vega: 0, theta: 0, rho: 0, vanna: 0, volga: 0 };
  const df = Math.exp(-r * T);
  const sqrtT = Math.sqrt(T);
  const { d1, d2 } = b76_d1d2(F, K, T, sigma);
  const nd1 = normPDF(d1);

  const delta = type === 'call' ? df * normCDF(d1) : df * (normCDF(d1) - 1);
  const gamma = df * nd1 / (F * sigma * sqrtT);
  const vega  = df * F * nd1 * sqrtT;
  const vanna = -df * nd1 * d2 / sigma;
  const volga = vega * d1 * d2 / sigma;

  const decay = -(F * df * nd1 * sigma) / (2 * sqrtT);
  const price = b76Price(F, K, T, r, sigma, type);
  const theta = (decay - r * price) / 365;
  const rho_val = -T * price / 100;

  return { delta, gamma, vega, theta, rho: rho_val, vanna, volga };
}

// ---------------------------------------------------------------------------
// Bachelier model (normal vol, supports negative prices)
// ---------------------------------------------------------------------------

export function bachPrice(F, K, T, r, sigma_n, type = 'call') {
  if (T <= 0) return Math.exp(-r * T) * Math.max(type === 'call' ? F - K : K - F, 0);
  const df = Math.exp(-r * T);
  const vol_sqrtT = sigma_n * Math.sqrt(T);
  const d = (F - K) / vol_sqrtT;
  if (type === 'call') return df * ((F - K) * normCDF(d) + vol_sqrtT * normPDF(d));
  return df * ((K - F) * normCDF(-d) + vol_sqrtT * normPDF(d));
}

export function bachGreeks(F, K, T, r, sigma_n, type = 'call') {
  if (T <= 0) return { delta: 0, gamma: 0, vega: 0, theta: 0, rho: 0, vanna: 0, volga: 0 };
  const df = Math.exp(-r * T);
  const sqrtT = Math.sqrt(T);
  const vol_sqrtT = sigma_n * sqrtT;
  const d = (F - K) / vol_sqrtT;
  const nd = normPDF(d);

  const delta = type === 'call' ? df * normCDF(d) : df * (normCDF(d) - 1);
  const gamma = df * nd / vol_sqrtT;
  const vega  = df * nd * sqrtT;
  const vanna = -df * nd * d / sigma_n;
  const volga = vega * (d * d - 1) / sigma_n;

  const price = bachPrice(F, K, T, r, sigma_n, type);
  const theta = (-df * sigma_n * nd / (2 * sqrtT) - r * price) / 365;
  const rho_val = -T * price / 100;

  return { delta, gamma, vega, theta, rho: rho_val, vanna, volga };
}

// ---------------------------------------------------------------------------
// Implied vol — Brent's method
// ---------------------------------------------------------------------------

function brent(f, lo, hi, tol = 1e-8, maxIter = 200) {
  let a = lo, b = hi, fa = f(a), fb = f(b);
  if (fa * fb > 0) return null;
  let c = a, fc = fa, s = 0, d = 0;
  let mflag = true;
  for (let i = 0; i < maxIter; i++) {
    if (Math.abs(b - a) < tol) return (a + b) / 2;
    if (fa !== fc && fb !== fc) {
      s = (a * fb * fc) / ((fa - fb) * (fa - fc))
        + (b * fa * fc) / ((fb - fa) * (fb - fc))
        + (c * fa * fb) / ((fc - fa) * (fc - fb));
    } else {
      s = b - fb * (b - a) / (fb - fa);
    }
    const cond1 = s < (3 * a + b) / 4 || s > b;
    const cond2 = mflag && Math.abs(s - b) >= Math.abs(b - c) / 2;
    const cond3 = !mflag && Math.abs(s - b) >= Math.abs(c - d) / 2;
    if (cond1 || cond2 || cond3) { s = (a + b) / 2; mflag = true; }
    else mflag = false;
    const fs = f(s);
    d = c; c = b; fc = fb;
    if (fa * fs < 0) { b = s; fb = fs; } else { a = s; fa = fs; }
    if (Math.abs(fa) < Math.abs(fb)) { [a, b] = [b, a]; [fa, fb] = [fb, fa]; }
  }
  return (a + b) / 2;
}

export function b76ImpliedVol(marketPrice, F, K, T, r, type = 'call') {
  const f = (s) => b76Price(F, K, T, r, s, type) - marketPrice;
  return brent(f, 1e-6, 20.0);
}

export function bachImpliedVol(marketPrice, F, K, T, r, type = 'call') {
  const f = (s) => bachPrice(F, K, T, r, s, type) - marketPrice;
  return brent(f, 1e-6, 500.0);
}

// ---------------------------------------------------------------------------
// Vol surface grid generator
// ---------------------------------------------------------------------------

export function buildVolSurface(F0, r, atm_vol = 0.50) {
  const tenors = [1/12, 2/12, 3/12, 6/12, 9/12, 1.0, 2.0];
  const deltaMoneyness = [-0.40, -0.30, -0.20, -0.10, 0, 0.10, 0.20, 0.30, 0.40]; // log-strike offsets

  const strikes = deltaMoneyness.map(dm => parseFloat((F0 * Math.exp(dm)).toFixed(4)));
  const vols = tenors.map((T, ti) => {
    const atmVol = atm_vol * (1 - 0.05 * ti); // term structure: vol declines with tenor
    return strikes.map((K, ki) => {
      const logStrike = Math.log(K / F0);
      // Skew: negative (downside more expensive), convexity
      const skew = -0.05 * logStrike;
      const convexity = 0.10 * logStrike * logStrike;
      return Math.max(atmVol + skew + convexity, 0.05);
    });
  });

  return { tenors, strikes, vols };
}

// ---------------------------------------------------------------------------
// Comparison: price & Greeks across strikes for both models
// ---------------------------------------------------------------------------

export function buildComparison(F, T, r, sigma_lognormal, sigma_normal, type = 'call') {
  const strikes = Array.from({ length: 41 }, (_, i) => F * (0.6 + i * 0.02));
  return strikes.map(K => ({
    K: parseFloat(K.toFixed(4)),
    b76: b76Price(F, K, T, r, sigma_lognormal, type),
    bach: bachPrice(F, K, T, r, sigma_normal, type),
    b76_delta: b76Greeks(F, K, T, r, sigma_lognormal, type).delta,
    bach_delta: bachGreeks(F, K, T, r, sigma_normal, type).delta,
  }));
}
