# Structure du projet Options_pricing

Guide complet de l'arborescence du repo et des procédures d'installation pour
Windows et macOS.

---

## 1. Arborescence

```
Options_pricing/
├── README.md                        Vue d'ensemble + quick-start
├── requirements.txt                 Dépendances Python
├── consistency_report.md            Rapport de consistance (ce projet)
├── file_structure.md                Ce document
├── user_manual.md                   Manuel utilisateur complet (partie 3)
├── user_manual.html                 Version HTML autonome (CSS inline)
├── user_manual.pdf                  Version PDF imprimable
│
├── main.py                          Script démo (Black-76, Bachelier, PCP)
│
├── black76_ttf.py                   Pricer TTF Black-76 + Bachelier
├── ttf_time.py                      Utilitaires temps / day-count / calendar
├── ttf_market_data.py               Forward curve + vol surface + SABR
├── ttf_hh_spread.py                 Spread TTF/HH (Margrabe)
├── structures_ttf.py                10 structures multi-legs (straddle, etc.)
│
├── pricing/                         Bibliothèque core (bas niveau)
│   ├── __init__.py                  Exports du package
│   ├── black76.py                   Black-76 (pur)
│   ├── bachelier.py                 Bachelier (pur)
│   ├── black_scholes.py             Black-Scholes (pour options sur actions)
│   ├── greeks.py                    Greeks pour les 3 modèles
│   ├── binomial_tree.py             Arbre CRR (Américain / Européen)
│   ├── monte_carlo.py               Monte Carlo (vanille + Asiatique)
│   └── implied_vol.py               Solveurs Brent (Black-76 & Bachelier)
│
├── ttf_output/                      Données précalculées (exportées par ttf_market_data)
│   ├── ttf_forward_curve.csv / .json    12 contrats TTF (EUR/MWh)
│   ├── ttf_vol_surface.csv / .json      Surface (T × K × vol)
│   ├── ttf_vol_surface_pivot.csv        Même surface, format pivot
│   └── ttf_sabr_params.csv / .json      Params SABR calibrés (α, β, ρ, ν)
│
├── dashboard/                       Dashboard React + Vite
│   ├── README.md                    Guide dashboard
│   ├── package.json                 Dépendances npm
│   ├── package-lock.json            Lock file
│   ├── vite.config.js               Config Vite
│   ├── eslint.config.js             Règles ESLint
│   ├── index.html                   Point d'entrée HTML
│   ├── public/                      Assets statiques
│   │   ├── favicon.svg
│   │   └── icons.svg
│   └── src/
│       ├── main.jsx                 Bootstrap React
│       ├── App.jsx                  Composant racine
│       ├── App.css                  Styles globaux
│       ├── index.css                Reset CSS
│       ├── assets/                  Images, hero.png
│       ├── lib/
│       │   ├── pricing.js           Port JS de black76_ttf (Black-76 + Bachelier + Brent)
│       │   └── export.js            Export Excel (SheetJS / xlsx)
│       └── components/
│           ├── InputPanel.jsx       Sliders (F, K, T, r, σ, σ_n, type)
│           ├── PriceCard.jsx        Prix + Greeks + bouton export
│           ├── GreeksChart.jsx      Courbes Greeks vs strike (recharts)
│           ├── VolSurface3D.jsx     Surface 3D (plotly)
│           └── ModelComparison.jsx  B76 vs Bachelier (recharts)
│
└── .gitignore                       Python, Node, artefacts de build
```

---

## 2. Rôle de chaque fichier

### Scripts et modules Python à la racine

| Fichier | Rôle |
|---|---|
| `main.py` | Script de démo. Exécute un exemple Black-76 ATM, un Bachelier en scénario prix négatif, et vérifie la put-call parity. |
| `black76_ttf.py` | Point d'entrée principal. Contient `b76_call/put/greeks/implied_vol`, `bach_call/put/greeks/implied_vol`, `t_from_contract`, `b76_price_ttf` (pricing par code de contrat). |
| `ttf_time.py` | Librairie de calcul du temps (ACT/365, ACT/360, ACT/ACT, BUS/252), parseur de formats de dates, calendrier TARGET2 avec jours fériés ECB. |
| `ttf_market_data.py` | Construit la forward curve via Yahoo Finance (fallback synthétique), bâtit la vol surface (ATM + RR25 + BF25), calibre SABR par tenor, exporte en CSV/JSON. |
| `ttf_hh_spread.py` | Pricer d'option sur le spread TTF − HH via Margrabe. Gère la conversion EUR/MWh → USD/MMBtu, implied correlation, sensibilités. |
| `structures_ttf.py` | 10 structures multi-legs (straddle, strangle, bull/bear spread, butterfly, condor, collar, risk reversal, calendar spread, ratio spread). Retourne prix net, Greeks nets, P&L à l'expiry, breakevens, max profit/loss. |

### Package `pricing/`

| Fichier | Rôle |
|---|---|
| `__init__.py` | Expose `black76`, `bachelier`, `black_scholes`, `binomial_tree`, `monte_carlo`, `greeks`, `implied_vol`. |
| `black76.py` | Implémentation nue de Black-76 : `call_price`, `put_price`, `price`. |
| `bachelier.py` | Implémentation nue du modèle Bachelier (normal). |
| `black_scholes.py` | Black-Scholes pour options sur actions (avec `implied_volatility` Newton-Raphson). |
| `greeks.py` | Delta/Gamma/Vega/Theta/Rho/Vanna/Volga pour Black-76, Bachelier et Black-Scholes. |
| `binomial_tree.py` | Arbre CRR pour options Américaines ou Européennes. |
| `monte_carlo.py` | Simulation Monte Carlo (européen vanille + Asiatique arithmétique/géométrique). |
| `implied_vol.py` | Solveur Brent pour implied vol lognormale (Black-76) et normale (Bachelier). |

### Dashboard React

| Fichier | Rôle |
|---|---|
| `dashboard/src/App.jsx` | Compose sidebar (inputs) + content (prix, Greeks, surface 3D, comparaison). |
| `dashboard/src/lib/pricing.js` | Réimplémente Black-76 et Bachelier en JS (approximation erf Abramowitz). Brent pour implied vol. |
| `dashboard/src/lib/export.js` | Génère un `.xlsx` via SheetJS avec 2 feuilles (Summary + Model Comparison). |
| `dashboard/src/components/InputPanel.jsx` | Sliders pour F, K, T, r, σ (lognormal), σ_n (normal), et toggle call/put. |
| `dashboard/src/components/PriceCard.jsx` | Affiche prix Black-76 et Bachelier côte-à-côte + les 7 Greeks + bouton export. |
| `dashboard/src/components/GreeksChart.jsx` | Recharts : courbes Delta/Gamma/Vega/Theta/Vanna/Volga vs strike. |
| `dashboard/src/components/VolSurface3D.jsx` | Plotly : surface 3D σ(K, T) générée synthétiquement (skew + convexité). |
| `dashboard/src/components/ModelComparison.jsx` | Recharts : prix Black-76 vs Bachelier à travers la grille de strikes. |

### Outputs précalculés (`ttf_output/`)

Générés par `python ttf_market_data.py`. Rafraîchir ces fichiers = relancer le script. Ils sont commités pour que le dashboard et les exemples fonctionnent hors ligne.

---

## 3. Installation locale — Windows

### 3.1 Prérequis

- **Python 3.9+** — [python.org/downloads](https://www.python.org/downloads/)
  Cocher *"Add Python to PATH"* durant l'installation.
- **(Optionnel) Anaconda** — [anaconda.com/download](https://www.anaconda.com/download)
  Anaconda simplifie la gestion des environnements et pré-installe numpy/scipy/pandas.
- **Node.js 18+** — [nodejs.org](https://nodejs.org/) (uniquement pour le dashboard).
- **Git** — [git-scm.com/download/win](https://git-scm.com/download/win)
  Ou téléchargez manuellement depuis GitHub (voir 3.3 b).

### 3.2 Récupération du code depuis GitHub

**Option a — via `git clone`** :

Ouvrez **PowerShell** ou **cmd.exe** :
```bat
cd %USERPROFILE%\Documents
git clone https://github.com/maziez11-lgtm/options_pricing.git
cd options_pricing
```

**Option b — téléchargement manuel ZIP** :
1. Aller sur `https://github.com/maziez11-lgtm/options_pricing`
2. Bouton vert **Code** → **Download ZIP**
3. Décompresser dans `Documents/options_pricing`
4. Ouvrir PowerShell dans ce dossier (Shift + clic droit → *Ouvrir PowerShell ici*)

### 3.3 Installation des dépendances Python

**Option standard (pip + venv)** :
```bat
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install numpy scipy pandas matplotlib requests
```

**Option Anaconda** :
```bat
conda create -n ttf python=3.11
conda activate ttf
conda install numpy scipy pandas matplotlib requests jupyter
```

> **NB** : `requirements.txt` ne liste actuellement que numpy et scipy. Pour
> `ttf_market_data.py` (DataFrame / Yahoo Finance) il faut aussi `pandas` et
> `requests`. `matplotlib` n'est pas requis par le code mais est utile pour
> afficher des graphiques dans Jupyter.

### 3.4 Test de l'installation

```bat
python main.py
python black76_ttf.py
python structures_ttf.py
python ttf_hh_spread.py
python ttf_market_data.py
```

Vous devriez voir les prix, les Greeks et la surface vol s'afficher dans le terminal.

### 3.5 Lancement dans Jupyter

**Démarrer Jupyter Notebook** :
```bat
.venv\Scripts\activate   # si venv
jupyter notebook
```

Dans le navigateur, créer un notebook Python 3 et saisir :

```python
from black76_ttf import b76_call, b76_greeks, b76_price_ttf
from datetime import date

# Exemple : call ATM sur TTF Jun-26, valorisé le 23 avril 2026
price = b76_price_ttf(
    F=30.0, K=30.0,
    contract="TTFM26",
    r=0.025, sigma=0.50,
    option_type="call",
    reference=date(2026, 4, 23)
)
print(f"Prix call : {price:.4f} EUR/MWh")

g = b76_greeks(F=30.0, K=30.0, T=0.25, r=0.025, sigma=0.50)
print(f"Delta = {g.delta:.4f}  Vega = {g.vega:.4f}")
```

Pour les structures multi-legs :
```python
from structures_ttf import straddle, butterfly, print_summary

res = straddle(F=30.0, K=30.0, T=0.25, r=0.025, sigma=0.50)
print_summary(res)
```

Pour le spread TTF/HH :
```python
from ttf_hh_spread import spread_price, print_summary

res = spread_price(
    F_ttf_eur=30.0, F_hh=3.0, fx_eurusd=1.08,
    T=0.5, r_usd=0.045,
    sigma_ttf=0.60, sigma_hh=0.50, rho=0.35,
    option_type="call"
)
print_summary(res)
```

### 3.6 Lancement du dashboard React (Windows)

```bat
cd dashboard
npm install
npm run dev
```

Ouvrir `http://localhost:5173` dans votre navigateur.

Pour produire une version statique déployable :
```bat
npm run build
# Sortie dans dashboard/dist/
```

---

## 4. Installation locale — macOS

### 4.1 Prérequis

- **Python 3.9+** — `brew install python@3.11` (ou `python.org/downloads`)
- **(Optionnel) Anaconda** — `brew install --cask anaconda` ou `anaconda.com/download`
- **Node.js 18+** — `brew install node`
- **Git** — fourni par Xcode Command Line Tools : `xcode-select --install`

### 4.2 Récupération du code depuis GitHub

```bash
cd ~/Documents
git clone https://github.com/maziez11-lgtm/options_pricing.git
cd options_pricing
```

Sans Git, téléchargez le ZIP (voir section Windows) et décompressez dans `~/Documents/options_pricing`.

### 4.3 Installation des dépendances Python

**Avec venv (recommandé)** :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy scipy pandas matplotlib requests
```

**Avec Anaconda** :
```bash
conda create -n ttf python=3.11
conda activate ttf
conda install numpy scipy pandas matplotlib requests jupyter
```

### 4.4 Test de l'installation

```bash
python3 main.py
python3 black76_ttf.py
python3 structures_ttf.py
python3 ttf_hh_spread.py
python3 ttf_market_data.py
```

### 4.5 Lancement dans Jupyter

```bash
source .venv/bin/activate
jupyter notebook
```

Mêmes exemples que pour Windows.

### 4.6 Lancement du dashboard React (macOS)

```bash
cd dashboard
npm install
npm run dev
```

Ouvrir `http://localhost:5173` dans Safari/Chrome.

---

## 5. Où modifier quoi ?

| Besoin | Fichier à modifier |
|---|---|
| Changer le taux sans risque par défaut | `black76_ttf.py` (pas de constante, passer `r` en argument) |
| Ajouter une nouvelle structure multi-legs | `structures_ttf.py` (suivre le pattern des 10 existantes) |
| Changer la convention day-count | Passer `convention="bus252"` etc. à `time_to_maturity` dans `ttf_time.py` |
| Remplacer Yahoo Finance par une autre source | `ttf_market_data.py::TTFForwardCurve._fetch_spot` |
| Ajuster les ATM vols par défaut du surface builder | `ttf_market_data.py::VolatilitySurfaceBuilder._ATM_VOLS` |
| Ajouter un onglet dans le dashboard | Créer un composant dans `dashboard/src/components/` et l'importer dans `App.jsx` |
| Changer les couleurs du dashboard | `dashboard/src/App.css` |
| Ajouter une colonne à l'export Excel | `dashboard/src/lib/export.js::exportToExcel` |

---

## 6. Checklist rapide « ça marche »

Après installation, ces 5 commandes doivent toutes passer sans erreur :

```bash
python3 main.py                 # demo Black-76 + Bachelier + PCP
python3 black76_ttf.py          # test complet du pricer TTF
python3 structures_ttf.py       # 10 structures avec résumé
python3 ttf_hh_spread.py        # spread TTF/HH + implied corr
python3 ttf_market_data.py      # forward curve + vol surface + SABR
```

Côté dashboard :
```bash
cd dashboard && npm install && npm run dev
```
Puis vérifier dans le navigateur que les 5 panneaux (InputPanel, PriceCard,
GreeksChart, VolSurface3D, ModelComparison) s'affichent correctement et que
le bouton **Export to Excel** télécharge bien un `.xlsx`.
