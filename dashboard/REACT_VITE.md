# React & Vite — Guide technique du dashboard TTF Options

Ce document décrit précisément **comment** et **pourquoi** le dashboard
`/dashboard` utilise React et Vite. Il cible un développeur qui rejoint le
projet et qui veut comprendre la stack avant de contribuer.

---

## 1. Vue d'ensemble

Le dashboard est une **Single Page Application** (SPA) entièrement côté client :
- Aucun serveur Python n'est appelé — la logique de pricing (Black-76,
  Bachelier, Brent implied vol) est **réimplémentée en JavaScript** dans
  `src/lib/pricing.js`.
- Chaque changement d'input déclenche un recalcul synchrone en mémoire,
  sans requête réseau.
- Le bundle final est 100 % statique : il peut être servi par n'importe
  quel hébergeur de fichiers (Nginx, Vercel, GitHub Pages, S3+CloudFront…).

```
┌────────────────────────────────────────────────────────────┐
│                 Navigateur (client-side)                   │
│                                                            │
│   React (UI)  ─────  pricing.js (Black-76 / Bachelier)    │
│        │                           │                       │
│        │           (useMemo)      │                       │
│        └────────────┬──────────────┘                       │
│                     │                                      │
│              Vite dev server  ←→  HMR                      │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Rôle de Vite

**Vite** (v8.0.9 dans `package.json`) est à la fois :

1. **Serveur de développement** (commande `npm run dev`)
   - Démarrage quasi-instantané (< 500 ms typique).
   - Hot Module Replacement (HMR) : modification d'un composant React
     → rafraîchissement partiel, **sans perte d'état**.
   - Sert directement les modules ES natifs au navigateur
     (pas de bundling complet en dev).

2. **Bundler de production** (commande `npm run build`)
   - Rollup sous le capot, avec tree-shaking agressif.
   - Produit un dossier `dist/` qui contient :
     - `index.html` (minifié)
     - `assets/*.js` (JS bundlé, minifié, code-splitted)
     - `assets/*.css` (CSS extrait)
     - Les ressources statiques copiées depuis `public/`
   - La taille finale est fortement dépendante de Plotly.js qui pèse ~3 MB
     non-gzippé à lui seul.

3. **Preview local** (commande `npm run preview`)
   - Sert le `dist/` statique pour tester la prod en local.

### Configuration Vite

Fichier : `dashboard/vite.config.js`
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

La configuration est **minimale** : un seul plugin (`@vitejs/plugin-react`)
qui active :
- Transformation du JSX en appels `React.createElement` (via SWC).
- Fast Refresh (= HMR préservant l'état des composants React).
- Injection automatique du `React` en scope dans les fichiers JSX.

Par défaut :
- Le serveur tourne sur `http://localhost:5173`.
- Le point d'entrée HTML est `dashboard/index.html`.
- Le point d'entrée JS est `src/main.jsx`.

### Le fichier `index.html`

```html
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
```

Vite consomme `index.html` comme point d'entrée. Le `<script type="module">`
est transformé à la volée (en dev) ou bundlé (en build). Le favicon
`/favicon.svg` est servi depuis `dashboard/public/` sans traitement.

---

## 3. Rôle de React

**React** (v19.2.5) est la bibliothèque UI. Elle remplit trois rôles :

1. **Décrire l'interface de façon déclarative** — chaque composant est
   une fonction JS qui retourne du JSX (arbre de `React.createElement`).
2. **Gérer l'état local** via `useState`.
3. **Mémoïser les calculs lourds** via `useMemo` pour éviter de
   re-pricer l'option 60 fois par seconde pendant qu'un slider bouge.

### Bootstrap

Fichier : `src/main.jsx`
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- `createRoot(...)` est l'API React 18+ (remplace `ReactDOM.render`).
- `StrictMode` active les warnings de développement (effets doublés,
  API dépréciées, etc.). Aucun effet en production.

### Arbre de composants

```
<App>                          (src/App.jsx)
  ├── <header>                 (inline JSX)
  │
  ├── <InputPanel>             (src/components/InputPanel.jsx)
  │     └── <Slider> × 6       sliders F, K, T, r, σ, σ_n
  │
  ├── <PriceCard>              (src/components/PriceCard.jsx)
  │     ├── <GreekCard> × 6    delta, gamma, vega, theta, vanna, volga
  │     └── <button export>
  │
  ├── <GreeksChart>            (src/components/GreeksChart.jsx)
  │     └── <ResponsiveContainer><LineChart>... (recharts)
  │
  ├── <VolSurface3D>           (src/components/VolSurface3D.jsx)
  │     └── <Plot type="surface">... (react-plotly.js)
  │
  ├── <ModelComparison>        (src/components/ModelComparison.jsx)
  │     └── <ResponsiveContainer><LineChart>... (recharts)
  │
  └── <footer>                 (inline JSX)
```

### État et flux de données

**Source unique de vérité** : `App.jsx` détient un seul objet d'état
`inputs` contenant toutes les valeurs utilisateur :

```jsx
const DEFAULT_INPUTS = {
  F: 35.0, K: 35.0, T: 0.25, r: 0.03,
  sigma: 0.50, sigma_n: 8.0, type: 'call',
};
const [inputs, setInputs] = useState(DEFAULT_INPUTS);
```

Cet objet est :
- **Modifié** uniquement depuis `InputPanel` via le callback `onChange`.
- **Lu** par tous les autres composants en props descendantes.

Le pricing est calculé dans `App.jsx` avec `useMemo` pour que
Black-76 et Bachelier ne tournent que quand leurs inputs changent :

```jsx
const b76P  = useMemo(() => b76Price(F, K, T, r, sigma, type),
                      [F, K, T, r, sigma, type]);
const b76G  = useMemo(() => b76Greeks(F, K, T, r, sigma, type),
                      [F, K, T, r, sigma, type]);
const bachP = useMemo(() => bachPrice(F, K, T, r, sigma_n, type),
                      [F, K, T, r, sigma_n, type]);
const bachG = useMemo(() => bachGreeks(F, K, T, r, sigma_n, type),
                      [F, K, T, r, sigma_n, type]);
const comp  = useMemo(() => buildComparison(F, T, r, sigma, sigma_n, type),
                      [F, T, r, sigma, sigma_n, type]);
```

- Quand **seul σ_n** change, **seuls** `bachP`, `bachG` et `comp` sont recalculés.
  `b76P` et `b76G` gardent leur valeur mémoïsée.
- Les composants enfants `GreeksChart`, `VolSurface3D`, `ModelComparison`
  ont aussi leur propre `useMemo` pour leurs grilles de strikes.

---

## 4. Dépendances npm — rôle de chacune

### Runtime (`dependencies`)

| Paquet | Version | Rôle |
|---|---|---|
| `react` | ^19.2.5 | Librairie UI |
| `react-dom` | ^19.2.5 | Moteur de rendu navigateur |
| `recharts` | ^3.8.1 | Graphiques 2D (Greeks vs strike, comparaison modèles) |
| `react-plotly.js` | ^2.6.0 | Wrapper React pour Plotly |
| `plotly.js-dist-min` | ^3.5.0 | Moteur Plotly minifié (surface 3D) |
| `lucide-react` | ^1.8.0 | Icônes SVG (TrendingUp, TrendingDown) |
| `xlsx` | ^0.18.5 | Export Excel côté client (SheetJS) |

### Développement (`devDependencies`)

| Paquet | Rôle |
|---|---|
| `vite` | Serveur dev + bundler de prod |
| `@vitejs/plugin-react` | Transformation JSX, Fast Refresh |
| `eslint` + plugins | Linting (rules React hooks + react-refresh) |
| `globals` | Globals standards (browser, node) pour ESLint |
| `@types/react`, `@types/react-dom` | Types TS (utilisé par l'IDE) |

---

## 5. Scripts npm

Définis dans `package.json` :

```json
"scripts": {
  "dev":     "vite",
  "build":   "vite build",
  "lint":    "eslint .",
  "preview": "vite preview"
}
```

| Commande | Effet |
|---|---|
| `npm run dev` | Dev server `http://localhost:5173`, HMR actif |
| `npm run build` | Bundle prod dans `dist/` |
| `npm run preview` | Sert `dist/` localement (test avant déploiement) |
| `npm run lint` | Lint du code JS/JSX |

---

## 6. Conventions adoptées

- **JSX** : composants **fonctionnels** uniquement (pas de class components).
- **Hooks** utilisés : `useState`, `useMemo`, `React.useState` (pour
  `selected` dans `GreeksChart`).
- **Nommage** : composants en `PascalCase`, fichiers en `PascalCase.jsx`,
  hooks en `camelCase`.
- **CSS** : un seul fichier `App.css` avec variables CSS custom
  (`--bg`, `--text`, etc.) et classes BEM-ish (`.panel`, `.greek-card`,
  `.price-row`).
- **Pas de state manager global** (pas de Redux, Zustand, Context) —
  la taille du projet ne le justifie pas. L'état `inputs` vit dans
  `App` et descend en props.
- **Pas de router** — une seule page, scrollable verticalement.

---

## 7. Pourquoi cette stack ?

### Pourquoi Vite plutôt que Create React App ou webpack ?

- Démarrage dev 10–50× plus rapide (pas de bundling préalable).
- Fast Refresh natif, stable avec React 18+.
- Config par défaut suffisante pour ce projet (pas de webpack.config.js
  à maintenir).
- Meilleur support de l'écosystème ESM moderne.

### Pourquoi React 19 ?

- API stable et familière.
- Écosystème riche (Plotly, recharts, xlsx existent tous en bindings React).
- `useMemo` suffit pour mémoïser le pricing sans gérer manuellement
  un graphe de dépendances.

### Pourquoi pas de serveur ?

- La logique de pricing tient en ~180 lignes de JS (`pricing.js`).
- Zéro latence : le slider réagit en < 16 ms.
- Aucun besoin d'authentification ni de persistance.
- Le déploiement est trivial (hébergement statique).

### Le trade-off

Le dashboard **ne consulte pas** `ttf_output/ttf_vol_surface.json` ni
aucun autre artefact Python. Il génère sa propre vol surface synthétique
dans `pricing.js::buildVolSurface`. Si la calibration SABR côté Python
évolue, le dashboard **ne la reflète pas**. C'est un choix de simplicité
assumé. Pour l'aligner, il suffirait d'ajouter un `fetch()` au montage
de `<VolSurface3D>` (cf. recommandation § 6.4 du `audit_report.md`).

---

## 8. Démarrer rapidement

```bash
# Depuis la racine du repo
cd dashboard
npm install            # ~30 s, ~250 Mo dans node_modules/
npm run dev            # dev server
# Ouvrir http://localhost:5173
```

Pour la prod :
```bash
npm run build          # génère dist/
npm run preview        # test local de la version buildée
```

Pour déployer la version buildée, copier le contenu de `dashboard/dist/`
sur n'importe quel hébergeur statique.

---

## 9. Dépannage courant

| Symptôme | Cause probable | Solution |
|---|---|---|
| `Error: Cannot find module '@vitejs/plugin-react'` | `node_modules` absent | `npm install` |
| Port 5173 déjà utilisé | Autre process sur le port | `npm run dev -- --port 5174` |
| Page blanche en prod | Chemin absolu `/` cassé | Ajouter `base: './'` dans `vite.config.js` |
| Bundle > 5 MB | Plotly full + xlsx | Accepter (dashboard analytique) ou lazy-load Plotly |
| Erreur HMR après install | Cache obsolète | Supprimer `node_modules/.vite` |

---

## 10. Références

- React : https://react.dev/
- Vite : https://vite.dev/
- @vitejs/plugin-react : https://github.com/vitejs/vite-plugin-react
- recharts : https://recharts.org/
- Plotly.js : https://plotly.com/javascript/
- SheetJS (xlsx) : https://sheetjs.com/
