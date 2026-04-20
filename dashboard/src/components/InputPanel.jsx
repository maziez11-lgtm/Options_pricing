import React from 'react';

function Slider({ label, value, min, max, step, onChange, format }) {
  return (
    <div className="input-group">
      <div className="input-label-row">
        <label>{label}</label>
        <span className="input-value">{format ? format(value) : value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}

export default function InputPanel({ inputs, onChange }) {
  const set = (key) => (val) => onChange({ ...inputs, [key]: val });

  return (
    <div className="panel">
      <h2 className="panel-title">Market Inputs</h2>

      <Slider
        label="Forward Price F"
        value={inputs.F}
        min={5} max={120} step={0.5}
        onChange={set('F')}
        format={v => `${v.toFixed(1)} €/MWh`}
      />
      <Slider
        label="Strike K"
        value={inputs.K}
        min={5} max={120} step={0.5}
        onChange={set('K')}
        format={v => `${v.toFixed(1)} €/MWh`}
      />
      <Slider
        label="Time to Expiry T"
        value={inputs.T}
        min={0.01} max={3} step={0.01}
        onChange={set('T')}
        format={v => `${v.toFixed(2)} y (${Math.round(v * 365)} d)`}
      />
      <Slider
        label="Risk-Free Rate r"
        value={inputs.r}
        min={0} max={0.10} step={0.001}
        onChange={set('r')}
        format={v => `${(v * 100).toFixed(2)}%`}
      />
      <Slider
        label="Lognormal Vol σ (Black-76)"
        value={inputs.sigma}
        min={0.01} max={2.5} step={0.01}
        onChange={set('sigma')}
        format={v => `${(v * 100).toFixed(0)}%`}
      />
      <Slider
        label="Normal Vol σₙ (Bachelier)"
        value={inputs.sigma_n}
        min={0.1} max={50} step={0.1}
        onChange={set('sigma_n')}
        format={v => `${v.toFixed(1)} €/MWh`}
      />

      <div className="toggle-row">
        <span>Option Type</span>
        <div className="toggle-buttons">
          {['call', 'put'].map(t => (
            <button
              key={t}
              className={`toggle-btn ${inputs.type === t ? 'active' : ''}`}
              onClick={() => onChange({ ...inputs, type: t })}
            >
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="moneyness-badge" style={{
        color: inputs.F > inputs.K ? '#4ade80' : inputs.F < inputs.K ? '#f87171' : '#facc15'
      }}>
        {inputs.F > inputs.K ? 'ITM' : inputs.F < inputs.K ? 'OTM' : 'ATM'}
        &nbsp;·&nbsp;
        {inputs.type === 'call'
          ? `Intrinsic: ${Math.max(inputs.F - inputs.K, 0).toFixed(2)} €/MWh`
          : `Intrinsic: ${Math.max(inputs.K - inputs.F, 0).toFixed(2)} €/MWh`}
      </div>
    </div>
  );
}
