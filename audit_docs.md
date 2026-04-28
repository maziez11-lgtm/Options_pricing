# Documentation Audit (main branch)

**Files reviewed**: `README.md`, `user_manual.md`, `user_manual.html`,
`file_structure.md` — all at `origin/main` HEAD.
**Audit date**: 2026-04-28

---

## 1. Results summary

| # | Check | Result |
|---|---|---|
| 1 | `user_manual.md` complete (6 parts + glossary) | **PASS** (with a structural note) |
| 2 | `user_manual.html` matches `user_manual.md`    | **PASS** |
| 3 | `README.md` up to date with all modules        | **FAIL** (5 modules missing) |
| 4 | ICE TFO expiry definition is correct everywhere | **PASS** |
| 5 | Everything is in English only                  | **PASS** for content (1 French filename — see §6) |

---

## 2. Check 1 — `user_manual.md` completeness — **PASS**

`user_manual.md` (1 819 lines) has **8 H2 headings** and **43 H3 sub-headings**.
The 6 numbered parts are:

| Part | Title | Lines |
|---|---|---|
| 1 | Introduction (1.1 What is a TTF option? · 1.2 Black-76 vs Bachelier · 1.3 The Greeks) | 25–91 |
| 2 | `black76_ttf.py` (2.1–2.8: ICE TFO calendar, contract parser, Black-76 / Bachelier pricing, Greeks, IV solvers, Δ→K inversion) | 93–500 |
| 3 | `ttf_market_data.py` (3.1–3.10: contracts, calendar, forward curve, vol surface, SABR, exports, end-to-end, manual loaders) | 502–1023 |
| 4 | `ttf_hh_spread.py` (4.1–4.8: Margrabe background, conversions, pricing, full pricer, implied correlation, sensitivities, display, PCP) | 1025–1342 |
| 5 | `dashboard_jupyter.ipynb` (5.0–5.5: launching + 5 dashboard sections) | 1343–1562 |
| 6 | **Financial glossary** (6.1–6.8: markets, mechanics, models, Greeks, vol, spread, structures, conventions) | 1564–1786 |

Plus two appendices: **Appendix A** (3-month ATM reference values),
**Appendix B** (TTF/HH spread reference values).

**Note on structure**: the audit prompt asks for "6 parts + glossary".
The glossary is implemented as **Part 6** rather than as a separate
appendix; if "+ glossary" is meant strictly as a 7th element this is a
labelling preference rather than a missing piece — all glossary content
(40+ terms across 8 sub-sections) is present.

### Modules covered vs. modules on main

| Module on `main` | Mentioned in `user_manual.md` |
|---|---|
| `black76_ttf.py`        | ✓ (Part 2, dedicated section) |
| `ttf_market_data.py`    | ✓ (Part 3, dedicated section) |
| `ttf_hh_spread.py`      | ✓ (Part 4, dedicated section) |
| `dashboard_jupyter.ipynb` | ✓ (Part 5, dedicated section) |
| `structures_ttf.py`     | △ — referenced inside §5.2 only, no dedicated module section |
| `pricing/` package      | ✗ |
| `ttf_time.py`           | ✗ |
| `dashboard_ttf.py`      | ✗ |
| `main.py`               | ✗ |
| `test_suite.py`         | ✗ |

**Overall**: the manual covers the four user-facing modules with
worked examples and a glossary, but `structures_ttf.py` deserves a
dedicated section (it has 10 public structures and is currently
documented only inside the dashboard chapter), and the lower-level
`pricing/` package and the `dashboard_ttf.py` Streamlit-style script
are not mentioned at all.

---

## 3. Check 2 — `user_manual.html` ↔ `user_manual.md` — **PASS**

Structural parity:

| Level | `.md` | `.html` |
|---|---:|---:|
| H1 | 1 | 1 |
| H2 | 8 | 8 |
| H3 | 43 | 43 |
| H4 | — | 48 (one per public function) |

All 8 H2 titles match 1-for-1 (the only formatting difference is that
the HTML strips backticks around code identifiers, e.g.
`` `black76_ttf.py` `` → `black76_ttf.py`, which is the expected
Markdown→HTML rendering).

Content spot-checks (presence in stripped HTML body vs MD source):

| Phrase | `.md` | `.html` |
|---|---:|---:|
| "Title Transfer Facility" | ✓ | ✓ |
| ICE TFO rule (verbatim quote) | ✓ | ✓ |
| `ttf_expiry_date(6, 2026)` | ✓ | ✓ |
| Margrabe | ✓ | ✓ |
| delta-neutral | ✓ | ✓ |
| 10 multi-leg | ✓ | ✓ |
| TTFM26 | ✓ | ✓ |
| ICE TFO | ✓ | ✓ |

The HTML adds `<h4>` anchors (one per public function, e.g.
`<h4 id="b76_callf-k-t-r-sigma-float">b76_call(F, K, T, r, sigma) -> float</h4>`),
which simply elevate Markdown bold function signatures into linkable
sub-headings. Body text, code blocks, tables and the verbatim ICE-rule
quote are identical. The HTML is a faithful render of the Markdown.

---

## 4. Check 3 — `README.md` module coverage — **FAIL**

The README's "Features" table and "Project Structure" tree list:

```
black76_ttf.py
ttf_market_data.py
ttf_time.py
main.py
pricing/
dashboard/
ttf_output/
```

Modules present on `origin/main` but **missing from README.md**:

| Missing module | What it is | Where it should appear |
|---|---|---|
| `structures_ttf.py`        | 10 multi-leg structure pricer (straddle, strangle, vertical, butterfly, condor, collar, risk-reversal, calendar, ratio) | Module table + Project Structure |
| `ttf_hh_spread.py`         | TTF/Henry Hub spread option (Margrabe) with EUR/MWh ↔ USD/MMBtu conversions | Module table + Project Structure |
| `dashboard_ttf.py`         | Top-level dashboard script (sibling of `dashboard/`) | Project Structure |
| `dashboard_jupyter.ipynb`  | Jupyter dashboard documented in user-manual Part 5 | Project Structure |
| `test_suite.py`            | Test suite | Project Structure |

Additionally:
- The README's **Quick Start** code samples reference only
  `black76_ttf` and `ttf_market_data`. Adding a one-liner each for
  `structures_ttf` (e.g. `straddle(F, K, T, r, sigma)`) and
  `ttf_hh_spread.spread_price` would bring the README in line with the
  manual's Parts 4–5.
- The README's expiry table (lines 336–349, monthly contracts in 2026)
  matches the implementation exactly — verified against
  `black76_ttf.ttf_expiry_date` for all 12 months.

**Recommended fix**: append two rows to the "Features" table and add
`structures_ttf.py`, `ttf_hh_spread.py`, `dashboard_ttf.py`,
`dashboard_jupyter.ipynb`, `test_suite.py` to the Project Structure
tree. No content needs to be removed.

---

## 5. Check 4 — ICE TFO expiry rule — **PASS**

The verbatim ICE TFO contract specification is present in **all three**
documentation surfaces (`README.md` lines 321–326, `user_manual.md`
lines ~115–120, `user_manual.html` rendered from the same source):

> *"Trading will cease when the intraday settlement price of the
> underlying futures contract is set, **five calendar days before the
> start of the contract month**. If that day is a non-business day or
> non-UK business day, expiry will occur on the nearest prior business
> day, except where that day is also the expiry date of the underlying
> futures contract, in which case expiry will occur on the preceding
> business day."*

Implementation cross-check — every documented expiry agrees with
`black76_ttf.ttf_expiry_date()`:

| Contract | Doc claim (README/manual) | Code result |
|---|---|---|
| TTFM26 (Jun-26) | 27 May 2026 (Wed) | 2026-05-27 ✓ |
| TTFK26 (May-26) | 24 Apr 2026 (Fri) | 2026-04-24 ✓ |
| TTFF26 (Jan-26) | 24 Dec 2025 (Wed) | 2025-12-24 ✓ |
| TTFH26 (Mar-26) | 24 Feb 2026 (Tue) | 2026-02-24 ✓ |
| TTFV26 (Oct-26) | 25 Sep 2026 (Fri) | 2026-09-25 ✓ |

No occurrences of the deprecated rule "5 BD before futures LTD" or
"last business day before delivery" remain in any documentation file.
Both `README.md` and `user_manual.md` correctly note the **UK-only**
holiday calendar (England & Wales: New Year, Good Friday, Easter
Monday, early-May / spring / summer bank holidays, Christmas, Boxing
Day) — matching `_uk_holidays` in `black76_ttf.py`.

---

## 6. Check 5 — English-only content — **PASS** (1 caveat)

### Body text

Scanned `README.md`, `user_manual.md`, and the stripped text of
`user_manual.html` for distinctively French phrases (`c'est`, `n'est`,
`déjà`, `où` (with grave accent in French context), `être`, `cela`,
`ainsi`, `cette`, `notre`, `votre`, French articles in front of
words, etc.). **Zero hits in any of the three files.**

The non-ASCII characters that do appear are all legitimate English /
mathematical typography:
- `—` (em-dash) and `–` (en-dash) for punctuation
- `≥`, `≤`, `≈`, `≫`, `→`, `²`, `√`, `∞`, `Σ`, `Φ⁻¹`, `Δ`, `σ`, `ρ`, `θ`, `φ` for math
- `²T/2` in formulas
- `°` etc.

### Filenames

One French filename exists under the dashboard tree:

```
dashboard/Initialisation dossier
```

`Initialisation dossier` is French for *"Initialization folder"*.
This is a stray placeholder file in the React project (visible at the
repository root listing). It should be removed or renamed
(`dashboard/.gitkeep`, `dashboard/init/` etc.) for consistency with
the project's English-only convention. **Not a content-language
issue, but a stylistic inconsistency worth fixing.**

### Code comments / docstrings

(Out of strict scope; spot-checked.) All Python docstrings sampled
during prior audits — `black76_ttf.py`, `ttf_market_data.py`,
`structures_ttf.py`, `ttf_hh_spread.py` — are in English.

---

## 7. Summary of recommended fixes (priority order)

1. **README**: add `structures_ttf.py` and `ttf_hh_spread.py` to the
   "Features" module table; add `structures_ttf.py`, `ttf_hh_spread.py`,
   `dashboard_ttf.py`, `dashboard_jupyter.ipynb`, `test_suite.py` to the
   "Project Structure" tree. Add one Quick-Start example per missing
   module.
2. **`user_manual.md`**: insert a dedicated Part for `structures_ttf.py`
   (currently only mentioned inside §5.2), and short subsections on
   `pricing/` and `ttf_time.py` if those modules are intended to be part
   of the public API.
3. **Repository hygiene**: rename or remove `dashboard/Initialisation
   dossier`.

No content changes are required for the ICE TFO rule, the HTML manual,
or the language of the documentation.
