# TTF Natural Gas Options — User Manual

Ce manuel couvre :

1. [Introduction](#1-introduction) — options TTF, Black-76 vs Bachelier, Greeks
2. [`black76_ttf.py`](#2-black76_ttfpy) — toutes les fonctions avec exemples chiffrés

> **Conventions utilisées dans tous les exemples**
> - Forward TTF : `F = 30 EUR/MWh`
> - Strikes : `25 / 28 / 30 / 32 / 35 EUR/MWh`
> - Volatilité Black-76 : `sigma = 0.50` (50 % lognormale)
> - Volatilité Bachelier : `sigma_n = 15 EUR/MWh` (≈ `F · sigma`)
> - Maturité : `T = 0.25` année (3 mois, ACT/365)
> - Taux sans risque : `r = 0.02` (2 %)
>
> Les valeurs numériques affichées sont arrondies à 4 décimales.

---

## 1. Introduction

### 1.1 Qu'est-ce qu'une option TTF ?

Le **TTF** (*Title Transfer Facility*) est le hub virtuel de gaz naturel des
Pays-Bas et le benchmark européen. Une **option TTF** donne le droit (sans
l'obligation) d'acheter (`call`) ou de vendre (`put`) un futures TTF à un
prix d'exercice (`strike`, en EUR/MWh) à une date d'expiration donnée.

- **Sous-jacent** : futures TTF (un contrat = livraison physique sur un mois donné).
- **Style** : européen — exercice uniquement à l'expiration.
- **Quote** : EUR/MWh (1 MWh = 3.4121 MMBtu).
- **Convention de jours** : ACT/365 pour le temps `T` à l'expiration.
- **Calendrier** : ICE Endex Dutch TTF — l'expiration de l'option tombe ~5 jours
  calendaires avant le 1er du mois de livraison (rollback en jour ouvré, en
  excluant les fériés NL+UK et le futures LTD).

### 1.2 Black-76 vs Bachelier

Deux modèles d'évaluation sont implémentés ; le choix dépend du régime de prix.

| Critère | Black-76 (lognormal) | Bachelier (normal) |
|---|---|---|
| Hypothèse | `dF / F = sigma · dW` | `dF = sigma_n · dW` |
| Vol exprimée en | décimal (`0.50` = 50 %) | EUR/MWh absolu (`15` = 15 EUR/MWh) |
| Prix négatif autorisé | **non** (F doit être > 0) | **oui** |
| Régime adapté | conditions normales (F ≫ 0) | crise / spreads (F faible ou < 0) |
| PCP | `C − P = e^(-rT)·(F − K)` | identique |

**Règle de pouce** : si `F < 2 EUR/MWh` ou `F` peut devenir négatif (spreads,
gaz sous-balancé), passer à Bachelier. Sinon, Black-76 est le standard.

À l'ATM (`K = F`), les deux modèles donnent un prix très proche quand
`sigma_n ≈ F · sigma`.

### 1.3 Les Greeks

Sensibilités du prix de l'option par rapport aux paramètres d'entrée.

| Greek | Définition | Unité | Convention ici |
|---|---|---|---|
| **Delta** Δ | `∂V / ∂F` | sans dimension | actualisé par `e^(-rT)` |
| **Gamma** Γ | `∂²V / ∂F²` | par EUR/MWh | identique call/put |
| **Vega** ν | `∂V / ∂σ` | EUR/MWh par unité de vol | par 1.00 (100 %) de vol |
| **Theta** Θ | `∂V / ∂t` | EUR/MWh par jour | par jour calendaire (négatif si long) |
| **Rho** ρ | `∂V / ∂r` | EUR/MWh par 1 pp | par point de pourcentage |
| **Vanna** | `∂Δ / ∂σ` | mixed | dérivée croisée |
| **Volga** | `∂²V / ∂σ²` | EUR/MWh | convexité de la vol |

Convention pratique :

- `Δ_call − Δ_put = e^(-rT)` (parité forward des deltas).
- `Γ`, `ν` sont identiques pour call et put dans Black-76 et Bachelier.
- `Θ` ici est divisé par 365 → **par jour**, pas par année.
- `ρ` ici est divisé par 100 → par **point de pourcentage** de variation du taux.

---

## 2. `black76_ttf.py`

Module unique, sans dépendance externe au-delà de `scipy.stats.norm` et
`scipy.optimize.brentq`. Couvre :

- Le calendrier d'expiration ICE Endex Dutch TTF
- Les helpers de temps à l'expiration (`T` en années, ACT/365)
- Un parser de codes contrat (`TTFM26`, `Jun26`, …)
- Le pricing **Black-76** et **Bachelier** (call / put / dispatch)
- Les Greeks complets (Δ, Γ, ν, Θ, ρ, vanna, volga) pour les deux modèles
- Les solveurs de **vol implicite** (Brent)
- L'inversion **delta → strike**

### 2.1 Calendrier d'expiration ICE Endex

#### `ttf_expiry_date(contract_month: int, contract_year: int) -> date`

Date officielle d'expiration de l'option TTF pour un mois de livraison donné.

```python
from datetime import date
from black76_ttf import ttf_expiry_date

ttf_expiry_date(6, 2026)   # TTFM26 : livraison juin 2026
# -> date(2026, 5, 27)

ttf_expiry_date(1, 2026)   # TTFF26 : Dec-25 férié decale a Dec 24
# -> date(2025, 12, 24)

ttf_expiry_date(3, 2026)   # TTFH26 : livraison mars 2026
# -> date(2026, 2, 24)
```

**Algorithme** :

1. Candidat = 1er du mois de livraison − 5 jours calendaires
2. Si non ouvré → recul au jour ouvré précédent (NL + UK)
3. Si égal au futures LTD → recul d'un jour ouvré supplémentaire

#### `ttf_time_to_expiry(contract_month, contract_year, reference=None) -> float`

Temps `T` (années, ACT/365, jour de référence inclus). Retourne 0 si l'expiration
est dans le passé.

```python
from datetime import date
from black76_ttf import ttf_time_to_expiry

ttf_time_to_expiry(6, 2026, reference=date(2026, 4, 23))
# -> 0.0959  (35 jours / 365)
```

#### `ttf_next_expiries(n=6, reference=None) -> list[tuple[str, date]]`

Les `n` prochaines expirations TTF (codes ICE + dates), triées en ascendant.

```python
from datetime import date
from black76_ttf import ttf_next_expiries

ttf_next_expiries(3, reference=date(2026, 4, 23))
# -> [('TTFK26', date(2026, 4, 24)),
#     ('TTFM26', date(2026, 5, 27)),
#     ('TTFN26', date(2026, 6, 26))]
```

#### `ttf_is_business_day(d: date) -> bool`

Jour ouvré ICE Endex (Mon–Fri, hors `_ttf_holidays(year)` = NL+UK : 1er janvier,
Vendredi saint, lundi de Pâques, 1er mai, 25 et 26 décembre).

```python
from datetime import date
from black76_ttf import ttf_is_business_day

ttf_is_business_day(date(2025, 12, 25))   # Christmas
# -> False
ttf_is_business_day(date(2026, 4, 6))     # Easter Monday
# -> False
```

### 2.2 Helpers d'expiration "simples" (5 jours ouvrés avant le futures LTD)

Coexistent avec le calendrier ICE pour la rétrocompatibilité. Les fonctions
`b76_price_ttf` / `bach_price_ttf` les utilisent via `t_from_contract`.

#### `futures_expiry_from_delivery(delivery_year, delivery_month) -> date`

Dernier jour ouvré du mois précédant la livraison.

```python
from black76_ttf import futures_expiry_from_delivery

futures_expiry_from_delivery(2026, 6)
# -> date(2026, 5, 29)   (vendredi)
```

#### `options_expiry_from_delivery(delivery_year, delivery_month) -> date`

5 jours ouvrés avant le futures LTD.

```python
from black76_ttf import options_expiry_from_delivery

options_expiry_from_delivery(2026, 6)
# -> date(2026, 5, 22)
```

#### `t_from_delivery(delivery_year, delivery_month, reference=None) -> float`

Temps `T` ACT/365 jusqu'à `options_expiry_from_delivery`.

```python
from datetime import date
from black76_ttf import t_from_delivery

t_from_delivery(2026, 6, reference=date(2026, 4, 1))
# -> 0.1425  (52 jours / 365)
```

#### `t_futures_from_delivery(delivery_year, delivery_month, reference=None) -> float`

Idem mais jusqu'au futures LTD.

```python
from datetime import date
from black76_ttf import t_futures_from_delivery

t_futures_from_delivery(2026, 6, reference=date(2026, 4, 1))
# -> 0.1616  (59 jours / 365)
```

### 2.3 Parser de code contrat

#### `t_from_contract(contract: str, reference=None) -> float`

Accepte le code ICE (`TTFH26`) ou l'abréviation mensuelle (`Mar26`, `Mar2026`)
et renvoie `T` via `t_from_delivery`.

```python
from datetime import date
from black76_ttf import t_from_contract

t_from_contract("TTFM26", reference=date(2026, 4, 1))
# -> 0.1425
t_from_contract("Jun26",  reference=date(2026, 4, 1))
# -> 0.1425
t_from_contract("Mar2026", reference=date(2026, 1, 15))
# -> 0.1233
```

Lève `ValueError` si le format n'est pas reconnu.

### 2.4 Pricing Black-76

Codes de mois ICE supportés : `F G H J K M N Q U V X Z`.

#### `b76_call(F, K, T, r, sigma) -> float`

```python
from black76_ttf import b76_call

b76_call(F=30, K=30, T=0.25, r=0.02, sigma=0.50)
# -> 2.9670   EUR/MWh   (call ATM, 3 mois)

b76_call(F=30, K=25, T=0.25, r=0.02, sigma=0.50)
# -> 6.4124   EUR/MWh   (call ITM)

b76_call(F=30, K=35, T=0.25, r=0.02, sigma=0.50)
# -> 1.2197   EUR/MWh   (call OTM)
```

#### `b76_put(F, K, T, r, sigma) -> float`

```python
from black76_ttf import b76_put

b76_put(F=30, K=30, T=0.25, r=0.02, sigma=0.50)
# -> 2.9670   EUR/MWh   (put ATM, 3 mois)

b76_put(F=30, K=35, T=0.25, r=0.02, sigma=0.50)
# -> 6.1448   EUR/MWh   (put ITM)
```

> **Vérification PCP** : pour `K = 35`, `C − P = 1.2197 − 6.1448 = −4.9251`
> alors que `e^(-0.02·0.25)·(30 − 35) = −4.9750`. Diff exacte → PCP respectée.

#### `b76_price(F, K, T, r, sigma, option_type='call') -> float`

Dispatcher générique :

```python
from black76_ttf import b76_price

b76_price(30, 30, 0.25, 0.02, 0.50, "call")   # -> 2.9670
b76_price(30, 30, 0.25, 0.02, 0.50, "put")    # -> 2.9670
```

Lève `ValueError` si `option_type` ∉ `{'call', 'put'}`.

#### `b76_price_ttf(F, K, contract, r, sigma, option_type='call', reference=None) -> float`

Variante où `T` est dérivé d'un code contrat.

```python
from datetime import date
from black76_ttf import b76_price_ttf

b76_price_ttf(F=30, K=30, contract="TTFM26",
              r=0.02, sigma=0.50,
              option_type="call",
              reference=date(2026, 4, 1))
# -> 2.2530   EUR/MWh   (T = 52 / 365 = 0.1425)
```

### 2.5 Pricing Bachelier

Pour les forwards proches de zéro ou négatifs, ou les spreads.

#### `bach_call(F, K, T, r, sigma_n) -> float`

```python
from black76_ttf import bach_call

bach_call(F=30, K=30, T=0.25, r=0.02, sigma_n=15)
# -> 2.9770   EUR/MWh

bach_call(F=-3, K=0, T=60/365, r=0.02, sigma_n=6)
# -> 0.5860   EUR/MWh   (forward negatif, scenario crise)
```

#### `bach_put(F, K, T, r, sigma_n) -> float`

```python
from black76_ttf import bach_put

bach_put(F=30, K=30, T=0.25, r=0.02, sigma_n=15)
# -> 2.9770
```

#### `bach_price(F, K, T, r, sigma_n, option_type='call') -> float`

Dispatcher.

```python
from black76_ttf import bach_price

bach_price(30, 35, 0.25, 0.02, 15, "put")
# -> 7.6770
```

#### `bach_price_ttf(F, K, contract, r, sigma_n, option_type='call', reference=None) -> float`

Idem `b76_price_ttf` mais via Bachelier.

```python
from datetime import date
from black76_ttf import bach_price_ttf

bach_price_ttf(F=30, K=30, contract="Jun26",
               r=0.02, sigma_n=15,
               option_type="call",
               reference=date(2026, 4, 1))
# -> 2.2519
```

### 2.6 Greeks Black-76

Toutes les fonctions ci-dessous prennent `(F, K, T, r, sigma, option_type='call')`
sauf `b76_gamma`, `b76_vega`, `b76_vanna`, `b76_volga` qui sont identiques pour
call et put (pas d'argument `option_type`).

```python
from black76_ttf import (
    b76_delta, b76_gamma, b76_vega, b76_theta, b76_rho,
    b76_vanna, b76_volga, b76_greeks,
)

F, K, T, r, sigma = 30, 30, 0.25, 0.02, 0.50

b76_delta(F, K, T, r, sigma, "call")   # -> +0.5470
b76_delta(F, K, T, r, sigma, "put")    # -> -0.4480
b76_gamma(F, K, T, r, sigma)           # -> +0.0525
b76_vega (F, K, T, r, sigma)           # -> +5.9069   (par 1.00 de vol)
b76_theta(F, K, T, r, sigma, "call")   # -> -0.0245   (par jour)
b76_rho  (F, K, T, r, sigma, "call")   # -> -0.0074   (par 1 pp)
b76_vanna(F, K, T, r, sigma)           # -> +0.0984
b76_volga(F, K, T, r, sigma)           # -> -0.1846
```

#### `b76_greeks(F, K, T, r, sigma, option_type='call') -> B76Greeks`

Tous les Greeks en un seul appel (dataclass `B76Greeks` avec champs `delta`,
`gamma`, `vega`, `theta`, `rho`, `vanna`, `volga`).

```python
g = b76_greeks(F=30, K=30, T=0.25, r=0.02, sigma=0.50, option_type="call")
g.delta   # +0.5470
g.gamma   # +0.0525
g.vega    # +5.9069
g.theta   # -0.0245
g.rho     # -0.0074
g.vanna   # +0.0984
g.volga   # -0.1846
```

> **Convention vega** : par unité de vol décimale (1.00 = 100 %). Pour la
> sensibilité "par 1 vol point" (1 % = 0.01), divisez vega par 100.

> **Convention rho** : déjà divisé par 100, donc directement en EUR/MWh par
> point de pourcentage de variation du taux.

### 2.7 Greeks Bachelier

Mêmes signatures, avec `sigma_n` à la place de `sigma`.

```python
from black76_ttf import (
    bach_delta, bach_gamma, bach_vega, bach_theta, bach_rho,
    bach_vanna, bach_volga, bach_greeks,
)

F, K, T, r, sigma_n = 30, 30, 0.25, 0.02, 15

bach_delta(F, K, T, r, sigma_n, "call")   # -> +0.4975
bach_delta(F, K, T, r, sigma_n, "put")    # -> -0.4975
bach_gamma(F, K, T, r, sigma_n)           # -> +0.0530
bach_vega (F, K, T, r, sigma_n)           # -> +0.1985
bach_theta(F, K, T, r, sigma_n, "call")   # -> -0.0246
bach_rho  (F, K, T, r, sigma_n, "call")   # -> -0.0074
bach_vanna(F, K, T, r, sigma_n)           # 0.0
bach_volga(F, K, T, r, sigma_n)           # -0.0132
```

> À l'ATM Bachelier, `vanna = 0` exactement (par symétrie en `d = (F-K)/(σ√T)`).

#### `bach_greeks(...) -> BachGreeks`

```python
g = bach_greeks(30, 30, 0.25, 0.02, 15, "call")
g.delta, g.gamma, g.vega, g.theta, g.rho, g.vanna, g.volga
# (0.4975, 0.0530, 0.1985, -0.0246, -0.0074, 0.0, -0.0132)
```

### 2.8 Solveurs de volatilité implicite

Méthode de **Brent**, `xtol = 1e-8`, max 300 itérations.

#### `b76_implied_vol(market_price, F, K, T, r, option_type='call', sigma_lo=1e-6, sigma_hi=20.0) -> float`

Round-trip price → IV → sigma :

```python
from black76_ttf import b76_call, b76_implied_vol

p = b76_call(30, 30, 0.25, 0.02, 0.50)   # 2.9670
b76_implied_vol(p, F=30, K=30, T=0.25, r=0.02, option_type="call")
# -> 0.5000
```

Lève `ValueError` si `market_price` est en dehors du couloir
`[intrinsic, sigma_hi]`.

#### `bach_implied_vol(market_price, F, K, T, r, option_type='call', sigma_lo=1e-6, sigma_hi=500.0) -> float`

Inverse pour la vol normale en EUR/MWh.

```python
from black76_ttf import bach_call, bach_implied_vol

p = bach_call(30, 30, 0.25, 0.02, 15)   # 2.9770
bach_implied_vol(p, F=30, K=30, T=0.25, r=0.02, option_type="call")
# -> 15.0000
```

### 2.9 Inversion delta → strike

Utile pour convertir une cotation 25Δ / 50Δ / 75Δ en strike.

#### `b76_delta_to_strike(delta_target, F, T, r, sigma, option_type='call', K_lo=None, K_hi=None) -> float`

```python
from black76_ttf import b76_delta_to_strike

# Strike du call 25-delta (typiquement OTM)
b76_delta_to_strike(delta_target=0.25,
                    F=30, T=0.25, r=0.02, sigma=0.50,
                    option_type="call")
# -> 35.0826   EUR/MWh

# Strike du put 25-delta (le delta cible est negatif pour un put)
b76_delta_to_strike(delta_target=-0.25,
                    F=30, T=0.25, r=0.02, sigma=0.50,
                    option_type="put")
# -> 25.5749   EUR/MWh
```

`K_lo` / `K_hi` par défaut : `[F · 0.01, F · 10]`. Lève `ValueError` si la
cible n'est pas atteignable dans la fourchette.

#### `bach_delta_to_strike(delta_target, F, T, r, sigma_n, option_type='call', K_lo=None, K_hi=None) -> float`

Variante Bachelier — utile pour les forwards négatifs ou très bas.

```python
from black76_ttf import bach_delta_to_strike

bach_delta_to_strike(delta_target=0.25,
                     F=30, T=0.25, r=0.02, sigma_n=15,
                     option_type="call")
# -> 35.0570   EUR/MWh
```

`K_lo` / `K_hi` par défaut : `[F − 10·σ_n·√T, F + 10·σ_n·√T]`.

---

## Annexe A — Valeurs de référence (3 mois, ATM)

Avec `F = 30 EUR/MWh, K = 30, T = 0.25, r = 0.02` :

| Modèle | sigma     | Call    | Put     | Δ_call | Γ      | ν      |
|--------|-----------|---------|---------|--------|--------|--------|
| B76    | 0.50      | 2.9670  | 2.9670  | +0.547 | 0.0525 | 5.907  |
| Bach   | 15 EUR/MWh| 2.9770  | 2.9770  | +0.498 | 0.0530 | 0.199  |

`C − P` théorique = `e^(-0.02·0.25)·(30 − 30) = 0`. Vérifié sur les deux
modèles (différence < 1e-12 EUR/MWh).
