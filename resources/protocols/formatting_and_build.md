# Formatting, Conversion & LaTeX Build Protocol

This protocol governs `po-format` (Stage 9).

## 1. Template-Year Freshness & Archive Safety

* Check `venue.template_year` in `paper_state.json` against the current calendar year. If a bundled starter template (`resources/templates/cvpr2025` or `resources/templates/iclr2025`) precedes the current year, alert the researcher and offer to fetch the current official venue CFP template before formatting.
* Keep upstream `.sty`/`.bst`/`.cls` files byte-for-byte unmodified.
* Before extracting or using any user-supplied or web-fetched venue template archive, run:

  ```bash
  python3 <plugin_root>/resources/scripts/po_tools.py format-verify --workspace <ws> --archive <archive_path>
  ```

  Reject any archive with Zip Slip path traversal (`../` or absolute paths) or explicit `\write18` / `\input{|` shell-pipe constructs. (Manual fallback if `python3` is absent: list archive contents with `unzip -l` / `tar -tf` and inspect `.sty`/`.cls`/`.tex` files before extraction.)

## 2. Structure-Preserving Markdown-to-LaTeX Conversion

* Read section ordering from `manuscript/manuscript.yaml` and venue/mode settings from `paper_state.json`.
* Prefer deterministic per-section conversion with `pandoc` (when `environment.pandoc == "available"`):
  * For `citation_macro_style == "natbib"` (e.g., ICLR): convert with `--natbib` so `[@key]` -> `\citep{key}` and `@key` -> `\citet{key}`.
  * For `citation_macro_style == "cite"` (e.g., CVPR): convert `[@key]` -> `\cite{key}` and expand narrative `@key` to preserve author names (e.g., `Smith et al.~\cite{key}`) from `literature/references.bib`.
  * Emit modular `submission/sections/<stem>.tex` files and strip inline `<!-- run:... -->` provenance comments.
  * When `pandoc` is unavailable, convert section by section with the coding agent while keeping modular `submission/sections/*.tex`.
* Generate a thin venue wrapper `submission/main.tex` that `\input{sections/<stem>}` in `manuscript.yaml` order, includes a clearly marked `% === Layout Tuning Block ===` in the preamble for global spacing/float-fraction adjustments only, and syncs `literature/references.bib` plus LaTeX-ready PDF/PNG assets into `submission/figures/` (never raw `.svg` requiring `--shell-escape`).
* **No split-brain edits:** Prose trimming, double-blind text edits, and citation fixes must route back to `po-resolve` (`manuscript/sections/*.md`); figure resizes or re-exports route back to `po-visuals`.
* Run `python3 <plugin_root>/resources/scripts/po_tools.py format-verify --workspace <ws> --check-tex-dir <ws>/submission` to verify `.md`↔`.tex` numeric-token, citation-key, and equation/figure-label parity before compiling.

## 3. Double-Blind Hygiene & Paranoid Compilation

* In `double-blind` mode:
  * Inject `\hypersetup{pdfauthor={},pdfcreator={},pdfproducer={}}` into `submission/main.tex` preamble (after `hyperref` loads).
  * Confirm CVPR uses `\usepackage[review]{cvpr}` and ICLR keeps `% \iclrfinalcopy` commented out.
  * Verify `po_tools.py format-verify` reports zero author names, local paths, identifying URLs, or `%`-comment leaks across `submission/*.tex` and `submission/sections/*.tex`.
  * When compiled locally and `pdfinfo` is available, inspect compiled `submission/main.pdf` metadata fields.
* Write reproducible `submission/compile.sh` enforcing native TeX paranoid sandboxing:
  * `openin_any=p openout_any=p`
  * `--no-shell-escape` (never `--shell-escape`)
  * Wall-clock timeout (e.g., `120s` per pass) and isolated auxiliary output under `submission/build/`.
  * Cap automated LaTeX/BibTeX compile repair loops at 2–3 iterations before escalating with plain-English `.log`/`.blg` diagnostics.
* **Overleaf Degraded Mode:** When `environment.tex_compiler == "none"`, write the complete modular `submission/` bundle, run `po_tools.py format-verify` static parity + double-blind checks, include an Overleaf anonymization checklist in `submission/build_report.md`, record `PDF_COMPILATION: NOT_RUN`, `VISUAL_AUDIT: NOT_RUN`, and `POST_COMPILE_CRITIC: skipped_no_pdf`, and instruct the user how to re-run `po-format` after saving an Overleaf-exported `main.pdf` into `submission/`.

## 4. Post-Compile Visual Audit & `submission/build_report.md`

* When `submission/main.pdf` exists, re-run `po_tools.py format-verify --workspace <ws>` to record TeX `.log`/`.aux`/`.blg` telemetry (`Overfull \hbox > 2pt`, undefined refs/cites, missing graphics, main-body page count before `\bibliography`).
* **Initial PDF inspection default:** Rasterize PDF pages to PNGs via `pdftoppm -png -r 150` (or `python_pymupdf`) when available, falling back to direct multimodal `read_file` on `submission/main.pdf`. Dispatch `po-visual-format-critic` in a fresh read-only subagent on `<= 4–5` page chunks (prioritizing pages with figures, tables, or `Overfull` warnings).
* `submission/build_report.md` must include literal status lines:
  * `PDF_COMPILATION: COMPLETED | FAILED | NOT_RUN`
  * `VISUAL_AUDIT: COMPLETED | DEGRADED_SOURCE_ONLY | NOT_RUN`
  * `POST_COMPILE_CRITIC: completed | skipped_no_pdf | not_run`
