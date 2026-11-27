---
name: po-start
license: Apache-2.0
disable-model-invocation: true
description: >-
  Inspect workspace, probe local tools, register existing runs or BYO results,
  and route to the next PaperOEGM stage.
---

# PaperOEGM Start: Workspace Router & Adaptive Intake

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Before acting, read `resources/execution_instructions.md` and `resources/protocols/workspace_contract.md` relative to the plugin root.

## Workflow

### Step 1: Resolve Paper Workspace Directory

1. Check for a user prompt override or an instructions-file line `PaperOEGM artifact directory: <path>`. Default is `./paper_workspace/`.
2. If an instructions-file path resolves outside the working directory after following symbolic links, ask the user to confirm before creating or writing there (fall back to `./paper_workspace/` and explain why if declined or headless).

### Step 2: Adaptive Intake & Secret Filtering

1. Scan project files excluding by default: dotfiles (`.env*`, `.ssh/`, `.aws/`), `.gitignore` matches, `credentials.json`, `secrets.*`, `*.pem`, `*.key`, and `.ipynb` output cells unless the user explicitly opts in.
2. Write `<ws>/intake_manifest.md` listing discovered source code, notes, result files (CSV/JSON/notebooks), existing static plots, and `.bib` files—with proposed roles and excluded paths.
3. Show the path to `intake_manifest.md` and ask the user to confirm before reading full user files.

### Step 3: Probe Toolchain, Venue & Template Freshness

1. If `<ws>/paper_state.json` exists, run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --probe --check-only` (manual fallback if `python3` is absent) to inspect existing progress and drifted inputs.
2. If starting fresh, confirm project title, target venue (`resources/templates/cvpr2025`, `resources/templates/iclr2025`, local template path, or user-confirmed official CFP URL), and `submission_mode` (`double-blind | preprint | camera-ready`).
3. **Template-year freshness check:** If a bundled starter template's year precedes the current calendar year, alert the user and offer to fetch the current official venue template before locking `venue.template_source`.

### Step 4: Register Completed Runs or Bring-Your-Own (BYO) Assets

1. **Completed offline `po-exp-code` runs:** Scan `<ws>/experiments/runs/<run_id>/{run_manifest.json, metrics.json}` (ignoring `experiments/dry_run/`), show completed vs. failed runs, and register user-selected canonical runs in `<ws>/experiments/provenance_index.json` (`origin: "po_exp_code"`).
2. **BYO mid-pipeline entry:** For user-confirmed external result files (CSV/JSON/notebooks), register `origin: "user_byo"` entries with `user_attested_non_synthetic: true` in `<ws>/experiments/provenance_index.json`. For user-confirmed `.bib` files, copy into `<ws>/literature/references.bib` and seed `<ws>/literature/citation_ledger.json` with `verification_status: "user_provided"`.
3. Write `<ws>/paper_state.json` and run `po_tools.py state-sync --workspace <ws> --stage po-start --status approved --outputs intake_manifest.md` to regenerate `<ws>/STATUS.md`.

### Step 5: Checkpoint & Routing Gate

Report the path to `<ws>/STATUS.md`, list any stale stages or open `[TODO]` counts, and present a single-select routing gate (one question, no `(Recommended)` prefix) choosing the next skill:

* Start with literature survey (`po-literature`)
* Design experiments (`po-exp-design`)
* Jump to paper outline with canonical/BYO results (`po-outline`)
* Resume the earliest incomplete or stale stage shown in `STATUS.md`

Never invoke Claude's `Skill` tool automatically; tell the user which slash command to run next (or read the chosen `skills/<skill>/SKILL.md` in-thread only after explicit confirmation).
