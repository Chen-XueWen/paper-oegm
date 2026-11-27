# Workspace Contract & State Protocol

## Workspace Directory Override

Default paper workspace path is `./paper_workspace/`. Users may override it via a prompt line or a project instructions-file marker:

```text
PaperOEGM artifact directory: <path>
```

Relative paths resolve against the current working directory. If an instructions-file override resolves outside the working directory after following symbolic links, ask the user to confirm before creating the directory or writing inside it (fall back to `./paper_workspace/` and explain why if declined or headless).

## Canonical Workspace Tree

```text
<paper_workspace>/
├── paper_state.json                 # Sole authoritative state: project_title, venue, submission_mode, environment, stages
├── STATUS.md                        # Auto-generated read-only dashboard regenerated from paper_state.json
├── intake_manifest.md               # User-approved inventory of project files, roles, and excluded secrets
├── plan/
│   ├── experiment_design.md         # Stage 1: RQs, hypotheses, baselines, datasets, ablations, seeds, metrics
│   └── outline.md                   # Stage 3: Section plan (mirrors venue/page budget from paper_state.json), claim->run_id & figure IDs
├── experiments/
│   ├── env.sh / check_env.sh / run_<exp_id>.sh
│   ├── provenance_index.json        # Run registry (origin: po_exp_code | user_byo)
│   ├── dry_run/<run_id>/            # Synthetic smoke tests (blocked from paper drafting)
│   └── runs/<run_id>/{run_manifest.json, metrics.json, series.csv, stdout.log, stderr.log}
├── literature/
│   ├── references.bib               # Verified or user-provided BibTeX entries
│   ├── citation_ledger.json         # Compact key -> status, source pointer, claim summary
│   ├── sources/<citekey>.{json,bib,txt}
│   └── literature_review.md
├── visuals/
│   ├── scripts/fig_<id>.{py,tex,mmd,dot}
│   ├── assets/fig_<id>.{pdf,png,svg}
│   └── manifest.md
├── manuscript/
│   ├── manuscript.yaml              # Section file order & camera-ready authors only
│   ├── sections/*.md                # Per-section Markdown with inline <!-- run:<run_id> --> provenance comments
│   └── snapshots/                   # Backups written before po-resolve edits
├── reviews/round_<N>/{review_report.md, resolution_report.md, manual_review_prompts.md}
└── submission/{main.tex, sections/*.tex, references.bib, figures/, <venue>.*, compile.sh, build/, main.pdf, build_report.md}
```

## `paper_state.json` & `STATUS.md` Rules

* `paper_state.json` is the sole authoritative store for `project_title`, `venue` (`name`, `template_source`, `template_year`, `submission_mode`, `page_limit_main`, `citation_macro_style`), `environment` (`hash_tool`, `pandoc`, `tex_compiler`, `bibtex_tool`, `pdf_rasterizer`, `python_plotting`), and `stages`.
* `STATUS.md` is regenerated from `paper_state.json` with `<!-- AUTO-GENERATED FROM paper_state.json — DO NOT EDIT SETTINGS HERE -->`.
* **Entry & Exit Sync:** On every stage entry and exit, run `python3 <plugin_root>/resources/scripts/po_tools.py state-sync --workspace <ws>` (`--check-only` on entry; `--stage <key> --status <status> --inputs ... --outputs ...` on exit). If `python3` is absent, probe `sha256sum`, `shasum -a 256`, or fall back to `mtime_size_degraded` and write `paper_state.json.tmp` -> `paper_state.json` atomically.
* **Malformed JSON:** If `state-sync` exits `2` due to manual JSON edits, report the exact parse error line/column and offer repair before continuing.
* **Multi-Phase & Revision Keying:** Key literature passes separately (`po-literature:early`, `po-literature:late`) so late Related Work additions do not invalidate completed GPU runs. Targeted edits in `po-resolve` advance `po-draft`'s recorded output hashes so `po-review` and `po-format` become `stale` without invalidating `po-draft`.

## Adaptive Intake Secret Denylist & BYO Registration

* Before reading full user files, present `intake_manifest.md` for approval. Exclude by default: dotfiles (`.env*`, `.ssh/`, `.aws/`), `.gitignore` matches, `credentials.json`, `secrets.*`, `*.pem`, `*.key`, and raw `.ipynb` output cells unless explicitly opted in.
* **Bring-Your-Own (BYO) Registration (`po-start` or direct `po-outline` entry):**
  * Register confirmed BYO result files (CSV/JSON/notebooks) in `experiments/provenance_index.json` with `origin: "user_byo"`, `status: "canonical"`, `source_path`, `content_hash`, `is_synthetic: false`, and `user_attested_non_synthetic: true` (after explicit researcher confirmation).
  * Import confirmed user `.bib` files into `literature/references.bib` and seed `literature/citation_ledger.json` with `verification_status: "user_provided"`.
