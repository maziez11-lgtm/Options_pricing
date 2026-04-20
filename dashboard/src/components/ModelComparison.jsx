import React, { useMemo, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { buildComparison } from '../lib/pricing';

const VIEWS = [
  { key: 'price', b76Key: 'b76',       bachKey: 'bach',       label: 'Price (€/MWh)' },
  { key: 'delta', b76Key: 'b76_delta', bachKey: 'bach_delta', label: 'Delta' },
];

export default function ModelComparison({ inputs }) {
  const [view, setView] = useState('price');
  const { F, T, r, sigma, sigma_n, type } = inputs;

  const data = useMemo(
    () => buildComparison(F, T, r, sigma, sigma_n, type),
    [F, T, r, sigma, sigma_n, type]
  );

  const current = VIEWS.find(v => v.key === view);

  return (
    <div className="panel">
      <div className="panel-header-row">
        <h2 className="panel-title">Black-76 vs Bachelier Comparison</h2>
        <div className="greek-tabs">
          {VIEWS.map(v => (
            <button
              key={v.key}
              className={`greek-tab ${view === v.key ? 'active' : ''}`}
              style={view === v.key ? { borderColor: '#60a5fa', color: '#60a5fa' } : {}}
              onClick={() => setView(v.key)}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3e" />
          <XAxis
            dataKey="K"
            tickFormatter={v => v.toFixed(0)}
            label={{ value: 'Strike (€/MWh)', position: 'insideBottom', offset: -4, fill: '#9ca3af', fontSize: 11 }}
            tick={{ fill: '#9ca3af', fontSize: 11 }}
          />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} width={60} />
          <Tooltip
            contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
            labelStyle={{ color: '#e2e8f0' }}
            formatter={(v, name) => [v?.toFixed(6), name]}
            labelFormatter={v => `K = ${parseFloat(v).toFixed(2)} €/MWh`}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
          <ReferenceLine x={parseFloat(F.toFixed(2))} stroke="#facc15" strokeDasharray="4 3"
            label={{ value: 'F (ATM)', fill: '#facc15', fontSize: 11 }} />
          <Line type="monotone" dataKey={current.b76Key}  name="Black-76"  stroke="#60a5fa" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey={current.bachKey} name="Bachelier" stroke="#34d399" dot={false} strokeWidth={2} strokeDasharray="5 3" />
        </LineChart>
      </ResponsiveContainer>

      <div className="comparison-legend">
        <div className="legend-item"><span className="dot" style={{ background: '#60a5fa' }} /> Black-76: lognormal vol σ = {(sigma * 100).toFixed(0)}% — suited for positive prices</div>
        <div className="legend-item"><span className="dot" style={{ background: '#34d399' }} /> Bachelier: normal vol σₙ = {sigma_n.toFixed(1)} €/MWh — handles negative prices</div>
      </div>
    </div>
  );
}
