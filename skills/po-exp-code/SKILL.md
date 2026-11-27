---
name: po-exp-code
license: Apache-2.0
disable-model-invocation: true
description: >-
  Generate experiment code, env.sh, check_env.sh, and safe runnable bash
  scripts emitting run_manifest.json and metrics.json.
---

# PaperOEGM Stage 3: Experiment Code & Runnable Bash Scripts

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/experiment_safety.md`, and `skills/po-exp-code/references/runner_template.sh` relative to the plugin root.

## Write Boundary

Allowed writes: user-approved `<paper_workspace>/experiments/` directory, `paper_state.json`, and `STATUS.md`. If any existing project file under `src/` must be modified, display the exact proposed diff and obtain explicit per-file user approval before editing.

## Workflow

### Step 1: Entry Sync & Scope Confirmation

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent).
2. Read `<ws>/plan/experiment_design.md` and relevant codebase files from `intake_manifest.md`.
3. Confirm target `experiments/` directory and any required `src/` diffs before writing code.

### Step 2: Generate Experiment Harness & Bash Runners

Using `skills/po-exp-code/references/runner_template.sh` and `resources/protocols/experiment_safety.md`, generate:

1. **`experiments/env.sh`:** Parameterized local paths, Python interpreter (`PYTHON_BIN`), dataset root, `CUDA_VISIBLE_DEVICES`, and telemetry disabled (`WANDB_MODE=offline`).
2. **`experiments/check_env.sh`:** Fast preflight validating interpreter, required Python imports, dataset paths, disk space, and GPU visibility without installing packages.
3. **Experiment entry scripts & `experiments/run_<exp_id>.sh`:**
   * Header `#!/usr/bin/env bash` + `set -euo pipefail`, double-quoted variables, zero `sudo` / `rm -rf` on user paths / `curl | sh` / silent `pip install`.
   * Writes startup `run_manifest.json` (`status: "running"`) immediately, registers `trap finalize EXIT` to record `finished_at`, `exit_code`, and final `status`, handles non-git directories (`git_commit: "none"`, `git_dirty: null`), and redacts sensitive CLI tokens and `$HOME` paths in `cmd`.
   * Writes compact `< 10 KB` `metrics.json` atomically (`metrics.json.tmp` -> `metrics.json`) and optional downsampled `series.csv` (`<= 500` rows) strictly inside `runs/<run_id>/` (never concurrently editing `provenance_index.json`).
   * Supports `--dry-run` (`< 60s` offline mock execution) writing strictly to `experiments/dry_run/<run_id>/` with `"is_synthetic": true`.

### Step 3: Local Smoke Test (`--dry-run` Only)

1. Never launch full GPU training jobs autonomously.
2. Run `bash experiments/check_env.sh` and `bash experiments/run_<exp_id>.sh --dry-run` locally (`< 60s` timeout) to verify exit code `0`, valid `run_manifest.json`, and valid `metrics.json` with `"is_synthetic": true` inside `experiments/dry_run/`.

### Step 4: Async GPU Handoff Gate

1. Update state via `po_tools.py state-sync --workspace <ws> --stage po-exp-code --status approved --inputs plan/experiment_design.md --outputs experiments/env.sh,experiments/check_env.sh`.
2. Present exact user-runnable GPU commands (e.g., `bash experiments/check_env.sh && bash experiments/run_<exp_id>.sh`) and explain that once offline runs finish, the user can open a fresh session and run `po-start` (or `po-outline`) to register canonical runs in `experiments/provenance_index.json`.
3. Present a single-select checkpoint gate (one question, no `(Recommended)` prefix) confirming whether the user wants to pause for offline GPU runs, adjust scripts, or inspect dry-run logs.
