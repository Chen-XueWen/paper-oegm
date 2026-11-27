---
name: po-outline
license: Apache-2.0
disable-model-invocation: true
description: >-
  Reconcile planned vs. actual canonical runs and map claims, figures, tables,
  and citations into plan/outline.md.
---

# PaperOEGM Stage 3: Paper Outline & Evidence Mapping

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/workspace_contract.md`, and `skills/po-outline/references/outline_template.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `plan/outline.md`, `experiments/provenance_index.json` (on direct BYO entry or run canonicalization), optional BYO `literature/{references.bib, citation_ledger.json}` seed imports, `paper_state.json`, and `STATUS.md`.

## Workflow

### Step 1: Entry Sync & Direct BYO Intake Support

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent).
2. If the user entered directly at `po-outline` without running `po-start`, execute the shared intake secret-denylist and BYO registration flow from `resources/protocols/workspace_contract.md` (`origin: "user_byo"`, `user_attested_non_synthetic: true`, and optional `.bib` import with `verification_status: "user_provided"`).
3. Inspect `<ws>/experiments/provenance_index.json`, canonical `experiments/runs/*/{metrics.json, run_manifest.json}`, registered BYO data files, `<ws>/experiments/dry_run/` (strictly to verify exclusion), `<ws>/plan/experiment_design.md` (if present), and `<ws>/literature/literature_review.md` (if present).

### Step 2: Reconcile Planned vs. Actual Evidence

1. Identify every completed canonical run, failed run, missing ablation, and negative result.
2. **Anti-synthetic rule:** Never treat `experiments/dry_run/` or any run with `is_synthetic: true` as evidence. If real runs are still missing, explicitly tag affected claims `[PENDING_REAL_RUN]` and alert the user.
3. Highlight any `git_dirty: true` canonical runs so the author knows they will require diff attestation or clean re-runs before submission.

### Step 3: Draft `plan/outline.md`

Using `skills/po-outline/references/outline_template.md`, write `<ws>/plan/outline.md` containing:

1. **Read-Only Venue & Page Budget Reference:** Mirror venue name, `submission_mode`, and `page_limit_main` from `paper_state.json` (noting `paper_state.json` remains authoritative) and allocate target page budgets per section.
2. **Core Thesis & Contribution Bullets:** Grounded strictly in observed canonical results (calibrating claims to include negative results and limitations).
3. **Section-by-Section Plan:** Abstract, Introduction, Related Work, Method, Experiments, Limitations, Conclusion, and Appendix—with explicit claim -> `run_id` mappings, planned Figure IDs (`fig_<id>`), planned Table IDs (`tab_<id>`), and required citation slots.
4. **Visuals & Literature Handoff Lists:** Exact list of figures/diagrams needed in `po-visuals` and remaining Related Work gaps for `po-literature:late`.

### Step 4: Exit Sync & Human Approval Gate

1. Run `po_tools.py state-sync --workspace <ws> --stage po-outline --status awaiting_human_gate --inputs experiments/provenance_index.json --outputs plan/outline.md`.
2. Point the user to `<ws>/plan/outline.md` and present a single-select gate (one question, no `(Recommended)` prefix):
   * Approve outline and proceed to `po-literature` (late Related Work pass)
   * Approve outline and proceed to `po-visuals`
   * Revise section framing, page budgets, or planned figures in `plan/outline.md`
3. Update stage status to `approved` upon confirmation and tell the user which slash command to invoke next.
