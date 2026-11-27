# Submission Build & Layout Audit Report

* **Venue:** `<venue.name>` (`template_year: <year>`)
* **Submission Mode:** `<double-blind | preprint | camera-ready>`
* **Converter:** `pandoc | agent_fallback`
* **Compiler:** `<latexmk | pdflatex | xelatex | tectonic | none>`

PDF_COMPILATION: COMPLETED | FAILED | NOT_RUN
VISUAL_AUDIT: COMPLETED | DEGRADED_SOURCE_ONLY | NOT_RUN
POST_COMPILE_CRITIC: completed | skipped_no_pdf | not_run

## 1. Conversion Parity & Security Pre-Checks (`po_tools.py format-verify`)

* **Template Archive / TeX Shell-Pipe Scan:** `PASS | N/A | BLOCKED`
* **Markdown-to-LaTeX Parity (citations, labels, decimal tokens):** `PASS | BLOCKED`
* **Double-Blind Text, `%`-Comment & PDF Metadata Scan:** `PASS | N/A | BLOCKED`

## 2. TeX Compilation Telemetry

* **Main-Body Page Count (before `\bibliography`):** `<N> / <venue.page_limit_main>`
* **Undefined References / Citations:** `<0 or list>`
* **Missing Graphics:** `<0 or list>`
* **`Overfull \hbox > 2pt` Warnings:** `<0 or list>`

## 3. Post-Compile Visual Layout Audit (`po-visual-format-critic`)

Summarize findings from chunked (`<= 4–5` pages) inspection of compiled PDF/PNGs, or state why skipped (`skipped_no_pdf`).

## 4. Overleaf Anonymization & Re-Entry Checklist (When `PDF_COMPILATION: NOT_RUN`)

1. Upload all files inside `submission/` (excluding `build/` and `build_report.md`) to Overleaf.
2. Confirm double-blind mode is active (`\usepackage[review]{cvpr}` or `% \iclrfinalcopy` commented out) and inspect Overleaf PDF metadata.
3. To run the post-compile visual audit later, export `main.pdf` from Overleaf into `<paper_workspace>/submission/main.pdf` and re-run `po-format`.
