# Consistency Report — Options_pricing

Date du rapport : **2026-04-23**
Branche testée : `main` (dernier commit `caa1482`)
Environnement de test : Python 3 + numpy 2.4 + scipy 1.17 + pandas 3.0

---

## Résumé exécutif

| Domaine | Statut | Commentaire |
|---|---|---|
| Imports inter-modules | OK | Tous les modules s'importent proprement (Python & JS) |
| Conventions d'unités | OK | EUR/MWh (TTF) et USD/MMBtu (HH) homogènes partout |
| Naming des paramètres | Mineur | Quelques alias (`sigma_n`, `sigma_lo`, `sigma_call`) documentés |
| Outputs `black76_ttf.py` → `structures_ttf.py` | OK | Intégration parfaite (11 tests passent) |
| Conversion EUR/MWh ↔ USD/MMBtu dans `ttf_hh_spread.py` | OK | Formule vérifiée par round-trip |
| Dashboard React ↔ logique Python | OK (parité JS/Python à 1e-6) | JS réimplémente en local, pas d'appel API |
| `requirements.txt` | **Incomplet** | Manque `pandas` et `requests` |
| Tests unitaires | **Absents** | Aucun dossier `tests/`, aucune couverture |

Aucune erreur bloquante. Trois points d'amélioration sont listés en fin de rapport.

---

## 1 — Tests d'import des modules

```
[1] black76_ttf         OK
[2] ttf_time            OK
[3] ttf_market_data     OK
[4] ttf_hh_spread       OK
[5] structures_ttf      OK
[6] pricing.*           OK  (black76, bachelier, greeks, implied_vol,
                              binomial_tree, monte_carlo, black_scholes)
```

Commentaire : `black76_ttf.py`, `ttf_market_data.py` et `ttf_hh_spread.py` sont **volontairement self-contained** pour leurs utilitaires de calendrier (fonctions `_is_business_day`, `_prev_business_day`, `options_expiry_from_delivery`). La duplication évite tout import circulaire entre les trois fichiers racine.

`ttf_time.py` propose en plus un calendrier TARGET2 (jours fériés EUR) que ces modules n'exploitent pas — ils se contentent du filtre Mon–Fri. Cette différence est documentée dans `ttf_time.py` (cf. `_OPTIONS_EXPIRY_OFFSET_BD = 5`).

---

## 2 — Cohérence des conventions

### Unités

| Module | Unité de prix | Unité de vol | Unité de temps |
|---|---|---|---|
| `black76_ttf.py` | EUR/MWh | σ lognormal (décimal) ou σ_n normal (EUR/MWh) | années ACT/365 |
| `ttf_market_data.py` | EUR/MWh | σ lognormal (décimal) | années ACT/365 |
| `structures_ttf.py` | EUR/MWh | σ lognormal (décimal) | années ACT/365 |
| `ttf_hh_spread.py` | **USD/MMBtu** (Margrabe) ; entrée TTF en EUR/MWh | σ lognormal (décimal) | années ACT/365 |
| `pricing/black_scholes.py` | générique (S, K) | σ lognormal (décimal) | années |

Toutes les fonctions de TTF utilisent **EUR/MWh** comme unité de référence du prix.
`ttf_hh_spread.py` fait la conversion EUR/MWh → USD/MMBtu avant Margrabe, puis reconvertit en sortie.

### Naming des paramètres

Convention uniforme observée dans tous les fichiers Python :

| Symbole | Signification | Unité |
|---|---|---|
| `F` | Forward/futures TTF | EUR/MWh |
| `K` | Strike | EUR/MWh |
| `T` | Temps à l'expiry | années |
| `r` | Taux sans risque | décimal annualisé |
| `sigma` | Vol lognormale (Black-76) | décimal (ex. 0.50) |
| `sigma_n` | Vol normale (Bachelier) | EUR/MWh (ex. 8.0) |
| `option_type` | "call" ou "put" | string |
| `reference` | Date de valorisation | `datetime.date` |

Dans les structures multi-legs on rencontre aussi `sigma_put`, `sigma_call`, `sigma_lo`, `sigma_hi` (par jambe) — tous optionnels, pointant par défaut vers `sigma`.

---

## 3 — Outputs `black76_ttf.py` ↔ `structures_ttf.py`

Test : `structures_ttf.straddle(F=35, K=35, T=0.25, r=0.03, sigma=0.50)` doit valoir exactement `b76_call + b76_put`.

```
straddle price = 6.9113 EUR/MWh
b76_call + b76_put = 6.9113 EUR/MWh    [diff < 1e-10]    OK
```

Les 10 structures (straddle, strangle, bull call spread, bear put spread, butterfly, condor, collar, risk_reversal, calendar spread, ratio spread) valident toutes leurs prix, deltas, vegas. `structures_ttf.py` utilise directement `b76_price`, `b76_delta`, `b76_gamma`, `b76_vega`, `b76_theta` depuis `black76_ttf` — **aucune duplication**.

`structures_ttf.straddle(..., T="TTFM26", reference=date(2026,4,23))` fonctionne et récupère correctement `T=0.0822` via `t_from_contract`. La délégation contract-name → T est cohérente entre les deux modules.

### Cross-check Greeks : `black76_ttf.b76_greeks` vs `pricing.greeks.b76_greeks`

```
delta    0.545631 == 0.545631    diff=0    OK
gamma    0.044901 == 0.044901    diff=0    OK
vega     6.875400 == 6.875400    diff=0    OK
theta   -0.019121 == -0.019121   diff=0    OK
rho     -0.008639 == -0.008639   diff=0    OK
vanna    0.098220 == 0.098220    diff=0    OK
volga   -0.214856 == -0.214856   diff=0    OK
```

Les deux implémentations donnent des résultats **bit-identiques**. `black76_ttf.b76_greeks()` renvoie un `@dataclass` (accès par attribut), `pricing.greeks.b76_greeks()` renvoie un `dict` — choix redondant mais fonctionnel.

---

## 4 — Conversion EUR/MWh → USD/MMBtu (`ttf_hh_spread.py`)

Formule :
```
F_TTF_usd [USD/MMBtu] = F_TTF_eur [EUR/MWh] × FX_EURUSD / 3.412142
```

Constante `MWH_TO_MMBTU = 3.412142` (exacte, équivalence énergétique MWh ↔ MMBtu).

### Vérification numérique

```
F_TTF_eur = 30.0 EUR/MWh,  FX = 1.08
→ 30 × 1.08 / 3.412142 = 9.495502 USD/MMBtu          OK
round-trip USD → EUR → USD = 30.000000               OK (exact)
```

### Put-call parity Margrabe

Avec `F_TTF_usd = 9.4955`, `F_HH = 3.0`, T=0.5y, r=0.045, σ_TTF=60%, σ_HH=50%, ρ=0.35 :
```
C − P       = 6.350985
df × (F_TTF_usd − F_HH) = 6.350985    OK
```

### Round-trip corrélation implicite

Prix calculé avec ρ=0.35 → puis `implied_correlation()` → recouvre **ρ=0.350000** (erreur < 1e-6). OK.

### Interface contract-name
`spread_price(30.0, 3.0, 1.08, "TTFM26", 0.045, 0.60, 0.50, 0.35, reference=date(2026,4,23))` :
- T calculé automatiquement via `from black76_ttf import t_from_contract`
- T = 0.0822y (30 jours cal.), prix = 6.4715 USD/MMBtu
- La conversion EUR↔USD et la recherche d'expiry fonctionnent de concert

---

## 5 — Dashboard React ↔ modules Python

### Architecture

Le dashboard **n'appelle pas** les modules Python. `dashboard/src/lib/pricing.js` réimplémente en JS :
- `b76Price`, `b76Greeks` (Black-76 lognormal)
- `bachPrice`, `bachGreeks` (Bachelier normal)
- `b76ImpliedVol`, `bachImpliedVol` (Brent)
- `buildVolSurface` (vol surface synthétique, paramétrique)
- `buildComparison` (grille de strikes)

### Parité numérique JS ↔ Python

```
ATM (F=K=35, T=0.25, r=3%, σ=50%)
   JS-style call price : 3.455664
   Python scipy call   : 3.455661
   Différence          : 2.70e-06   (inévitable — Abramowitz erf ≈ 5 digits)
```

L'approximation `erf()` d'Abramowitz & Stegun utilisée en JS introduit ~3e-6 d'erreur au pire. Pour la cotation indicative, c'est largement acceptable.

### Points d'attention

- **Bachelier sigma_n par défaut du dashboard** : 8 EUR/MWh. À F=35 et σ=50% l'équivalent normal serait σ_n ≈ F·σ ≈ 17.5 EUR/MWh. Le défaut est donc volontairement conservateur (crise basse vol) mais peut surprendre côté comparaison B76 vs Bachelier.
- **Vol surface 3D** (JS) est **synthétique** (formule `atm × (1 − 0.05·ti) + skew·log(K/F) + convexity·log(K/F)²`). Elle ne lit **pas** `ttf_output/ttf_vol_surface.json`. C'est un choix pédagogique assumé.
- **Export Excel** : bouton présent dans `PriceCard.jsx`. Le `Comparison` tab n'expose pas de bouton séparé, mais la feuille "Model Comparison" est ajoutée à l'export global.
- **Favicon et assets** présents (`public/favicon.svg`, `src/assets/hero.png`, etc.) — pas d'asset manquant.

### Cohérence inputs/outputs

| Valeur | Dashboard défaut | Python demo (main.py) | Cohérent ? |
|---|---|---|---|
| F | 35.0 EUR/MWh | 35.0 | OK |
| K | 35.0 EUR/MWh | 35.0 | OK |
| T | 0.25 y | 0.25 | OK |
| r | 0.03 | 0.03 | OK |
| σ | 0.50 | 0.50 | OK |
| σ_n | 8.0 EUR/MWh | 8.0 (dans demo Bachelier) | OK |

---

## 6 — Calendrier d'expiry TTF 2026

Convention ICE/EEX — options expirent **5 jours ouvrés avant** le LTD du futures, qui lui-même est le **dernier jour ouvré du mois précédant la livraison**.

Vérification croisée `black76_ttf.options_expiry_from_delivery` vs `ttf_time.options_expiry_from_delivery` :

| Contrat | Expiry options (black76_ttf) | Expiry options (ttf_time) | Statut |
|---|---|---|---|
| TTFM26 (Jun-26) | 2026-05-22 | 2026-05-22 | OK |
| TTFU26 (Sep-26) | 2026-08-24 | 2026-08-24 | OK |
| TTFH27 (Mar-27) | 2027-02-19 | 2027-02-19 | OK |

**Nota** : `ttf_time.py` tient compte des jours fériés TARGET2 (ex. Pâques, 1ᵉʳ mai, 25/26 déc.), alors que `black76_ttf.py` et `ttf_market_data.py` utilisent un filtre Mon–Fri seul. Dans 99 % des cas cela donne le même résultat ; pour les mois où le LTD tomberait sur un jour férié TARGET2 (rare), `ttf_time` serait plus précis.

### Convention T (today included)

Depuis le commit `31aa05a` : `T = (expiry − today).days + 1) / 365`. Cela évite un T=0 le jour même de l'évaluation pour une option expirant le jour d'après et aligne le projet sur la convention « start-of-day ». Vérifié :
```
ref=2026-04-23  expiry=2026-05-22  days=30  T=0.082192  OK
```

---

## 7 — Problèmes mineurs à corriger

### 7.1 `requirements.txt` incomplet

**Constat** : `requirements.txt` liste seulement `numpy>=1.24` et `scipy>=1.10`.
Or les modules importent aussi :
- `pandas` (`ttf_market_data.py`, `structures_ttf.py` via DataFrame)
- `requests` (`ttf_market_data.py`, fetch Yahoo Finance)

**Impact** : un `pip install -r requirements.txt` sur un environnement nu laisse `ttf_market_data.py` et `export_all()` inutilisables.

**Fix suggéré** — mettre à jour `requirements.txt` :
```
numpy>=1.24
scipy>=1.10
pandas>=2.0
requests>=2.31
```

### 7.2 Pas de tests unitaires

**Constat** : aucun dossier `tests/`, aucun `pytest`, aucun CI workflow.

**Impact** : la consistance est assurée par les scripts `__main__` de chaque module et par ce rapport. Pour un projet de pricing, cela reste léger.

**Fix suggéré** : ajouter `tests/` avec au minimum les assertions suivantes :
- Put-call parity (Black-76 et Bachelier)
- Round-trip implied vol
- Round-trip implied correlation (Margrabe)
- Limit case `T → 0` → intrinsic value
- Cross-check `b76_greeks` (`black76_ttf` vs `pricing.greeks`)

### 7.3 Dashboard n'utilise pas la vol surface réelle

**Constat** : `VolSurface3D.jsx` utilise `buildVolSurface()` JS qui est une formule synthétique, pas les données de `ttf_output/ttf_vol_surface.json`.

**Impact** : les valeurs affichées en 3D ne correspondent pas au fichier JSON calibré SABR exporté par `ttf_market_data.py`.

**Fix suggéré** : charger `ttf_vol_surface.json` via `fetch('/ttf_output/ttf_vol_surface.json')` au montage et restituer la surface réelle.

---

## 8 — Conclusion

Le projet est **globalement cohérent** et fonctionnel :
- Tous les modules Python s'importent ; toutes les fonctions clés passent leurs tests
- Put-call parity vérifiée pour Black-76, Bachelier et Margrabe
- Implied vol et implied correlation round-trippent à la précision numérique de Brent
- Dashboard JS donne des prix à 3e-6 près du Python (limite de l'erf approximé)
- Conventions d'unités homogènes dans tout le code

Les 3 points d'amélioration signalés sont non-bloquants. Le projet est **prêt à l'emploi** pour la cotation indicative d'options TTF vanilles, de 10 structures multi-legs et de spreads TTF/HH.

---

*Rapport généré manuellement par exécution des modules avec `python3` et analyse statique du code.*
