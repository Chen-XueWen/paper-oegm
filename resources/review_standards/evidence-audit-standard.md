# Evidence Audit Standard (`po-evidence-auditor`)

Use this rubric to verify scientific provenance between claims/tables/plots in `manuscript/sections/*.md` and recorded experimental outputs. Read only local workspace files; never execute commands or edit files.

## Audit Scope

Read `manuscript/sections/*.md`, `experiments/provenance_index.json`, canonical `experiments/runs/<run_id>/{metrics.json, run_manifest.json}`, registered BYO data files, `visuals/manifest.md`, and `visuals/scripts/*.py` (plus any `po_tools.py review-preflight` findings passed by the root agent).

## Audit Checks & Severity Rules

1. **Synthetic / Dry-Run Leakage (`Blocker`):** Any table cell, inline metric, or figure backed by `experiments/dry_run/`, a manifest/metrics file with `is_synthetic: true`, or an unregistered `run_id`.
2. **Numeric Transcription Drift (`Blocker`):** Any table cell, bolded headline number, delta calculation, or plot script value that disagrees with the referenced canonical `metrics.json` or BYO source beyond rounding precision, or any hardcoded numerical result array inside a newly generated `visuals/scripts/fig_*.py` script.
3. **Unbacked Claims & Missing Placeholders (`Blocker`):** Quantitative claims lacking an inline `<!-- run:<run_id> -->` pointer or canonical source when not marked `[PENDING_REAL_RUN]` / `[TODO: USER DATA REQUIRED]`.
4. **BYO Provenance Rules:** For `origin: "user_byo"` entries with `user_attested_non_synthetic: true`, waive `git_commit` and seed checks, but verify `source_path` exists and reported numbers match the BYO source. Flag `user_byo` entries lacking `user_attested_non_synthetic: true` as **Blocker**.
5. **Dirty Git Tree (`Major`):** Canonical `po_exp_code` runs with `git_dirty: true` in `run_manifest.json` (waivable by the researcher in `po-resolve` with an explicit recorded diff/attestation).
6. **Reproducibility Gaps (`Major` / `Minor`):** Missing seed counts (`n`), missing variance/error bars on multi-seed claims, or mismatched hyperparameter settings between `plan/experiment_design.md` and `run_manifest.json`.

## Output Contract

* Return structured findings with stable IDs `evidence-r<round>-<nn>` (`Affected Scope`, `Severity`, `Discrepancy`, `Evidence`, `Suggested Action`).
* Cap total output at `<= 1,500` tokens.
