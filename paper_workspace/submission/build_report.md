# Submission Build & Layout Audit Report

* **Venue:** `agentskills2027` (`template_year: 2027`, `\documentclass[sigplan,review,anonymous,pbalance]{acmart}`)
* **Submission Mode:** `double-blind`
* **Converter:** `pandoc` (`--from markdown+tex_math_dollars+raw_tex+citations --to latex --natbib --wrap=none` + post-processing for 2/3-line aligned equations, `\textasciitilde{}` cleanup, indivisible `\mbox{-{}-}` CLI flags, clean breakable `\texttt` paths/commas, `\footnotesize` tables, and `\begin{figure*}[t]`)
* **Compiler:** `pdflatex` + `bibtex` (TeX Live 2026 via `submission/compile.sh`: `openin_any=p openout_any=p --no-shell-escape`)

PDF_COMPILATION: COMPLETED
VISUAL_AUDIT: COMPLETED
POST_COMPILE_CRITIC: completed

## 1. Conversion Parity & Security Pre-Checks (`po_tools.py format-verify`)

* **Template Archive / TeX Shell-Pipe Scan:** `PASS` (`0` blockers across `submission/`)
* **Markdown-to-LaTeX Parity (citations, labels, decimal tokens):** `PASS` (`0` dropped citations, labels, or decimals across all 7 sections)
* **Double-Blind Text, `%`-Comment & PDF Metadata Scan:** `PASS` (`0` blockers in `.tex`; `pdfinfo` confirms empty `/Author` and `/Producer`, zero personal paths/usernames; generic non-identifying `Creator: LaTeX with acmart 2025/08/27 v2.16 ...` injected by `acmart`/`hyperxmp`)
* **Preflight Provenance Check (`po_tools.py review-preflight`):** `PASS` (`ok: true`, `0` blockers, `20/20` citations verified, `4/4` canonical aggregate runs verified; `git_dirty: true` Majors attested in `reviews/round_1/resolution_report.md` because `paper_workspace/` is tracked in git while `git diff -- ':!paper_workspace'` is empty)

## 2. TeX Compilation Telemetry

* **Main-Body Page Count (before `\bibliography`):** `9 / 9` (**PASS**; Section 6 Conclusion finishes on Page 9 right column line 967, followed by `References` starting on Page 9 through Page 10; `10` pages total)
* **Undefined References / Citations:** `0`
* **Missing Graphics:** `0`
* **`Overfull \hbox > 2pt` Warnings:** `1` (`3.07pt` at `04_method.tex` lines 56–57; visually clean on `page-04.png` with zero gutter/margin protrusion; reduced from 60+ initially)
* **Column Balance Warnings:** `0` (`acmart` `pbalance` option balances final Page 10 cleanly: `[6]`–`[11]` left column vs. `[12]`–`[20]` right column)

## 3. Post-Compile Visual Layout Audit (`po-visual-format-critic` + Direct 10-Page Inspection)

Two Pass 2 visual audit cycles were executed on `150 DPI` rasterized PNGs (`submission/build/pages/page-*.png`):

* **Pass 2 Cycle 1 (Pre-Trim 13-page build, 3 read-only chunks):** Fixed odd-page running header collision via short `\title[...]` + `\acmConference[Agent Skills '27]{...}`, wrapped Equations (1)–(2), scaled Tables 1–3 with `\footnotesize` + `\setlength{\tabcolsep}{4pt}`, normalized `\textasciitilde{}` refs, switched arXiv preprints to `@misc` (`eprint`/`archivePrefix`) to remove duplicate years, and routed the `12 / 9` page overrun through `po-resolve` (`manuscript/snapshots/round_2/`, trimming `7,104` → `5,015` words while preserving all 20 citations, 4 figures, 3 tables, 2 equations, and every empirical finding).
* **Pass 2 Cycle 2 (Trimmed 10-page build, 2 flat parallel read-only chunks: `pages 1–5` and `pages 6–10`):**
  * **Pages 6–10 Critic Verdict:** `0 Blockers, 0 Majors`, `1 Minor`, `3 Nits`. Confirmed strict `9 / 9` main-body limit compliance, clean double-blind compliance, zero `Overfull \hbox`, crisp Figures 2–4 and Tables 1–3.
  * **Pages 1–5 Critic Verdict:** `0 Blockers, 2 Majors`, `4 Minors`, `1 Nit`.
  * **All Cycle 2 Findings Resolved & Visually Re-Verified Across All 10 Pages:**
    * `visual-r2-01` (Major): Indented Equation (2) and continuation inside item 3 of `04_method.md` so `4. format-verify:` renders cleanly inside the unified `enumerate` list.
    * `visual-r2-02` (Major): Wrapped Equation (2) onto 3 narrow aligned lines inside `\begin{aligned}`, clearing both column edges cleanly inside `enumerate`.
    * `visual-r2-03` / `visual-r2-04` / `visual-r2-05` / `p6-10 visual-r2-01` (Minors): Added `\allowbreak{}` after commas inside `\texttt{...}`, suppressed trailing `\allowbreak{}` before `}`, protected double-dash CLI flags with `\mbox{-{}-}` (`--dry-run`, `--no-shell-escape`), and allowed breaks at `\immediate\allowbreak{}\write18` and filename dots.
    * `visual-r2-06` (Minor): Corrected `"We make four contributions:"` → `"We make five contributions:"` in `manuscript/sections/02_introduction.md`.
    * `visual-r2-07` & `p6-10 visual-r2-02`..`04` (Nits): Harmonized Phase 2 (`Plan & Draft`) and Phase 3 (`Review & Build`) labels in `04_method.md` to match Figure 1; added `\renewcommand\showeprint[2][]{arXiv:#2.}` in `main.tex` for uniform bibliography punctuation; protected `{Han-chung} Lee` in `references.bib`; switched to `acmart` `pbalance` option eliminating the `\balance` warning while balancing Page 10 symmetrically.
* **Final Post-Fix Visual Check:** All 10 rasterized pages (`page-01.png`–`page-10.png`) visually verified clean: **0 Blockers, 0 Majors** remaining.

## 4. Overleaf Anonymization & Re-Entry Checklist

*Not applicable (`PDF_COMPILATION: COMPLETED` locally via TeX Live 2026); `submission/` is also self-contained (`figures/`, `sections/`, `references.bib`, `main.tex`, `compile.sh`) for direct Overleaf upload if desired.*
