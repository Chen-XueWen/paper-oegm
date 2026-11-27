# Visual & Format Audit Standard (`po-visual-format-critic`)

Use this rubric in two read-only passes: (1) figure auditing during `po-review` on `visuals/manifest.md` + figure assets/PNG previews, and (2) compiled layout auditing during `po-format` on `submission/main.pdf` (or rasterized PNG pages in `<= 4–5` page chunks) and `submission/build_report.md`.

## Pass 1 — Figure Quality Audit (`po-review`)

* **Quantitative integrity (`Blocker`):** Flag any quantitative chart using `native_image_tool` or hardcoded values inconsistent with `visuals/manifest.md` input `run_id`s.
* **Legibility & overlaps (`Major`):** Flag clipped axis labels, unreadable small fonts, overlapping legend/data points, missing axis units, or embedded captions inside the figure canvas.
* **Colorblind & print accessibility (`Minor` / `Major`):** Flag red-green-only encodings lacking distinct line styles, markers, or hatching.
* **Caption-to-visual alignment (`Major`):** Flag captions or prose references that describe trends or subfigure labels (`(a)`, `(b)`) missing from the actual rendered figure.
* **Degraded visual state:** If a figure exists only as raw `.svg`/code without a rendered raster preview on a host lacking SVG rendering, record `VISUAL_AUDIT: DEGRADED_SOURCE_ONLY` explicitly rather than claiming visual sign-off.

## Pass 2 — Compiled Layout & Venue Compliance Audit (`po-format`)

Inspect rendered pages in `<= 4–5` page chunks, prioritizing pages containing figures, tables, or `Overfull \hbox > 2pt` warnings from `submission/build_report.md`:

* **Page-limit & venue structure (`Blocker`):** Verify main-body page count before `\bibliography` complies with `paper_state.json` `venue.page_limit_main` and venue column layout.
* **Double-blind compliance (`Blocker`):** In `double-blind` mode, check title block, headers, acknowledgments, figures, URLs, and footnotes for identifying author names, affiliations, grant IDs, or non-anonymous repositories.
* **Layout defects (`Major` / `Minor`):** Flag column/margin overflows (`Overfull \hbox`), awkwardly orphaned headings, broken `[?]` / `??` citations or references, overflowing tables, and figure float placement pushing visuals far from their discussion.

## Output Contract

* Return structured findings with stable IDs `visual-r<round>-<nn>` (`Affected Scope`, `Severity`, `Discrepancy`, `Evidence`, `Suggested Action`).
* Cap total output at `<= 1,500` tokens.
