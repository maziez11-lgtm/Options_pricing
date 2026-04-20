import React, { useState, useMemo } from 'react';
import InputPanel from './components/InputPanel';
import PriceCard from './components/PriceCard';
import GreeksChart from './components/GreeksChart';
import VolSurface3D from './components/VolSurface3D';
import ModelComparison from './components/ModelComparison';
import { b76Price, b76Greeks, bachPrice, bachGreeks, buildComparison } from './lib/pricing';
import './App.css';

const DEFAULT_INPUTS = {
  F: 35.0,
  K: 35.0,
  T: 0.25,
  r: 0.03,
  sigma: 0.50,
  sigma_n: 8.0,
  type: 'call',
};

export default function App() {
  const [inputs, setInputs] = useState(DEFAULT_INPUTS);
  const { F, K, T, r, sigma, sigma_n, type } = inputs;

  const b76P  = useMemo(() => b76Price(F, K, T, r, sigma, type),              [F, K, T, r, sigma, type]);
  const b76G  = useMemo(() => b76Greeks(F, K, T, r, sigma, type),             [F, K, T, r, sigma, type]);
  const bachP = useMemo(() => bachPrice(F, K, T, r, sigma_n, type),           [F, K, T, r, sigma_n, type]);
  const bachG = useMemo(() => bachGreeks(F, K, T, r, sigma_n, type),          [F, K, T, r, sigma_n, type]);
  const comp  = useMemo(() => buildComparison(F, T, r, sigma, sigma_n, type), [F, T, r, sigma, sigma_n, type]);

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <div>
              <div className="logo-title">TTF Options Pricer</div>
              <div className="logo-sub">Natural Gas Futures · Black-76 &amp; Bachelier · EUR/MWh</div>
            </div>
          </div>
          <div className="header-badges">
            <span className="badge badge-green">● Live</span>
            <span className="badge badge-blue">ICE TTF</span>
          </div>
        </div>
      </header>

      <main className="main-grid">
        <aside className="sidebar">
          <InputPanel inputs={inputs} onChange={setInputs} />
        </aside>

        <section className="content">
          <PriceCard
            inputs={inputs}
            b76Price={b76P}
            b76Greeks={b76G}
            bachPrice={bachP}
            bachGreeks={bachG}
            comparison={comp}
          />

          <div className="two-col">
            <GreeksChart inputs={inputs} />
            <ModelComparison inputs={inputs} />
          </div>

          <VolSurface3D inputs={inputs} />
        </section>
      </main>

      <footer className="footer">
        TTF Options Pricer · Black-76 &amp; Bachelier models · All prices indicative only
      </footer>
    </div>
  );
}
