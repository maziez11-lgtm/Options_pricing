# Repository Inventory — TTF Options

Snapshot of every branch and every tracked file with its last commit date and short SHA. Generated from the remote refs at the time of audit.

**Total branches:** 23

## Branch summary

| Branch | Latest commit | Date | Subject | Files |
|---|---|---|---|---|
| `origin/Dashboard` | `f94c4aa` | 2026-04-20 | Initial commit | 1 |
| `origin/Data` | `f94c4aa` | 2026-04-20 | Initial commit | 1 |
| `origin/Docs` | `caa1482` | 2026-04-22 | Merge pull request #7 from maziez11-lgtm/claude/finish-documentatio… | 48 |
| `origin/Pricing` | `f94c4aa` | 2026-04-20 | Initial commit | 1 |
| `origin/Spread` | `e41679d` | 2026-04-21 | feat: add b76_price_ttf and bach_price_ttf — price by contract name | 45 |
| `origin/Structures` | `e41679d` | 2026-04-21 | feat: add b76_price_ttf and bach_price_ttf — price by contract name | 45 |
| `origin/claude/add-vol-interpolation-cDcgm` | `ab3deb9` | 2026-04-28 | Merge pull request #20 from maziez11-lgtm/claude/add-vol-interpolat… | 58 |
| `origin/claude/complete-user-manual-NlQeR` | `bdc5ccd` | 2026-04-26 | docs: add Part 6 (financial glossary) to the user manual | 58 |
| `origin/claude/find-latest-docs-QJ8Oy` | `67a5c0c` | 2026-04-28 | docs(readme): align README with the ICE TFO calendar and the manual… | 58 |
| `origin/claude/finish-documentation-oN97r` | `a74abfc` | 2026-04-22 | feat: add ICE Endex official TTF options expiry calendar to black76… | 46 |
| `origin/claude/fix-ttf-expiry-calculation-XeHKp` | `abce643` | 2026-04-27 | fix: use raw calendar days / 365 in ttf_time_to_expiry | 58 |
| `origin/claude/jupyter-options-pricer-343IL` | `b2dd83c` | 2026-04-24 | test: extend test_suite.py with structures, spread, and edge cases | 56 |
| `origin/claude/pricing-feature-ea0hD` | `80b336a` | 2026-04-20 | fix(greeks): add missing rho to b76_greeks, add theta+rho to bach_g… | 12 |
| `origin/claude/rewrite-user-manual-english-on1Bj` | `2a73ea0` | 2026-04-26 | Regenerate user_manual.html and user_manual.pdf in English | 58 |
| `origin/claude/translate-reports-english-d5Q8p` | `130c6d4` | 2026-04-26 | docs: add Part 6 (financial glossary) to the user manual | 58 |
| `origin/claude/update-user-manual-pdf-Ae10o` | `a5bf23f` | 2026-04-26 | docs: regenerate user_manual.pdf from current user_manual.md | 58 |
| `origin/claude/user-manual-html-jGGp1` | `53e1559` | 2026-04-26 | docs: regenerate user_manual.html and .pdf from rewritten markdown | 58 |
| `origin/dashboard` | `f3d1323` | 2026-04-20 | fix(dashboard): correct Brent cond1 for b<a case, remove unused ki … | 43 |
| `origin/data` | `5a5776e` | 2026-04-20 | fix(data): 4 bugs + 2 style fixes in ttf_market_data.py | 20 |
| `origin/docs` | `2a29ed9` | 2026-04-25 | docs: add English sections for ttf_market_data.py and ttf_hh_spread.py | 52 |
| `origin/main` | `67a5c0c` | 2026-04-28 | docs(readme): align README with the ICE TFO calendar and the manual… | 58 |
| `origin/spread` | `81a91b1` | 2026-04-21 | feat: add ttf_hh_spread.py — TTF/Henry Hub spread option pricer (Ma… | 47 |
| `origin/structures` | `c898843` | 2026-04-21 | feat: add structures_ttf.py — 10 multi-leg option structure pricer | 46 |

---

## Per-branch file inventory

### `origin/Dashboard`

_Head: `f94c4aa` (2026-04-20) — Initial commit_

_1 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |

### `origin/Data`

_Head: `f94c4aa` (2026-04-20) — Initial commit_

_1 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |

### `origin/Docs`

_Head: `caa1482` (2026-04-22) — Merge pull request #7 from maziez11-lgtm/claude/finish-documentation-oN97r_

_48 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `black76_ttf.py` | 2026-04-21 | `e41679d` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.md` | 2026-04-21 | `6fa5a97` |

### `origin/Pricing`

_Head: `f94c4aa` (2026-04-20) — Initial commit_

_1 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |

### `origin/Spread`

_Head: `e41679d` (2026-04-21) — feat: add b76_price_ttf and bach_price_ttf — price by contract name_

_45 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-21 | `e41679d` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-20 | `4c691b4` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |

### `origin/Structures`

_Head: `e41679d` (2026-04-21) — feat: add b76_price_ttf and bach_price_ttf — price by contract name_

_45 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-21 | `e41679d` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-20 | `4c691b4` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |

### `origin/claude/add-vol-interpolation-cDcgm`

_Head: `ab3deb9` (2026-04-28) — Merge pull request #20 from maziez11-lgtm/claude/add-vol-interpolation-cDcgm_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-28 | `5015232` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-27 | `abce643` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-28 | `40dfc75` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `130c6d4` |
| `user_manual.md` | 2026-04-26 | `130c6d4` |
| `user_manual.pdf` | 2026-04-26 | `130c6d4` |

### `origin/claude/complete-user-manual-NlQeR`

_Head: `bdc5ccd` (2026-04-26) — docs: add Part 6 (financial glossary) to the user manual_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `bdc5ccd` |
| `user_manual.md` | 2026-04-26 | `bdc5ccd` |
| `user_manual.pdf` | 2026-04-26 | `bdc5ccd` |

### `origin/claude/find-latest-docs-QJ8Oy`

_Head: `67a5c0c` (2026-04-28) — docs(readme): align README with the ICE TFO calendar and the manual loader_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-28 | `67a5c0c` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-28 | `a87f8ff` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-28 | `a1c74a1` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-28 | `a1c74a1` |
| `user_manual.md` | 2026-04-28 | `a1c74a1` |
| `user_manual.pdf` | 2026-04-28 | `67a5c0c` |

### `origin/claude/finish-documentation-oN97r`

_Head: `a74abfc` (2026-04-22) — feat: add ICE Endex official TTF options expiry calendar to black76_ttf.py_

_46 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `black76_ttf.py` | 2026-04-22 | `a74abfc` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.md` | 2026-04-21 | `6fa5a97` |

### `origin/claude/fix-ttf-expiry-calculation-XeHKp`

_Head: `abce643` (2026-04-27) — fix: use raw calendar days / 365 in ttf_time_to_expiry_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-27 | `abce643` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `130c6d4` |
| `user_manual.md` | 2026-04-26 | `130c6d4` |
| `user_manual.pdf` | 2026-04-26 | `130c6d4` |

### `origin/claude/jupyter-options-pricer-343IL`

_Head: `b2dd83c` (2026-04-24) — test: extend test_suite.py with structures, spread, and edge cases_

_56 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-23 | `865d991` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-23 | `6cf28b8` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.md` | 2026-04-21 | `6fa5a97` |

### `origin/claude/pricing-feature-ea0hD`

_Head: `80b336a` (2026-04-20) — fix(greeks): add missing rho to b76_greeks, add theta+rho to bach_greeks_

_12 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-20 | `d1dd9dc` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `80b336a` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |

### `origin/claude/rewrite-user-manual-english-on1Bj`

_Head: `2a73ea0` (2026-04-26) — Regenerate user_manual.html and user_manual.pdf in English_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-23 | `865d991` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-23 | `6cf28b8` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `2a73ea0` |
| `user_manual.md` | 2026-04-26 | `786f475` |
| `user_manual.pdf` | 2026-04-26 | `2a73ea0` |

### `origin/claude/translate-reports-english-d5Q8p`

_Head: `130c6d4` (2026-04-26) — docs: add Part 6 (financial glossary) to the user manual_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `130c6d4` |
| `user_manual.md` | 2026-04-26 | `130c6d4` |
| `user_manual.pdf` | 2026-04-26 | `130c6d4` |

### `origin/claude/update-user-manual-pdf-Ae10o`

_Head: `a5bf23f` (2026-04-26) — docs: regenerate user_manual.pdf from current user_manual.md_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `130c6d4` |
| `user_manual.md` | 2026-04-26 | `130c6d4` |
| `user_manual.pdf` | 2026-04-26 | `a5bf23f` |

### `origin/claude/user-manual-html-jGGp1`

_Head: `53e1559` (2026-04-26) — docs: regenerate user_manual.html and .pdf from rewritten markdown_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `audit_report.md` | 2026-04-23 | `865d991` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-23 | `6cf28b8` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-26 | `53e1559` |
| `user_manual.md` | 2026-04-25 | `18e5185` |
| `user_manual.pdf` | 2026-04-26 | `53e1559` |

### `origin/dashboard`

_Head: `f3d1323` (2026-04-20) — fix(dashboard): correct Brent cond1 for b<a case, remove unused ki variable_

_43 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-20 | `d1dd9dc` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-20 | `4c691b4` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `f3d1323` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `ttf_market_data.py` | 2026-04-20 | `7719d52` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |

### `origin/data`

_Head: `5a5776e` (2026-04-20) — fix(data): 4 bugs + 2 style fixes in ttf_market_data.py_

_20 files._

| File | Last commit | SHA |
|---|---|---|
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-20 | `d1dd9dc` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `ttf_market_data.py` | 2026-04-20 | `5a5776e` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |

### `origin/docs`

_Head: `2a29ed9` (2026-04-25) — docs: add English sections for ttf_market_data.py and ttf_hh_spread.py_

_52 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-22 | `64784c1` |
| `black76_ttf.py` | 2026-04-23 | `98d5cb8` |
| `consistency_report.md` | 2026-04-23 | `6cf28b8` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-23 | `a06c29e` |
| `user_manual.md` | 2026-04-25 | `2a29ed9` |
| `user_manual.pdf` | 2026-04-23 | `a06c29e` |

### `origin/main`

_Head: `67a5c0c` (2026-04-28) — docs(readme): align README with the ICE TFO calendar and the manual loader_

_58 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-28 | `67a5c0c` |
| `audit_report.md` | 2026-04-26 | `cb1d798` |
| `black76_ttf.py` | 2026-04-28 | `a87f8ff` |
| `consistency_report.md` | 2026-04-26 | `cb1d798` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/Initialisation dossier` | 2026-04-23 | `f6cfb1c` |
| `dashboard/REACT_VITE.md` | 2026-04-23 | `0bd6ada` |
| `dashboard/README.md` | 2026-04-22 | `64784c1` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard_jupyter.ipynb` | 2026-04-24 | `4800ab3` |
| `dashboard_ttf.py` | 2026-04-23 | `3636458` |
| `file_structure.md` | 2026-04-23 | `1c3ae48` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `test_suite.py` | 2026-04-24 | `b2dd83c` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-28 | `a1c74a1` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |
| `user_manual.html` | 2026-04-28 | `a1c74a1` |
| `user_manual.md` | 2026-04-28 | `a1c74a1` |
| `user_manual.pdf` | 2026-04-28 | `67a5c0c` |

### `origin/spread`

_Head: `81a91b1` (2026-04-21) — feat: add ttf_hh_spread.py — TTF/Henry Hub spread option pricer (Margrabe)_

_47 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-21 | `e41679d` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-20 | `4c691b4` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `ttf_hh_spread.py` | 2026-04-21 | `81a91b1` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |

### `origin/structures`

_Head: `c898843` (2026-04-21) — feat: add structures_ttf.py — 10 multi-leg option structure pricer_

_46 files._

| File | Last commit | SHA |
|---|---|---|
| `.gitignore` | 2026-04-20 | `8dcfaad` |
| `README.md` | 2026-04-20 | `f94c4aa` |
| `black76_ttf.py` | 2026-04-21 | `e41679d` |
| `dashboard/.gitignore` | 2026-04-20 | `4c691b4` |
| `dashboard/README.md` | 2026-04-20 | `4c691b4` |
| `dashboard/eslint.config.js` | 2026-04-20 | `4c691b4` |
| `dashboard/index.html` | 2026-04-20 | `4c691b4` |
| `dashboard/package-lock.json` | 2026-04-20 | `4c691b4` |
| `dashboard/package.json` | 2026-04-20 | `4c691b4` |
| `dashboard/public/favicon.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/public/icons.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/App.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/hero.png` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/react.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/assets/vite.svg` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/GreeksChart.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/InputPanel.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/ModelComparison.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/PriceCard.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/components/VolSurface3D.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/src/index.css` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/export.js` | 2026-04-20 | `4c691b4` |
| `dashboard/src/lib/pricing.js` | 2026-04-20 | `4393f8d` |
| `dashboard/src/main.jsx` | 2026-04-20 | `4c691b4` |
| `dashboard/vite.config.js` | 2026-04-20 | `4c691b4` |
| `main.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/__init__.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/bachelier.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/binomial_tree.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black76.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/black_scholes.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/greeks.py` | 2026-04-20 | `ebcdfbf` |
| `pricing/implied_vol.py` | 2026-04-20 | `d1dd9dc` |
| `pricing/monte_carlo.py` | 2026-04-20 | `d1dd9dc` |
| `requirements.txt` | 2026-04-20 | `d1dd9dc` |
| `structures_ttf.py` | 2026-04-21 | `c898843` |
| `ttf_market_data.py` | 2026-04-21 | `31aa05a` |
| `ttf_output/ttf_forward_curve.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_forward_curve.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_sabr_params.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface.json` | 2026-04-20 | `40f4ff5` |
| `ttf_output/ttf_vol_surface_pivot.csv` | 2026-04-20 | `40f4ff5` |
| `ttf_time.py` | 2026-04-21 | `20cbca6` |

