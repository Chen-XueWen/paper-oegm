# PaperOEGM Shared Resources

This directory holds the harness-agnostic execution rules, cross-stage protocols, zero-dependency verification helper, critic review standards, and starter venue LaTeX templates used by `paper-oegm` skills and read-only critic personas.

## Directory Layout

* `execution_instructions.md` — Universal interaction rules, untrusted-data boundaries, and the Per-Stage Write Policy.
* `scripts/po_tools.py` — Zero-dependency Python 3.10+ stdlib CLI (`state-sync`, `check-readonly`, `review-preflight`, `format-verify`) with documented manual fallbacks when `python3` is unavailable.
* `protocols/` — Stage contracts and schemas:
  * `protocols/workspace_contract.md` — Canonical workspace tree, `paper_state.json`, `STATUS.md`, intake secret denylist, and Bring-Your-Own (BYO) registration.
  * `protocols/experiment_safety.md` — Safe runnable bash script contract, `run_manifest.json`, `metrics.json`, `series.csv`, and `provenance_index.json`.
  * `protocols/citation_provenance.md` — Primary-source citation verification, `literature/sources/`, deduplication, and `citation_ledger.json`.
  * `protocols/visual_standards.md` — Quantitative vs. conceptual figure rules, `visuals/manifest.md`, legibility checklist, and `VISUAL_AUDIT` states.
  * `protocols/markdown_manuscript.md` — Per-section LaTeX-friendly Markdown conventions, `manuscript.yaml`, and inline `<!-- run:<run_id> -->` provenance comments.
  * `protocols/formatting_and_build.md` — Venue template freshness, Zip Slip/shell-pipe checks, `pandoc` conversion, paranoid TeX compilation, Overleaf fallback, and `build_report.md`.
* `review_standards/` — Audit rubrics loaded by the 5 stateless read-only critics:
  * `review_standards/peer-review-standard.md`
  * `review_standards/evidence-audit-standard.md`
  * `review_standards/citation-audit-standard.md`
  * `review_standards/visual-format-standard.md`
  * `review_standards/clarity-standard.md`
* `templates/` — Unmodified upstream conference `.sty`/`.bst` starter files with PaperOEGM double-blind starter `template.tex` and `guidelines.md`:
  * `templates/cvpr2025/`
  * `templates/iclr2025/`
