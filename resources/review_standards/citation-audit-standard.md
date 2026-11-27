# Citation Audit Standard (`po-citation-auditor`)

Use this rubric to audit bibliographic integrity using strictly local workspace files. **Never fetch external URLs or run network lookups inside this reviewer.**

## Audit Scope

Read `manuscript/sections/*.md`, `literature/references.bib`, `literature/citation_ledger.json`, saved primary-source snapshots under `literature/sources/`, and `literature/literature_review.md` (plus any `po_tools.py review-preflight` findings passed by the root agent).

## Audit Checks & Severity Rules

1. **Key Parity (`Blocker`):** Every `[@key]`, `@key`, or `\cite*{key}` in `manuscript/sections/*.md` must resolve 1:1 to both `literature/references.bib` and `literature/citation_ledger.json`. Flag dangling keys or malformed BibTeX entries.
2. **Unverified Citations (`Blocker`):** Any cited entry tagged `unverified_needs_human_check`, or any `verified_source` entry missing its saved local snapshot in `literature/sources/`.
3. **User-Provided Entries (`user_provided`):** Verify the key exists in `literature/references.bib` with syntactically complete author/title/year fields; do **not** raise a Blocker solely because no abstract snapshot exists in `literature/sources/`.
4. **Claim-vs-Source Fidelity (`Blocker` / `Major`):** For entries with saved `literature/sources/` snapshots or `claim_summary` records, verify that manuscript claims attributed to the citation do not contradict or overstate the source paper's actual method, dataset, or result.
5. **Missing Foundational / Dataset / Baseline Citations (`Major`):** Flag named datasets, benchmarks, metrics, or compared baselines in the manuscript that lack citations.
6. **Unused / Duplicate Entries (`Minor` / `Nit`):** Flag duplicate papers under distinct citekeys (same DOI, arXiv ID, or title) and uncited entries left in `references.bib`.

## Output Contract

* Return structured findings with stable IDs `citation-r<round>-<nn>` (`Affected Scope`, `Severity`, `Discrepancy`, `Evidence`, `Suggested Action`).
* Cap total output at `<= 1,500` tokens.
