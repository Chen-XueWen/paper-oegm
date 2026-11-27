# Third-Party Notices

The starter conference LaTeX style, bibliography, and math-macro files bundled under `resources/templates/` are preserved **byte-for-byte unmodified** from their respective upstream distributions. PaperOEGM modifies only its own starter `template.tex` and `guidelines.md` wrappers.

## CVPR 2025 Starter Files (`resources/templates/cvpr2025/`)

* **`cvpr.sty` & `preamble.tex`**
  * Source: CVPR Official Author Kit (`https://github.com/cvpr-org/author-kit`).
  * Retained byte-for-byte unmodified for CVPR double-blind (`[review]`), preprint (`[pagenumbers]`), and camera-ready compilation.
* **`ieeenat_fullname.bst`**
  * Copyright 1993–2007 Patrick W. Daly (`abbrvnat.bst` / `natbst.mbs` derivative).
  * License: **LaTeX Project Public License (LPPL)**, version 1 or any later version (CTAN `macros/latex/base/lppl.txt`).
  * Retained byte-for-byte unmodified.

## ICLR 2025 Starter Files (`resources/templates/iclr2025/`)

* **`iclr2025_conference.sty`**
  * Source: ICLR 2025 Official LaTeX Style File (adapted by Hugo Larochelle from the NIPS stylefile macros).
  * Retained byte-for-byte unmodified.
* **`iclr2025_conference.bst`**
  * Copyright 2010 Hal Daumé III (modified by J. Fürnkranz), derived from `plainnl.bst` / `icml2010.mbs`, Copyright 1993–2007 Patrick W. Daly.
  * License: **LaTeX Project Public License (LPPL)**, version 1 or any later version (CTAN `macros/latex/base/lppl.txt`).
  * Retained byte-for-byte unmodified.
* **`math_commands.tex`**
  * Source: Deep Learning Book Notation (`https://github.com/goodfeli/dlbook_notation`), Ian Goodfellow et al.
  * License: **MIT License**.
  * Retained byte-for-byte unmodified.

*Note:* Standard TeX Live packages `natbib.sty` and `fancyhdr.sty` are **not** redistributed by PaperOEGM; TeX installations provide their own maintained copies.
