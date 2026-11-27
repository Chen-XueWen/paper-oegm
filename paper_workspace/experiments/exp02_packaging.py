#!/usr/bin/env python3
"""Experiment 2: Multi-Harness Packaging, Context Footprint & Build Determinism.

Measures live local artifacts:
  - PaperOEGM (repo_root): 10 skills, 5 critics, 6 protocols, 5 standards, deterministic pack_plugin.py
  - B2 (Monolithic Single-Skill): concatenated all skills + protocols + standards + execution_instructions
  - B3 (Local Google EGM): ~/.gemini/config/plugins/egm (RQ2 packaging footprint comparison only)
  - Live `claude plugin validate .` CLI check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def audit_paperoegm_defects(repo_root: Path) -> int:
    """Specification-compliance defect checklist inspired by Zhang et al. (2026)."""
    defects = 0
    # 1. Check 5 JSON manifests parse cleanly
    manifests = [
        repo_root / "plugin.json",
        repo_root / ".claude-plugin/plugin.json",
        repo_root / ".claude-plugin/marketplace.json",
        repo_root / ".codex-plugin/plugin.json",
        repo_root / ".agents/plugins/marketplace.json",
    ]
    for mp in manifests:
        try:
            data = json.loads(mp.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                defects += 1
        except Exception:
            defects += 1

    # 2. Check every SKILL.md frontmatter, <=250 lines, <=12000 bytes, openai.yaml & icon.svg
    for sk_dir in sorted((repo_root / "skills").glob("po-*")):
        sk = sk_dir / "SKILL.md"
        if not sk.is_file():
            defects += 1
            continue
        raw = sk.read_bytes()
        text = raw.decode("utf-8")
        fm = parse_frontmatter(text)
        if not fm.get("name") or not fm.get("description") or fm.get("disable-model-invocation") != "true":
            defects += 1
        if len(raw) > 12000 or len(text.splitlines()) > 250:
            defects += 1
        if not (sk_dir / "agents/openai.yaml").is_file() or not (sk_dir / "assets/icon.svg").is_file():
            defects += 1

    # 3. Check 5 critic personas <= 6000 bytes and Claude read-only adapters exist
    for ag in sorted((repo_root / "agents").glob("po-*.md")):
        if len(ag.read_bytes()) > 6000:
            defects += 1
        adapter = repo_root / ".claude-plugin/agents" / ag.name
        if not adapter.is_file():
            defects += 1
    return defects


def run_packaging_audit(repo_root: Path, egm_dir: Path | None, dry_run: bool) -> dict[str, Any]:
    skill_files = sorted((repo_root / "skills").glob("po-*/SKILL.md"))
    skill_bytes: dict[str, int] = {}
    skill_lines: dict[str, int] = {}
    frontmatter_bytes = 0
    for sf in skill_files:
        name = sf.parent.name
        raw = sf.read_bytes()
        text = raw.decode("utf-8")
        skill_bytes[name] = len(raw)
        skill_lines[name] = len(text.splitlines())
        m = re.match(r"^---\n.*?\n---\n", text, flags=re.DOTALL)
        if m:
            frontmatter_bytes += len(m.group(0).encode("utf-8"))

    agent_files = sorted((repo_root / "agents").glob("po-*.md"))
    agent_bytes = {af.stem: len(af.read_bytes()) for af in agent_files}

    exec_inst = repo_root / "resources/execution_instructions.md"
    protocol_files = sorted((repo_root / "resources/protocols").glob("*.md"))
    standard_files = sorted((repo_root / "resources/review_standards").glob("*.md"))

    exec_bytes = len(exec_inst.read_bytes()) if exec_inst.is_file() else 0
    protocols_total = sum(len(p.read_bytes()) for p in protocol_files)
    standards_total = sum(len(s.read_bytes()) for s in standard_files)

    # B2 Monolithic single-skill baseline = all 10 SKILL.md + execution_instructions + all protocols + all standards
    monolithic_bytes = sum(skill_bytes.values()) + exec_bytes + protocols_total + standards_total

    # Per-stage active context load: SKILL.md + execution_instructions + directly referenced protocols
    stage_active_bytes: dict[str, int] = {}
    for sf in skill_files:
        txt = sf.read_text(encoding="utf-8")
        active = len(sf.read_bytes()) + exec_bytes
        for pf in protocol_files:
            if pf.name in txt:
                active += len(pf.read_bytes())
        stage_active_bytes[sf.parent.name] = active

    median_skill = int(statistics.median(skill_bytes.values()))
    max_skill = max(skill_bytes.values())
    min_skill = min(skill_bytes.values())
    median_active = int(statistics.median(stage_active_bytes.values()))
    max_active = max(stage_active_bytes.values())

    # Reduction comparing single SKILL.md load vs monolithic, and full per-stage active load vs monolithic
    skill_only_reduction = round((1.0 - (median_skill / monolithic_bytes)) * 100.0, 2)
    context_reduction_pct = round((1.0 - (median_active / monolithic_bytes)) * 100.0, 2)
    startup_index_reduction_pct = round((1.0 - (frontmatter_bytes / monolithic_bytes)) * 100.0, 2)

    # B3 Local Google EGM measurement (RQ2 packaging only)
    egm_max_skill = None
    egm_median_skill = None
    egm_skill_count = 0
    egm_agent_max = None
    if egm_dir and egm_dir.is_dir():
        egm_skills = sorted((egm_dir / "skills").glob("*/SKILL.md"))
        if egm_skills:
            sizes = [len(p.read_bytes()) for p in egm_skills]
            egm_max_skill = max(sizes)
            egm_median_skill = int(statistics.median(sizes))
            egm_skill_count = len(sizes)
        egm_agents = sorted((egm_dir / "agents").glob("*.md"))
        if egm_agents:
            egm_agent_max = max(len(p.read_bytes()) for p in egm_agents)

    # Deterministic build SHA-256 parity across 2 consecutive builds per run
    pack_script = repo_root / "scripts/pack_plugin.py"
    build_repeats = 1 if dry_run else 2
    targets = ("antigravity", "claude", "openai")
    hashes_by_target: dict[str, list[str]] = {t: [] for t in targets}
    zip_sizes_kb: dict[str, float] = {}
    build_latencies: list[float] = []

    with tempfile.TemporaryDirectory(prefix="po_pack_exp02_") as tmp:
        for b_idx in range(build_repeats):
            out_dir = Path(tmp) / f"build_{b_idx}"
            t0 = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, str(pack_script), "--target", "all", "--output", str(out_dir)],
                capture_output=True,
                text=True,
                check=True,
            )
            dt_ms = (time.perf_counter() - t0) * 1000.0
            build_latencies.append(dt_ms)
            for t in targets:
                zips = sorted(out_dir.glob(f"*{t}*.zip"))
                if zips:
                    hashes_by_target[t].append(sha256_file(zips[0]))
                    zip_sizes_kb[t] = round(zips[0].stat().st_size / 1024.0, 2)

    repro_matches = 0
    for t in targets:
        if hashes_by_target[t] and len(set(hashes_by_target[t])) == 1:
            repro_matches += 1
    repro_pass_rate = round((repro_matches / len(targets)) * 100.0, 2)

    # Live claude plugin validate check
    claude_validate_ok = None
    claude_bin = shutil.which("claude")
    if claude_bin and not dry_run:
        cproc = subprocess.run(
            [claude_bin, "plugin", "validate", str(repo_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        combined = (cproc.stdout + "\n" + cproc.stderr).lower()
        claude_validate_ok = 1 if (cproc.returncode == 0 and "warning" not in combined and "error" not in combined) else 0
    elif dry_run:
        claude_validate_ok = 1

    defect_count = audit_paperoegm_defects(repo_root)

    metrics: dict[str, Any] = {
        "skill_count": len(skill_bytes),
        "agent_count": len(agent_bytes),
        "min_skill_bytes": min_skill,
        "median_skill_bytes": median_skill,
        "max_skill_bytes": max_skill,
        "max_skill_lines": max(skill_lines.values()),
        "max_agent_bytes": max(agent_bytes.values()),
        "frontmatter_index_bytes": frontmatter_bytes,
        "median_active_stage_bytes": median_active,
        "max_active_stage_bytes": max_active,
        "monolithic_bytes": monolithic_bytes,
        "skill_only_reduction_pct": skill_only_reduction,
        "context_reduction_pct": context_reduction_pct,
        "startup_index_reduction_pct": startup_index_reduction_pct,
        "headroom_vs_12kb_pct": round((1.0 - max_skill / 12000.0) * 100.0, 2),
        "headroom_vs_24kb_pct": round((1.0 - max_skill / 24000.0) * 100.0, 2),
        "egm_skill_count": egm_skill_count,
        "egm_median_skill_bytes": egm_median_skill,
        "egm_max_skill_bytes": egm_max_skill,
        "egm_max_agent_bytes": egm_agent_max,
        "defect_count": defect_count,
        "repro_pass_rate": repro_pass_rate,
        "pack_latency_ms": round(sum(build_latencies) / max(1, len(build_latencies)), 2),
        "zip_antigravity_kb": zip_sizes_kb.get("antigravity"),
        "zip_claude_kb": zip_sizes_kb.get("claude"),
        "zip_openai_kb": zip_sizes_kb.get("openai"),
        "claude_validate_ok": claude_validate_ok,
        "per_skill_bytes": skill_bytes,
        "per_stage_active_bytes": stage_active_bytes,
    }
    return metrics


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--egm-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    metrics = run_packaging_audit(args.repo_root.resolve(), args.egm_dir, args.dry_run)
    payload = {"run_id": args.run_id, "is_synthetic": bool(args.dry_run), "metrics": metrics}
    tmp = args.out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, args.out_dir / "metrics.json")
    print(
        f"[exp02] Wrote {args.out_dir / 'metrics.json'} "
        f"(max_skill={metrics['max_skill_bytes']}B, mono={metrics['monolithic_bytes']}B, "
        f"ctx_red={metrics['context_reduction_pct']}%, repro={metrics['repro_pass_rate']}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
