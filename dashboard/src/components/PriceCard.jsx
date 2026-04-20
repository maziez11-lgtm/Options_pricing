import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { exportToExcel } from '../lib/export';

function GreekCard({ label, value, description, color }) {
  return (
    <div className="greek-card" title={description}>
      <div className="greek-label">{label}</div>
      <div className="greek-value" style={{ color }}>{value}</div>
    </div>
  );
}

export default function PriceCard({ inputs, b76Price, b76Greeks, bachPrice, bachGreeks, comparison }) {
  const priceDiff = b76Price - bachPrice;

  function fmt(v, d = 4) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    return v.toFixed(d);
  }

  const greekMeta = [
    { key: 'delta', label: 'Δ Delta',  description: 'Price sensitivity to forward move', color: '#60a5fa' },
    { key: 'gamma', label: 'Γ Gamma',  description: 'Delta sensitivity to forward move', color: '#a78bfa' },
    { key: 'vega',  label: 'ν Vega',   description: 'Price sensitivity to vol change',   color: '#34d399' },
    { key: 'theta', label: 'Θ Theta',  description: 'Daily time decay (per calendar day)', color: '#f87171' },
    { key: 'vanna', label: 'Vanna',    description: 'd(delta)/d(vol) — mixed partial',    color: '#fb923c' },
    { key: 'volga', label: 'Volga',    description: 'd²V/d(vol)² — vol convexity',        color: '#e879f9' },
  ];

  function handleExport() {
    exportToExcel({
      inputs,
      price: b76Price,
      greeks: b76Greeks,
      comparison,
      model: inputs.F < 2 ? 'Bachelier' : 'Black-76',
    });
  }

  return (
    <div className="panel">
      <h2 className="panel-title">Pricing Results</h2>

      {/* Price comparison row */}
      <div className="price-row">
        <div className="price-block">
          <div className="price-model-label">Black-76</div>
          <div className="price-main">{fmt(b76Price)} <span className="unit">€/MWh</span></div>
        </div>
        <div className="price-divider" />
        <div className="price-block">
          <div className="price-model-label">Bachelier</div>
          <div className="price-main">{fmt(bachPrice)} <span className="unit">€/MWh</span></div>
        </div>
      </div>

      <div className="diff-badge" style={{ color: priceDiff >= 0 ? '#4ade80' : '#f87171' }}>
        {priceDiff >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        &nbsp;Difference: {fmt(Math.abs(priceDiff))} €/MWh
        &nbsp;({fmt(Math.abs(priceDiff / (bachPrice || 1) * 100), 2)}%)
      </div>

      {/* Greeks — Black-76 */}
      <h3 className="section-subtitle">Greeks — Black-76</h3>
      <div className="greeks-grid">
        {greekMeta.map(g => (
          <GreekCard
            key={g.key}
            label={g.label}
            value={fmt(b76Greeks?.[g.key], g.key === 'gamma' || g.key === 'vanna' || g.key === 'volga' ? 6 : 4)}
            description={g.description}
            color={g.color}
          />
        ))}
      </div>

      {/* Greeks — Bachelier */}
      <h3 className="section-subtitle" style={{ marginTop: '1.2rem' }}>Greeks — Bachelier</h3>
      <div className="greeks-grid">
        {greekMeta.map(g => (
          <GreekCard
            key={g.key}
            label={g.label}
            value={fmt(bachGreeks?.[g.key], g.key === 'gamma' || g.key === 'vanna' || g.key === 'volga' ? 6 : 4)}
            description={g.description}
            color={g.color}
          />
        ))}
      </div>

      <button className="export-btn" onClick={handleExport}>
        ⬇ Export to Excel
      </button>
    </div>
  );
}
