# Visual Standards & Figure Provenance Protocol

This protocol governs `po-visuals` (Stage 5) and figure auditing by `po-visual-format-critic`.

## Quantitative vs. Conceptual Rule

1. **Newly generated quantitative plots:** Must be produced by a checked-in script under `visuals/scripts/fig_<id>.py` that loads data directly from canonical `experiments/runs/<run_id>/{metrics.json, series.csv}` or registered BYO data files. Zero hardcoded result arrays in plotting code; generative raster image tools are strictly prohibited on numerical data.
2. **Pre-existing user plots (BYO):** Existing static user figures may be registered in `visuals/manifest.md` with `Generator = byo_static_asset` and explicit source-data attestation (restricting the script requirement to newly generated plots).
3. **Conceptual diagrams & illustrations:** Default across all harnesses to version-controlled vector code (`visuals/scripts/fig_<id>.{tex,mmd,dot}` or direct SVG code). Where the active host exposes a native image generation tool, the coding agent may optionally use it for non-quantitative illustrations (e.g., teaser artwork or custom icons), flagging `Non-Quantitative = true` and `Generator = native_image_tool`.

## Export, Double-Blind Metadata & LaTeX Readiness

* Export LaTeX-ready `.pdf` or `.png` assets under `visuals/assets/fig_<id>.{pdf,png}` alongside any `.svg` sources so `po-format` never requires `\includesvg` or banned `--shell-escape`.
* Export a high-DPI PNG preview (`>= 200 DPI`) whenever a rasterizer is available so multimodal inspection works reliably across harnesses.
* When `submission_mode == "double-blind"`, strip PDF/PNG metadata (e.g., matplotlib `metadata={"Creator": "", "Author": "", "Producer": ""}` and `pdfinfo` checks) to prevent username or path leaks.

## Publication Legibility & Critique Checklist

Apply this checklist during self-inspection in `po-visuals` and independent critique in `po-visual-format-critic`:

* **Data fidelity:** Every plotted curve, bar, error bar, and annotation matches the referenced canonical `metrics.json` / `series.csv` values.
* **Caption exclusion:** Do not bake figure captions (`Figure 1: ...`) inside the image canvas—captions belong in LaTeX `\caption{...}`.
* **Colorblind-safe & dual encoding:** Never rely solely on red-vs-green color contrast. Pair colorblind-safe palettes (e.g., Okabe-Ito or blue `#1b6ef3` vs. orange `#e86e00`) with a second discriminative cue (line styles, markers, or hatch patterns).
* **Layout & overlap:** Zero overlapping tick labels, clipped axis titles, legend collisions with data points, or cramped subplots.
* **Print legibility:** Match figure label font sizes to body text (at least 8–9pt at final column width) with legible line widths (`>= 1.5pt`) and clear axis units.

## `visuals/manifest.md` Schema

Maintain a canonical Markdown table in `visuals/manifest.md`:

```markdown
| Figure ID | Role | Script / Source | Asset Paths (LaTeX / Preview) | Input Run IDs | Generator | Non-Quantitative | VISUAL_AUDIT | Caption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fig_main_acc | Main accuracy comparison | visuals/scripts/fig_main_acc.py | visuals/assets/fig_main_acc.pdf, visuals/assets/fig_main_acc.png | exp01_baseline_s42, exp02_ours_s42 | python_matplotlib | false | COMPLETED | Main accuracy across seeds. |
```

* **Allowed `Generator` values:** `python_matplotlib`, `python_other`, `tikz`, `svg_code`, `mermaid`, `graphviz`, `native_image_tool`, `byo_static_asset`.
* **Allowed `VISUAL_AUDIT` values:** `COMPLETED` (visually inspected rendered PNG/PDF), `DEGRADED_SOURCE_ONLY` (code/SVG inspected without raster visual check), `NOT_RUN`.
