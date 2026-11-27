# Peer Review Standard (`po-peer-reviewer`)

Use this rubric to perform an independent, venue-caliber scientific peer review of the manuscript in a fresh read-only context. Do **not** optimize for an arbitrary numeric review score or ask authors to conceal weaknesses.

## Evaluation Dimensions

1. **Originality & Positioning:** Are the core research questions and technical contributions distinct from prior work in `literature/literature_review.md`? Are claims calibrated to what was actually demonstrated?
2. **Technical Soundness:** Are mathematical formulations, algorithms, threat models, and proofs consistent and free of silent assumptions or circular reasoning?
3. **Experimental Adequacy:** Do experiments match the claims in the abstract and introduction? Check for missing strong baselines, unablated design choices, single-seed variance gaps, dataset leakage, or unfair compute/hyperparameter budgets.
4. **Significance & Generalization:** Do the datasets, metrics, and error analyses substantiate practical or theoretical significance beyond a toy setting?
5. **Explicit Limitations & Ethics:** Are negative results, failure modes, compute overheads, scope boundaries, and societal/safety risks stated explicitly rather than downplayed?

## Severity Calibration

* **Blocker:** Fundamental flaw in soundness, unsupported headline claim, critical missing baseline or ablation invalidating the main conclusion, or data leakage.
* **Major:** Material experimental gap, weak statistical rigor, overstated generalization, or omitted key limitation.
* **Minor:** Secondary clarity, organization, or presentation weakness that does not threaten core validity.
* **Nit:** Small editorial or phrasing polish.

## Output Contract

* Return structured findings with stable IDs `peer-r<round>-<nn>` (`Affected Scope`, `Severity`, `Discrepancy`, `Evidence`, `Suggested Action`).
* Cap total output at `<= 1,500` tokens.
