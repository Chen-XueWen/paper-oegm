---
name: po-exp-design
license: Apache-2.0
disable-model-invocation: true
description: >-
  Plan research questions, hypotheses, baselines, datasets, ablations, seeds,
  and metric schemas in plan/experiment_design.md.
---

# PaperOEGM Stage 1: Experiment Design

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/workspace_contract.md`, and `skills/po-exp-design/references/experiment_design_template.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `plan/experiment_design.md`, `paper_state.json`, and `STATUS.md`. Do **not** modify user source code or launch training jobs in this stage.

## Workflow

### Step 1: Entry State Check & Context Intake

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent) to verify `paper_state.json` and check upstream digest drift.
2. Read `<ws>/intake_manifest.md`, `<ws>/literature/literature_review.md` (if `po-literature:early` ran), and user-approved idea notes or starter codebase files.
3. Ask focused clarifying questions—one question at a time—only for genuinely missing research constraints (compute budget, target datasets, hardware limits, primary metric, or required baselines).

### Step 2: Draft `plan/experiment_design.md`

Using `skills/po-exp-design/references/experiment_design_template.md`, write `<ws>/plan/experiment_design.md` covering:

1. **Research Questions (RQs) & Falsifiable Hypotheses:** State what would *refute* each hypothesis, not only what would confirm it.
2. **Baselines & Fair Comparison Budget:** Match model sizes, training budgets, data splits, and hyperparameter tuning effort across proposed and baseline methods.
3. **Datasets, Splits & Evaluation Metrics:** Name exact datasets, preprocessing, train/val/test splits, primary and secondary metrics, and statistical significance tests (multi-seed `mean ± std`, `n >= 3` where feasible).
4. **Ablation Matrix & Negative-Result Plan:** Map each proposed component to an explicit ablation experiment and define how null or negative outcomes will be reported.
5. **Expected `metrics.json` Keys & Planned Result Tables:** Pin exact metric key names and `run_id` naming conventions (`exp<NN>_<variant>_s<seed>`) so `po-exp-code` and `po-outline` align without translation.

### Step 3: Stress-Test Before Presenting

Challenge the draft plan in 3–5 concise bullets before presenting the checkpoint: flag weak baselines, potential data leakage, single-seed variance gaps, or compute bottlenecks.

### Step 4: Exit Sync & Human Approval Gate

1. Run `po_tools.py state-sync --workspace <ws> --stage po-exp-design --status awaiting_human_gate --inputs intake_manifest.md --outputs plan/experiment_design.md`.
2. Point the user to `<ws>/plan/experiment_design.md` and present a single-select gate (one question, no `(Recommended)` prefix):
   * Approve experiment design and proceed to `po-exp-code`
   * Revise specific baselines, ablations, or metrics in `plan/experiment_design.md`
   * Run `po-literature` first to verify missing baselines or datasets
3. Upon approval, update stage status to `approved` via `po_tools.py state-sync` and instruct the user to invoke `po-exp-code`.
