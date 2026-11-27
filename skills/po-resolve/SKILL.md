---
name: po-resolve
license: Apache-2.0
disable-model-invocation: true
description: >-
  Snapshot manuscript sections, triage peer-review findings in batches, apply
  approved targeted edits, and write reviews/round_<N>/resolution_report.md.
---

# PaperOEGM Stage 8: Batched Review Resolution & Targeted Edits

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/markdown_manuscript.md`, and `skills/po-resolve/references/resolution_report_template.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `manuscript/snapshots/`, targeted edits to `manuscript/sections/*.md` and `manuscript/manuscript.yaml`, `reviews/round_<N>/resolution_report.md`, `paper_state.json`, and `STATUS.md`.

## Workflow

### Step 1: Entry Sync & Triage Batching

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent).
2. Read `<ws>/reviews/round_<N>/review_report.md`, any prior `resolution_report.md` settled-findings log, and affected `manuscript/sections/*.md` files.
3. Group all findings into three decision buckets inside `<ws>/reviews/round_<N>/resolution_report.md` using `skills/po-resolve/references/resolution_report_template.md`:
   * **Bucket 1 — Mechanical fixes (single batch diff):** Notation definitions, acronym expansions, typos, cross-reference syntax, or minor prose tightening.
   * **Bucket 2 — Scientific decisions (explicit researcher choice required):** Missing experiments/ablations, `git_dirty: true` waiver attestations, unverified citations, claim narrowing vs. new runs, or limitation additions. Never fabricate data or conceal limitations to clear a finding.
   * **Bucket 3 — Optional polish (`Minor` / `Nit`):** Stylistic suggestions the researcher may accept or decline.
4. **Anti-churn & settled-findings rules:**
   * Do not reopen findings marked settled in prior rounds unless the underlying evidence changed.
   * Cap edits to **max 2 revisions per finding** (escalating to the user instead of oscillating).

### Step 2: Human Triage Gate (Before Editing Manuscript)

Point the user to `<ws>/reviews/round_<N>/resolution_report.md` and yield for their batch decisions (e.g., accept Bucket 1, choose concrete actions for Bucket 2, accept/decline Bucket 3). Do **not** edit `manuscript/sections/*.md` until the user approves the resolution choices.

### Step 3: Snapshot & Apply Approved Targeted Edits

1. Copy every section scheduled for modification into `<ws>/manuscript/snapshots/round_<N>/`.
2. Apply approved targeted edits to `<ws>/manuscript/sections/*.md` (and `<ws>/manuscript/manuscript.yaml` if section order changed), preserving inline `<!-- run:<run_id> -->` provenance comments.
3. Record exact applied diffs, researcher waivers (e.g., `git_dirty: true` attestation), and updated settled-findings log in `<ws>/reviews/round_<N>/resolution_report.md`.
4. Run `po_tools.py state-sync --workspace <ws> --stage po-resolve --status approved --inputs reviews/round_<N>/review_report.md --outputs reviews/round_<N>/resolution_report.md` (advancing `po-draft` output hashes while marking `po-review` and `po-format` stale).

### Step 4: Back-Edge & Convergence Gate

Enforce the default 2-round review cap (if Blockers remain open after Round 2, offer either a targeted re-audit limited to modified sections or halting with open Blockers documented in `STATUS.md`). Present a single-select gate (one question, no `(Recommended)` prefix):

* Proceed to `po-format` (convert to venue LaTeX/PDF)
* Run targeted re-check in `po-review` (if Blockers were resolved)
* Route back to `po-exp-code` (new experiments/ablations needed)
* Route back to `po-visuals` or `po-literature` (figure re-render or missing citations needed)
