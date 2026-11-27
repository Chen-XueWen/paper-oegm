# Experiment Design Plan

* **Project:** `<project_title>`
* **Target Venue:** `<venue_name>` (authoritative copy in `paper_state.json`)
* **Date:** `<YYYY-MM-DD>`

## 1. Research Questions & Falsifiable Hypotheses

| ID | Research Question | Hypothesis | Falsification Criterion |
| --- | --- | --- | --- |
| RQ1 | ... | ... | Hypothesis is refuted if ... |

## 2. Datasets, Splits & Evaluation Metrics

| Dataset | Split / Size | Preprocessing | Primary Metric | Secondary Metrics | Statistical Protocol |
| --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | `mean ± std` over `n >= 3` seeds |

## 3. Baselines & Fair Compute Budget

| Method | Code / Citation | Model Size | Compute / Epochs | Hyperparameter Budget |
| --- | --- | --- | --- | --- |
| Baseline A | `[@key]` | ... | ... | ... |
| Proposed Method | `src/...` | ... | ... | ... |

## 4. Experiment & Ablation Matrix

| `run_id` Pattern | Variant / Ablation | Seeds | Expected `metrics.json` Keys | Linked RQ |
| --- | --- | --- | --- | --- |
| `exp01_baseline_s<seed>` | ... | `42, 43, 44` | `primary_acc`, `latency_ms` | RQ1 |
| `exp02_ours_s<seed>` | ... | `42, 43, 44` | `primary_acc`, `latency_ms` | RQ1 |
| `exp03_ablation_no_x_s<seed>` | Remove component X | `42, 43, 44` | `primary_acc` | RQ2 |

## 5. Planned Result Tables & Figures

* **Table 1 (`tab_main`):** Main comparison across datasets (`exp01_*`, `exp02_*`).
* **Table 2 (`tab_ablation`):** Component ablations (`exp02_*`, `exp03_*`).
* **Figure 1 (`fig_convergence`):** Training curves from `series.csv`.

## 6. Negative-Result & Risk Policy

* Describe how negative or null outcomes will be reported honestly in `plan/outline.md` and `06_limitations.md`.
* List known threats to validity (compute limits, dataset scope, variance sensitivity).
