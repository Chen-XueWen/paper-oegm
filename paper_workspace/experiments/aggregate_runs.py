#!/usr/bin/env python3
"""Deterministically aggregate multi-seed canonical experiment runs into summary runs.

Reads strictly from non-synthetic canonical metrics.json files under experiments/runs/
(never dry_run/) and writes <exp_prefix>_agg/{run_manifest.json,metrics.json} plus
experiments/provenance_index.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mean_std(vals: list[float]) -> dict[str, Any]:
    n = len(vals)
    m = sum(vals) / n
    s = statistics.stdev(vals) if n > 1 else 0.0
    return {"mean": round(m, 2), "std": round(s, 2), "n": n}


def aggregate_group(runs_dir: Path, run_ids: list[str], agg_id: str, repo_root: Path) -> dict[str, Any]:
    records = []
    for rid in run_ids:
        mj = json.loads((runs_dir / rid / "metrics.json").read_text(encoding="utf-8"))
        rm = json.loads((runs_dir / rid / "run_manifest.json").read_text(encoding="utf-8"))
        if mj.get("is_synthetic") is True or rm.get("is_synthetic") is True:
            raise RuntimeError(f"Refusing to aggregate synthetic run {rid}")
        records.append(mj["metrics"])

    # Aggregate numeric keys
    all_keys = list(records[0].keys())
    agg_metrics: dict[str, Any] = {}
    for k in all_keys:
        vals = [r.get(k) for r in records]
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
            fvals = [float(v) for v in vals]
            agg_metrics[k] = mean_std(fvals)
        elif all(isinstance(v, dict) for v in vals):
            sub: dict[str, Any] = {}
            for sk in vals[0]:
                svals = [d.get(sk) for d in vals]
                if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in svals):
                    sub[sk] = mean_std([float(v) for v in svals])
                elif all(isinstance(v, bool) for v in svals):
                    sub[sk] = round(sum(1 for v in svals if v) / len(svals) * 100.0, 2)
            if sub:
                agg_metrics[k] = sub

    # Also aggregate series.csv if present on all runs (e.g., exp03)
    csv_paths = [runs_dir / rid / "series.csv" for rid in run_ids]
    out_dir = runs_dir / agg_id
    out_dir.mkdir(parents=True, exist_ok=True)
    if all(p.is_file() for p in csv_paths):
        by_scale: dict[str, list[dict[str, str]]] = {}
        order: list[str] = []
        for cp in csv_paths:
            with cp.open(encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    sc = row["scale"]
                    if sc not in by_scale:
                        by_scale[sc] = []
                        order.append(sc)
                    by_scale[sc].append(row)
        agg_rows = []
        num_cols = [
            "state_sync_ms",
            "review_preflight_ms",
            "format_verify_ms",
            "check_readonly_ms",
            "total_ms",
            "ledger_bytes",
            "sources_bytes",
            "offload_pct",
        ]
        for sc in order:
            rs = by_scale[sc]
            out_row: dict[str, Any] = {
                "step": int(rs[0]["step"]),
                "scale": sc,
                "citations": int(rs[0]["citations"]),
                "runs": int(rs[0]["runs"]),
            }
            for col in num_cols:
                vals = [float(r[col]) for r in rs]
                ms = mean_std(vals)
                out_row[f"{col}_mean"] = ms["mean"]
                out_row[f"{col}_std"] = ms["std"]
            agg_rows.append(out_row)
        with (out_dir / "series.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(agg_rows[0].keys()))
            w.writeheader()
            w.writerows(agg_rows)

    git_commit = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    git_dirty = bool(subprocess.check_output(["git", "-C", str(repo_root), "status", "--porcelain"], text=True).strip())
    now = utc_now()
    manifest = {
        "run_id": agg_id,
        "status": "completed",
        "started_at": now,
        "finished_at": now,
        "exit_code": 0,
        "is_synthetic": False,
        "git_commit": git_commit,
        "git_dirty": git_dirty,
        "cmd": f"aggregate_runs.py --agg-id {agg_id} --sources {','.join(run_ids)}",
        "source_runs": run_ids,
        "seeds": [int(rid.split("_s")[-1]) for rid in run_ids if "_s" in rid],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    payload = {"run_id": agg_id, "is_synthetic": False, "source_runs": run_ids, "metrics": agg_metrics}
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    return payload


def build_provenance_index(ws: Path) -> dict[str, Any]:
    runs_dir = ws / "experiments/runs"
    runs_map: dict[str, Any] = {}
    for run_path in sorted(runs_dir.iterdir()):
        if not run_path.is_dir():
            continue
        mj_path = run_path / "metrics.json"
        rm_path = run_path / "run_manifest.json"
        if not (mj_path.is_file() and rm_path.is_file()):
            continue
        mj = json.loads(mj_path.read_text(encoding="utf-8"))
        rm = json.loads(rm_path.read_text(encoding="utf-8"))
        if mj.get("is_synthetic") is True or rm.get("is_synthetic") is True:
            continue
        rel = mj_path.relative_to(ws).as_posix()
        runs_map[run_path.name] = {
            "origin": "po_exp_code",
            "status": "canonical",
            "source_path": rel,
            "content_hash": sha256_file(mj_path),
            "is_synthetic": False,
            "user_attested_non_synthetic": False,
        }
    index = {"schema_version": "1.0", "runs": runs_map}
    out = ws / "experiments/provenance_index.json"
    tmp = out.with_name(".provenance_index.json.tmp")
    tmp.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    return index


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    args = ap.parse_args()

    ws = args.workspace.resolve()
    runs_dir = ws / "experiments/runs"

    groups = [
        ("exp01_faultbench_agg", [f"exp01_faultbench_s{s}" for s in range(42, 47)]),
        ("exp02_packaging_agg", [f"exp02_packaging_s{s}" for s in range(42, 47)]),
        ("exp03_scalability_agg", [f"exp03_scalability_s{s}" for s in range(42, 47)]),
        ("exp04_hybrid_agg", [f"exp04_hybrid_s{s}" for s in range(42, 45)]),
    ]
    for agg_id, members in groups:
        if all((runs_dir / m / "metrics.json").is_file() for m in members):
            aggregate_group(runs_dir, members, agg_id, args.repo_root.resolve())
            sz = (runs_dir / agg_id / "metrics.json").stat().st_size
            print(f"[aggregate] Built {agg_id} ({len(members)} runs, metrics.json={sz} bytes)")

    idx = build_provenance_index(ws)
    print(f"[aggregate] Registered {len(idx['runs'])} canonical runs in experiments/provenance_index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
