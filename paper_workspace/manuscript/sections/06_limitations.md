# Limitations and Threats to Validity {#sec:limitations}

We highlight six candid limitations and threats to validity.

<!-- run:exp01_faultbench_agg -->
**Self-Benchmark Circularity and Deterministic Scope (RQ1).** Because `po_tools.py` and PO-FaultBench were co-authored, 100.0% recall and 0.0% FPR on FF1--FF8 verify adherence to PaperOEGM's schema rather than universal error detection, and four families target PaperOEGM-specific files. Unordered set matching in Equation~\eqref{eq:decimal-match} also cannot detect metric-key swaps, unit-ambiguous $[0, 1]$ scaling, or untagged paragraphs. Our 20-case evasion suite (0.0% recall) makes these boundaries explicit; external evaluation on PaperBench [@starace2025paperbench] or historical errata remains future work.

<!-- run:exp03_scalability_agg -->
**TeX Read-Sandbox Regression and Prompt Injection (RQ3).** Static regexes miss macro-obfuscated TeX escapes (0.0% recall on E2). While RQ3 confirmed `--no-shell-escape` and `openout_any=p` block `\csname write18\endcsname` (1.0) and parent `\openout` writes (1.0), upstream TeX Live 2026 made `openin_any=p` a silent no-op (0.0 blocked on parent `\openin` reads), requiring OS-level containers or `sandbox-exec` for read isolation. Furthermore, although @schmotz2026skillinject report up to 80% ASR for skill-file prompt injections, we did not empirically test adaptive indirect prompt injection inside scraped abstracts or PDFs against our read-only critics; read-only isolation bounds write blast radius but does not prevent finding suppression.

<!-- run:exp04_hybrid_agg -->
**RQ4 Scope and Missing Baselines.** Under zero external API keys, RQ4 evaluates $n=3$ compact (~150--180 word) seeded drafts on one host/model (Antigravity / Gemini 4) without a same-context self-review or single-agent critic ablation. Achieving 100.0% recall reflects dense planted flaws on short drafts; subtler defects on 9-page papers with 80+ citations will incur lower recall, consistent with the findings of @liang2024feedback, and `clean_control_fp` inspects targeted tokens rather than a defect-free manuscript.

**Asymmetric Cross-Harness Verification.** Antigravity (all 10 skills and 5 live critics) and Claude Code CLI packaging (`claude plugin validate` and install) were live-verified; Codex support is structurally verified via manifests and deterministic ZIP builds, not yet live-executed.

<!-- run:exp03_scalability_agg -->
**Dogfooding Friction Points.** Self-hosting exposed four minor trade-offs: four separate `po_tools.py` process launches incur ~266 ms startup overhead (`266.00`--`268.55 ms`); `acmart` v2.16 writes a generic non-identifying `Creator` via `hyperxmp`; literal path/marker mentions in meta-papers describing PaperOEGM can trip substring guards; and `check-readonly` tracks macOS `.DS_Store` metadata unless excluded.

**Human Accountability.** PaperOEGM is strictly a human-in-the-loop aid (`disable-model-invocation: true`), not an autonomous paper mill; researchers remain responsible for scientific validity, Institutional Review Board (IRB) compliance, real experiments, and final verification.
