# Documentation Audit — `audit_docs.md`

**Scope.** Verify the user-facing documentation (`user_manual.md`,
`user_manual.html`, `README.md`) and check that the project no longer carries
the legacy/incorrect TTF option expiry rule.

**Date.** 2026-04-28
**Branch.** `claude/create-audit-docs-rGuam`

---

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | `user_manual.md` is complete (6 parts + glossary) | **PASS** *(with caveat — see §1)* |
| 2 | `user_manual.html` matches `user_manual.md` content | **PASS** |
| 3 | `README.md` includes all modules and the ICE TFO definition | **FAIL** |
| 4 | Expiry-date definition is the correct ICE TFO rule everywhere | **FAIL** |
| 5 | Everything is in English only | **PASS** |
| 6 | No reference to the wrong rule "5 business days before futures LTD" | **FAIL** |

---

## 1. `user_manual.md` is complete (6 parts + glossary) — PASS *(with caveat)*

The manual's own table of contents (lines 5–10) declares **6 parts**, and
Part 6 *is* the Financial Glossary:

```
Part 1. Introduction
Part 2. black76_ttf.py
Part 3. ttf_market_data.py
Part 4. ttf_hh_spread.py
Part 5. dashboard_jupyter.ipynb
Part 6. Financial glossary
```

All six declared parts are present in the body (`user_manual.md:25, 93, 502,
1025, 1343, 1564`), the glossary covers 8 sub-sections (6.1 → 6.8) plus
Appendices A and B (`user_manual.md:1788, 1802`).

> **Caveat.** The audit prompt says *"6 parts **+** glossary"* (i.e. seven
> sections). The manual ships with **5 content parts + glossary as Part 6**
> (= six sections in total). If the requirement is *six content parts plus a
> separate glossary*, an additional part covering `structures_ttf.py` and/or
> `ttf_time.py` is missing and this check should be downgraded to FAIL.
> Marked PASS because the manual's own ToC matches "6 parts including the
> glossary", which is the simplest reading consistent with the file.

---

## 2. `user_manual.html` matches `user_manual.md` content — PASS

Heading-by-heading comparison of the two files (`grep '^#'` on the Markdown
vs. `grep '<h[1-3]'` on the HTML) shows a 1-to-1 match:

| Section | Markdown anchor | HTML anchor |
|---------|-----------------|-------------|
| 1. Introduction | `user_manual.md:25` | `user_manual.html:54` |
| 1.1–1.3 | present | present |
| 2. `black76_ttf.py` | `user_manual.md:93` | `user_manual.html:185` |
| 2.1–2.8 | present | present |
| 3. `ttf_market_data.py` | `user_manual.md:502` | `user_manual.html:564` |
| 3.1–3.10 | present | present |
| 4. `ttf_hh_spread.py` | `user_manual.md:1025` | `user_manual.html:1155` |
| 4.1–4.8 | present | present |
| 5. `dashboard_jupyter.ipynb` | `user_manual.md:1343` | `user_manual.html:1471` |
| 5.0–5.5 | present | present |
| 6. Financial glossary | `user_manual.md:1564` | `user_manual.html:1897` |
| 6.1–6.8 | present | present |
| Appendix A | `user_manual.md:1788` | `user_manual.html:2116` |
| Appendix B | `user_manual.md:1802` | `user_manual.html:2154` |

Both files state the ICE TFO algorithm identically:

* `user_manual.md:164` — *"Candidate = 1st of delivery month − 5 calendar days."*
* `user_manual.html:316` — *"Candidate = 1st of delivery month − 5 calendar days."*

No structural drift detected.

---

## 3. `README.md` includes all modules and the ICE TFO definition — FAIL

**ICE TFO definition** — present and correct (`README.md:316–332`):

> *"TTF options follow the official **ICE TFO** (TTF Options) contract rule.
> ICE product code: **TFO**. Trading will cease when the intraday settlement
> price of the underlying futures contract is set, five calendar days before
> the start of the contract month…"*

**Modules** — the README only lists 5 modules in the *Features* table
(`README.md:17–23`):

* `black76_ttf.py`
* `ttf_market_data.py`
* `ttf_time.py`
* `pricing/`
* `dashboard/`

The following top-level modules **exist in the repo but are not mentioned
anywhere in the README** (verified with `grep -n "structures\|hh_spread\|
dashboard_ttf\|dashboard_jupyter" README.md` → no matches):

| Missing module | Purpose |
|----------------|---------|
| `ttf_hh_spread.py` | TTF/Henry-Hub Margrabe spread option (≈ 21 KB, has its own user-manual chapter) |
| `structures_ttf.py` | 10 multi-leg payoffs used by the dashboard (≈ 22 KB) |
| `dashboard_ttf.py` | Streamlit/CLI dashboard companion (≈ 36 KB) |
| `dashboard_jupyter.ipynb` | Jupyter dashboard with 5 interactive sections (≈ 37 KB) |

`ttf_hh_spread.py` and `structures_ttf.py` in particular are first-class
modules covered by Parts 4 and 5.2 of the user manual, so omitting them
from the README is a real gap.

**Verdict — FAIL** (ICE TFO present, but the module list is incomplete).

---

## 4. Expiry date is the correct ICE TFO definition everywhere — FAIL

**User-facing docs — correct.**
The ICE TFO rule (5 *calendar* days before the start of the contract month,
roll back to nearest prior UK business day, with the futures-LTD tiebreak)
is stated correctly and consistently in:

* `README.md:321–326` (full quoted rule)
* `user_manual.md:114–119, 162–166` (rule + 3-step algorithm)
* `user_manual.html:316, 1828` (same algorithm, rendered)

The 2026 expiry table (Jan-26 → Dec-26) is identical in `README.md:336–349`
and `user_manual.md:127–142` and matches the implementation in
`black76_ttf.ttf_expiry_date`.

**Code — incorrect rule still present.**
`ttf_time.py` still defines the legacy/incorrect rule in three docstrings:

* `ttf_time.py:330` — *"TTF options expiry: 5 business days before the futures expiry."*
* `ttf_time.py:332` — *"ICE/EEX convention: TTF options stop trading 5 business days before the underlying futures expires…"*
* `ttf_time.py:344` — *"TTF option expiry (= 5 business days before futures expiry)."*

These belong to `options_expiry_from_delivery()` and its alias
`expiry_from_delivery()`, which return a date that does **not** match the
official ICE TFO rule used by `black76_ttf.ttf_expiry_date`. The README
explicitly steers users away from `ttf_time.py` for expiry dates
(`README.md:21`), but the wrong rule is still in the public docstring of an
exported function.

**Verdict — FAIL** (definition correct in user-facing docs but incorrect in
shipped code docstrings).

---

## 5. Everything is in English only — PASS

* `grep -nE '[àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]' README.md user_manual.md user_manual.html` → no matches.
* `grep -niE '\b(le|la|les|des|une|bonjour|merci|année|sous-jacent|écart)\b'` produced no genuine French hits (only English `expir…` substrings).
* All section titles, table headers, code comments and prose in the three
  audited files are in English.

---

## 6. No reference to the wrong rule "5 business days before futures LTD" — FAIL

`grep -rn "5 business days\|five business days"` across `*.md`, `*.py`,
`*.html`, `*.ipynb` returns:

| File:line | Context | Verdict |
|-----------|---------|---------|
| `ttf_time.py:330` | Active docstring of `options_expiry_from_delivery` | **Wrong rule in shipped code** |
| `ttf_time.py:332` | Same docstring (ICE/EEX convention paragraph) | **Wrong rule in shipped code** |
| `ttf_time.py:344` | Active docstring of `expiry_from_delivery` | **Wrong rule in shipped code** |
| `consistency_report.md:188` | States the wrong rule as the convention without disclaimer | **Wrong rule in published doc** |
| `audit_report.md:112` | Tags it as the *"Legacy rule"* — historical context | OK |
| `audit_black76.md:116` | States the rule does **not** exist in `black76_ttf.py` | OK |

**No occurrences** in `README.md`, `user_manual.md`, `user_manual.html`,
`user_manual.pdf` (per text grep) or the dashboard sources.

**Verdict — FAIL.** Two artefacts (the `ttf_time.py` docstrings and
`consistency_report.md`) still describe the wrong rule as if it were the
authoritative ICE TFO definition. They should either be corrected to the
"5 calendar days before the start of the contract month" rule, or be
explicitly flagged as the legacy/non-ICE convention they implement.

---

## Recommendations

1. **README** — extend the *Features* table to list `ttf_hh_spread.py`,
   `structures_ttf.py`, `dashboard_ttf.py` and `dashboard_jupyter.ipynb`,
   and update the *Project Structure* tree to match.
2. **`ttf_time.py`** — rewrite the docstrings of
   `options_expiry_from_delivery` / `expiry_from_delivery` so they no
   longer claim to implement the ICE TFO rule. Either delete the helpers
   or relabel them as a non-ICE "5 business days before futures LTD"
   convention with a pointer to `black76_ttf.ttf_expiry_date` for the
   official rule.
3. **`consistency_report.md`** — fix the rule statement at line 188 (or
   add a disclaimer) so it agrees with the ICE TFO definition used in
   `README.md` and `user_manual.md`.
4. **`user_manual.md`** — if the project standard is genuinely *6 content
   parts + a separate glossary*, add a part covering `structures_ttf.py`
   (and optionally `ttf_time.py`) and renumber the glossary accordingly.
