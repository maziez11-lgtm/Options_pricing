import * as XLSX from 'xlsx';

export function exportToExcel({ inputs, price, greeks, comparison, model }) {
  const wb = XLSX.utils.book_new();

  // Sheet 1 — Summary
  const summaryData = [
    ['TTF Options Pricing — Export', '', '', ''],
    ['Model', model, '', ''],
    ['Date', new Date().toISOString().slice(0, 10), '', ''],
    [],
    ['=== Inputs ===', '', '', ''],
    ['Forward Price (EUR/MWh)', inputs.F],
    ['Strike (EUR/MWh)', inputs.K],
    ['Time to Expiry (years)', inputs.T],
    ['Risk-Free Rate', inputs.r],
    ['Vol (σ)', inputs.sigma],
    ['Option Type', inputs.type],
    [],
    ['=== Price ===', '', '', ''],
    ['Price (EUR/MWh)', price],
    [],
    ['=== Greeks ===', '', '', ''],
    ['Delta', greeks.delta],
    ['Gamma', greeks.gamma],
    ['Vega', greeks.vega],
    ['Theta (per day)', greeks.theta],
    ['Rho (per 1pp)', greeks.rho],
    ['Vanna', greeks.vanna],
    ['Volga', greeks.volga],
  ];
  const ws1 = XLSX.utils.aoa_to_sheet(summaryData);
  ws1['!cols'] = [{ wch: 28 }, { wch: 18 }, { wch: 14 }, { wch: 14 }];
  XLSX.utils.book_append_sheet(wb, ws1, 'Summary');

  // Sheet 2 — Black-76 vs Bachelier comparison
  if (comparison && comparison.length > 0) {
    const header = ['Strike', 'Black-76 Price', 'Bachelier Price', 'Black-76 Delta', 'Bachelier Delta'];
    const rows = comparison.map(r => [r.K, r.b76?.toFixed(6), r.bach?.toFixed(6), r.b76_delta?.toFixed(6), r.bach_delta?.toFixed(6)]);
    const ws2 = XLSX.utils.aoa_to_sheet([header, ...rows]);
    ws2['!cols'] = header.map(() => ({ wch: 18 }));
    XLSX.utils.book_append_sheet(wb, ws2, 'Model Comparison');
  }

  XLSX.writeFile(wb, `TTF_Options_${model}_${new Date().toISOString().slice(0,10)}.xlsx`);
}
