# Experimental Evaluation {#sec:experiments}

We evaluate PaperOEGM across four research questions targeting deterministic fault detection (**RQ1**), multi-harness packaging and context economics (**RQ2**), runtime scalability and paranoid compilation (**RQ3**), and live hybrid semantic review (**RQ4**). All experiments execute on CPU without external LLM API keys (Python 3.12.8, TeX Live 2026, `pandoc`, `pdfinfo`, and local Claude Code CLI 2.1.328) against an unmodified repository checkout (`git_dirty: false`). Every quantitative script writes strictly non-synthetic artifacts (`is_synthetic: false`) under `experiments/runs/` registered in `experiments/provenance_index.json`; dry-run smoke checks remain isolated in a segregated `dry_run/` tree.

## RQ1: Fault Detection and Deterministic Boundaries (PO-FaultBench) {#sec:exp-rq1}

**Setup.** We construct **PO-FaultBench**, a reproducible fault-injection benchmark comprising 120 realistic workspaces per seed across five random seeds (`s42`–`s46`, 600 main cases plus 100 adversarial evasion cases = 700 live CLI evaluations). Each seed varies citation keys, numeric scales, and workspace layouts across eight positive fault families (10 cases each, 80 positive cases/seed):

* **F1 (Hallucinated citation):** Cited key absent from `references.bib` (50%) or present in `.bib` but missing from `citation_ledger.json` (50%).
* **F2 (Unverified or missing source):** Cited entry tagged `unverified_needs_human_check` or lacking its saved file under `literature/sources/`.
* **F3 (Synthetic or dry-run leak):** Manuscript referencing the isolated `dry_run/` smoke-test path, a run marked `is_synthetic: true`, or a `user_byo` run lacking `user_attested_non_synthetic: true`.
* **F4 (Inline metric drift):** Decimal mismatch beyond $\epsilon(d)$ under an inline `run:<id>` provenance comment or an unregistered `run_id`.
* **F5 (Markdown-to-LaTeX drop):** Converted `.tex` section dropping a citation, `\label{}`, or decimal metric present in `.md`.
* **F6 (Double-blind leak):** Local path (`/Users/`, `/home/`), GitHub URL (including inside `%` comments), `\iclrfinalcopy`, or `\usepackage{cvpr}` in double-blind mode.
* **F7 (Template supply chain):** `.zip`/`.tar.gz` template archives containing Zip Slip (`../`), symlinks, or active `\write18` primitives.
* **F8 (Read-only tamper or digest drift):** Silent workspace mutation during `check-readonly` or upstream input drift during `state-sync --check-only`.

Forty hard negative controls per seed test false-positive resistance across five valid regimes: standard metric rounding and $0\text{--}1 \to \%$ conversion, valid `user_provided` Zotero bibliographies paired with attested `user_byo` runs, valid LaTeX dimensions (`0.92\linewidth`, `10.5pt`) with commented `% \write18` lines, legitimate camera-ready URLs and flags under `submission_mode: camera-ready`, and clean read-only/drift snapshots. To probe deterministic blind spots honestly, an additional **20-case Adversarial Evasion suite** per seed injects four non-syntactic attacks: integer-only count falsification (**E1**), macro-obfuscated TeX shell escapes such as `\csname write18\endcsname` (**E2**), valid-key semantic citation distortion (**E3**), and prose institution deanonymization without paths or URLs (**E4**). We compare **PaperOEGM Full** (`po_tools.py`), **B1 (No Inline Provenance)** disabling inline decimal matching, and **B0 (Compiler-Only)** reflecting standard `pdflatex`/`bibtex` compile checks.

<!-- run:exp01_faultbench_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{PO-FaultBench detection performance across $n=5$ seeds (80 positive faults, 40 hard negative controls, and 20 adversarial evasion cases per seed). All percentages are mean $\pm$ SD.}
\label{tab:faultbench}
\begin{tabular}{lcccccc}
\toprule
\textbf{System / Condition} & \textbf{Recall (\%)} & \textbf{Precision (\%)} & \textbf{F1 (\%)} & \textbf{FPR (\%)} & \textbf{Evasion Recall (\%)} & \textbf{Latency (ms)} \\
\midrule
B0: Compiler-Only & 6.25 $\pm$ 0.00 & 100.00 $\pm$ 0.00 & 11.76 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & --- \\
B1: No Inline Provenance & 87.50 $\pm$ 0.00 & 100.00 $\pm$ 0.00 & 93.33 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & --- \\
\textbf{PaperOEGM Full (\texttt{po\_tools.py})} & \textbf{100.00 $\pm$ 0.00} & \textbf{100.00 $\pm$ 0.00} & \textbf{100.00 $\pm$ 0.00} & \textbf{0.00 $\pm$ 0.00} & \textbf{0.00 $\pm$ 0.00} & \textbf{115.72 $\pm$ 6.03} \\
\bottomrule
\end{tabular}
\end{table*}
```

<!-- run:exp01_faultbench_agg -->
**Results.** Table~\ref{tab:faultbench} and Figure~\ref{fig:faultbench} summarize RQ1 outcomes. Across all five seeds, PaperOEGM Full achieves 100.0% recall, 100.0% precision, 100.0% F1, and 0.0% FPR across all 40 hard negative controls in 115.72 $\pm$ 6.03 ms per workspace (real subprocess CLI timing). Compiler-Only (B0) reaches only 6.25% overall recall (catching the 50.0% subset of F1 where keys are missing from `.bib` while missing ledger-only gaps, unverified snapshots, synthetic runs, metric drift, anonymity leaks, and supply-chain payloads). Removing inline `run:<id>` provenance verification (B1) drops overall recall to 87.5% (93.33% F1) by missing 100.0% of F4 metric drift faults.

Crucially, as highlighted below the dashed boundary in Figure~\ref{fig:faultbench}, deterministic verification records **0.0% recall** across all four adversarial evasion families (E1–E4). Because we co-authored both `po_tools.py` and PO-FaultBench, main-suite recall verifies specification compliance rather than security completeness; the 0.0% evasion result empirically proves why deterministic checks must be paired with native TeX sandboxing (stopping E2 macro escapes at the OS/TeX engine boundary) and fresh-context semantic critics (catching E1, E3, and E4 in RQ4).

![Per-family detection recall (%) on PO-FaultBench (8 fault families, 120 cases/seed, n=5) and the 20-case adversarial evasion suite comparing PaperOEGM Full (`po_tools.py`), Ablated No-Inline-Provenance (B1), and Compiler-Only (B0).](../visuals/assets/fig_faultbench_recall.pdf){#fig:faultbench width=0.98\textwidth}

## RQ2: Multi-Harness Packaging, Context Footprint, and Determinism {#sec:exp-rq2}

**Setup.** We audit live repository artifacts across five independent runs (`exp02_packaging_s42`–`s46`), comparing PaperOEGM against two baselines: **B2 (Monolithic Single-Skill)** concatenating all 10 skills, shared execution rules, 6 protocols, and 5 review standards into a single skill file, and **B3 (Reference Multi-Harness Plugin — EGM)** measured directly on the locally installed Google Elephant-Goldfish Model plugin [@google2026egm]. Because EGM targets engineering specifications rather than research execution or LaTeX builds, B3 is strictly scoped to RQ2 packaging footprint. We evaluate whole-file `SKILL.md` bytes, active-stage prompt load, startup YAML frontmatter index size, a specification-compliance defect checklist adapted from @zhang2026reusable, live `claude plugin validate` execution, and deterministic ZIP SHA-256 parity across `antigravity`, `claude`, and `openai` builds via `scripts/pack_plugin.py`.

<!-- run:exp02_packaging_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{Multi-harness skill packaging footprint, context reduction, compliance defects, and deterministic build parity ($n=5$ builds). EGM (B3) is scoped strictly to RQ2 packaging footprint.}
\label{tab:packaging}
\begin{tabular}{lccccccc}
\toprule
\textbf{Packaging Strategy} & \textbf{Skills} & \textbf{Median / Max Skill (B)} & \textbf{Active Stage (B)} & \textbf{vs. Mono (\%)} & \textbf{Max Agent (B)} & \textbf{Defects} & \textbf{ZIP SHA-256} \\
\midrule
B2: Monolithic Single-Skill & 1 & 79,454 / 79,454 & 79,454 & 0.00\% & --- & --- & --- \\
B3: Local EGM Reference & 7 & 15,205 / 24,257 & --- & --- & 7,355 & --- & --- \\
\textbf{PaperOEGM (10 Skills)} & \textbf{10} & \textbf{3,900 / 4,526} & \textbf{14,171} & \textbf{-82.16\%} & \textbf{2,376} & \textbf{0} & \textbf{100.0\%} \\
\bottomrule
\end{tabular}
\end{table*}
```

<!-- run:exp02_packaging_agg -->
**Results.** As shown in Table~\ref{tab:packaging} and Figure~\ref{fig:footprint}, every PaperOEGM `SKILL.md` file fits between 3,466 and 4,526 bytes (median 3,900 bytes, maximum 63 lines)—preserving 62.28% headroom below our 12 KB target and 81.14% headroom below Antigravity's 24 KB skill ceiling. Notably, live measurement of local EGM (B3) reveals a median skill size of 15,205 bytes and a maximum skill size of 24,257 bytes, exceeding Antigravity's 24 KB limit by 257 bytes; PaperOEGM's largest critic persona (2,376 bytes) is also smaller than EGM's largest persona (7,355 bytes). Offloading stage protocols reduces median active-stage prompt context from 79,454 bytes (B2) to 14,171 bytes (82.16% reduction; 15,749 bytes worst-case stage) and shrinks startup frontmatter routing context to 2,270 bytes (97.14% reduction). PaperOEGM passes the specification-compliance audit with 0 defects, passes live `claude plugin validate` with 0 errors or warnings, and builds byte-identical ZIP distributions (`124.88` KB Antigravity, `142.37` KB Claude, `125.75` KB OpenAI) with 100.0% SHA-256 reproducibility in 143.00 $\pm$ 10.09 ms across all five runs.

![Skill packaging footprint and context economics: (a) whole-file `SKILL.md` size across all 10 PaperOEGM skills relative to the 12 KB budget, local EGM median/max, and Antigravity's 24 KB limit; (b) loaded prompt context across Monolithic (B2), active stage max/median, and startup frontmatter index.](../visuals/assets/fig_skill_footprint.pdf){#fig:footprint width=0.98\textwidth}

## RQ3: Scalability, Context Offloading, and Paranoid Venue Builds {#sec:exp-rq3}

**Setup.** We benchmark real subprocess invocations of all four `po_tools.py` subcommands (`state-sync --check-only`, `review-preflight`, `format-verify`, `check-readonly --verify`) across four realistic workspace scales repeated over $n=5$ seeds (`exp03_scalability_s42`–`s46`): **S** (20 citations, 5 runs), **M** (50 citations, 10 runs), **L** (80 citations, 20 runs), and **XL** (120 citations, 30 runs), with primary-source JSON snapshots modeled on live arXiv API records. In each seed, we also compile full minimal manuscripts for three double-blind venues—**ACM SIGPLAN** (`acmart[sigplan,review,anonymous]`), **CVPR 2025** (`cvpr[review]`), and **ICLR 2025** (double-blind)—inside our paranoid TeX sandbox (`openin_any=p openout_any=p pdflatex --no-shell-escape`, `bibtex`, two rebuilds), auditing every PDF with `pdfinfo` and `po_tools.py format-verify`.

<!-- run:exp03_scalability_agg -->
**Results.** Figure~\ref{fig:scalability}(a) shows total 4-command verification time rising gently from 260.37 $\pm$ 8.73 ms at scale S (263.89 $\pm$ 6.85 ms at M, 268.75 $\pm$ 2.28 ms at L) to 272.48 $\pm$ 3.99 ms at scale XL (`state-sync`: 134.18 $\pm$ 1.83 ms, `check-readonly`: 55.68 $\pm$ 1.08 ms, `review-preflight`: 41.68 $\pm$ 0.98 ms, `format-verify`: 40.94 $\pm$ 2.61 ms). In Figure~\ref{fig:scalability}(b), offloading raw primary-source JSON records to `literature/sources/` cuts `citation_ledger.json` footprint by 87.82% at S to 87.96% at XL (24,169 bytes loaded vs. 176,550 bytes offloaded). Paranoid LaTeX compilation succeeds on 3/3 venues across all five seeds (`acmart[sigplan]`: 1844.44 $\pm$ 16.46 ms; `cvpr2025`: 1388.22 $\pm$ 17.73 ms; `iclr2025`: 1079.45 $\pm$ 13.33 ms) with 0 identity leaks.

Two honest empirical nuances emerged from RQ3. First, our 4-subprocess XL latency (272.48 ms) slightly exceeded our pre-experiment 250 ms target (while remaining over 7$\times$ below the 2,000 ms falsification criterion) because four separate Python process startups—especially toolchain binary probing in `state-sync`—dominate fixed overhead; actual marginal scaling across a 6$\times$ increase in citations and runs is only +12.11 ms (~0.12 ms per extra citation). Second, `pdfinfo` revealed that while `cvpr2025` and `iclr2025` leave `/Author`, `/Creator`, and `/Producer` completely blank under our metadata-stripping preamble, `acmart` v2.16 injects a generic non-identifying `Creator: LaTeX with acmart ...` string via `hyperxmp` while leaving `/Author` and `/Producer` blank (`pdfinfo_generic_creator_tags = 1`, `pdfinfo_leaks = 0`), underscoring the need for venue-aware PDF metadata audits.

![Verification scalability across 4 workspace scales (S: 20 citations / 5 runs to XL: 120 citations / 30 runs, n=5): (a) wall-clock CLI latency (`mean ± std`) across all 4 `po_tools.py` subcommands; (b) compact `citation_ledger.json` vs. offloaded `literature/sources/` snapshot footprint.](../visuals/assets/fig_scalability.pdf){#fig:scalability width=0.98\textwidth}

## RQ4: Live Hybrid Fresh-Context Critic Audit {#sec:exp-rq4}

**Setup.** To test whether flat parallel fresh-context read-only critics recover semantic flaws invisible to `po_tools.py`, we generate $n=3$ distinct realistic mini-paper workspaces spanning three domains (`exp04_hybrid_s42` ML Systems, `exp04_hybrid_s43` Vision Benchmarks, `exp04_hybrid_s44` Agent Security). Each workspace contains **10 ground-truth defects**—5 mechanical (**M1** missing citation, **M2** unverified citation, **M3** decimal metric drift, **M4** synthetic/`dry_run` leak, **M5** double-blind path/URL leak) and 5 semantic/evasion (**S1** claim-vs-abstract citation distortion on a `verified_source` entry, **S2** integer-only count falsification bypassing decimal regexes, **S3** missing core ablation + universal overclaim + prose lab deanonymization, **S4** undefined mathematical symbol and unexplained method acronym, **S5** real matplotlib PNG chart rendered with colliding horizontal tick labels, 4.5pt annotations, missing units, and red-green-only bars)—alongside verified clean controls (accurate citation, accurate secondary decimal, defined scalar $\alpha_{\text{base}} = 0.5$). Ground truth is stored outside the fixture directories so critics never observe answer keys. We run `po_tools.py` (`check-readonly --create`, `review-preflight`, `format-verify`) as **B4 (Deterministic-Only)**, dispatch all five live read-only `po-*` critic subagents flat in parallel on Antigravity (15 total subagent invocations), verify `check-readonly --verify`, and score verbatim outputs against ground truth.

<!-- run:exp04_hybrid_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{Live hybrid audit across $n=3$ seeded domain manuscripts (30 planted defects: 15 mechanical M1--M5, 15 semantic S1--S5; 15 live Antigravity read-only critic runs).}
\label{tab:hybrid}
\begin{tabular}{lcccccc}
\toprule
\textbf{Review Configuration} & \textbf{Mech. Recall (\%)} & \textbf{Sem. Recall (\%)} & \textbf{Total Recall (\%)} & \textbf{Clean FP} & \textbf{Mutations} & \textbf{Max Critic Tok.} \\
\midrule
B4: Deterministic-Only (\texttt{po\_tools.py}) & 100.0 $\pm$ 0.0 & 0.0 $\pm$ 0.0 & 50.0 $\pm$ 0.0 & 0.0 $\pm$ 0.0 & 0.0 & 0 \\
Fresh Read-Only Critics Alone (5 agents) & 100.0 $\pm$ 0.0 & 100.0 $\pm$ 0.0 & 100.0 $\pm$ 0.0 & 0.0 $\pm$ 0.0 & 0.0 & 1411.0 $\pm$ 35.68 \\
\textbf{PaperOEGM Hybrid (Full)} & \textbf{100.0 $\pm$ 0.0} & \textbf{100.0 $\pm$ 0.0} & \textbf{100.0 $\pm$ 0.0} & \textbf{0.0 $\pm$ 0.0} & \textbf{0.0} & \textbf{1411.0 $\pm$ 35.68} \\
\bottomrule
\end{tabular}
\end{table*}
```

<!-- run:exp04_hybrid_agg -->
**Results.** Table~\ref{tab:hybrid} demonstrates clear complementarity. Deterministic-Only (B4) detects 100.0% of mechanical defects (M1–M5) in under 100 ms at zero token cost, but misses 100.0% of semantic flaws (0.0% semantic recall, 50.0% total). Live flat-parallel read-only critics recover 100.0% of planted semantic flaws across all three domains (S1–S5, including multimodal raster inspection of `fig_results.png` by `po-visual-format-critic` and integer count reconciliation by `po-evidence-auditor`), lifting hybrid recall to 100.0% with 0.0 clean-control false positives and 0.0 workspace mutations verified by `check-readonly`. All 15 subagents completed within the 1,500-token ceiling (mean peak 1411.0 $\pm$ 35.68 tokens; per-role means: `po-clarity-reader` 1400.33 $\pm$ 48.81, `po-peer-reviewer` 1363.0 $\pm$ 44.19, `po-visual-format-critic` 1108.33 $\pm$ 64.78, `po-citation-auditor` 923.33 $\pm$ 31.79, `po-evidence-auditor` 830.67 $\pm$ 31.34).

Two qualitative observations sharpen interpretation of Table~\ref{tab:hybrid}. First, although fresh critics also caught 100.0% of mechanical defects (M1–M5) on these compact seeded drafts, deterministic `po_tools.py` remains essential on full-length manuscripts (where LLM attention over 120 citations and 30 runs is stochastic and costly) and on binary/archive operations (Zip Slip extraction scans, `.md`-to-`.tex` exact parity, and `check-readonly` hashing) that read-only critics without shell tools cannot perform. Second, `po-citation-auditor` surfaced an unplanted real defect in `s43` and `s44`—correctly noting that our generic introductory template sentence ("demonstrate strong baseline efficiency") was unsupported by `greshake2023indirect`'s abstract on indirect prompt injection—confirming genuine semantic grounding rather than pattern matching.
