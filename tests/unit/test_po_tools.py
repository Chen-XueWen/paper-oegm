"""Unit tests for all 4 subcommands of resources/scripts/po_tools.py."""

import json
import subprocess
import sys
import zipfile
from pathlib import Path


def run_tool(repo_root: Path, *args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(repo_root / "resources/scripts/po_tools.py"), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return proc.returncode, payload


def seed_workspace(ws: Path) -> None:
    (ws / "plan").mkdir(parents=True, exist_ok=True)
    (ws / "manuscript/sections").mkdir(parents=True, exist_ok=True)
    (ws / "experiments/runs/exp01_s42").mkdir(parents=True, exist_ok=True)
    (ws / "literature/sources").mkdir(parents=True, exist_ok=True)
    (ws / "submission/sections").mkdir(parents=True, exist_ok=True)
    (ws / "submission/build").mkdir(parents=True, exist_ok=True)

    (ws / "intake_manifest.md").write_text("# Intake\n", encoding="utf-8")
    (ws / "plan/outline.md").write_text("# Outline\n[TODO: check]\n", encoding="utf-8")
    state = {
        "schema_version": "1.0",
        "project_title": "Test Paper",
        "venue": {
            "name": "iclr2025",
            "template_source": "resources/templates/iclr2025",
            "template_year": 2025,
            "submission_mode": "double-blind",
            "page_limit_main": 10,
            "citation_macro_style": "natbib",
        },
        "stages": {},
    }
    (ws / "paper_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def test_state_sync_drift_atomic_and_malformed(repo_root: Path, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    seed_workspace(ws)

    rc, out = run_tool(
        repo_root,
        "state-sync",
        "--workspace",
        str(ws),
        "--stage",
        "po-outline",
        "--status",
        "approved",
        "--inputs",
        "intake_manifest.md",
        "--outputs",
        "plan/outline.md",
    )
    assert rc == 0 and out["ok"] is True
    assert out["todo_count"] == 1
    assert (ws / "STATUS.md").is_file()
    assert "AUTO-GENERATED FROM paper_state.json" in (ws / "STATUS.md").read_text(encoding="utf-8")

    # Mutate input -> check-only detects drift (exit 1) and sync marks stage stale
    (ws / "intake_manifest.md").write_text("# Intake modified\n", encoding="utf-8")
    rc_chk, out_chk = run_tool(repo_root, "state-sync", "--workspace", str(ws), "--check-only")
    assert rc_chk == 1 and "po-outline" in out_chk["drifted_inputs"]

    rc_upd, out_upd = run_tool(repo_root, "state-sync", "--workspace", str(ws))
    assert rc_upd == 0 and "po-outline" in out_upd["stale_stages"]

    # Malformed JSON -> exit 2
    (ws / "paper_state.json").write_text("{bad json", encoding="utf-8")
    rc_bad, out_bad = run_tool(repo_root, "state-sync", "--workspace", str(ws))
    assert rc_bad == 2 and out_bad["ok"] is False


def test_check_readonly_pass_and_detect_mutation(repo_root: Path, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    seed_workspace(ws)
    snap = tmp_path / "snap.json"

    rc1, out1 = run_tool(repo_root, "check-readonly", "--workspace", str(ws), "--snapshot", str(snap), "--create")
    assert rc1 == 0 and out1["ok"] is True

    rc2, out2 = run_tool(repo_root, "check-readonly", "--workspace", str(ws), "--snapshot", str(snap), "--verify")
    assert rc2 == 0 and out2["ok"] is True

    (ws / "plan/outline.md").write_text("# Tampered\n", encoding="utf-8")
    rc3, out3 = run_tool(repo_root, "check-readonly", "--workspace", str(ws), "--snapshot", str(snap), "--verify")
    assert rc3 == 1 and "plan/outline.md" in out3["modified"]


def test_review_preflight_pass_and_blockers(repo_root: Path, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    seed_workspace(ws)

    # Zero-blocker pass setup
    (ws / "literature/sources/smith2024.json").write_text('{"title": "Smith"}\n', encoding="utf-8")
    (ws / "literature/references.bib").write_text(
        "@article{smith2024, title={Demo}, author={Smith}, year={2024}}\n", encoding="utf-8"
    )
    (ws / "literature/citation_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": {
                    "smith2024": {
                        "verification_status": "verified_source",
                        "source_file": "literature/sources/smith2024.json",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (ws / "experiments/runs/exp01_s42/run_manifest.json").write_text(
        json.dumps({"run_id": "exp01_s42", "is_synthetic": False, "git_dirty": False}), encoding="utf-8"
    )
    (ws / "experiments/runs/exp01_s42/metrics.json").write_text(
        json.dumps({"run_id": "exp01_s42", "is_synthetic": False, "metrics": {"acc": 88.42}}), encoding="utf-8"
    )
    (ws / "experiments/provenance_index.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "runs": {
                    "exp01_s42": {
                        "origin": "po_exp_code",
                        "status": "canonical",
                        "source_path": "experiments/runs/exp01_s42/metrics.json",
                        "is_synthetic": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (ws / "manuscript/sections/05_experiments.md").write_text(
        "# Experiments\n\n<!-- run:exp01_s42 -->\nOur model reaches 88.4 accuracy following [@smith2024].\n",
        encoding="utf-8",
    )

    rc_ok, out_ok = run_tool(repo_root, "review-preflight", "--workspace", str(ws))
    assert rc_ok == 0 and out_ok["ok"] is True and not out_ok["blockers"]

    # Inject synthetic run + git_dirty + unverified citation + wrong decimal -> blockers & major
    (ws / "experiments/runs/exp01_s42/run_manifest.json").write_text(
        json.dumps({"run_id": "exp01_s42", "is_synthetic": True, "git_dirty": True}), encoding="utf-8"
    )
    (ws / "manuscript/sections/05_experiments.md").write_text(
        "# Experiments\n\n<!-- run:exp01_s42 -->\nOur model reaches 99.9 accuracy [@smith2024; @missing2025].\n",
        encoding="utf-8",
    )
    rc_bad, out_bad = run_tool(repo_root, "review-preflight", "--workspace", str(ws))
    assert rc_bad == 1 and out_bad["ok"] is False
    issues = " ".join(b["issue"] for b in out_bad["blockers"])
    assert "missing2025" in issues
    assert "is_synthetic=true" in issues
    assert "99.9" in issues
    assert any("git_dirty=true" in m["issue"] for m in out_bad["majors"])


def test_format_verify_security_parity_logs_and_anonymity(repo_root: Path, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    seed_workspace(ws)

    # Matching .md <-> .tex
    (ws / "manuscript/sections/05_experiments.md").write_text(
        "# Experiments {#sec:exp}\n\nAccuracy is 88.4 per [@smith2024].\n", encoding="utf-8"
    )
    (ws / "submission/sections/05_experiments.tex").write_text(
        "\\section{Experiments}\\label{sec:exp}\nAccuracy is 88.4 per \\citep{smith2024}.\n", encoding="utf-8"
    )
    (ws / "submission/main.tex").write_text(
        "\\documentclass{article}\n\\usepackage{iclr2025_conference}\n% \\iclrfinalcopy\n\\input{sections/05_experiments}\n",
        encoding="utf-8",
    )
    rc_ok, out_ok = run_tool(repo_root, "format-verify", "--workspace", str(ws), "--check-tex-dir", str(ws / "submission"))
    assert rc_ok == 0 and out_ok["ok"] is True

    # Test Zip Slip + \write18 archive rejection
    bad_zip = tmp_path / "bad_tpl.zip"
    with zipfile.ZipFile(bad_zip, "w") as zf:
        zf.writestr("../escape.sty", "% bad")
        zf.writestr("evil.sty", "\\immediate\\write18{id}\n")
    rc_zip, out_zip = run_tool(repo_root, "format-verify", "--workspace", str(ws), "--archive", str(bad_zip))
    assert rc_zip == 1
    z_issues = " ".join(b["issue"] for b in out_zip["blockers"])
    assert "Zip Slip" in z_issues and "shell-pipe" in z_issues

    # Test numeric drift, Overfull \hbox telemetry, and double-blind % comment leak
    (ws / "submission/sections/05_experiments.tex").write_text(
        "% built at /Users/alice/secret\n\\section{Experiments}\\label{sec:exp}\nAccuracy is 77.1.\n",
        encoding="utf-8",
    )
    (ws / "submission/build/main.log").write_text(
        "Overfull \\hbox (8.5pt too wide) in paragraph at lines 10--12\n", encoding="utf-8"
    )
    rc_drift, out_drift = run_tool(repo_root, "format-verify", "--workspace", str(ws))
    assert rc_drift == 1
    d_issues = " ".join(b["issue"] for b in out_drift["blockers"])
    assert "dropped citations" in d_issues
    assert "dropped decimal tokens" in d_issues
    assert "Local user path leak" in d_issues
    assert len(out_drift["telemetry"]["overfull_hbox_gt_2pt"]) == 1
