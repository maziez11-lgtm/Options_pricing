import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { b76Greeks, bachGreeks } from '../lib/pricing';

const GREEK_OPTIONS = [
  { key: 'delta', label: 'Delta',  color: '#60a5fa' },
  { key: 'gamma', label: 'Gamma',  color: '#a78bfa' },
  { key: 'vega',  label: 'Vega',   color: '#34d399' },
  { key: 'theta', label: 'Theta',  color: '#f87171' },
  { key: 'vanna', label: 'Vanna',  color: '#fb923c' },
  { key: 'volga', label: 'Volga',  color: '#e879f9' },
];

export default function GreeksChart({ inputs }) {
  const [selected, setSelected] = React.useState('delta');
  const { F, T, r, sigma, sigma_n, type } = inputs;

  const data = useMemo(() => {
    const strikes = Array.from({ length: 61 }, (_, i) => F * (0.5 + i * 0.017));
    return strikes.map(K => {
      const g76   = b76Greeks(F, K, T, r, sigma, type);
      const gBach = bachGreeks(F, K, T, r, sigma_n, type);
      return {
        K: parseFloat(K.toFixed(2)),
        b76:  g76[selected],
        bach: gBach[selected],
      };
    });
  }, [F, T, r, sigma, sigma_n, type, selected]);

  const meta = GREEK_OPTIONS.find(g => g.key === selected);

  return (
    <div className="panel">
      <div className="panel-header-row">
        <h2 className="panel-title">Greeks Profile</h2>
        <div className="greek-tabs">
          {GREEK_OPTIONS.map(g => (
            <button
              key={g.key}
              className={`greek-tab ${selected === g.key ? 'active' : ''}`}
              style={selected === g.key ? { borderColor: g.color, color: g.color } : {}}
              onClick={() => setSelected(g.key)}
            >
              {g.label}
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
          <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} width={56} />
          <Tooltip
            contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
            labelStyle={{ color: '#e2e8f0' }}
            formatter={(v) => v?.toFixed(6)}
            labelFormatter={v => `K = ${v} €/MWh`}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
          <ReferenceLine x={parseFloat(F.toFixed(2))} stroke="#facc15" strokeDasharray="4 3" label={{ value: 'F', fill: '#facc15', fontSize: 11 }} />
          <Line type="monotone" dataKey="b76"  name="Black-76"  stroke="#60a5fa" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="bach" name="Bachelier" stroke="#34d399" dot={false} strokeWidth={2} strokeDasharray="5 3" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
