# Testing & Verification Guide (`paper-oegm`)

## Per-Harness Verification Status (v0.1)

| Host Harness | Verification Status | Notes |
| --- | --- | --- |
| **Antigravity (CLI / App)** | Live-verified upon implementation | Runtime-enforced read-only plugin subagents; installed locally into `~/.gemini/config/plugins/paper-oegm/` and tested end-to-end. |
| **Claude Code / Cowork** | Packaged and structurally verified via offline `pytest`; live end-to-end verification pending | Manifest parity, read-only adapter tool allowlists (`[Read, Grep, Glob]`, `model: inherit`, `omitClaudeMd: true`), icon dimensions, and deterministic ZIP packaging tested offline. |
| **Codex / ChatGPT Work** | Packaged and structurally verified via offline `pytest`; live end-to-end verification pending | `.codex-plugin/plugin.json`, `openai.yaml` bounds (25–64 chars), two-color SVG palette parity, `po_tools.py check-readonly`, and deterministic ZIP packaging tested offline. |

## 1. Offline Unit & Packaging Suite

Requires Python 3.10+ with dev test dependencies (`pytest`, `pyyaml` — zero runtime dependencies for end users):

```bash
python3 -m pytest tests/unit -v
```

Covers all 7 modules:
* `tests/unit/test_frontmatter.py`
* `tests/unit/test_skill_load_limits.py`
* `tests/unit/test_harnesses.py`
* `tests/unit/test_packaging.py`
* `tests/unit/test_link_integrity.py`
* `tests/unit/test_domain_invariants.py`
* `tests/unit/test_po_tools.py`

## 2. Deterministic Runtime Build Verification

```bash
python3 scripts/pack_plugin.py --target all --output /tmp/paper-oegm-dist
```

Verifies byte-reproducible ZIP archives (`paper-oegm-antigravity`, `paper-oegm-claude`, `paper-oegm-openai`) with zero dev, test, or design-doc files included.

## 3. Synthetic End-to-End Workspace Fixture

To validate the full research-to-paper lifecycle locally:

1. Initialize a temporary workspace through `po-start` -> `po-exp-design` -> `po-literature` (seeding one `verified_source` with a saved `literature/sources/` snapshot and one `unverified_needs_human_check` entry).
2. Run `po-exp-code` (`--dry-run` writing `is_synthetic: true` to `experiments/dry_run/` plus a minimal non-synthetic Python experiment writing `experiments/runs/<run_id>/metrics.json`).
3. Run `po-outline` -> `po-visuals` -> `po-draft` -> `po-review` (confirming `po_tools.py review-preflight` blocks synthetic and unverified entries and flat parallel read-only dispatch writes the 4-state `## Reviewer Status` table).
4. Resolve blockers in `po-resolve`, then run `po-format` to confirm `po_tools.py format-verify` parity, local paranoid TeX compilation (`openin_any=p openout_any=p --no-shell-escape`), post-compile visual layout audit, and Overleaf `PDF_COMPILATION: NOT_RUN` fallback.
