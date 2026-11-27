# Markdown-First Manuscript Protocol

This protocol defines the structure-preserving, per-section LaTeX-friendly Markdown format written by `po-draft` (Stage 6), refined by `po-resolve` (Stage 8), and converted to venue LaTeX by `po-format` (Stage 9).

## `manuscript/manuscript.yaml` Schema

`manuscript/manuscript.yaml` owns **only** section ordering and camera-ready author metadata. `project_title`, `venue`, and `submission_mode` live solely in `paper_state.json`.

```yaml
schema_version: "1.0"
sections:
  - 01_abstract.md
  - 02_introduction.md
  - 03_related_work.md
  - 04_method.md
  - 05_experiments.md
  - 06_limitations.md
  - 07_conclusion.md
authors:
  - name: "First Author"
    affiliation: "Institution"
    email: "author@institution.edu"
```

## Per-Section Markdown Conventions (`manuscript/sections/*.md`)

1. **Section headings:** Begin each section file with a single H1 (`# Section Title`), using `##` and `###` for subsections. Reserve `01_abstract.md` for a single abstract paragraph under `# Abstract`.
2. **Math & equations:** Use inline `$...$` and display `$$...$$` math. Attach explicit equation labels as `{#eq:id}` immediately after display equations or use raw LaTeX `\begin{equation}...\label{eq:id}\end{equation}` for multi-line derivations.
3. **Citations:**
   * Parenthetical citations: `[@key]` or `[@key1; @key2]` -> converted to `\citep{...}` (`natbib` venues like ICLR) or `\cite{...}` (numeric venues like CVPR).
   * Narrative citations: `@key` -> converted to `\citet{key}` (`natbib`) or `Author et al.~\cite{key}` (numeric venues, preserving author names).
4. **Figures & cross-references:** Reference figures by their `visuals/manifest.md` ID using `![Caption text.](../visuals/assets/fig_id.pdf){#fig:id width=0.9\linewidth}` and cross-reference via `@fig:id`, `@tab:id`, `@eq:id`, `@sec:id` (mapped to `\cref{...}` / `Figure~\ref{...}` according to venue guidelines).
5. **Tables:** Use standard pipe tables for simple comparisons; for multi-column headers (`\multicolumn`, `\multirow`) or publication `booktabs` layouts, embed a fenced `raw_latex` block (` ```{=latex} ... ``` `) with explicit `\label{tab:id}` so conversion preserves exact table markup.
6. **Inline Provenance Comments:** Immediately above every quantitative table or headline-metric paragraph, embed an inline HTML provenance tag linking back to canonical `experiments/provenance_index.json` run IDs:

   ```markdown
   <!-- run:exp02_ours_s42 -->
   ```

   HTML comments are stripped during LaTeX export and read directly by `po_tools.py review-preflight` and `po-evidence-auditor` to audit reported numbers against canonical `metrics.json` without maintaining a detached sidecar map.
7. **Missing data placeholders:** Never guess unmeasured metrics; write `[PENDING_REAL_RUN]` or `[TODO: USER DATA REQUIRED]`.
8. **Snapshots before edits:** Before applying `po-resolve` edits, copy modified section files into `manuscript/snapshots/round_<N>/` so diffs are reversible.
