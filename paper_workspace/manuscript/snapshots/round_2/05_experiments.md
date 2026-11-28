# Experimental Evaluation {#sec:experiments}

We evaluate PaperOEGM across four research questions targeting deterministic fault detection (**RQ1**), multi-harness packaging and context economics (**RQ2**), verification scalability and paranoid TeX containment (**RQ3**), and live hybrid semantic critique (**RQ4**). Benchmarks RQ1--RQ3 execute locally on CPU without external LLM API keys (Python 3.12.8, TeX Live 2026, `pandoc`, `pdfinfo`, and Claude Code CLI 2.1.328); RQ4 runs the deterministic baseline locally on CPU and dispatches 15 live read-only critic subagents on the Antigravity host runtime (Gemini 4). All runs execute against an unmodified plugin codebase (`git diff` outside `paper_workspace/` is empty; workspace artifact updates during review resolution carry recorded `git_dirty` attestations) and write strictly non-synthetic outputs (`is_synthetic: false`) registered in `experiments/provenance_index.json`, keeping smoke checks isolated in the segregated `dry_run/` tree.

## RQ1: Fault Detection and Deterministic Boundaries (PO-FaultBench) {#sec:exp-rq1}

**Setup.** We construct **PO-FaultBench**, an author-constructed fault-injection benchmark comprising 120 realistic workspaces per seed across five random seeds (`42`--`46`, yielding 600 main cases plus 100 adversarial evasion cases = 700 live CLI evaluations of `po_tools.py`). Each seed varies citation keys, numeric scales, and layouts across eight positive fault families (10 cases each, 80 positive cases/seed), spanning both *schema-independent* authoring faults (**FF1a**, **FF5**, **FF6**, **FF7**) and *PaperOEGM-schema* provenance checks (**FF1b**, **FF2**, **FF3**, **FF4**, **FF8**):

* **FF1 (Hallucinated citation):** Cited key absent from `references.bib` (**FF1a**, 50%) or present in `.bib` but missing from `citation_ledger.json` (**FF1b**, 50%).
* **FF2 (Unverified or missing source):** Cited entry tagged `unverified_needs_human_check` or lacking its saved snapshot under `literature/sources/`.
* **FF3 (Synthetic or dry-run leak):** Manuscript referencing the isolated `dry_run/` smoke-test path, a run marked `is_synthetic: true`, or a `user_byo` run lacking `user_attested_non_synthetic: true`.
* **FF4 (Inline metric drift):** Decimal mismatch beyond $\epsilon(d)$ under an inline `run:<id>` provenance comment or an unregistered `run_id`.
* **FF5 (Markdown-to-LaTeX drop):** Converted `.tex` section dropping a citation, `\label{}`, or decimal metric present in `.md`.
* **FF6 (Double-blind leak):** Local path (`/Users/`, `/home/`), GitHub URL (including inside `%` comments), `\iclrfinalcopy`, or `\usepackage{cvpr}` in double-blind mode.
* **FF7 (Template supply chain):** `.zip`/`.tar.gz` template archives containing Zip Slip (`../`), symlinks, or active `\write18` primitives.
* **FF8 (Read-only tamper or digest drift):** Silent workspace mutation during `check-readonly` or upstream input drift during `state-sync --check-only`.

Forty hard negative controls per seed test false-positive resistance across five valid regimes: standard rounding and $0\text{--}1 \to \%$ conversion, valid `user_provided` Zotero bibliographies paired with attested `user_byo` runs, valid LaTeX dimensions (`0.92\linewidth`, `10.5pt`) with commented `% \write18` lines, legitimate camera-ready URLs and flags under `submission_mode: camera-ready`, and clean read-only/drift snapshots. An additional **20-case Adversarial Evasion suite** per seed injects four non-syntactic attacks: integer-only count falsification (**E1**), macro-obfuscated TeX shell escapes such as `\csname write18\endcsname` (**E2**), valid-key semantic citation distortion (**E3**), and prose institution deanonymization without paths or URLs (**E4**). We compare **PaperOEGM Full** (live subprocess `po_tools.py`), **B1 (No Inline Provenance)** scored by filtering inline decimal-drift blockers from `po_tools.py` output (latency omitted as `---`), and **B0 (Compiler-Only)** scored analytically for standard `pdflatex`/`bibtex` compile errors (missing `.bib` keys and missing `\input` `.tex` files; latency omitted as `---`).

<!-- run:exp01_faultbench_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{PO-FaultBench detection performance across $n=5$ seeds (80 positive faults, 40 hard negative controls, and 20 adversarial evasion cases per seed). Percentages and latency are mean $\pm$ SD; B0/B1 latencies are omitted (---) as analytical/filtered baselines.}
\label{tab:faultbench}
\begin{tabular}{lcccccc}
\toprule
\textbf{System / Condition} & \textbf{Recall (\%)} & \textbf{Precision (\%)} & \textbf{F1-Score (\%)} & \textbf{FPR (\%)} & \textbf{Evasion Recall (\%)} & \textbf{Latency (ms)} \\
\midrule
B0: Compiler-Only & 6.25 $\pm$ 0.00 & 100.00 $\pm$ 0.00 & 11.76 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & --- \\
B1: No Inline Provenance & 87.50 $\pm$ 0.00 & 100.00 $\pm$ 0.00 & 93.33 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & 0.00 $\pm$ 0.00 & --- \\
\textbf{PaperOEGM Full (\texttt{po\_tools.py})} & \textbf{100.00 $\pm$ 0.00} & \textbf{100.00 $\pm$ 0.00} & \textbf{100.00 $\pm$ 0.00} & \textbf{0.00 $\pm$ 0.00} & \textbf{0.00 $\pm$ 0.00} & \textbf{108.20 $\pm$ 2.07} \\
\bottomrule
\end{tabular}
\end{table*}
```

<!-- run:exp01_faultbench_agg -->
**Results.** Table~\ref{tab:faultbench} and Figure~\ref{fig:faultbench} summarize RQ1 outcomes. Across all five seeds, PaperOEGM Full achieves 100.0% recall, 100.0% precision, 100.0% F1-score, and 0.0% FPR across all 40 hard negative controls in 108.20 $\pm$ 2.07 ms per workspace. Compiler-Only (B0) reaches 6.25% overall recall, catching the 50.0% FF1a subset where keys are absent from `.bib` while missing ledger-only gaps (FF1b), unverified snapshots, synthetic runs, metric drift, conversion drops (FF5), anonymity leaks (FF6), and archive supply-chain payloads (FF7). Disabling inline `run:<id>` verification (B1) lowers recall to 87.5% (93.33% F1-score) by missing 100.0% of FF4 metric drift faults.

<!-- run:exp01_faultbench_agg -->
Crucially, as highlighted below the dashed divider in Figure~\ref{fig:faultbench}, all three deterministic systems record **0.0% recall** across all four adversarial evasion families (E1--E4). Because we co-authored both `po_tools.py` and PO-FaultBench, main-suite recall verifies specification compliance rather than security completeness; the 0.0% evasion boundary empirically motivates pairing `po_tools.py` with native TeX containment (RQ3) and fresh-context semantic critics (RQ4).

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=0.98\textwidth]{../visuals/assets/fig_faultbench_recall.pdf}
\caption{Per-family detection recall (\%) on PO-FaultBench (8 fault families FF1--FF8, 80 positive faults + 40 hard negative controls/seed, $n=5$, SD $= 0.0\%$) and the 20-case/seed adversarial evasion suite comparing PaperOEGM Full (\texttt{po\_tools.py}), Ablated No-Inline-Provenance (B1), and Compiler-Only (B0).}
\label{fig:faultbench}
\end{figure*}
```

## RQ2: Multi-Harness Packaging, Context Footprint, and Determinism {#sec:exp-rq2}

**Setup.** We audit repository packaging across five independent build runs (`42`--`46`), comparing PaperOEGM against two baselines: **B2 (Monolithic Single-Skill)** concatenating all 10 `SKILL.md` files, `execution_instructions.md`, 6 protocols, and 5 review standards into a single skill file, and **B3 (Public EGM Reference)** measured on the open-source Elephant-Goldfish Model v0.1.1 plugin (`google/elephant-goldfish-model` [@google2026egm]). Because EGM v0.1.1 targets software design documents rather than PaperOEGM's stage-protocol split or scientific packager, B3 is scoped strictly to whole-file skill and agent size comparisons (Table~\ref{tab:packaging} marks non-applicable B2/B3 cells as `---`). We measure whole-file `SKILL.md` bytes (reporting decimal KB = 1,000 bytes for loader ceilings and binary KiB = 1,024 bytes for ZIP archives), active-stage prompt load, startup YAML frontmatter index size, a specification-compliance defect checklist adapted from @zhang2026reusable, live `claude plugin validate`, and deterministic ZIP SHA-256 parity across `antigravity`, `claude`, and `openai` builds via `scripts/pack_plugin.py`.

<!-- run:exp02_packaging_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{Multi-harness skill packaging footprint, context reduction, compliance defects, and deterministic build parity ($n=5$ builds). Non-applicable baseline columns are marked ---; public EGM (B3) is scoped strictly to skill/agent footprint.}
\label{tab:packaging}
\begin{tabular}{lccccccc}
\toprule
\textbf{Packaging Strategy} & \textbf{Skills} & \textbf{Median / Max Skill (B)} & \textbf{Active Stage (B)} & \textbf{vs. Mono (\%)} & \textbf{Max Agent (B)} & \textbf{Defects} & \textbf{ZIP SHA-256} \\
\midrule
B2: Monolithic Single-Skill & 1 & 79,454 / 79,454 & 79,454 & 0.00\% & --- & --- & --- \\
B3: Public EGM Reference & 7 & 15,205 / 24,257 & --- & --- & 7,355 & --- & --- \\
\textbf{PaperOEGM (10 Skills)} & \textbf{10} & \textbf{3,900 / 4,526} & \textbf{14,171} & \textbf{-82.16\%} & \textbf{2,376} & \textbf{0} & \textbf{100.0\%} \\
\bottomrule
\end{tabular}
\end{table*}
```

<!-- run:exp02_packaging_agg -->
**Results.** Table~\ref{tab:packaging} and Figure~\ref{fig:footprint} show that every PaperOEGM `SKILL.md` file spans 3,466 to 4,526 bytes (median 3,900 bytes, maximum 63 lines)—preserving 62.28% headroom below our 12 KB (12,000-byte) budget and 81.14% headroom below Antigravity's 24 KB (24,000-byte) skill ceiling. By comparison, the public EGM reference plugin (B3) has a median skill size of 15,205 bytes and a maximum skill size of 24,257 bytes (+257 bytes above Antigravity's 24,000-byte ceiling), alongside a larger maximum critic persona (7,355 vs. 2,376 bytes). Offloading shared protocols reduces median active-stage prompt load from 79,454 bytes (B2) to 14,171 bytes (82.16% reduction; 15,749 bytes worst-case stage) and compresses startup frontmatter routing context to 2,270 bytes (97.14% reduction). PaperOEGM records 0 packaging compliance defects, passes live `claude plugin validate` with 0 errors or warnings, and builds byte-identical ZIP distributions (124.88 KiB Antigravity, 142.37 KiB Claude, 125.75 KiB OpenAI) with 100.0% SHA-256 reproducibility in 143.00 $\pm$ 10.09 ms across all five runs.

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=0.98\textwidth]{../visuals/assets/fig_skill_footprint.pdf}
\caption{Skill packaging footprint and context economics: (a) whole-file \texttt{SKILL.md} size (decimal KB, 1,000 B) across all 10 PaperOEGM skills relative to the 12 KB budget, public EGM v0.1.1 median/max (+257 B over ceiling), and Antigravity's 24 KB ceiling; (b) loaded prompt context across Monolithic (B2), active stage max/median, and startup frontmatter index.}
\label{fig:footprint}
\end{figure*}
```

## RQ3: Scalability, Context Offloading, and Paranoid TeX Containment {#sec:exp-rq3}

**Setup.** We benchmark live subprocess invocations of all four `po_tools.py` subcommands (`state-sync --check-only`, `review-preflight`, `format-verify`, `check-readonly --verify`) across four realistic workspace scales over $n=5$ seeds (`42`--`46`): **S** (20 citations, 5 runs), **M** (50 citations, 10 runs), **L** (80 citations, 20 runs), and **XL** (120 citations, 30 runs), with primary-source JSON snapshots modeled on live arXiv API records. To test interactive responsiveness, we set a pre-experiment design target of `< 250 ms` total verification latency at XL and a falsification threshold of `> 2,000 ms`. In every seed, we also evaluate two TeX build suites under our paranoid wrapper (`openin_any=p openout_any=p pdflatex --no-shell-escape`): (1) benign double-blind builds across **ACM SIGPLAN** (`acmart[sigplan,review,anonymous]`), **CVPR 2025** (`cvpr[review]`), and **ICLR 2025**, audited with `pdfinfo` and `format-verify`; and (2) a **3-vector adversarial containment suite** executing E2 obfuscated shell escape (`\def\cmd{write18}\immediate\csname \cmd\endcsname{touch ...}`), parent-directory write traversal (`\openout ../pwn_out.txt`), and parent-directory read traversal (`\openin ../secret_parent.txt` checked via `pdftotext`).

<!-- run:exp03_scalability_agg -->
**Results.** Figure~\ref{fig:scalability}(a) shows total 4-command latency staying nearly flat from 266.00 $\pm$ 7.28 ms at scale S (265.49 $\pm$ 4.94 ms at M, 262.39 $\pm$ 7.84 ms at L) to 268.55 $\pm$ 6.80 ms at scale XL (`state-sync`: 125.52 $\pm$ 2.81 ms, `check-readonly`: 58.07 $\pm$ 3.56 ms, `review-preflight`: 43.06 $\pm$ 3.75 ms, `format-verify`: 41.91 $\pm$ 3.51 ms). In Figure~\ref{fig:scalability}(b), offloading raw snapshots to `literature/sources/` reduces `citation_ledger.json` footprint by 87.82% at S to 87.96% at XL (24,169 bytes loaded vs. 176,550 bytes offloaded). All 3/3 double-blind venues compile cleanly across all five seeds (`acmart[sigplan]`: 1698.11 $\pm$ 27.14 ms; `cvpr2025`: 1285.42 $\pm$ 28.64 ms; `iclr2025`: 982.74 $\pm$ 7.24 ms) with 0 identity leaks. On the 3-vector adversarial containment suite, paranoid `pdflatex` blocks **2/3** exploits across all five seeds: E2 obfuscated `\csname write18\endcsname` shell execution is blocked (1.0) and parent-directory `\openout` write traversal is blocked (1.0), whereas parent-directory `\openin` read traversal is **not blocked** (0.0).

Three empirical findings emerge from RQ3. First, 4-subprocess XL latency (268.55 ms) exceeded our 250 ms target by 18.55 ms (while staying over 7$\times$ below the 2,000 ms falsification bar) because four separate Python startups and PATH probes dominate fixed overhead; marginal latency across a 6$\times$ scale jump is only +2.55 ms (within run-to-run SD). Second, `pdfinfo` showed that while `cvpr2025` and `iclr2025` clear `/Author`, `/Creator`, and `/Producer` completely, `acmart` v2.16 injects a generic non-identifying `Creator: LaTeX with acmart ...` string via `hyperxmp` while leaving `/Author` and `/Producer` blank (1 generic creator tag, 0 identity leaks). Third, inspecting TeX Live 2026's `texmf.cnf` confirmed *why* parent-directory `\openin` succeeded: upstream TeX Live 2026 deprecated `openin_any` into a silent no-op (always permitting input paths even when `kpsewhich` echoes `p`), proving that untrusted LaTeX templates require OS-level filesystem sandboxing (e.g., containers or `sandbox-exec`) in addition to `--no-shell-escape` and `openout_any=p`.

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=0.98\textwidth]{../visuals/assets/fig_scalability.pdf}
\caption{Verification scalability across 4 workspace scales (S: 20 citations / 5 runs to XL: 120 citations / 30 runs, $n=5$): (a) wall-clock CLI latency (mean $\pm$ SD) across all 4 \texttt{po\_tools.py} subcommands with zoomed 35--63 ms inset; (b) compact \texttt{citation\_ledger.json} vs. offloaded \texttt{literature/sources/} footprint (labeled with \% of total citation metadata offloaded).}
\label{fig:scalability}
\end{figure*}
```

## RQ4: Live Hybrid Fresh-Context Critic Audit {#sec:exp-rq4}

**Setup.** To test whether flat parallel fresh-context read-only critics recover semantic flaws missed by `po_tools.py`, we construct $n=3$ compact seeded mini-paper workspaces (~150--180 words across two Markdown sections each) spanning three domains: ML Systems (`s42`), Vision Benchmarks (`s43`), and Agent Security (`s44`). Each workspace embeds **10 ground-truth defects**—5 mechanical (**M1** missing citation, **M2** unverified citation, **M3** decimal metric drift, **M4** synthetic/`dry_run` leak, **M5** double-blind path/URL leak) and 5 semantic/evasion (**S1** claim-vs-abstract citation distortion on a `verified_source` entry, **S2** integer-only count falsification bypassing decimal regexes, **S3** missing core ablation + universal overclaim + prose lab deanonymization, **S4** undefined mathematical symbol and unexplained acronym, **S5** real `matplotlib` PNG figure rendered with colliding x-ticks, 4.5pt annotations, missing units, and red-green-only bars). Ground truth lives outside the inspected workspaces so critics never see answer keys. We run timed `po_tools.py` (`review-preflight` + `format-verify`) as **B4 (Deterministic-Only)**, capture pre/post SHA-256 `check-readonly` snapshots, dispatch all five live read-only `po-*` critic subagents flat in parallel on Antigravity (Gemini 4; 15 total invocations), estimate output token budgets via a whitespace proxy ($\text{round}(\text{words} \times 1.3)$), and track clean-control false positives specifically on whether critics erroneously mark the valid baseline citation missing/unverified or flag the accurately transcribed secondary decimal as mismatched.

<!-- run:exp04_hybrid_agg -->
```{=latex}
\begin{table*}[t]
\centering
\small
\caption{Live hybrid audit across $n=3$ compact seeded domain manuscripts (30 planted defects: 15 mechanical M1--M5, 15 semantic S1--S5; 15 live Antigravity read-only critic invocations; token counts estimated via whitespace word-count proxy).}
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
**Results.** Table~\ref{tab:hybrid} quantifies semantic recovery over deterministic checks. Deterministic-Only (B4) detects 100.0% of mechanical defects (M1--M5) in 91.71 $\pm$ 0.26 ms at zero token cost, but catches 0.0% of semantic flaws (50.0% total). Live flat-parallel read-only critics recover 100.0% of planted semantic flaws across all three domains (S1--S5, including multimodal raster inspection of `fig_results.png` by `po-visual-format-critic` and integer count auditing by `po-evidence-auditor`), lifting total recall to 100.0% with 0.0 clean-control false positives and 0.0 workspace mutations verified by `check-readonly`. All 15 invocations remained within the 1,500-token budget (mean peak 1411.0 $\pm$ 35.68 tokens; per-role means: `po-clarity-reader` 1400.33 $\pm$ 48.81, `po-peer-reviewer` 1363.0 $\pm$ 44.19, `po-visual-format-critic` 1108.33 $\pm$ 64.78, `po-citation-auditor` 923.33 $\pm$ 31.79, `po-evidence-auditor` 830.67 $\pm$ 31.34).

<!-- run:exp04_hybrid_agg -->
We note two strict scope qualifications on Table~\ref{tab:hybrid}. First, because fresh critics also recovered 100.0% of M1--M5 on these compact (~150--180 word) drafts, RQ4 empirically demonstrates *one-way semantic lift* over B4 (0.0% $\to$ 100.0%) rather than two-way recall separation on M1--M5; the complementary necessity of `po_tools.py` rests on RQ1 and RQ3—namely zero-stochasticity sub-110 ms auditing at 120-citation scale and binary archive/TeX checks (Zip Slip, SHA-256 tamper verification) that read-only critics without shell tools cannot execute. Second, `po-citation-auditor` independently caught an unplanted template imprecision in two domains—flagging `"demonstrate strong baseline efficiency"` as unsupported by `wang2021tent` in `s43` (Nit) and contradicting `greshake2023indirect` (an indirect prompt-injection paper) in `s44` (Major)—confirming genuine snapshot-grounded critique while highlighting why our narrow `clean_control_fp` metric does not capture all unplanted findings.
