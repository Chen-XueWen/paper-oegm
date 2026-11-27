# Paper Outline & Evidence Map

* **Working Title:** `<project_title>`
* **Venue & Page Limit (mirror from `paper_state.json`):** `<venue.name>` | `<venue.submission_mode>` | `<venue.page_limit_main>` main pages

## 1. Core Thesis & Verified Contributions

1. **Contribution 1:** ... (`run_id`: `exp02_ours_s42` vs. `exp01_baseline_s42`)
2. **Contribution 2:** ... (`run_id`: `...`)
3. **Explicit Scope & Negative Results:** ...

## 2. Canonical Evidence Summary

| `run_id` | Origin | Status | Key Metrics | Notes / `git_dirty` |
| --- | --- | --- | --- | --- |
| `exp01_baseline_s42` | `po_exp_code` | `canonical` | ... | ... |

## 3. Section-by-Section Plan & Page Budget

| Section File | Target Pages | Core Claims | Linked `run_id`s | Figures / Tables | Required Citations |
| --- | --- | --- | --- | --- | --- |
| `01_abstract.md` | 0.25 | ... | ... | — | — |
| `02_introduction.md` | 1.25 | ... | ... | `fig_overview` | `[@key]` |
| `03_related_work.md` | 1.00 | ... | — | — | `[@key]` |
| `04_method.md` | 2.00 | ... | — | `fig_arch` | `[@key]` |
| `05_experiments.md` | 2.50 | ... | `exp01_*`, `exp02_*` | `tab_main`, `fig_acc` | `[@key]` |
| `06_limitations.md` | 0.50 | ... | ... | — | — |
| `07_conclusion.md` | 0.50 | ... | ... | — | — |

## 4. Handoff to `po-visuals` & `po-literature:late`

* **Planned Figures:** `fig_overview` (diagram), `fig_acc` (quantitative plot from canonical `metrics.json`)
* **Remaining Citation Slots:** List missing dataset, benchmark, or baseline citations to verify in `po-literature:late`.
