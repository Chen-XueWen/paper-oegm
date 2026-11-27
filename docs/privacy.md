# Privacy & Local Execution Policy

PaperOEGM (`paper-oegm`) is a local-first research-to-paper plugin with zero external plugin backend servers, zero telemetry hooks, and zero required third-party API keys.

## Data Handling & Network Access

* **Local workspace execution:** All paper artifacts (`paper_state.json`, `plan/`, `experiments/`, `literature/`, `visuals/`, `manuscript/`, `reviews/`, `submission/`) are written locally inside `<paper_workspace>/` (default `./paper_workspace/`).
* **No external plugin servers or hooks:** All manifests declare zero `hooks`, `mcpServers`, `mcp`, or `apps`. Installing `paper-oegm` runs no background services or network callbacks.
* **Host-mediated web lookup only:** Literature search (`po-literature`) and user-confirmed official venue template fetching (`po-start`, `po-format`) use only the host coding harness's built-in web tools and never transmit repository secrets. Read-only critics (`agents/po-*.md`) never fetch external URLs.

## Secret Hygiene & Untrusted Content Isolation

* **Adaptive intake denylist:** `po-start` and `po-outline` exclude dotfiles (`.env*`, `.ssh/`, `.aws/`), `.gitignore` matches, `credentials.json`, `secrets.*`, `*.pem`, `*.key`, and raw `.ipynb` cell outputs by default, presenting `intake_manifest.md` for user approval before full file reads.
* **Experiment runner redaction:** Generated `run_*.sh` scripts disable experiment telemetry (`WANDB_MODE=offline`) by default and redact sensitive CLI flags (`--token`, `--api-key`, `--password`, `KEY=VALUE`) and `$HOME` prefixes before writing `run_manifest.json`.
* **Untrusted content:** External web pages, paper PDFs, notebooks, fetched venue templates, and critic responses are treated strictly as untrusted data, never as executable commands.
* **Double-blind hygiene:** In `double-blind` mode, `po-visuals` strips figure PDF metadata and `po-format` injects blank PDF author/creator/producer metadata, scans `.tex` text and `%` comments for local paths/author leaks, and compiles with `openin_any=p`, `openout_any=p`, and `--no-shell-escape`.
