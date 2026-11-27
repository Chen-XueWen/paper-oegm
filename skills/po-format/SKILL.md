---
name: po-format
license: Apache-2.0
disable-model-invocation: true
description: >-
  Convert Markdown sections to modular venue LaTeX, verify parity and anonymity,
  compile PDF or export Overleaf bundle, and audit layout.
---

# PaperOEGM Stage 9: Venue Formatting, Build & Layout Audit

When running in Codex or ChatGPT Work, first read [Codex integration](../../docs/codex.md).
In Claude Code or Cowork, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first.

## Required Rules & Protocols

Read `resources/execution_instructions.md`, `resources/protocols/formatting_and_build.md`, `resources/review_standards/visual-format-standard.md`, and `skills/po-format/references/build_report_template.md` relative to the plugin root.

## Write Boundary

Allowed writes inside `<paper_workspace>/`: `submission/`, `paper_state.json`, and `STATUS.md`. Never edit `manuscript/sections/*.md` silently from `po-format`—route prose trimming or anonymity text changes back to `po-resolve`, and figure resizes back to `po-visuals`.

## Workflow

### Step 1: Entry Sync, Template Freshness & Archive Security

1. Run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws> --check-only` (manual fallback if `python3` is absent). Warn if `po-review` is stale or has open Blockers.
2. Check `venue.template_year` in `paper_state.json` against the current year; if older, alert the user and offer fetching the current official CFP template.
3. For any fetched or user-supplied template archive, run `po_tools.py format-verify --workspace <ws> --archive <path>` before extraction to block Zip Slip and explicit `\write18` / `\input{|` shell pipes. Keep upstream `.sty`/`.bst`/`.cls` files byte-for-byte unmodified.

### Step 2: Modular Conversion & Deterministic Parity Verification

1. Read section order from `<ws>/manuscript/manuscript.yaml` and venue/mode from `<ws>/paper_state.json`.
2. Convert each section into `<ws>/submission/sections/<stem>.tex` using `pandoc` (`--natbib` for `natbib` venues; numeric `\cite` preserving narrative author names for `cite` venues; per-section agent conversion fallback when `pandoc` is absent), stripping `<!-- run:... -->` HTML comments.
3. Write thin venue wrapper `<ws>/submission/main.tex` (`\input{sections/...}`, marked `% === Layout Tuning Block ===` preamble section, `\hypersetup{pdfauthor={},pdfcreator={},pdfproducer={}}` in `double-blind` mode), sync `<ws>/literature/references.bib` and LaTeX-ready PDF/PNG figures into `<ws>/submission/figures/`, and write `<ws>/submission/compile.sh` (`openin_any=p openout_any=p`, wall-clock `timeout`, `--no-shell-escape`, isolated `build/` dir).
4. Run `python3 <plugin_root>/resources/scripts/po_tools.py format-verify --workspace <ws> --check-tex-dir <ws>/submission` to verify `.md`↔`.tex` numeric-token, citation-key, and label parity plus double-blind text/`%`-comment hygiene.

### Step 3: Local Compile (or Overleaf Mode) & Post-Compile Visual Audit

* **If `tex_compiler != "none"`:** Run `bash submission/compile.sh` (cap compile-error repair iterations at 2–3 passes), inspect metadata with `pdfinfo` in `double-blind` mode when available, re-run `po_tools.py format-verify --workspace <ws>` for `.log`/`.aux`/`.blg` telemetry, rasterize pages (`pdftoppm -png -r 150` or `python_pymupdf` if available; fallback to direct `read_file` on `submission/main.pdf`), and dispatch `agents/po-visual-format-critic.md` in a fresh read-only subagent on `<= 4–5` page chunks.
* **If `tex_compiler == "none"` (Overleaf mode):** Skip compilation, record `PDF_COMPILATION: NOT_RUN`, `VISUAL_AUDIT: NOT_RUN`, and `POST_COMPILE_CRITIC: skipped_no_pdf`, include an Overleaf anonymization checklist in `submission/build_report.md`, and document how to re-run `po-format` after saving an Overleaf-exported `main.pdf` in `submission/`.

### Step 4: Write `submission/build_report.md`, Exit Sync & Final Gate

1. Write `<ws>/submission/build_report.md` from `skills/po-format/references/build_report_template.md`.
2. Run `po_tools.py state-sync --workspace <ws> --stage po-format --status approved --inputs manuscript/manuscript.yaml,literature/references.bib --outputs submission/main.tex,submission/build_report.md`.
3. Present a single-select final gate (one question, no `(Recommended)` prefix):
   * Finalize submission bundle
   * Route prose trimming or anonymity fixes to `po-resolve`
   * Route figure resizes or re-exports to `po-visuals`
   * Adjust global spacing in `submission/main.tex` layout block and recompile
