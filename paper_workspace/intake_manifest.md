# PaperOEGM Adaptive Intake Manifest

* **Paper Workspace:** `./paper_workspace/` (gitignored in `.gitignore`)
* **Target Venue:** Agent Skills Workshop (ACM CAIS 2027) — Full Paper (`9` pages + references, `\documentclass[sigplan,review,anonymous]{acmart}`, `double-blind`)
* **Intake Date (UTC):** `2026-11-27`

## Discovered Project Materials & Proposed Roles

| Path / Directory | Count | Proposed Paper Role |
| --- | --- | --- |
| `plugin.json`, `.claude-plugin/*.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | 5 files | Multi-harness manifest architecture & cross-host parity artifact |
| `skills/po-*/{SKILL.md, agents/openai.yaml, assets/icon.svg, references/*}` | 36 files (10 skills) | Primary system artifact: modular `SKILL.md` composition, size ceilings, and stage contracts |
| `agents/po-*.md`, `.claude-plugin/agents/po-*.md` | 10 files (5 critics) | Flat 1-level fresh-context read-only critic architecture & Claude tool-allowlist adapters |
| `resources/{execution_instructions.md, protocols/*.md, review_standards/*.md}` | 13 files | Cross-stage provenance contracts, write policies, and scientific review rubrics |
| `resources/scripts/po_tools.py` | 1 file | Zero-dependency Python 3.10+ stdlib deterministic verifier (`state-sync`, `check-readonly`, `review-preflight`, `format-verify`) |
| `resources/templates/{cvpr2025,iclr2025}/` | 12 files | Bundled unmodified upstream venue starter templates & double-blind wrappers |
| `scripts/pack_plugin.py` | 1 file | Deterministic multi-harness packager (`antigravity`, `claude`, `openai`) with supply-chain checks |
| `tests/unit/test_*.py` | 7 modules (22 tests) | Offline invariant, packaging, link-integrity, and `po_tools.py` unit test suite |
| `docs/{harnesses,claude,codex,privacy}.md`, `docs/designs/paper-oegm.md`, `README.md`, `TESTING.md` | 7 docs | Architectural design record, cross-harness verification matrix, and privacy/threat model |

## Excluded Paths (Secret & Hygiene Denylist)

* `.git/` — Git internals (excluded from intake reads)
* `.env*`, `credentials.json`, `secrets.*`, `*.pem`, `*.key` — Credential denylist (none present in repository)
* `.pytest_cache/`, `__pycache__/`, `.DS_Store`, `dist/`, `paper_workspace/` — Ignored local caches and generated workspace outputs
* `.ipynb` output cells — Excluded by default (none present in repository)

## Existing Experiment Runs / BYO Data

* None yet (`experiments/provenance_index.json` has `0` registered runs). Real quantitative experiments will be designed in Stage 2 (`po-exp-design`) and executed in Stage 3 (`po-exp-code`).
