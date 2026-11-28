# Peer Review Report — Round 1

* **Workspace:** `paper_workspace`
* **Date (UTC):** `2026-11-28T02:28:00Z`
* **Read-Only Verification (`po_tools.py check-readonly`):** `PASS (0 modified, 0 deleted workspace files; 3 macOS Finder .DS_Store OS-metadata files noted)`

## Reviewer Status

| Critic | Status | Token Budget | Notes |
| --- | --- | --- | --- |
| `po-peer-reviewer` | `completed` | `<= 1,500` | `2` Blocker, `3` Major, `1` Minor |
| `po-evidence-auditor` | `completed` | `<= 1,500` | `2` Blocker, `2` Major, `2` Minor, `1` Nit (completed on retry after transient 429) |
| `po-citation-auditor` | `completed` | `<= 1,500` | `0` Blocker, `6` Major, `3` Minor, `2` Nit (20/20 BibTeX/ledger/snapshot parity PASS) |
| `po-visual-format-critic` | `completed` | `<= 1,500` | `0` Blocker, `3` Major, `2` Minor, `1` Nit (`VISUAL_AUDIT: COMPLETED` across all 4 PNGs) |
| `po-clarity-reader` | `completed` | `<= 1,500` | `0` Blocker, `5` Major, `2` Minor, `1` Nit |

## Deterministic Pre-Check (`po_tools.py review-preflight`)

* **Status:** `PASS` (`ok: true`, `0` blockers, `0` majors)
* **Summary:** Scanned `7` sections (`01_abstract.md`..`07_conclusion.md`), `20/20` cited keys present in `literature/references.bib` and `literature/citation_ledger.json` (`verified_source` with existing snapshots under `literature/sources/`), `4` canonical aggregate runs audited with zero synthetic/`dry_run` leakage, `git_dirty: false`, and zero inline decimal mismatches.

## Prioritized Findings (`Blocker` -> `Major` -> `Minor` -> `Nit`)

### Blockers (`4`)

#### `peer-r1-01` — Missing Core Baselines and Unproven Hybrid Complementarity in RQ4
* **Severity:** Blocker
* **Critic:** `po-peer-reviewer`
* **Affected Scope:** `manuscript/sections/05_experiments.md` (Section 5.4, Table 3), `01_abstract.md`, `02_introduction.md`
* **Discrepancy:** RQ4 omits a same-context self-review baseline and a single-agent fresh critic ablation; moreover, Table 3 shows identical `100.0%` metrics for `Fresh Read-Only Critics Alone` and `PaperOEGM Hybrid (Full)`, so RQ4 does not empirically establish two-way complementarity over critics alone. Clean-FP checking inspects only three tokens without full precision/unplanted-finding accounting or a defect-free control.
* **Evidence:** `05_experiments.md` Table 3 (`100.0 ± 0.0` identical across Critics Alone and Hybrid) vs. line 109 (`"Table~\ref{tab:hybrid} demonstrates clear complementarity"`).
* **Suggested Action:** Either (a) expand `exp04` to add a same-context/single-critic ablation and a mechanical fault read-only critics cannot inspect (e.g., template archive Zip Slip / SHA-256 tamper), or (b) narrow complementarity wording in Table 3 / prose to distinguish empirical semantic gain (`0%` -> `100%` over B4) from structural/cost/binary-archive complementarity established in RQ1 and RQ3.

#### `peer-r1-02` — Mathematical Error and Aliasing Gaps in Inline Metric Verification (also `clarity-r1-01`)
* **Severity:** Blocker
* **Critic:** `po-peer-reviewer` (corroborated by `po-clarity-reader` `clarity-r1-01`)
* **Affected Scope:** `manuscript/sections/04_method.md` (Section 4.2, Eq. `#eq:decimal-match`)
* **Discrepancy:** Equation (2) uses `\min(|m-v|, \mathbb{I}[0 \le m \le 1] \cdot |100m - v|) \le \epsilon(d)`, which evaluates to `0 \le \epsilon(d)` whenever any $m \notin [0, 1]$ (vacuously passing every fabricated decimal $v$). Unordered set matching $\mathcal{M}(r)$ also cannot catch metric-key swaps, unit-ambiguous `[0,1]` scaling, or untagged paragraphs.
* **Evidence:** `04_method.md` line 30.
* **Suggested Action:** Replace Eq. (2) with the exact disjunction $|m - v| \le \epsilon(d) \lor (0 \le m \le 1 \land |100m - v| \le \epsilon(d))$ matching `po_tools.py:number_matches_any()`, and explicitly note key-swap / untagged-paragraph boundaries in Section 4.2 and Section 6.

#### `evidence-r1-01` — Unbacked B4 Latency Claim (`"in under 100 ms"`) in RQ4
* **Severity:** Blocker
* **Critic:** `po-evidence-auditor`
* **Affected Scope:** `manuscript/sections/05_experiments.md` (Section 5.4, line 109)
* **Discrepancy:** Prose states B4 detects M1–M5 `"in under 100 ms"`, but `exp04_hybrid.py` does not log timing and the 3-command total in `exp03` at scale S is `126.85 ms` (`115.72 ± 6.03 ms` in `exp01`).
* **Evidence:** `05_experiments.md:109` vs. `experiments/runs/exp04_hybrid_agg/metrics.json` (no timing key).
* **Suggested Action:** Remove the unlogged `"in under 100 ms"` claim (or instrument and re-run `exp04` to log actual latency).

#### `evidence-r1-02` — Unlogged B0/B1 Evasion Recall in Table 1 and Hardcoded `0.0` in `fig_faultbench_recall.py`
* **Severity:** Blocker
* **Critic:** `po-evidence-auditor` (also noted in `visual-r1-05`)
* **Affected Scope:** `manuscript/sections/05_experiments.md` (`tab:faultbench`, lines 31–32); `visuals/scripts/fig_faultbench_recall.py` (lines 43–47, 70)
* **Discrepancy:** Table 1 reports `0.00 ± 0.00` Evasion Recall for B0 and B1, and `fig_faultbench_recall.py` hardcodes `b0_vals.append(0.0)` and aliases `b1_vals` to Full's `evasion_det_recall`, because `exp01_faultbench.py` only exported `evasion_det_recall` for Full.
* **Evidence:** `experiments/runs/exp01_faultbench_agg/metrics.json` lacks `evasion_b1_recall` and `evasion_b0_recall`; `fig_faultbench_recall.py:44-47,70`.
* **Suggested Action:** Export `evasion_b1_recall` and `evasion_b0_recall` in `exp01_faultbench.py`, re-run `exp01` (`n=5`), and read all three keys dynamically in `fig_faultbench_recall.py` (or replace B0/B1 evasion cells with `---`).

---

### Majors (`18` — deduplicated across 5 critics)

#### `peer-r1-03` — Tautological RQ1 Baselines, Unreproducible Local EGM Baseline, and Anonymity Risk
* **Severity:** Major | **Critic:** `po-peer-reviewer` | **Scope:** `05_experiments.md` (Sections 5.1–5.2, Tables 1–2)
* **Discrepancy:** B0 omits latency (`---`) and standard schema-independent linters on F1a/F5–F7; B3 (EGM) leaves 4 Table 2 columns blank (`---`) and refers to an unversioned `"locally installed"` plugin, risking reproducibility and double-blind affiliation inference.
* **Suggested Action:** Separate schema-independent vs. schema-specific families in RQ1 discussion, explain `---` cells explicitly, and cite EGM strictly via its public GitHub repository (`google/elephant-goldfish-model` v0.1.1) without `"locally installed"` phrasing.

#### `peer-r1-04` — Unverified Security Claims for Paranoid TeX Sandboxing and Prompt Injection
* **Severity:** Major | **Critic:** `po-peer-reviewer` | **Scope:** `02_introduction.md`, `03_related_work.md`, `04_method.md`, `05_experiments.md`
* **Discrepancy:** RQ3 compiles only benign minimal manuscripts—never empirically executing E2 (`\csname write18\endcsname`) or `\openin`/`\openout` traversal payloads under paranoid vs. default `pdflatex`. Indirect prompt injection against critics is motivated without being empirically tested.
* **Suggested Action:** Add an adversarial paranoid-TeX exploit containment test to `exp03` (verifying E2 `\csname write18\endcsname` and parent-path `\openin` fail closed under paranoid flags) and clearly separate tested TeX containment from untested prompt-injection resilience in Abstract/Intro.

#### `peer-r1-05` — Overclaimed Cross-Harness Support and Internal Technical Contradictions
* **Severity:** Major | **Critic:** `po-peer-reviewer` (corroborated by `clarity-r1-05`) | **Scope:** `01_abstract.md`, `02_introduction.md`, `04_method.md`, `05_experiments.md`, `06_limitations.md`, `07_conclusion.md`
* **Discrepancy:** (1) Abstract/Intro/Conclusion present Antigravity, Claude Code, and Codex symmetrically without stating up front that live execution was tested on Antigravity, packaging validated on Claude Code, and manifests verified structurally on Codex; (2) `"87.96% from critic context"` overlooks that `po-citation-auditor` reads `literature/sources/` on demand; (3) `"zero third-party Python package installations"` conflicts with optional `matplotlib` in Stage 5.
* **Suggested Action:** Qualify per-harness verification levels in Abstract/Intro, reframe `87.96%` offloading as compacting the shared ledger while loading snapshots on demand during citation auditing, and clarify zero third-party dependencies for the core verifier (`po_tools.py`) with optional `matplotlib` for Stage 5 plotting.

#### `evidence-r1-03` — Empty RQ1 Runner Script (`run_exp01_faultbench.sh`) Breaks Reproducibility
* **Severity:** Major | **Critic:** `po-evidence-auditor` (corroborated by `peer-r1-06`) | **Scope:** `experiments/run_exp01_faultbench.sh`, `paper_state.json`
* **Discrepancy:** `experiments/run_exp01_faultbench.sh` is `0` bytes on disk (`sha256:e3b0c442...` in `paper_state.json`), breaking reproduction of `exp01_faultbench_*`.
* **Suggested Action:** Restore `experiments/run_exp01_faultbench.sh`, verify execution, and re-sync `paper_state.json`.

#### `evidence-r1-04` — Misattributed `s43` Unplanted Defect and Clean-Control C1 Accounting in RQ4
* **Severity:** Major | **Critic:** `po-evidence-auditor` | **Scope:** `05_experiments.md` (Section 5.4, lines 87, 111)
* **Discrepancy:** Line 111 claims `greshake2023indirect` was flagged in both `s43` and `s44`; in `s43` the flagged entry was `wang2021tent` (Nit), whereas `greshake2023indirect` (Major) occurred only in `s44`. Clean-control C1 wording in line 87 also conflicts with line 111.
* **Suggested Action:** Separate `s43` (`wang2021tent`, Nit) from `s44` (`greshake2023indirect`, Major) and explicitly document the `clean_control_fp` scoring criterion.

#### `citation-r1-01` — Overstatement and Conflation of SkillsBench Findings
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `02_introduction.md` (line 3)
* **Discrepancy:** Conflates overall curated-skill lift (`+16.6 pp`, `33.9% -> 50.5%`) with focused skills (`<= 3` modules) and claims exhaustive bundles "degrade performance" rather than being outperformed by focused skills.
* **Suggested Action:** Mirror the exact phrasing from `03_related_work.md` matching `literature/sources/li2026skillsbench.json`.

#### `citation-r1-02` — Misattribution of `26.1%` Vulnerability Rate and Lifecycle Stages
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `03_related_work.md` (line 13)
* **Discrepancy:** Jointly attributes `26.1%` and `"acquisition, execution, and maintenance"` to both `xu2026agentskills` and `badhe2026skillsecurity`; `badhe2026skillsecurity` evaluates 327 skills across a five-stage lifecycle (`repository admission, semantic retrieval, planner selection, execution, skill evolution`) with no `26.1%` figure.
* **Suggested Action:** Split the sentence to attribute each finding accurately to its respective snapshot.

#### `citation-r1-03` — Unsupported EGM Claims and Editorialized BibTeX Metadata
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `03_related_work.md`, `04_method.md`, `literature/references.bib` (`google2026egm`)
* **Discrepancy:** Claims about Antigravity/Claude Code targeting, Goldfish personas, and nested `synthesizer`, plus BibTeX subtitle/`Google LLC`/`year={2026}`, are absent from `literature/sources/google2026egm.json`.
* **Suggested Action:** Expand `literature/sources/google2026egm.json` with verified snapshots from EGM's `README.md`/`plugin.json`/`agents/synthesizer.md` (or ground strictly in `exp02` inspection) and align `references.bib` fields with the manifest.

#### `citation-r1-04` — PaperOrchestra Implementation Claims Exceed Saved Abstract Snapshot
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `02_introduction.md`, `03_related_work.md`, `literature/literature_review.md` (`song2026paperorchestra`)
* **Discrepancy:** Describing PaperOrchestra as an `"API-key-dependent Python pipeline"` lacking separation between code-rendered plots and non-quantitative diagrams exceeds `literature/sources/song2026paperorchestra.json` (abstract-only).
* **Suggested Action:** Narrow PaperOrchestra characterization strictly to what the verified arXiv abstract establishes (post-experiment automated manuscript/visual pipeline vs. interactive pre-experiment skills and deterministic verification).

#### `citation-r1-05` — Claims Exceed Saved Snapshots for `schmotz2026skillinject` and `liang2024feedback`
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `03_related_work.md` (line 25), `06_limitations.md` (line 7)
* **Discrepancy:** `06_limitations.md` attributes scraped-abstract/PDF adaptive attacks to `schmotz2026skillinject` (which tested skill-file injections); `03_related_work.md` attributes `"persistent factual-verification weaknesses"` to `liang2024feedback` (whose saved abstract states `"we also identify several limitations"`).
* **Suggested Action:** Align both sentences strictly with their saved primary-source abstracts.

#### `citation-r1-06` — Uncited Quantitative Evaluation Threshold (Antigravity 24 KB Limit) & `SKILL.md` Spec
* **Severity:** Major | **Critic:** `po-citation-auditor` | **Scope:** `02_introduction.md`, `04_method.md`, `05_experiments.md`
* **Discrepancy:** `24,000`-byte Antigravity skill ceiling and the open `SKILL.md` specification are invoked as quantitative evaluation baselines without a citation.
* **Suggested Action:** Clarify the `24,000`-byte skill ceiling as an empirical host-loader constraint documented in the plugin packaging spec (or add verified specification citations with snapshots).

#### `visual-r1-01` — Severe Curve & Marker Collision in `fig_scalability` Panel (a)
* **Severity:** Major | **Critic:** `po-visual-format-critic` | **Scope:** `visuals/assets/fig_scalability.png` (Panel a)
* **Discrepancy:** `review-preflight`, `format-verify`, and `check-readonly` collide around `40–55 ms` on the `0–380 ms` linear y-axis, hiding subcommand trends and error bars.
* **Suggested Action:** Move legend outside above Panel (a) at `>= 7.2 pt` and add a zoomed inset (`35–62 ms`) or broken y-axis separating the `40–58 ms` subcommands cleanly.

#### `visual-r1-02` — Sub-6pt Print Fonts, Cramped `Gate` Diamonds, and Malformed Stub Arrows in `fig_architecture`
* **Severity:** Major | **Critic:** `po-visual-format-critic` | **Scope:** `visuals/assets/fig_architecture.png`
* **Discrepancy:** Subtitle (`5.5–5.7 pt`) and `Gate` (`5.8 pt`) text shrink to `~5.1–5.4 pt` at ACM `sigplan` width; `Gate` touches diamond edges; horizontal blue arrows (`dx=0.011`) and dotted orange arrows collapse into stub arrowheads.
* **Suggested Action:** Raise subtitles to `>= 6.8 pt`, widen `Gate` diamonds and inter-box spacing so arrows have clean visible shafts, and replace dotted arrowheads with solid/dashed arrows.

#### `visual-r1-03` — Legend Obscures Reference Lines & Near-Fused `24.0 KB` vs `24.3 KB` Thresholds in `fig_skill_footprint` (a)
* **Severity:** Major | **Critic:** `po-visual-format-critic` | **Scope:** `visuals/assets/fig_skill_footprint.png` (Panel a)
* **Discrepancy:** Lower-right legend overlaps three vertical reference lines, and `24.0 KB` vs `24.3 KB` lines nearly merge visually.
* **Suggested Action:** Move Panel (a) legend outside above the axes (`ncol=2`, `>= 7.2 pt`) and add a clear callout arrow annotating `EGM Max (+257 B over 24 KB)`.

#### `clarity-r1-02` — Symbol Collision on `F1` (Fault Family 1 vs. F1-Score)
* **Severity:** Major | **Critic:** `po-clarity-reader` | **Scope:** `05_experiments.md` (Section 5.1, Table 1)
* **Discrepancy:** `F1` denotes both Fault Family 1 and harmonic-mean F1-score in the same paragraph.
* **Suggested Action:** Rename fault families to `FF1`–`FF8` (updating `fig_faultbench_recall.py` labels to match) and write `F1-score` consistently.

#### `clarity-r1-03` — Missing RQ1 Baseline Operationalization & Unintroduced RQ3 Thresholds
* **Severity:** Major | **Critic:** `po-clarity-reader` | **Scope:** `05_experiments.md` (Sections 5.1, 5.3)
* **Discrepancy:** B0/B1 evaluation method and `---` latency are unexplained in Setup; RQ3's `250 ms` target and `2,000 ms` falsification criterion appear in Results without prior introduction in Setup.
* **Suggested Action:** Document B0/B1 evaluation protocol and introduce RQ3 latency targets in Setup.

#### `clarity-r1-04` — Unexplained Codebase Identifiers & Invisible Run IDs
* **Severity:** Major | **Critic:** `po-clarity-reader` | **Scope:** `04_method.md`, `05_experiments.md`, `06_limitations.md`
* **Discrepancy:** Internal run IDs (`exp01`, `exp01_evasion`, `exp03`, `exp04`) and raw code identifiers (`SHELL_PIPE_RE`, `pdfinfo_generic_creator_tags`, `shutil.which`) appear in reader-facing prose without definition.
* **Suggested Action:** Replace internal run IDs with visible `RQ1`–`RQ4` references and define or replace raw code constants.

#### `clarity-r1-05` — Cross-Section Metric, Environment, and Scope Drifts
* **Severity:** Major | **Critic:** `po-clarity-reader` (corroborated by `evidence-r1-07`) | **Scope:** `01_abstract.md`, `02_introduction.md`, `05_experiments.md`
* **Discrepancy:** `"under 63 lines"` vs. `"maximum 63 lines"`; `"All experiments execute on CPU"` omits Antigravity LLM execution for RQ4; Intro `87.96%` offloading vs. `87.82%–87.96%` range; Abstract omits per-seed / 40-negative-control / author-constructed qualifiers for PO-FaultBench.
* **Suggested Action:** Align all four details cleanly across Abstract, Introduction, and Experiments.

---

### Minors (`10`) & Nits (`5`)

* **`peer-r1-06` (`Minor`, `po-peer-reviewer`):** Report the underlying LLM model/environment, mini-paper lengths, and token-counting heuristic in RQ4; reconcile `paper_state.json` hashes.
* **`evidence-r1-05` (`Minor`, `po-evidence-auditor`):** Add inline `<!-- run:<run_id> -->` markers above secondary single-run quantitative paragraphs.
* **`evidence-r1-06` (`Minor`, `po-evidence-auditor`):** Sync `plan/experiment_design.md` (`n=3` for `exp04`), disclose the `1.3x` word-count token proxy in Section 5.4, and distinguish decimal `KB` (`1,000 B`) vs. binary `KiB` (`1,024 B`).
* **`citation-r1-07` (`Minor`, `po-citation-auditor`):** Update accepted venues in `references.bib` (`huang2024selfcorrect` ICLR 2024, `weng2024cycleresearcher` ICLR 2025, `xu2026agentskills` Agent Skills '26 @ ACM CAIS 2026) and align years with citekeys.
* **`citation-r1-08` (`Minor`, `po-citation-auditor`):** Populate full author lists in `references.bib` for `starace2025paperbench` (13 authors) and `li2026skillsbench` (removing premature `and others`).
* **`citation-r1-09` (`Minor`, `po-citation-auditor`):** Tighten 4 minor phrasing drifts (`saha2026underhood` paired-trial selection rate, `schmotz2026skillinject` obvious-to-subtle spectrum, `weng2024cycleresearcher` no "code execution", `starace2025paperbench` average rubric replication score).
* **`visual-r1-04` (`Minor`, `po-visual-format-critic`):** Emit all 4 full-width figures as two-column `\begin{figure*}[t]` floats in `po-format` for ACM `sigplan`.
* **`visual-r1-05` (`Minor`, `po-visual-format-critic`):** Center `fig_faultbench_recall` callout at `y=8.0`, label `B1: 0%` on FF4, and clarify `80 positive faults/seed (SD=0.0%)` in caption.
* **`clarity-r1-06` (`Minor`, `po-clarity-reader`):** Expand `IRB` and `AST`, gloss `openin_any=p`/`openout_any=p`, `"three-bucket triage"`, `"Elephant-Goldfish"`, write `24 KB (24,000 bytes)`, and standardize harness names.
* **`clarity-r1-07` (`Minor`, `po-clarity-reader`):** Note `po-literature` reuse across Stages 1a/1b, specify all files counted in $B_{\text{stage}}(s)$, and explain Table 2 `---` cells.
* **`evidence-r1-07` (`Nit`, `po-evidence-auditor`):** Change `"under 63 lines"` to `"at most 63 lines"` in Abstract.
* **`citation-r1-10` (`Nit`, `po-citation-auditor`):** Replace truncated `claim_summary` prefixes in `literature/citation_ledger.json`.
* **`citation-r1-11` (`Nit`, `po-citation-auditor`):** Rewrite `@liang2024feedback's` to `of @liang2024feedback` in `06_limitations.md`.
* **`visual-r1-06` (`Nit`, `po-visual-format-critic`):** Use typographic Unicode `→`, `↔`, `≤` in vector labels, add `%` label on `Active (Max)` in `fig_skill_footprint(b)`, and clarify `% offloaded` in `fig_scalability(b)` caption.
* **`clarity-r1-08` (`Nit`, `po-clarity-reader`):** Break 100+ word sentences in Abstract/Method/RQ4, standardize on `SD`, and restore `"median"` in Conclusion.
