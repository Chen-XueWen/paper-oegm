# Review Resolution Report — Round 1

* **Source Report:** `reviews/round_1/review_report.md`
* **Snapshots Directory:** `manuscript/snapshots/round_1/` (all 7 pre-edit sections backed up)
* **Status:** `resolved`

## Bucket 1 — Mechanical Fixes (Single Batch Diff)

| Finding ID | Scope | Applied Edit | Decision |
| --- | --- | --- | --- |
| `peer-r1-02`, `clarity-r1-01` | `04_method.md`, `06_limitations.md` | Rewrote Eq. (2) as exact disjunction $\|m-v\| \le \epsilon(d) \lor (0 \le m \le 1 \land \|100m-v\| \le \epsilon(d))$; documented unordered-set key-swap, unit-ambiguous `[0,1]` scaling, and untagged-paragraph boundaries | `accepted` |
| `evidence-r1-01` | `experiments/exp04_hybrid.py`, `05_experiments.md` | Instrumented real B4 timing in `exp04_hybrid.py`, re-ran deterministic scoring (`91.71 ± 0.26 ms`, `n=3`), and replaced unbacked `"in under 100 ms"` with exact canonical logged latency | `accepted` |
| `evidence-r1-03`, `peer-r1-06` | `experiments/run_exp01_faultbench.sh`, `05_experiments.md`, `paper_state.json` | Restored full `run_exp01_faultbench.sh` (`3,313 B`, verified live on 5 seeds), documented Antigravity/Gemini 4 runtime, ~150–180 word draft lengths, and `1.3x` word-count token proxy, and re-synced `paper_state.json` | `accepted` |
| `evidence-r1-04` | `05_experiments.md` | Separated `s43` unplanted citation catch (`wang2021tent`, Nit) from `s44` (`greshake2023indirect`, Major) and explicitly defined `clean_control_fp` scope | `accepted` |
| `peer-r1-05`, `clarity-r1-05`, `evidence-r1-07` | `01_abstract.md`, `02_introduction.md`, `04_method.md`, `05_experiments.md`, `07_conclusion.md` | Qualified per-harness verification tiers upfront; fixed `"under 63 lines"` -> `"at most 63 lines"`; separated CPU-local runs (RQ1–RQ3) from live Antigravity runs (RQ4); clarified `87.82%–87.96%` `citation_ledger.json` offloading (snapshots loaded on demand by `po-citation-auditor`); clarified zero third-party deps for `po_tools.py` with optional `matplotlib` for Stage 5; specified per-seed and author-constructed PO-FaultBench counts in Abstract | `accepted` |
| `citation-r1-01`, `citation-r1-02`, `citation-r1-04`, `citation-r1-05`, `citation-r1-06` | `02_introduction.md`, `03_related_work.md`, `04_method.md`, `05_experiments.md`, `06_limitations.md` | Aligned SkillsBench, `xu2026agentskills`/`badhe2026skillsecurity`, PaperOrchestra (`song2026paperorchestra`), `schmotz2026skillinject`, and `liang2024feedback` strictly with saved primary-source abstracts; framed Antigravity's `24,000`-byte ceiling explicitly as an observed host-loader limit | `accepted` |
| `citation-r1-03`, `peer-r1-03` | `literature/sources/google2026egm.json`, `literature/references.bib`, `03_related_work.md`, `05_experiments.md` | Enriched `google2026egm.json` snapshot from EGM manifests/README/synthesizer; cited strictly as public `google/elephant-goldfish-model` v0.1.1 (removed `"locally installed"` phrasing); separated schema-independent vs. schema-specific RQ1 families and explained `---` cells in Tables 1–2 | `accepted` |
| `clarity-r1-02`, `clarity-r1-03`, `clarity-r1-04`, `clarity-r1-06`, `clarity-r1-07`, `evidence-r1-05`, `evidence-r1-06` | `02_introduction.md`..`07_conclusion.md` | Renamed `F1`–`F8` -> `FF1`–`FF8` and wrote `F1-score` consistently; documented B0/B1 evaluation and RQ3 latency thresholds in Setup; removed raw internal run IDs (`exp01`..`exp04`, `SHELL_PIPE_RE`, `shutil.which`) from prose; expanded `IRB`/`AST`; glossed `openin_any=p`/`openout_any=p`, three-bucket triage, Elephant-Goldfish; separated decimal `KB` (`1,000 B`) vs. binary `KiB` (`1,024 B`); clarified `po-literature` Stages 1a/1b and $B_{\text{stage}}(s)$; added inline `<!-- run:<id> -->` to secondary quantitative blocks | `accepted` |
| `visual-r1-04` | `02_introduction.md`, `05_experiments.md` | Wrapped all 4 full-width figures in explicit two-column `\begin{figure*}[t]` blocks for ACM `sigplan` | `accepted` |

## Bucket 2 — Scientific Decisions (Researcher Choice Executed)

| Finding ID | Severity | Issue | Executed Resolution | Researcher Decision / Attestation |
| --- | --- | --- | --- | --- |
| `evidence-r1-02`, `evidence-r1-01`, `peer-r1-04` | `Blocker` / `Major` | Unlogged B0/B1 evasion recall & hardcoded `0.0` in `fig_faultbench_recall.py`; untimed B4 in `exp04`; untested adversarial TeX containment in `exp03` | Exported `evasion_b0_recall`/`evasion_b1_recall` and re-ran `exp01` (`n=5`, `108.20 ± 2.07 ms`); added 3-vector adversarial TeX containment test to `exp03` (`n=5`: E2 `\csname write18\endcsname` blocked `1/1`, `\openout` parent blocked `1/1`, `\openin` parent `0/1` uncovering TeX Live 2026 `openin_any=p` upstream no-op regression); timed B4 in `exp04` (`91.71 ± 0.26 ms`, preserving all 15 live critic outputs); re-aggregated all 22 canonical runs (`git_dirty: false`, `is_synthetic: false`) | `accepted (Option A: fast <60s CPU patches)` |
| `peer-r1-01` | `Blocker` | Identical `100.0%` rows for Critics Alone vs. Hybrid in RQ4 & missing same-context / single-agent critic baseline | Narrowed Table 3 & prose strictly to one-way semantic recovery over B4 (`0.0% -> 100.0%`), tied deterministic archive/scale complementarity explicitly to RQ1/RQ3, and candidly disclosed missing same-context / single-agent critic baseline and targeted `clean_control_fp` scope in `05_experiments.md` and `06_limitations.md` | `accepted (Option B: scope narrowing + explicit limitation)` |
| `visual-r1-01`, `visual-r1-02`, `visual-r1-03`, `visual-r1-05`, `visual-r1-06` | `Major` / `Minor` | Curve overlap in `fig_scalability(a)`, sub-6pt subtitles & stub arrows in `fig_architecture`, legend/threshold overlap in `fig_skill_footprint(a)`, callout & labels in `fig_faultbench_recall` | Re-rendered all 4 figures (`35–63 ms` zoomed inset + exterior legend on `fig_scalability(a)`, `>= 6.5–7.2 pt` labels & solid arrow shafts on `fig_architecture`, exterior legend + `+257 B` callout on `fig_skill_footprint(a)`, dynamic `evasion_b0`/`b1` reads + `FF1`–`FF8` + centered callout on `fig_faultbench_recall`, Unicode `→`, `↔`, `≤`), visually re-verified via `read_file` | `accepted (Option A: full Pass 2 visual re-render)` |

## Bucket 3 — Optional Polish (`Minor` / `Nit`)

| Finding ID | Scope | Applied Edit | Decision |
| --- | --- | --- | --- |
| `citation-r1-07`, `citation-r1-08`, `citation-r1-09`, `citation-r1-10`, `citation-r1-11` | `literature/references.bib`, `literature/citation_ledger.json`, `03_related_work.md`, `06_limitations.md` | Upgraded `huang2024selfcorrect` (ICLR 2024), `weng2024cycleresearcher` (ICLR 2025), `xu2026agentskills` (Agent Skills '26), `destefanis2026gitskills` (MSR '27); expanded full author lists (`starace2025paperbench` 13 authors, `li2026skillsbench` full authors); tightened 4 Related Work phrasings; rewrote all 20 `claim_summary` entries cleanly; fixed `@liang2024feedback's` -> `of @liang2024feedback` | `accepted` |
| `clarity-r1-08` | `01_abstract.md`, `04_method.md`, `05_experiments.md`, `07_conclusion.md` | Split 100+ word sentences, standardized `SD` across text/tables/figures, restored `"median"` in Conclusion | `accepted` |

## Settled-Findings Log (Do Not Reopen Unless Evidence Changes; Max 2 Revisions/Finding)

| Finding ID | Revision Count | Resolution / Waiver Attestation | Evidence Hash / Basis |
| --- | --- | --- | --- |
| `peer-r1-01` | `1` | Narrowed RQ4 Table 3 claim to one-way semantic recovery over B4; missing same-context/single-agent baseline explicitly disclosed in `06_limitations.md` per researcher approval | `manuscript/sections/05_experiments.md`, `06_limitations.md` |
| `peer-r1-02`, `clarity-r1-01` | `1` | Fixed Eq. (2) to exact disjunction matching `po_tools.py:number_matches_any()` and documented aliasing boundaries | `manuscript/sections/04_method.md`, `06_limitations.md` |
| `evidence-r1-01` | `1` | Instrumented and logged canonical `b4_latency_ms = 91.71 ± 0.26 ms` (`n=3`) | `experiments/runs/exp04_hybrid_agg/metrics.json` |
| `evidence-r1-02` | `1` | Exported `evasion_b0_recall` / `evasion_b1_recall` (`0.0 ± 0.0`) across `n=5` seeds and removed hardcoded `0.0` in `fig_faultbench_recall.py` | `experiments/runs/exp01_faultbench_agg/metrics.json` |
| `peer-r1-04` | `1` | Executed 3-vector adversarial TeX containment suite (`e2_macro_shell_blocked=1.0`, `openout_parent_blocked=1.0`, `openin_parent_blocked=0.0` exposing TeX Live 2026 no-op regression) | `experiments/runs/exp03_scalability_agg/metrics.json` |
| `evidence-r1-03` | `1` | Restored `experiments/run_exp01_faultbench.sh` (`3,313 B`) and verified 5-seed execution | `experiments/run_exp01_faultbench.sh` |
| `visual-r1-01`..`06` | `1` | Re-rendered all 4 figures, verified zero overlaps via multimodal `read_file`, switched to `\begin{figure*}[t]` | `visuals/manifest.md`, `visuals/assets/fig_*.png` |
| `citation-r1-01`..`11`, `peer-r1-03`, `peer-r1-05`, `clarity-r1-02`..`08` | `1` | Applied all citation-snapshot alignments, EGM snapshot expansion, `FF1`–`FF8` renaming, prose tightening, and BibTeX upgrades | `literature/references.bib`, `manuscript/sections/*.md` |
| `git_dirty` (Round 1 re-runs) | `1` | Attested waiver per `experiment_safety.md`: `paper_workspace/` became tracked in commit `a0bf832`; `git diff --name-only -- ':!paper_workspace'` is completely empty (zero modifications to plugin code under `skills/`, `agents/`, `resources/`, `scripts/`, or manifests) | `git diff -- ':!paper_workspace'` empty |
| `format-c2-01`, `format-c3-01` (Pass 2 Cycle 1) | `1` | User-approved `po-resolve` prose trim (`manuscript/snapshots/round_2/` backed up pre-trim sections; tightened `7,104` -> `5,015` words across all 7 sections while preserving all 20 citations, 4 figures, 3 tables, 2 equations, inline tags, and negative results); compiled cleanly to `9 / 9` main-body pages (`10` pages total) | `submission/build_report.md`, `submission/main.pdf` |
| `visual-r2-01`, `visual-r2-06`, `visual-r2-07`, `p6-10 visual-r2-03` (Pass 2 Cycle 2) | `1` | Indented Eq. (2) inside item 3 of `04_method.md` so `4. format-verify:` stays inside the numbered list; fixed `"four"` -> `"five"` contributions in `02_introduction.md`; harmonized Phase 2 (`Plan & Draft`) and Phase 3 (`Review & Build`) titles with Figure 1; protected `{Han-chung} Lee` in `literature/references.bib` | `manuscript/sections/02_introduction.md`, `04_method.md`, `literature/references.bib` |

## Applied Edits Summary

* **Experiments re-run (`git_dirty: false`, `is_synthetic: false`):** `experiments/run_exp01_faultbench.sh` (restored), `exp01_faultbench.py`, `exp03_scalability.py`, `exp04_hybrid.py`, `experiments/provenance_index.json` (`22` canonical runs).
* **Literature upgraded:** `literature/sources/google2026egm.json`, `literature/references.bib`, `literature/citation_ledger.json`.
* **Visuals re-rendered & audited:** `visuals/scripts/fig_{architecture,faultbench_recall,skill_footprint,scalability}.py`, `visuals/assets/fig_*.{pdf,png}`, `visuals/manifest.md`.
* **Manuscript updated (pre-edit snapshots in `manuscript/snapshots/round_1/` and `manuscript/snapshots/round_2/`):** `manuscript/sections/01_abstract.md` through `07_conclusion.md` (Round 1 fixes + Pass 2 page trim to `9 / 9` pages + Pass 2 Cycle 2 list/count/title polish).
