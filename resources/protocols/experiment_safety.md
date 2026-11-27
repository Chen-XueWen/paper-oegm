# Experiment Safety & Provenance Protocol

This protocol governs `po-exp-code` (Stage 2) and experiment run auditing in downstream stages.

## Bash Runner Safety Contract

Every generated `experiments/run_<exp_id>.sh` script must satisfy:

1. **Strict shell header & quoted paths:** Begin with `#!/usr/bin/env bash` and `set -euo pipefail`. Double-quote all variable expansions (`"$VAR"`).
2. **Environment separation:** Source `experiments/env.sh` (user-edited local paths, Python binary, `CUDA_VISIBLE_DEVICES`) and pair with `experiments/check_env.sh` (fast preflight checking datasets, interpreter, and GPU visibility).
3. **Forbidden operations:** Never emit `sudo`, `rm -rf` on user paths, `curl | sh`, silent `pip install`, enabled telemetry (`WANDB_MODE=offline` or disabled by default), or autonomous long GPU launches.
4. **Edit boundary:** Write by default only inside the user-approved `experiments/` directory. If an existing file under `src/` must change to support an ablation or metric export, show the proposed diff and require explicit per-file user approval before editing.
5. **Startup manifest & `EXIT` trap:** Immediately write `experiments/runs/<run_id>/run_manifest.json` with `"status": "running"`, register `trap finalize EXIT` so `finished_at`, `exit_code`, and final `status` (`"completed"` or `"failed"`) are recorded even on crash or signal, and keep offline runner writes strictly inside `runs/<run_id>/` (never concurrently mutating `experiments/provenance_index.json`).
6. **Non-git resilience & secret redaction:** If the project is not a git repository, emit `"git_commit": "none"` and `"git_dirty": null` without aborting under `set -euo pipefail`. Redact sensitive CLI flags (`--token`, `--api-key`, `--password`, `KEY=VALUE`) and absolute `$HOME` prefixes when writing `cmd` in `run_manifest.json`.
7. **Isolated `--dry-run` smoke check:** Every runner supports `--dry-run` running offline with tiny mock inputs (`< 60s` timeout), writing strictly to `experiments/dry_run/<run_id>/` with `"is_synthetic": true` in both `run_manifest.json` and `metrics.json`.

## Canonical Artifact Schemas

### `experiments/runs/<run_id>/run_manifest.json`

Emitted using shell / Python stdlib only:

```json
{
  "run_id": "exp01_baseline_s42",
  "status": "completed",
  "started_at": "2026-11-27T00:00:00Z",
  "finished_at": "2026-11-27T01:15:00Z",
  "exit_code": 0,
  "is_synthetic": false,
  "git_commit": "a1b2c3d",
  "git_dirty": false,
  "cmd": "python3 train.py --seed 42 --epochs 100",
  "seeds": [42],
  "hardware": {
    "hostname_hash": "sha256:...",
    "gpu": "NVIDIA A100 80GB",
    "cpu_count": 16
  }
}
```

### `experiments/runs/<run_id>/metrics.json` & Optional `series.csv`

* Write `metrics.json.tmp` and rename atomically to `metrics.json` (`< 10 KB`):

```json
{
  "run_id": "exp01_baseline_s42",
  "is_synthetic": false,
  "metrics": {
    "top1_acc": {"mean": 84.2, "std": 0.3, "n": 3},
    "latency_ms": 12.4
  }
}
```

* Optional `series.csv` stores downsampled training/convergence curves (`<= 500` rows, header `step,<metric_1>,...`).

### `experiments/provenance_index.json`

Maintained by `po-start` (and `po-outline` on direct entry/canonicalization):

```json
{
  "schema_version": "1.0",
  "runs": {
    "exp01_baseline_s42": {
      "origin": "po_exp_code",
      "status": "canonical",
      "source_path": "experiments/runs/exp01_baseline_s42/metrics.json",
      "content_hash": "sha256:...",
      "is_synthetic": false,
      "user_attested_non_synthetic": false
    }
  }
}
```

## Audit Severity Policy

* `is_synthetic: true` or any reference to `experiments/dry_run/` in plots/manuscript -> **Blocker**.
* `git_dirty: true` on a canonical `po_exp_code` run -> **Major** (waivable with a recorded diff/attestation in `resolution_report.md`).
* `origin: "user_byo"` with `user_attested_non_synthetic: true` waives `git_commit` and seed checks while keeping numeric-accuracy auditing active.
