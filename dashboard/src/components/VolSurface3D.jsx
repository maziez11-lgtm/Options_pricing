import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { buildVolSurface } from '../lib/pricing';

export default function VolSurface3D({ inputs }) {
  const { F, sigma } = inputs;

  const { tenors, strikes, vols } = useMemo(
    () => buildVolSurface(F, inputs.r, sigma),
    [F, inputs.r, sigma]
  );

  const tenorLabels = tenors.map(t => {
    if (t < 1 / 11) return '1M';
    if (t < 3 / 11) return '2M';
    if (t < 4 / 11) return '3M';
    if (t < 7 / 11) return '6M';
    if (t < 11 / 11) return '9M';
    if (t < 1.5)    return '1Y';
    return '2Y';
  });

  return (
    <div className="panel">
      <h2 className="panel-title">Volatility Surface — Black-76 (3D)</h2>
      <Plot
        data={[
          {
            type: 'surface',
            x: strikes,
            y: tenorLabels,
            z: vols,
            colorscale: [
              [0,    '#1e3a5f'],
              [0.25, '#2563eb'],
              [0.5,  '#7c3aed'],
              [0.75, '#db2777'],
              [1,    '#ef4444'],
            ],
            contours: {
              z: { show: true, usecolormap: true, highlightcolor: '#fff', project: { z: true } },
            },
            opacity: 0.92,
            hovertemplate:
              'Strike: %{x:.2f} €/MWh<br>Tenor: %{y}<br>Vol: %{z:.2%}<extra></extra>',
          },
        ]}
        layout={{
          paper_bgcolor: '#0f0f1a',
          plot_bgcolor: '#0f0f1a',
          font: { color: '#e2e8f0', size: 11 },
          margin: { t: 10, r: 10, b: 10, l: 10 },
          scene: {
            bgcolor: '#0f0f1a',
            xaxis: { title: 'Strike (€/MWh)', gridcolor: '#2a2a3e', color: '#9ca3af' },
            yaxis: { title: 'Tenor',          gridcolor: '#2a2a3e', color: '#9ca3af' },
            zaxis: {
              title: 'Vol (σ)',
              gridcolor: '#2a2a3e',
              color: '#9ca3af',
              tickformat: '.0%',
            },
            camera: { eye: { x: 1.6, y: -1.6, z: 0.9 } },
          },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '380px' }}
      />
    </div>
  );
}
