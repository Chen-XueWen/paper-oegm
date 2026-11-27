---
name: po-draft
license: Apache-2.0
disable-model-invocation: true
description: >-
  Draft per-section LaTeX-friendly Markdown manuscripts with inline run
  provenance tags and manuscript/manuscript.yaml.
---

# PaperOEGM Stage 6: Markdown-First Manuscript Drafting

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md` and `resources/protocols/markdown_manuscript.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `manuscript/manuscript.yaml`, `manuscript/sections/*.md`, `paper_state.json`, and `STATUS.md`.

## Workflow

### Step 1: Entry Sync & Context Load

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent).
2. Read `<ws>/plan/outline.md`, `<ws>/literature/literature_review.md`, `<ws>/literature/citation_ledger.json`, `<ws>/visuals/manifest.md`, `<ws>/experiments/provenance_index.json`, and canonical `experiments/runs/*/{metrics.json, run_manifest.json}` (or registered BYO files).

### Step 2: Author `manuscript/manuscript.yaml` & Per-Section Markdown

1. Create `<ws>/manuscript/manuscript.yaml` containing **only** `schema_version`, ordered `sections` filenames, and camera-ready `authors` metadata (venue, title, and `submission_mode` remain solely in `paper_state.json`).
2. Draft modular sections under `<ws>/manuscript/sections/` (`01_abstract.md` through `07_conclusion.md`, plus appendix sections if planned) following `resources/protocols/markdown_manuscript.md`:
   * Use `$...$` / `$$...$$` + `{#eq:id}` for equations, `[@key]` / `@key` strictly for keys present in `literature/references.bib`, and `![caption](../visuals/assets/fig_id.pdf){#fig:id}` for visuals from `visuals/manifest.md`.
   * Use pipe tables for simple tables or fenced ` ```{=latex} ... ``` ` blocks with `booktabs` and `\label{tab:id}` for complex multi-column tables.
   * Immediately above every quantitative table or headline-metric paragraph, insert an inline provenance comment `<!-- run:<run_id> -->` matching a canonical non-synthetic entry in `experiments/provenance_index.json`.
   * **Anti-fabrication gate:** Never invent missing results or cite `experiments/dry_run/` / `is_synthetic: true`. Insert `[PENDING_REAL_RUN]` or `[TODO: USER DATA REQUIRED]` wherever measurements are absent.
   * **Explicit limitations:** Write `06_limitations.md` candidly covering negative results, compute costs, assumptions, and threats to validity.

### Step 3: Self-Check Before Checkpoint

Verify every cited key exists in `literature/references.bib`, every figure path exists in `visuals/manifest.md`, and abstract claims match `05_experiments.md` and `07_conclusion.md`.

### Step 4: Exit Sync & Human Approval Gate

1. Run `po_tools.py state-sync --workspace <ws> --stage po-draft --status awaiting_human_gate --inputs plan/outline.md,literature/references.bib,visuals/manifest.md --outputs manuscript/manuscript.yaml,manuscript/sections/01_abstract.md,manuscript/sections/05_experiments.md`.
2. Report section word/page estimates and any open `[TODO]` / `[PENDING_REAL_RUN]` counts, then present a single-select gate (one question, no `(Recommended)` prefix):
   * Approve draft and proceed to fresh-context peer review (`po-review`)
   * Revise specific manuscript sections before review
   * Return to `po-visuals` or `po-literature` to fill missing assets or citations
3. Mark stage `approved` upon confirmation and tell the user which slash command to invoke next.
