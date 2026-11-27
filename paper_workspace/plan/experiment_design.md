# Experiment Design Plan

* **Project:** PaperOEGM: Composable Zero-API-Key Agent Skills with Deterministic Provenance Verification and Fresh-Context Peer Review
* **Target Venue:** `agentskills2027` — Agent Skills Workshop (ACM CAIS 2027), 9-page Full Paper (`acmart[sigplan,review,anonymous]`, double-blind; authoritative settings in `paper_state.json`)
* **Date:** `2026-11-27`

---

## 1. Research Questions & Falsifiable Hypotheses

| ID | Research Question | Hypothesis | Falsification Criterion |
| --- | --- | --- | --- |
| **RQ1** | How accurately and fast does PaperOEGM's zero-dependency stdlib verifier (`po_tools.py`) detect scientific provenance, conversion-parity, anonymity, tamper, and template supply-chain faults compared to compiler-only and ablated baselines—and where do deterministic checks fail? | Across a 120-case fault-injection corpus (`PO-FaultBench`: 80 faults across 8 families + 40 hard negative controls), `po_tools.py` achieves `>= 98%` recall and `<= 2%` false-positive rate (FPR) in `< 50 ms`/workspace, outperforming a TeX-compiler-only baseline (`< 25%` recall); on an adversarial/semantic evasion suite (`20` cases), deterministic recall drops below `30%`, proving semantic critics and native TeX sandboxing remain indispensable. | Hypothesis is refuted if `po_tools.py` recall on `PO-FaultBench` is `< 95%`, FPR exceeds `5%`, median latency exceeds `200 ms`, or compiler-only baseline detects `>= 60%` of injected faults. |
| **RQ2** | How does PaperOEGM's 10-skill modular packaging compare against monolithic single-skill prompting, legacy Python-CLI orchestration, and EGM's reference layout on context footprint, packaging defect compliance, and multi-harness build determinism? | Splitting the workflow into 10 modular `SKILL.md` files (`<= 12,000` bytes each) reduces per-stage prompt overhead by `>= 75%` relative to loading a single monolithic workflow skill, maintains `0` packaging defects under the specification-compliance checklist [@zhang2026reusable] and `claude plugin validate`, and achieves `100%` byte-reproducible ZIP SHA-256 parity across 3 targets (`antigravity`, `claude`, `openai`) over 5 independent builds. | Hypothesis is refuted if per-stage byte/token overhead reduction is `< 50%`, any skill exceeds Antigravity's `24,000`-byte ceiling, any target fails deterministic SHA-256 parity, or `claude plugin validate` emits errors/warnings. |
| **RQ3** | How do `po_tools.py` latency, compact citation-ledger offloading (`literature/sources/`), and paranoid multi-venue LaTeX compilation (`openin_any=p`, `openout_any=p`, `--no-shell-escape`) scale across realistic paper sizes (20–120 citations, 5–30 experiment runs)? | End-to-end deterministic verification scales linearly with `< 250 ms` total wall-clock time at 120 citations / 30 runs; offloading raw primary-source snapshots to `literature/sources/` cuts `po-citation-auditor` ledger context size by `>= 65%`; and paranoid compilation produces zero-metadata-leak PDFs (`pdfinfo`) across all 3 venue classes (`acmart[sigplan]`, `cvpr2025[review]`, `iclr2025`). | Hypothesis is refuted if verification exceeds `2 s` at 120 citations, ledger offloading saves `< 30%` bytes/tokens, or paranoid mode breaks compilation or leaks `/Author`/`/Creator`/`/Producer` metadata on any venue. |
| **RQ4** | On seeded manuscripts containing **semantic** scientific flaws invisible to deterministic checks (claim-vs-abstract distortion, missing baseline ablation, undefined mathematical symbols, and prose deanonymization), does PaperOEGM's flat parallel fresh-context read-only critic architecture recover flaws missed by `po_tools.py` alone and respect read-only/token-budget bounds? | Dispatching the 5 read-only critics flat in parallel recovers `>= 80%` of planted semantic flaws missed by `po_tools.py` (lifting combined hybrid recall above either component alone) while maintaining `0` workspace mutations (`check-readonly`) and keeping per-critic outputs within `<= 1,500` tokens. | Hypothesis is refuted if fresh-context critics detect `< 50%` of planted semantic flaws, produce `> 50%` false positives on clean controls, violate read-only isolation, or fail to complete on live Antigravity runtime. |

---

## 2. Datasets, Workspaces & Evaluation Metrics

| Benchmark / Corpus | Scope & Construction | Primary Metrics | Secondary Metrics | Statistical Protocol |
| --- | --- | --- | --- | --- |
| **`PO-FaultBench` (`exp01`)** | 120 deterministic workspace fixtures (8 fault families × 10 positive cases + 40 hard negative controls: valid rounding, `0..1 -> %` scaling, `user_provided` Zotero `.bib`, `user_byo` attested data, valid LaTeX dimensions, commented `% \write18`) + 20 adversarial/semantic evasion cases (`exp01_evasion`) | Recall, Precision, F1, FPR (overall & per fault family) | Wall-clock latency (`ms`, `mean ± std` over `n=5` seeds) | Exact confusion matrix (`TP/FP/TN/FN`) + 5-seed timing `mean ± std` |
| **Packaging & Context Audit (`exp02`)** | Live repository artifacts (`paper-oegm`), synthetic monolithic concatenation baseline, legacy PaperOrchestra metrics (from archived git/design spec), and local EGM reference plugin (`~/.gemini/config/plugins/egm/`) | Per-stage byte/token reduction ratio, defect count (0 target), SHA-256 reproducibility rate | Build latency (`ms`, `n=5`), ZIP size (`KB`), `claude plugin validate` status | Exact counts + 5-run timing `mean ± std` |
| **Scalability & Multi-Venue Build (`exp03`)** | 4 synthetic workspace scales (`S`: 20 cites / 5 runs; `M`: 50 / 10; `L`: 80 / 20; `XL`: 120 / 30) + 3 venue builds (`acmart[sigplan,review,anonymous]`, `cvpr2025[review]`, `iclr2025`) | Total `po_tools.py` latency (`ms`), ledger vs. raw source size reduction (`%`), paranoid compile pass rate (`3/3`) | Per-subcommand scaling curve (`series.csv`), `pdfinfo` leak count (`0` target) | `n=5` timing repeats per scale (`mean ± std`) |
| **Hybrid Semantic Audit (`exp04`)** | Seeded realistic research paper draft (`manuscript/sections/*.md`, `references.bib`, `literature/sources/`, `metrics.json`) with 10 controlled defects (5 mechanical + 5 semantic/evasion) + clean control sections | Recall on mechanical vs. semantic defects (Deterministic-only vs. Critics-only vs. Hybrid) | Per-critic output tokens (`<= 1,500`), `check-readonly` mutation count (`0`), `Reviewer Status` completion rate | Exact per-defect detection table; sample-size limitation explicitly disclosed |

---

## 3. Baselines & Ablations

| System / Condition | What Is Included | Linked RQ |
| --- | --- | --- |
| **B0 — Compiler-Only Baseline** | Standard `pdflatex`/`bibtex` undefined ref/cite & missing graphics checks only (no `po_tools.py`, no fresh critics) | RQ1 |
| **B1 — Ablated Verifier (No Inline Provenance)** | `po_tools.py` citation + anonymity + archive scans with `<!-- run:id -->` numeric verification disabled | RQ1 |
| **B2 — Monolithic Single-Skill Baseline** | All 10 skills + 6 protocols + 5 standards concatenated into one monolithic `SKILL.md` loaded upfront | RQ2 |
| **B3 — Reference Multi-Harness Plugin (EGM)** | Locally installed Google EGM (`~/.gemini/config/plugins/egm/`) measured with identical file-size & packaging scripts [@google2026egm] | RQ2 |
| **B4 — Deterministic-Only (`po_tools.py` alone)** | `po_tools.py review-preflight` + `format-verify` without read-only semantic critics | RQ1, RQ4 |
| **Ours — PaperOEGM Full Hybrid** | 10 modular skills (`<= 12 KB`) + `po_tools.py` + 5 flat parallel read-only critics + paranoid TeX sandbox | RQ1–RQ4 |

---

## 4. Experiment & Ablation Matrix

| `run_id` Pattern | Script | Seeds (`n`) | Expected `metrics.json` Keys | Linked RQ |
| --- | --- | --- | --- | --- |
| `exp01_faultbench_s<seed>` | `experiments/run_exp01_faultbench.sh` | `42, 43, 44, 45, 46` (`n=5`) | `full_recall`, `full_precision`, `full_f1`, `full_fpr`, `compiler_only_recall`, `no_inline_prov_recall`, `evasion_det_recall`, `mean_latency_ms`, `per_family_*` | RQ1 |
| `exp02_packaging_s<seed>` | `experiments/run_exp02_packaging.sh` | `42, 43, 44, 45, 46` (`n=5`) | `max_skill_bytes`, `median_skill_bytes`, `monolithic_bytes`, `context_reduction_pct`, `repro_pass_rate`, `pack_latency_ms`, `egm_max_skill_bytes`, `defect_count` | RQ2 |
| `exp03_scalability_s<seed>` | `experiments/run_exp03_scalability.sh` | `42, 43, 44, 45, 46` (`n=5`) | `xl_total_ms`, `ledger_bytes_xl`, `sources_bytes_xl`, `context_offload_pct`, `venues_compiled_ok`, `pdfinfo_leaks` (+ `series.csv`) | RQ3 |
| `exp04_hybrid_critics_s42` | `experiments/run_exp04_hybrid.sh` + live read-only critic dispatch | `42` (seeded controlled audit) | `det_mech_recall`, `det_sem_recall`, `critic_sem_recall`, `hybrid_total_recall`, `readonly_mutations`, `max_critic_tokens` | RQ4 |

---

## 5. Planned Result Tables & Figures

* **Table 1 (`tab_faultbench`):** Per-family detection recall, precision, F1, and FPR on `PO-FaultBench` (8 families, 120 cases) + adversarial evasion recall comparing B0, B1, and PaperOEGM (`exp01_*`).
* **Table 2 (`tab_packaging`):** Multi-harness skill size, loader headroom, packaging defect count, and deterministic build comparison across Monolithic (B2), EGM (B3), and PaperOEGM (`exp02_*`).
* **Table 3 (`tab_hybrid`):** Defect-level ablation across 5 mechanical + 5 semantic flaws comparing Deterministic-Only (B4), Fresh Critics-Only, and PaperOEGM Hybrid (`exp04_*`).
* **Figure 1 (`fig_architecture`):** Clean vector architecture diagram of PaperOEGM's 10-skill progressive-disclosure graph, `po_tools.py` backbone, and flat 1-level read-only critic topology (matching ACM `sigplan` two-column width).
* **Figure 2 (`fig_faultbench_recall`):** Grouped horizontal bar chart comparing Recall across the 8 `PO-FaultBench` fault families + Adversarial Evasion for Compiler-Only (B0), Ablated (B1), and PaperOEGM Full (`exp01_*` canonical `metrics.json`).
* **Figure 3 (`fig_scalability`):** Two-panel scaling plot from `exp03_*` `series.csv` + `metrics.json`: (a) `po_tools.py` subcommand latency vs. workspace scale (`20 -> 120` citations, `mean ± std` error bars); (b) compact `citation_ledger.json` vs. offloaded `literature/sources/` context size across scales.
* **Figure 4 (`fig_skill_footprint`):** Per-skill whole-file size (`bytes`) across all 10 PaperOEGM skills vs. PaperOEGM `12 KB` budget, Antigravity `24 KB` ceiling, EGM max skill (`egm-bootstrap`), and Monolithic baseline (`exp02_*` canonical `metrics.json`).

---

## 6. Negative-Result, Honest Limitations & Risk Policy

* **Expected negative / boundary results to report explicitly:**
  * `exp01_evasion` is *expected* to show low deterministic recall on integer-only falsification, `\csname`-obfuscated LaTeX macros, and semantic citation distortion—establishing an honest empirical boundary rather than claiming deterministic scripts solve all attacks.
  * `exp04` runs on a single controlled seeded manuscript on live Antigravity (not a 200-paper multi-model benchmark due to zero-external-API-key constraints); we will state this scope boundary explicitly in `06_limitations.md` and avoid generalizing beyond the tested harness/model.
  * Codex live end-to-end execution remains structurally verified (not live-executed) unless run interactively on Codex CLI; all claims will respect the per-harness verification status in `docs/harnesses.md`.
* **No synthetic leakage:** All `--dry-run` checks isolate strictly into `experiments/dry_run/` with `is_synthetic: true`; only canonical non-synthetic runs registered in `experiments/provenance_index.json` may feed Tables 1–3 and Figures 2–4.
