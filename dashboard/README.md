# TTF Options Dashboard

Interactive React + Vite dashboard for visualising TTF natural gas option prices, Greeks, and vol surfaces.

## Running Locally

```bash
cd dashboard
npm install
npm run dev
# Opens at http://localhost:5173
```

## Features

| Tab | Description |
|-----|-------------|
| **Pricer** | Price a single call or put using Black-76 or Bachelier; displays full Greeks (Δ, Γ, ν, Θ, ρ, Vanna, Volga) |
| **Vol Surface** | Interactive 3D implied vol surface across strikes and maturities |
| **Greeks Chart** | Delta, Gamma, Vega plotted against strike — B76 and Bachelier side-by-side |
| **Comparison** | Price comparison table: Black-76 vs Bachelier across the strike range |

Click **Export to Excel** in any tab to download a `.xlsx` file of the current results.

## Build for Production

```bash
npm run build
# Output in dist/
```

The `dist/` folder can be served by any static file host (Nginx, Vercel, GitHub Pages, etc.).

## Tech Stack

- [React](https://react.dev/) + [Vite](https://vitejs.dev/) (HMR, fast dev server)
- Pricing logic mirrors `black76_ttf.py` — Brent's method for implied vol, Black-76 and Bachelier models implemented in JavaScript
- Excel export via [SheetJS (xlsx)](https://sheetjs.com/)
