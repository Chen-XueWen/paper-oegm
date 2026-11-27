---
name: po-review
license: Apache-2.0
disable-model-invocation: true
description: >-
  Run deterministic pre-checks and dispatch up to 5 fresh-context read-only
  critics flat in parallel to produce reviews/round_<N>/review_report.md.
---

# PaperOEGM Stage 7: Fresh-Context Parallel Peer Review

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/workspace_contract.md`, and `skills/po-review/references/review_report_template.md` relative to the plugin root.

## Write Boundary

The root session writes only `<ws>/reviews/round_<N>/review_report.md` (or `manual_review_prompts.md` fallback), `paper_state.json`, and `STATUS.md`. Critic subagents are strictly read-only.

## Workflow

### Step 1: Entry Sync & Deterministic Pre-Check

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent). Determine the next round number `N` under `<ws>/reviews/round_<N>/`.
2. Run deterministic pre-verification:

   ```bash
   python3 <plugin_root>/resources/scripts/po_tools.py review-preflight --workspace <ws>
   ```

   Record JSON blockers/majors (citation parity, `unverified_needs_human_check`, missing `literature/sources/`, `is_synthetic: true`, `git_dirty: true`, and inline `<!-- run:<run_id> -->` numeric checks). If `python3` is unavailable, instruct `po-evidence-auditor` and `po-citation-auditor` to perform these checks manually.

### Step 2: Fail-Closed Fresh-Context Check

Check whether the active host exposes a fresh-context subagent dispatch tool (Antigravity: named subagent dispatch; Claude Code: `Agent`; Codex: `spawn_agent` with `fork_context: false` / `fork_turns: "none"`).

* **If NO subagent tool exists** (e.g., standalone IDE without subagents): **Halt instead of self-reviewing in the authoring thread.** Write self-contained critic prompts with absolute file paths to `<ws>/reviews/round_<N>/manual_review_prompts.md` so the user can run them in fresh sessions, and stop.

### Step 3: Flat Parallel Dispatch (Up to 5 Read-Only Critics)

Never spawn a nested orchestrator. Dispatch directly from the root session in parallel (1 instance per applicable critic, `<= 1,500` tokens per critic, canonical runs only, `<= 4–5` figure/page chunks for visuals; never leak prior settled findings into critic prompts):

1. `agents/po-peer-reviewer.md` (`resources/review_standards/peer-review-standard.md`)
2. `agents/po-evidence-auditor.md` (`resources/review_standards/evidence-audit-standard.md`)
3. `agents/po-citation-auditor.md` (`resources/review_standards/citation-audit-standard.md`)
4. `agents/po-visual-format-critic.md` (`resources/review_standards/visual-format-standard.md` — mark `skipped_not_applicable` if no visuals exist yet)
5. `agents/po-clarity-reader.md` (`resources/review_standards/clarity-standard.md`)

* **On Codex (prompt-enforced read-only):** Snapshot `<ws>` with `po_tools.py check-readonly --workspace <ws> --snapshot <scratch>/ro.json --create` before dispatch and `--verify` on return (failing closed if any file changed).
* **Round >= 2 optimization:** Mark critics whose input file digests did not change since Round `N-1` as `carried_forward` instead of re-running.
* **Retry-once rule:** Retry any failed/timed-out critic once. Any remaining `not_run` entry blocks signing off the review round.

### Step 4: Compile `reviews/round_<N>/review_report.md` & Gate

1. Validate each critic return against the structured finding schema and write `<ws>/reviews/round_<N>/review_report.md` using `skills/po-review/references/review_report_template.md`, opening with the 4-state `## Reviewer Status` table (`completed | skipped_not_applicable | carried_forward | not_run`), pre-check summary, and prioritized findings (`Blocker -> Major -> Minor -> Nit`).
2. Run `po_tools.py state-sync --workspace <ws> --stage po-review --status awaiting_human_gate --outputs reviews/round_<N>/review_report.md`.
3. Present a single-select gate (one question, no `(Recommended)` prefix):
   * Proceed to `po-resolve` to triage findings and apply approved edits
   * Proceed directly to `po-format` (only if zero Blockers and zero `not_run` critics)
   * Pause here to inspect `reviews/round_<N>/review_report.md`
