#!/usr/bin/env python3
"""Experiment 3: Scalability, Context Offloading & Multi-Venue Paranoid LaTeX Compilation.

Measures:
  1. Real CLI latency of all 4 po_tools.py subcommands across 4 scales (S/M/L/XL: 20->120 citations, 5->30 runs).
  2. Context size savings from compact citation_ledger.json vs. offloaded literature/sources/*.json.
  3. Paranoid LaTeX compilation (openin_any=p, openout_any=p, --no-shell-escape) across 3 venue classes
     (acmart[sigplan,review,anonymous], cvpr2025[review], iclr2025) + pdfinfo anonymity leak check.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


SCALES_FULL = [
    ("S", 20, 5),
    ("M", 50, 10),
    ("L", 80, 20),
    ("XL", 120, 30),
]

SCALES_DRY = [
    ("S", 10, 3),
    ("M", 20, 5),
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, indent=2) + "\n")


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def build_scaled_workspace(ws: Path, n_cites: int, n_runs: int, seed: int) -> tuple[int, int]:
    """Create a realistic clean workspace of given citation and run counts; return (ledger_bytes, sources_bytes)."""
    rng = random.Random(seed + n_cites * 100 + n_runs)
    write_text(ws / "intake_manifest.md", f"# Intake\nScale cites={n_cites} runs={n_runs}\n")
    intake_hash = sha256_bytes((ws / "intake_manifest.md").read_bytes())
    write_json(
        ws / "paper_state.json",
        {
            "schema_version": "1.0",
            "project_title": f"Scale Benchmark {n_cites}c/{n_runs}r",
            "venue": {
                "name": "agentskills2027",
                "template_year": 2027,
                "submission_mode": "double-blind",
                "page_limit_main": 9,
            },
            "stages": {
                "po-start": {
                    "status": "approved",
                    "outputs": ["intake_manifest.md"],
                    "output_hashes": {"intake_manifest.md": intake_hash},
                },
                "po-draft": {
                    "status": "approved",
                    "input_hashes": {"intake_manifest.md": intake_hash},
                    "outputs": ["manuscript/sections/01_intro.md"],
                },
            },
        },
    )

    bib_chunks: list[str] = []
    ledger_entries: dict[str, Any] = {}
    sources_bytes = 0
    cite_keys: list[str] = []

    # Realistic ~1.9 KB arXiv metadata snapshot payload modeled on live arXiv API records
    sample_abstract = (
        "Autonomous coding agents increasingly rely on reusable markdown skill packages to execute multi-stage "
        "software and scientific workflows. Prior empirical audits show that packaging bloat, unverified external "
        "claims, and mutable workspace state cause cascading errors across long-horizon executions. We present "
        "a systematic evaluation across multiple benchmarks, measuring latency, memory footprint, recall, false-positive "
        "rates, and cross-runtime portability under strict zero-dependency verification constraints. Our experiments "
        "confirm that deterministic preflight validation paired with isolated read-only review substantially improves "
        "artifact reliability while keeping runtime overhead negligible compared to interactive model inference."
    )

    for i in range(n_cites):
        k = f"author{2020 + (i % 7)}paper{i:03d}"
        cite_keys.append(k)
        bib_chunks.append(
            f"@article{{{k},\n"
            f"  title={{Modular Verification Study {i}}},\n"
            f"  author={{Researcher, A. and Scientist, B. and Engineer, C.}},\n"
            f"  journal={{arXiv preprint arXiv:2601.{10000 + i}}},\n"
            f"  year={{{2020 + (i % 7)}}}\n"
            f"}}\n"
        )
        src_obj = {
            "citekey": k,
            "arxiv_id": f"2601.{10000 + i}v1",
            "title": f"Modular Verification Study {i}: Empirical Audit of Agent Skill Packages",
            "authors": ["Alice Researcher", "Bob Scientist", "Carol Engineer", "David Analyst"],
            "published": f"{2020 + (i % 7)}-03-15T00:00:00Z",
            "updated": f"{2020 + (i % 7)}-04-01T00:00:00Z",
            "primary_category": "cs.SE",
            "categories": ["cs.SE", "cs.AI", "cs.CL"],
            "url": f"https://arxiv.org/abs/2601.{10000 + i}",
            "pdf_url": f"https://arxiv.org/pdf/2601.{10000 + i}",
            "abstract": f"[Study {i}] {sample_abstract} Additional benchmark details for corpus split {i} include {n_cites} references and {n_runs} runs.",
            "fetched_at": "2026-11-27T00:00:00Z",
            "source_api": "https://export.arxiv.org/api/query",
        }
        src_path = ws / f"literature/sources/{k}.json"
        write_json(src_path, src_obj)
        sources_bytes += src_path.stat().st_size

        ledger_entries[k] = {
            "verification_status": "verified_source",
            "source_file": f"literature/sources/{k}.json",
            "arxiv_id": f"2601.{10000 + i}",
            "year": 2020 + (i % 7),
        }

    write_text(ws / "literature/references.bib", "\n".join(bib_chunks))
    ledger_path = ws / "literature/citation_ledger.json"
    write_json(ledger_path, {"schema_version": "1.0", "entries": ledger_entries})
    ledger_bytes = ledger_path.stat().st_size

    prov_runs: dict[str, Any] = {}
    run_blocks_md: list[str] = []
    run_blocks_tex: list[str] = []
    for r in range(n_runs):
        rid = f"exp{r:02d}_scale_s{seed}"
        acc = round(rng.uniform(75.0, 96.5), 2)
        lat = round(rng.uniform(4.2, 42.8), 2)
        write_json(
            ws / f"experiments/runs/{rid}/metrics.json",
            {"run_id": rid, "is_synthetic": False, "metrics": {"accuracy": acc, "latency_ms": lat}},
        )
        write_json(
            ws / f"experiments/runs/{rid}/run_manifest.json",
            {"run_id": rid, "status": "completed", "is_synthetic": False, "git_commit": "abc1234", "git_dirty": False},
        )
        prov_runs[rid] = {
            "origin": "po_exp_code",
            "status": "canonical",
            "source_path": f"experiments/runs/{rid}/metrics.json",
            "is_synthetic": False,
            "user_attested_non_synthetic": False,
        }
        run_blocks_md.append(f"<!-- run:{rid} -->\nRun {r} achieves {acc:.2f}% accuracy in {lat:.2f} ms.\n")
        run_blocks_tex.append(f"Run {r} achieves {acc:.2f}\\% accuracy in {lat:.2f} ms.\n")

    write_json(ws / "experiments/provenance_index.json", {"schema_version": "1.0", "runs": prov_runs})

    # Spread citations across 4 sections
    sec_names = ["01_intro", "02_related", "03_method", "04_results"]
    chunk_size = max(1, len(cite_keys) // len(sec_names))
    for idx, sname in enumerate(sec_names):
        sub_keys = cite_keys[idx * chunk_size : (idx + 1) * chunk_size if idx < 3 else len(cite_keys)]
        md_cites = "; ".join(f"@{k}" for k in sub_keys)
        tex_cites = ",".join(sub_keys)
        md_body = f"# Section {idx + 1} {{#sec:{sname}}}\n\nPrior work [{md_cites}] motivates this stage.\n\n"
        tex_body = f"\\section{{Section {idx + 1}}}\\label{{sec:{sname}}}\n\nPrior work \\citep{{{tex_cites}}} motivates this stage.\n\n"
        if sname == "04_results":
            md_body += "\n".join(run_blocks_md)
            tex_body += "\n".join(run_blocks_tex)
        write_text(ws / f"manuscript/sections/{sname}.md", md_body)
        write_text(ws / f"submission/sections/{sname}.tex", tex_body)

    write_text(
        ws / "submission/main.tex",
        "\\documentclass{article}\n\\begin{document}\n"
        + "\n".join(f"\\input{{sections/{s}}}" for s in sec_names)
        + "\n\\end{document}\n",
    )
    return ledger_bytes, sources_bytes


def run_po_cmd(python_bin: str, po_tools: Path, args: list[str]) -> tuple[int, float]:
    t0 = time.perf_counter()
    proc = subprocess.run([python_bin, str(po_tools), *args], capture_output=True, text=True, check=False)
    dt_ms = (time.perf_counter() - t0) * 1000.0
    return proc.returncode, dt_ms


def check_pdfinfo_leaks(pdf_path: Path) -> tuple[int, int]:
    """Inspect pdfinfo metadata.

    Returns (identity_leaks, generic_creator_tags):
      - identity_leaks: non-empty Author/Producer or any username, /Users/, /home/, github.com leak.
      - generic_creator_tags: non-empty generic venue-class Creator string (e.g. acmart hyperxmp).
    """
    proc = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return 1, 0
    identity_leaks = 0
    generic_creator = 0
    user_login = getpass.getuser().lower()
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k_l = k.strip().lower()
        v_s = v.strip()
        v_l = v_s.lower()
        if k_l in {"author", "producer"} and v_s != "":
            identity_leaks += 1
        elif k_l == "creator" and v_s != "":
            if v_l.startswith("latex with acmart"):
                generic_creator += 1
            else:
                identity_leaks += 1
        if user_login and user_login in v_l:
            identity_leaks += 1
        if "/users/" in v_l or "/home/" in v_l or "github.com/" in v_l:
            identity_leaks += 1
    return identity_leaks, generic_creator


def compile_paranoid_venue(venue_name: str, repo_root: Path, po_tools: Path, tmp_root: Path) -> tuple[bool, int, int, float]:
    """Compile a realistic minimal paper for a venue under openin_any=p openout_any=p --no-shell-escape."""
    ws = tmp_root / f"venue_{venue_name}"
    sub = ws / "submission"
    sec = sub / "sections"
    sec.mkdir(parents=True, exist_ok=True)

    write_json(
        ws / "paper_state.json",
        {
            "schema_version": "1.0",
            "project_title": f"Paranoid Build Test ({venue_name})",
            "venue": {"name": venue_name, "template_year": 2025, "submission_mode": "double-blind", "page_limit_main": 9},
            "stages": {},
        },
    )
    write_text(
        ws / "manuscript/sections/01_body.md",
        "# Introduction {#sec:intro}\n\nVerified workflow claim [@smith2025test] with score 92.4%.\n",
    )
    write_text(
        sec / "01_body.tex",
        "\\section{Introduction}\\label{sec:intro}\n\nVerified workflow claim \\cite{smith2025test} with score 92.4\\%.\n",
    )
    write_text(
        sub / "references.bib",
        "@article{smith2025test,\n  title={Deterministic Skill Verification},\n  author={Smith, Alex},\n  journal={Proceedings of Agent Skills},\n  year={2025}\n}\n",
    )

    if venue_name == "acmart_sigplan":
        main_tex = (
            "\\pdfinfoomitdate=1\n"
            "\\pdftrailerid{}\n"
            "\\pdfsuppressptexinfo=-1\n"
            "\\documentclass[sigplan,review,anonymous]{acmart}\n"
            "\\settopmatter{printacmref=false}\n"
            "\\renewcommand\\footnotetextcopyrightpermission[1]{}\n"
            "\\AtBeginDocument{\\hypersetup{pdfauthor={},pdfcreator={},pdfproducer={}}}\n"
            "\\title{Paranoid Build Verification for ACM SIGPLAN}\n"
            "\\author{Anonymous Author(s)}\n"
            "\\begin{document}\n"
            "\\begin{abstract}Clean double-blind compilation test.\\end{abstract}\n"
            "\\maketitle\n"
            "\\input{sections/01_body}\n"
            "\\bibliographystyle{ACM-Reference-Format}\n"
            "\\bibliography{references}\n"
            "\\end{document}\n"
        )
    elif venue_name == "cvpr2025":
        src_tpl = repo_root / "resources/templates/cvpr2025"
        for item in src_tpl.iterdir():
            if item.is_file() and item.suffix in {".sty", ".bst", ".cls"}:
                shutil.copy2(item, sub / item.name)
        main_tex = (
            "\\pdfinfoomitdate=1\n"
            "\\pdftrailerid{}\n"
            "\\pdfsuppressptexinfo=-1\n"
            "\\documentclass[10pt,twocolumn,letterpaper]{article}\n"
            "\\usepackage[review]{cvpr}\n"
            "\\usepackage{hyperref}\n"
            "\\hypersetup{pdfauthor={},pdfcreator={},pdfproducer={}}\n"
            "\\def\\paperID{0000}\n"
            "\\def\\confName{CVPR}\n"
            "\\def\\confYear{2025}\n"
            "\\title{Paranoid Build Verification for CVPR}\n"
            "\\author{Anonymous Authors}\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\begin{abstract}Clean double-blind compilation test.\\end{abstract}\n"
            "\\input{sections/01_body}\n"
            "{\\small\\bibliographystyle{ieeenat_fullname}\\bibliography{references}}\n"
            "\\end{document}\n"
        )
    elif venue_name == "iclr2025":
        src_tpl = repo_root / "resources/templates/iclr2025"
        for item in src_tpl.iterdir():
            if item.is_file() and item.suffix in {".sty", ".bst", ".cls"}:
                shutil.copy2(item, sub / item.name)
        main_tex = (
            "\\pdfinfoomitdate=1\n"
            "\\pdftrailerid{}\n"
            "\\pdfsuppressptexinfo=-1\n"
            "\\documentclass{article}\n"
            "\\usepackage{iclr2025_conference,times}\n"
            "\\usepackage{hyperref}\n"
            "\\hypersetup{pdfauthor={},pdfcreator={},pdfproducer={}}\n"
            "\\title{Paranoid Build Verification for ICLR}\n"
            "\\author{Anonymous Authors}\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\begin{abstract}Clean double-blind compilation test.\\end{abstract}\n"
            "\\input{sections/01_body}\n"
            "\\bibliography{references}\n"
            "\\bibliographystyle{iclr2025_conference}\n"
            "\\end{document}\n"
        )
    else:
        raise ValueError(venue_name)

    write_text(sub / "main.tex", main_tex)

    env = os.environ.copy()
    env["openin_any"] = "p"
    env["openout_any"] = "p"

    t0 = time.perf_counter()
    pdflatex_cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "--no-shell-escape", "main.tex"]
    steps = [pdflatex_cmd, ["bibtex", "main"], pdflatex_cmd, pdflatex_cmd]
    ok = True
    for cmd in steps:
        p = subprocess.run(cmd, cwd=sub, env=env, capture_output=True, text=True, check=False)
        if p.returncode != 0:
            ok = False
            break
    dt_ms = (time.perf_counter() - t0) * 1000.0

    pdf_path = sub / "main.pdf"
    if not ok or not pdf_path.is_file():
        return False, 1, 0, round(dt_ms, 2)

    id_leaks, gen_creator = check_pdfinfo_leaks(pdf_path)
    fmt_rc, _ = run_po_cmd(sys.executable, po_tools, ["format-verify", "--workspace", str(ws), "--check-tex-dir", str(sub)])
    return (fmt_rc == 0), id_leaks, gen_creator, round(dt_ms, 2)


def test_paranoid_containment(tmp_root: Path) -> dict[str, int]:
    """Empirically test paranoid TeX containment across 3 adversarial payloads:
      1. E2 macro-obfuscated \\csname write18\\endcsname shell execution (--no-shell-escape)
      2. Parent-directory \\openout write traversal (openout_any=p)
      3. Parent-directory \\openin read traversal (openin_any=p; no-op in TeX Live 2026)
    """
    adv_dir = tmp_root / "adv_sandbox"
    sub_dir = adv_dir / "sub"
    sub_dir.mkdir(parents=True, exist_ok=True)
    secret_file = adv_dir / "secret_parent.txt"
    secret_token = "TOPSECRET9471"
    secret_file.write_text(secret_token + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["openin_any"] = "p"
    env["openout_any"] = "p"

    # Attack 1: E2 obfuscated \csname write18\endcsname shell execution
    marker = sub_dir / "pwned_marker.txt"
    (sub_dir / "attack_e2.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\def\\cmd{write18}\n\\immediate\\csname \\cmd\\endcsname{touch pwned_marker.txt}\n"
        "Hello.\n\\end{document}\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "--no-shell-escape", "attack_e2.tex"],
        cwd=sub_dir, env=env, capture_output=True, text=True, check=False,
    )
    e2_blocked = 1 if not marker.exists() else 0

    # Attack 2: Parent-directory \openout write traversal (blocked by openout_any=p)
    pwn_out = adv_dir / "pwn_out.txt"
    (sub_dir / "attack_openout.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\newwrite\\w\\immediate\\openout\\w=../pwn_out.txt\\immediate\\write\\w{pwn}\\immediate\\closeout\\w\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "--no-shell-escape", "attack_openout.tex"],
        cwd=sub_dir, env=env, capture_output=True, text=True, check=False,
    )
    openout_blocked = 1 if not pwn_out.exists() else 0

    # Attack 3: Parent-directory \openin read traversal (tests openin_any=p; TeX Live 2026 regression)
    (sub_dir / "attack_openin.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\newread\\sf\\openin\\sf=../secret_parent.txt\n"
        "\\ifeof\\sf BLOCKED\\else\\read\\sf to\\sline EXFIL:\\sline\\fi\\closein\\sf\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "--no-shell-escape", "attack_openin.tex"],
        cwd=sub_dir, env=env, capture_output=True, text=True, check=False,
    )
    openin_pdf = sub_dir / "attack_openin.pdf"
    exfiltrated = False
    if openin_pdf.is_file() and shutil.which("pdftotext"):
        txt = subprocess.run(["pdftotext", str(openin_pdf), "-"], capture_output=True, text=True, check=False).stdout
        exfiltrated = secret_token in txt
    openin_blocked = 0 if exfiltrated else 1

    return {
        "adversarial_tex_tested": 3,
        "adversarial_tex_blocked": e2_blocked + openout_blocked + openin_blocked,
        "e2_macro_shell_blocked": e2_blocked,
        "openout_parent_blocked": openout_blocked,
        "openin_parent_blocked": openin_blocked,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--po-tools", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    scales = SCALES_DRY if args.dry_run else SCALES_FULL
    venues = ["acmart_sigplan"] if args.dry_run else ["acmart_sigplan", "cvpr2025", "iclr2025"]
    rows: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix=f"po_scale_s{args.seed}_") as tmp:
        tmp_root = Path(tmp)
        for label, n_cites, n_runs in scales:
            ws = tmp_root / f"scale_{label}"
            snap = tmp_root / f"snap_{label}.json"
            ledger_bytes, sources_bytes = build_scaled_workspace(ws, n_cites, n_runs, args.seed)
            run_po_cmd(sys.executable, args.po_tools, ["check-readonly", "--workspace", str(ws), "--snapshot", str(snap), "--create"])

            rc1, ms_sync = run_po_cmd(sys.executable, args.po_tools, ["state-sync", "--workspace", str(ws), "--check-only"])
            rc2, ms_pre = run_po_cmd(sys.executable, args.po_tools, ["review-preflight", "--workspace", str(ws)])
            rc3, ms_fmt = run_po_cmd(sys.executable, args.po_tools, ["format-verify", "--workspace", str(ws)])
            rc4, ms_ro = run_po_cmd(sys.executable, args.po_tools, ["check-readonly", "--workspace", str(ws), "--snapshot", str(snap), "--verify"])
            if any(rc != 0 for rc in (rc1, rc2, rc3, rc4)):
                raise RuntimeError(f"Clean scaled workspace {label} failed check: {(rc1, rc2, rc3, rc4)}")

            total_ms = ms_sync + ms_pre + ms_fmt + ms_ro
            offload_pct = round((1.0 - ledger_bytes / max(1, ledger_bytes + sources_bytes)) * 100.0, 2)
            rows.append(
                {
                    "step": n_cites,
                    "scale": label,
                    "citations": n_cites,
                    "runs": n_runs,
                    "state_sync_ms": round(ms_sync, 2),
                    "review_preflight_ms": round(ms_pre, 2),
                    "format_verify_ms": round(ms_fmt, 2),
                    "check_readonly_ms": round(ms_ro, 2),
                    "total_ms": round(total_ms, 2),
                    "ledger_bytes": ledger_bytes,
                    "sources_bytes": sources_bytes,
                    "offload_pct": offload_pct,
                }
            )

        venues_ok = 0
        total_leaks = 0
        total_gen_creator = 0
        venue_timings: dict[str, float] = {}
        for v in venues:
            v_ok, v_leaks, v_gen, v_ms = compile_paranoid_venue(v, args.repo_root.resolve(), args.po_tools.resolve(), tmp_root)
            venue_timings[f"compile_{v}_ms"] = v_ms
            if v_ok:
                venues_ok += 1
            total_leaks += v_leaks
            total_gen_creator += v_gen

        adv_metrics = test_paranoid_containment(tmp_root)

    # Write series.csv
    csv_path = args.out_dir / "series.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    last = rows[-1]
    metrics: dict[str, Any] = {
        "max_scale_label": last["scale"],
        "xl_total_ms": last["total_ms"],
        "xl_state_sync_ms": last["state_sync_ms"],
        "xl_review_preflight_ms": last["review_preflight_ms"],
        "xl_format_verify_ms": last["format_verify_ms"],
        "xl_check_readonly_ms": last["check_readonly_ms"],
        "ledger_bytes_xl": last["ledger_bytes"],
        "sources_bytes_xl": last["sources_bytes"],
        "context_offload_pct": last["offload_pct"],
        "venues_tested": len(venues),
        "venues_compiled_ok": venues_ok,
        "pdfinfo_leaks": total_leaks,
        "pdfinfo_generic_creator_tags": total_gen_creator,
        **adv_metrics,
        **venue_timings,
    }
    for r in rows:
        s_l = r["scale"].lower()
        metrics[f"scale_{s_l}_total_ms"] = r["total_ms"]
        metrics[f"scale_{s_l}_offload_pct"] = r["offload_pct"]

    payload = {"run_id": args.run_id, "is_synthetic": bool(args.dry_run), "metrics": metrics}
    tmp_m = args.out_dir / "metrics.json.tmp"
    tmp_m.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_m, args.out_dir / "metrics.json")
    print(
        f"[exp03] Wrote {args.out_dir / 'metrics.json'} & series.csv "
        f"(max_total={last['total_ms']}ms, offload={last['offload_pct']}%, venues={venues_ok}/{len(venues)}, leaks={total_leaks})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
