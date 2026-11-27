---
name: po-visuals
license: Apache-2.0
disable-model-invocation: true
description: >-
  Generate reproducible data plots from canonical metrics and vector paper
  diagrams, visually inspect assets, and write visuals/manifest.md.
---

# PaperOEGM Stage 5: Publication Visuals & Reproducible Plots

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md` and `resources/protocols/visual_standards.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `visuals/scripts/`, `visuals/assets/`, `visuals/manifest.md`, `paper_state.json`, and `STATUS.md`.

## Workflow

### Step 1: Entry Sync & Visual Inventory

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent).
2. Read `<ws>/plan/outline.md`, `<ws>/experiments/provenance_index.json`, canonical `experiments/runs/*/{metrics.json, series.csv, run_manifest.json}`, registered BYO data/plots, and venue guidelines (`paper_state.json` `venue.template_source`).
3. Confirm the planned figure list and identify whether any pre-existing static user plots should be registered as `generator: "byo_static_asset"` with source-data attestation.

### Step 2: Author Quantitative Plots & Conceptual Diagrams

1. **Newly generated quantitative plots (strictly code-rendered):**
   * Write a reproducible script `visuals/scripts/fig_<id>.py` reading directly from canonical `metrics.json` / `series.csv` or registered BYO data files—zero hardcoded result arrays.
   * Refuse `experiments/dry_run/` or `is_synthetic: true` inputs. Never call generative raster image tools on numerical data.
   * Use colorblind-safe palettes paired with distinct line styles, markers, or hatching; exclude embedded figure captions; strip PDF metadata (`Author`, `Creator`, `Producer`) when `submission_mode == "double-blind"`.
2. **Conceptual diagrams & architecture figures:**
   * Default across all harnesses to version-controlled vector code (`visuals/scripts/fig_<id>.{tex,mmd,dot}` or SVG).
   * Where the active host exposes a native image generation tool, you may optionally use it for non-quantitative artwork/icons, tagging `Non-Quantitative = true` and `Generator = native_image_tool`.
3. **LaTeX-ready exports & previews:** Export `.pdf` or `.png` under `visuals/assets/fig_<id>.{pdf,png}` alongside any `.svg` sources (so `po-format` never needs `--shell-escape`), plus a high-DPI PNG preview when a rasterizer is available.

### Step 3: Multimodal Self-Inspection & `visuals/manifest.md`

1. Visually inspect each rendered PNG/PDF using the host's multimodal file reader against the legibility checklist in `resources/protocols/visual_standards.md` (cap figure polish iterations at 2–3 passes).
2. Record `VISUAL_AUDIT` honestly in `<ws>/visuals/manifest.md`:
   * `COMPLETED` — rendered PNG/PDF visually inspected.
   * `DEGRADED_SOURCE_ONLY` — only code/SVG inspected without raster visual preview.
   * `NOT_RUN` — visual check not performed.

### Step 4: Exit Sync & Human Approval Gate

1. Run `po_tools.py state-sync --workspace <ws> --stage po-visuals --status awaiting_human_gate --inputs plan/outline.md,experiments/provenance_index.json --outputs visuals/manifest.md`.
2. Point the user to `<ws>/visuals/manifest.md` and rendered assets, then present a single-select gate (one question, no `(Recommended)` prefix):
   * Approve figures and proceed to `po-draft`
   * Refine specific figures, styles, or captions in `po-visuals`
   * Return to `po-outline` to adjust figure allocation
3. Mark stage `approved` upon confirmation and tell the user which slash command to run next.
