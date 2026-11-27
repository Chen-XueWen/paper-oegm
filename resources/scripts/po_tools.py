#!/usr/bin/env python3
# Copyright 2026 Chen-XueWen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Zero-dependency Python 3.10+ stdlib verification helper for PaperOEGM.

Subcommands:
  state-sync       Validate paper_state.json, check digest drift, update atomically, regenerate STATUS.md.
  check-readonly   Snapshot or verify tracked files inside <paper_workspace>/ only.
  review-preflight Deterministic citation, synthetic/git_dirty, and inline run-metric audit.
  format-verify    Zip Slip & TeX shell-pipe checks, .md<->.tex parity, TeX .log telemetry, double-blind scan.

Exit codes:
  0  Pass (no blockers / no unexpected mutations)
  1  Blocking issue, drift, or mutation detected
  2  CLI usage error or malformed JSON
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGE_ORDER = [
    "po-start",
    "po-literature:early",
    "po-exp-design",
    "po-exp-code",
    "po-outline",
    "po-literature:late",
    "po-visuals",
    "po-draft",
    "po-review",
    "po-resolve",
    "po-format",
]

IGNORED_DIRS = {".git", "__pycache__", "build", ".pytest_cache"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def probe_environment() -> dict[str, str]:
    tex_compiler = "none"
    for candidate in ("latexmk", "pdflatex", "xelatex", "tectonic"):
        if shutil.which(candidate):
            tex_compiler = candidate
            break

    bibtex_tool = "none"
    for candidate in ("bibtex", "biber"):
        if shutil.which(candidate):
            bibtex_tool = candidate
            break

    pdf_rasterizer = "none"
    if shutil.which("pdftoppm"):
        pdf_rasterizer = "pdftoppm"
    else:
        try:
            __import__("fitz")
            pdf_rasterizer = "python_pymupdf"
        except Exception:
            pdf_rasterizer = "none"

    python_plotting = "unavailable"
    try:
        __import__("matplotlib")
        python_plotting = "available"
    except Exception:
        python_plotting = "unavailable"

    return {
        "hash_tool": "python3",
        "pandoc": "available" if shutil.which("pandoc") else "unavailable",
        "tex_compiler": tex_compiler,
        "bibtex_tool": bibtex_tool,
        "pdf_rasterizer": pdf_rasterizer,
        "python_plotting": python_plotting,
    }


def load_json_checked(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"Missing file: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"Malformed JSON in {path} (line {exc.lineno}, col {exc.colno}): {exc.msg}"
    if not isinstance(data, dict):
        return None, f"Expected JSON object in {path}"
    return data, None


def count_todos(workspace: Path) -> int:
    total = 0
    pattern = re.compile(r"\[(?:TODO\b[^\]]*|PENDING_REAL_RUN)\]")
    for subdir in ("plan", "manuscript/sections"):
        base = workspace / subdir
        if not base.exists():
            continue
        for md in base.glob("*.md"):
            total += len(pattern.findall(md.read_text(encoding="utf-8", errors="replace")))
    return total


def recommend_next_stage(stages: dict[str, Any]) -> str:
    for key in STAGE_ORDER:
        info = stages.get(key)
        if not info:
            return key.split(":")[0]
        if info.get("status") in {"not_started", "in_progress", "awaiting_human_gate", "stale"}:
            return key.split(":")[0]
    return "po-format"


def render_status_md(state: dict[str, Any], stale: list[str], todo_count: int) -> str:
    venue = state.get("venue", {})
    env = state.get("environment", {})
    stages = state.get("stages", {})
    next_skill = recommend_next_stage(stages)

    lines = [
        "<!-- AUTO-GENERATED FROM paper_state.json — DO NOT EDIT SETTINGS HERE -->",
        "",
        f"# Paper Workspace Status — {state.get('project_title', 'Untitled Project')}",
        "",
        f"* **Venue:** `{venue.get('name', 'unspecified')}` (template year: `{venue.get('template_year', 'unknown')}`)",
        f"* **Submission Mode:** `{venue.get('submission_mode', 'double-blind')}`",
        f"* **Page Limit (Main Body):** `{venue.get('page_limit_main', 'unspecified')}`",
        f"* **Open `[TODO]` / `[PENDING_REAL_RUN]` Markers:** `{todo_count}`",
        f"* **Recommended Next Skill:** `{next_skill}`",
        "",
        "## Toolchain Probe",
        "",
        f"* `hash_tool`: `{env.get('hash_tool', 'unknown')}` | `pandoc`: `{env.get('pandoc', 'unknown')}` | `tex_compiler`: `{env.get('tex_compiler', 'none')}` | `bibtex_tool`: `{env.get('bibtex_tool', 'none')}` | `pdf_rasterizer`: `{env.get('pdf_rasterizer', 'none')}` | `python_plotting`: `{env.get('python_plotting', 'unknown')}`",
        "",
        "## Stage Progress",
        "",
        "| Stage | Status | Updated (UTC) | Outputs |",
        "| --- | --- | --- | --- |",
    ]
    seen: set[str] = set()
    ordered_keys = [k for k in STAGE_ORDER if k in stages] + [k for k in stages if k not in STAGE_ORDER]
    for key in ordered_keys:
        seen.add(key)
        info = stages.get(key, {})
        outputs = ", ".join(f"`{o}`" for o in info.get("outputs", [])) or "—"
        lines.append(
            f"| `{key}` | `{info.get('status', 'not_started')}` | `{info.get('updated_at', '—')}` | {outputs} |"
        )
    if not seen:
        lines.append("| `po-start` | `not_started` | — | — |")

    if stale:
        lines.extend(["", "## Stale Stage Warnings", ""])
        for s in stale:
            lines.append(f"* `{s}` has upstream input files modified since its last approved run.")

    lines.append("")
    return "\n".join(lines)


def cmd_state_sync(args: argparse.Namespace) -> int:
    ws = Path(args.workspace).resolve()
    state_path = ws / "paper_state.json"
    state, err = load_json_checked(state_path)
    if err:
        print(json.dumps({"ok": False, "error": err}, indent=2))
        return 2
    assert state is not None

    if args.probe or "environment" not in state:
        state["environment"] = probe_environment()

    stages: dict[str, Any] = state.setdefault("stages", {})

    if args.stage and not args.check_only:
        entry = stages.setdefault(args.stage, {})
        entry["status"] = args.status or "approved"
        inputs = [p.strip() for p in (args.inputs or "").split(",") if p.strip()]
        outputs = [p.strip() for p in (args.outputs or "").split(",") if p.strip()]
        if inputs:
            entry["input_hashes"] = {
                rel: sha256_file(ws / rel) for rel in inputs if (ws / rel).is_file()
            }
        if outputs:
            entry["outputs"] = outputs
            entry["output_hashes"] = {
                rel: sha256_file(ws / rel) for rel in outputs if (ws / rel).is_file()
            }
        entry["updated_at"] = utc_now()

        # When po-resolve updates manuscript sections, advance po-draft's output_hashes
        # so po-draft is not falsely marked stale, while po-review / po-format become stale.
        if args.stage == "po-resolve" and "po-draft" in stages:
            draft_out = stages["po-draft"].get("output_hashes", {})
            for rel in list(draft_out.keys()):
                if (ws / rel).is_file():
                    draft_out[rel] = sha256_file(ws / rel)

    drifted: dict[str, list[str]] = {}
    stale_stages: list[str] = []

    for stage_key, info in stages.items():
        in_hashes = info.get("input_hashes", {})
        changed: list[str] = []
        for rel, recorded in in_hashes.items():
            target = ws / rel
            if not target.is_file():
                changed.append(f"{rel} (missing)")
                continue
            current = sha256_file(target)
            if current != recorded:
                changed.append(rel)
        if changed:
            drifted[stage_key] = changed
            if info.get("status") == "approved":
                stale_stages.append(stage_key)
                if not args.check_only:
                    info["status"] = "stale"
        elif info.get("status") == "stale":
            stale_stages.append(stage_key)

    todo_count = count_todos(ws)
    if not args.check_only:
        atomic_write_text(state_path, json.dumps(state, indent=2) + "\n")
        atomic_write_text(ws / "STATUS.md", render_status_md(state, stale_stages, todo_count))

    result = {
        "ok": not (args.check_only and drifted),
        "workspace": str(ws),
        "stale_stages": stale_stages,
        "drifted_inputs": drifted,
        "todo_count": todo_count,
        "recommended_next_skill": recommend_next_stage(stages),
    }
    print(json.dumps(result, indent=2))
    return 1 if (args.check_only and drifted) else 0


def scan_workspace_hashes(ws: Path, ignore_paths: set[Path]) -> dict[str, str]:
    digests: dict[str, str] = {}
    for root, dirs, files in os.walk(ws):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)
        root_p = Path(root)
        for fname in sorted(files):
            fp = root_p / fname
            if fp.resolve() in ignore_paths or fp.is_symlink():
                continue
            if fname.startswith(".") and ".tmp." in fname:
                continue
            rel = fp.relative_to(ws).as_posix()
            digests[rel] = sha256_file(fp)
    return digests


def cmd_check_readonly(args: argparse.Namespace) -> int:
    ws = Path(args.workspace).resolve()
    snap_path = Path(args.snapshot).resolve()
    if not ws.is_dir():
        print(json.dumps({"ok": False, "error": f"Workspace not found: {ws}"}, indent=2))
        return 2

    current = scan_workspace_hashes(ws, {snap_path})
    if args.create:
        atomic_write_text(snap_path, json.dumps({"workspace": str(ws), "files": current}, indent=2) + "\n")
        print(json.dumps({"ok": True, "action": "created", "file_count": len(current)}, indent=2))
        return 0

    snap, err = load_json_checked(snap_path)
    if err:
        print(json.dumps({"ok": False, "error": err}, indent=2))
        return 2
    assert snap is not None
    before: dict[str, str] = snap.get("files", {})

    added = sorted(set(current) - set(before))
    deleted = sorted(set(before) - set(current))
    modified = sorted(k for k in set(current) & set(before) if current[k] != before[k])
    ok = not (added or deleted or modified)
    print(
        json.dumps(
            {"ok": ok, "added": added, "modified": modified, "deleted": deleted},
            indent=2,
        )
    )
    return 0 if ok else 1


def strip_fenced_code(md: str) -> str:
    return re.sub(r"```.*?```", "", md, flags=re.DOTALL)


def extract_md_citations(md: str) -> set[str]:
    clean = strip_fenced_code(md)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
    clean = re.sub(r"`[^`]*`", "", clean)
    keys: set[str] = set()
    # Bracketed pandoc citations: [@key1; @key2, p. 3]
    for grp in re.findall(r"\[([^\]]*@[^\]]+)\]", clean):
        for k in re.findall(r"@([A-Za-z][A-Za-z0-9_:\-]*)", grp):
            keys.add(k)
    # Narrative citations: @key not preceded by word/dot (avoid emails)
    for k in re.findall(r"(?<![A-Za-z0-9._%+-])@([A-Za-z][A-Za-z0-9_:\-]*)", clean):
        keys.add(k)
    # Raw LaTeX \cite*{} commands inside fenced-free blocks
    for grp in re.findall(r"\\cite[a-zA-Z*]*\{([^}]+)\}", clean):
        for k in grp.split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


def parse_bib_keys(bib_text: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text))


def flatten_numbers(obj: Any) -> list[float]:
    vals: list[float] = []
    if isinstance(obj, bool):
        return vals
    if isinstance(obj, (int, float)):
        vals.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            vals.extend(flatten_numbers(v))
    elif isinstance(obj, list):
        for v in obj:
            vals.extend(flatten_numbers(v))
    return vals


def number_matches_any(token: str, refs: list[float]) -> bool:
    try:
        val = float(token)
    except ValueError:
        return True
    if "." in token:
        decimals = len(token.split(".", 1)[1])
        tol = 0.55 * (10 ** (-decimals))
    else:
        tol = 0.55
    for r in refs:
        if abs(r - val) <= tol:
            return True
        # Also allow percentage presentation of 0..1 metrics (e.g. 0.854 -> 85.4)
        if 0.0 <= r <= 1.0 and abs(r * 100.0 - val) <= tol:
            return True
    return False


def cmd_review_preflight(args: argparse.Namespace) -> int:
    ws = Path(args.workspace).resolve()
    blockers: list[dict[str, Any]] = []
    majors: list[dict[str, Any]] = []

    sections_dir = ws / "manuscript/sections"
    section_files = sorted(sections_dir.glob("*.md")) if sections_dir.is_dir() else []
    cited_keys: set[str] = set()
    section_texts: dict[str, str] = {}
    for sf in section_files:
        txt = sf.read_text(encoding="utf-8")
        section_texts[sf.name] = txt
        cited_keys.update(extract_md_citations(txt))

    # 1. Citation parity & verification ledger check
    bib_path = ws / "literature/references.bib"
    bib_keys = parse_bib_keys(bib_path.read_text(encoding="utf-8")) if bib_path.is_file() else set()
    ledger_path = ws / "literature/citation_ledger.json"
    ledger_entries: dict[str, Any] = {}
    if ledger_path.is_file():
        ledger_data, err = load_json_checked(ledger_path)
        if err:
            print(json.dumps({"ok": False, "error": err}, indent=2))
            return 2
        assert ledger_data is not None
        ledger_entries = ledger_data.get("entries", {})

    for k in sorted(cited_keys):
        if k not in bib_keys:
            blockers.append({"category": "citation", "issue": f"Cited key '{k}' missing from literature/references.bib"})
        entry = ledger_entries.get(k)
        if entry is None:
            blockers.append({"category": "citation", "issue": f"Cited key '{k}' missing from literature/citation_ledger.json"})
            continue
        vstatus = entry.get("verification_status")
        if vstatus == "unverified_needs_human_check":
            blockers.append({"category": "citation", "issue": f"Cited key '{k}' is tagged unverified_needs_human_check"})
        elif vstatus == "verified_source":
            src = entry.get("source_file")
            if not src or not (ws / src).is_file():
                blockers.append(
                    {"category": "citation", "issue": f"Verified key '{k}' lacks saved source snapshot '{src}'"}
                )

    # 2. Provenance index, synthetic/git_dirty checks, and inline <!-- run:<id> --> metric audit
    prov_path = ws / "experiments/provenance_index.json"
    runs_index: dict[str, Any] = {}
    if prov_path.is_file():
        prov_data, err = load_json_checked(prov_path)
        if err:
            print(json.dumps({"ok": False, "error": err}, indent=2))
            return 2
        assert prov_data is not None
        runs_index = prov_data.get("runs", {})

    run_ref_pattern = re.compile(r"<!--\s*run:([A-Za-z0-9_.\-/]+)\s*-->")
    decimal_token_re = re.compile(r"(?<![A-Za-z0-9_])(\d+\.\d+)(?![A-Za-z0-9_])")
    referenced_runs: set[str] = set()

    for sname, txt in section_texts.items():
        if "experiments/dry_run/" in txt:
            blockers.append({"category": "evidence", "issue": f"{sname} references experiments/dry_run/ path"})
        matches = list(run_ref_pattern.finditer(txt))
        for idx, m in enumerate(matches):
            run_id = m.group(1)
            referenced_runs.add(run_id)
            run_info = runs_index.get(run_id)
            if not run_info:
                blockers.append({"category": "evidence", "issue": f"{sname} references unregistered run_id '{run_id}'"})
                continue
            if run_info.get("is_synthetic") is True:
                blockers.append({"category": "evidence", "issue": f"Referenced run_id '{run_id}' has is_synthetic=true"})
            origin = run_info.get("origin", "po_exp_code")
            src_rel = run_info.get("source_path")
            src_file = (ws / src_rel) if src_rel else None

            if origin == "po_exp_code":
                manifest_p = ws / "experiments/runs" / run_id / "run_manifest.json"
                if manifest_p.is_file():
                    mdata, merr = load_json_checked(manifest_p)
                    if merr:
                        blockers.append({"category": "evidence", "issue": merr})
                    elif mdata:
                        if mdata.get("is_synthetic") is True:
                            blockers.append(
                                {"category": "evidence", "issue": f"run_manifest.json for '{run_id}' has is_synthetic=true"}
                            )
                        if mdata.get("git_dirty") is True:
                            majors.append(
                                {"category": "evidence", "issue": f"run_manifest.json for '{run_id}' has git_dirty=true"}
                            )
            elif origin == "user_byo":
                if run_info.get("user_attested_non_synthetic") is not True:
                    blockers.append(
                        {"category": "evidence", "issue": f"BYO run_id '{run_id}' lacks user_attested_non_synthetic=true"}
                    )

            # Audit decimal metrics in the block following <!-- run:<run_id> --> up to blank-line-separated section or next tag
            if src_file and src_file.is_file() and src_file.suffix == ".json":
                mjson, jerr = load_json_checked(src_file)
                if not jerr and mjson:
                    if mjson.get("is_synthetic") is True:
                        blockers.append({"category": "evidence", "issue": f"{src_rel} has is_synthetic=true"})
                    ref_nums = flatten_numbers(mjson.get("metrics", mjson))
                    start = m.end()
                    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(txt)
                    segment = txt[start:end].split("\n\n", 1)[0]
                    for num_tok in decimal_token_re.findall(segment):
                        if ref_nums and not number_matches_any(num_tok, ref_nums):
                            blockers.append(
                                {
                                    "category": "evidence",
                                    "issue": f"{sname} reports decimal '{num_tok}' under run '{run_id}' not matching {src_rel}",
                                }
                            )

    result = {
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "majors": majors,
        "stats": {
            "sections_scanned": len(section_files),
            "cited_keys": len(cited_keys),
            "referenced_runs": len(referenced_runs),
        },
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


SHELL_PIPE_RE = re.compile(r"\\write18\b|\\input\s*\{\s*\||\\immediate\\write18\b")


def scan_tex_for_shell_pipes(text: str, label: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines(), 1):
        # Strip LaTeX comments before matching
        code = re.sub(r"(?<!\\)%.*$", "", line)
        if SHELL_PIPE_RE.search(code):
            hits.append({"category": "security", "issue": f"Unsafe TeX shell-pipe primitive in {label}:{i}"})
    return hits


def validate_archive(archive_path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    suffixes = "".join(archive_path.suffixes).lower()
    if suffixes.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as zf:
            for info in zf.infolist():
                member = info.filename
                parts = Path(member).parts
                if member.startswith("/") or ".." in parts:
                    issues.append({"category": "security", "issue": f"Zip Slip path traversal in archive member '{member}'"})
                    continue
                if Path(member).suffix.lower() in {".tex", ".sty", ".cls"} and not info.is_dir():
                    data = zf.read(info).decode("utf-8", errors="replace")
                    issues.extend(scan_tex_for_shell_pipes(data, f"{archive_path.name}:{member}"))
    elif any(suffixes.endswith(ext) for ext in (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")):
        with tarfile.open(archive_path, "r:*") as tf:
            for member in tf.getmembers():
                parts = Path(member.name).parts
                if member.name.startswith("/") or ".." in parts or member.issym() or member.islnk():
                    issues.append({"category": "security", "issue": f"Unsafe archive member '{member.name}'"})
                    continue
                if member.isfile() and Path(member.name).suffix.lower() in {".tex", ".sty", ".cls"}:
                    fh = tf.extractfile(member)
                    if fh:
                        data = fh.read().decode("utf-8", errors="replace")
                        issues.extend(scan_tex_for_shell_pipes(data, f"{archive_path.name}:{member.name}"))
    else:
        issues.append({"category": "security", "issue": f"Unsupported archive format: {archive_path.name}"})
    return issues


def extract_tex_citations(tex: str) -> set[str]:
    clean = re.sub(r"(?<!\\)%.*$", "", tex, flags=re.MULTILINE)
    keys: set[str] = set()
    for grp in re.findall(r"\\cite[a-zA-Z*]*\{([^}]+)\}", clean):
        for k in grp.split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


def extract_md_labels(md: str) -> set[str]:
    clean = strip_fenced_code(md)
    labels = set(re.findall(r"\{#([A-Za-z0-9_:\-]+)\}", clean))
    labels.update(re.findall(r"\\label\{([^}]+)\}", clean))
    return labels


def extract_tex_labels(tex: str) -> set[str]:
    clean = re.sub(r"(?<!\\)%.*$", "", tex, flags=re.MULTILINE)
    return set(re.findall(r"\\label\{([^}]+)\}", clean))


def extract_decimal_tokens(text: str) -> set[str]:
    clean = strip_fenced_code(text)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
    clean = re.sub(r"(?<!\\)%.*$", "", clean, flags=re.MULTILINE)
    # Remove LaTeX dimension numbers like 0.8\linewidth, 10.5pt
    clean = re.sub(r"\d+\.\d+\s*(?:\\linewidth|\\textwidth|\\columnwidth|pt|cm|mm|in|em|ex)\b", "", clean)
    return set(re.findall(r"(?<![A-Za-z0-9_])(\d+\.\d+)(?![A-Za-z0-9_])", clean))


def parse_tex_logs(sub_dir: Path) -> dict[str, Any]:
    telemetry: dict[str, Any] = {
        "overfull_hbox_gt_2pt": [],
        "undefined_refs_or_cites": [],
        "missing_graphics": [],
        "pages_before_bibliography": None,
    }
    log_candidates = list((sub_dir / "build").glob("*.log")) + list(sub_dir.glob("*.log"))
    for lp in log_candidates:
        txt = lp.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\).*", txt):
            if float(m.group(1)) > 2.0:
                telemetry["overfull_hbox_gt_2pt"].append(m.group(0).strip())
        for m in re.finditer(r"LaTeX Warning: (?:Reference|Citation) `([^']+)' .* undefined.*", txt):
            telemetry["undefined_refs_or_cites"].append(m.group(0).strip())
        for m in re.finditer(r"LaTeX Error: File `([^']+)' not found\.", txt):
            telemetry["missing_graphics"].append(m.group(1))

    aux_candidates = list((sub_dir / "build").glob("*.aux")) + list(sub_dir.glob("*.aux"))
    for ap in aux_candidates:
        txt = ap.read_text(encoding="utf-8", errors="replace")
        bib_match = re.search(r"\\@writefile\{toc\}\{\\contentsline\s*\{section\}\{References\}\{(\d+)\}", txt)
        if bib_match:
            telemetry["pages_before_bibliography"] = int(bib_match.group(1))
    return telemetry


def cmd_format_verify(args: argparse.Namespace) -> int:
    ws = Path(args.workspace).resolve()
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if args.archive:
        ap = Path(args.archive).resolve()
        if not ap.is_file():
            print(json.dumps({"ok": False, "error": f"Archive not found: {ap}"}, indent=2))
            return 2
        blockers.extend(validate_archive(ap))

    if args.check_tex_dir:
        td = Path(args.check_tex_dir).resolve()
        if td.is_dir():
            for fp in sorted(td.rglob("*")):
                if fp.is_file() and fp.suffix.lower() in {".tex", ".sty", ".cls"}:
                    blockers.extend(scan_tex_for_shell_pipes(fp.read_text(encoding="utf-8", errors="replace"), fp.name))

    # .md <-> .tex parity check
    md_dir = ws / "manuscript/sections"
    tex_sec_dir = ws / "submission/sections"
    if md_dir.is_dir() and tex_sec_dir.is_dir():
        for md_file in sorted(md_dir.glob("*.md")):
            tex_file = tex_sec_dir / f"{md_file.stem}.tex"
            if not tex_file.is_file():
                blockers.append({"category": "parity", "issue": f"Missing converted LaTeX section {tex_file.name}"})
                continue
            md_txt = md_file.read_text(encoding="utf-8")
            tex_txt = tex_file.read_text(encoding="utf-8")
            missing_cites = sorted(extract_md_citations(md_txt) - extract_tex_citations(tex_txt))
            if missing_cites:
                blockers.append(
                    {"category": "parity", "issue": f"{tex_file.name} dropped citations: {missing_cites}"}
                )
            missing_labels = sorted(extract_md_labels(md_txt) - extract_tex_labels(tex_txt))
            if missing_labels:
                blockers.append(
                    {"category": "parity", "issue": f"{tex_file.name} dropped labels: {missing_labels}"}
                )
            missing_nums = sorted(extract_decimal_tokens(md_txt) - extract_decimal_tokens(tex_txt))
            if missing_nums:
                blockers.append(
                    {"category": "parity", "issue": f"{tex_file.name} dropped decimal tokens: {missing_nums}"}
                )

    sub_dir = ws / "submission"
    telemetry = parse_tex_logs(sub_dir) if sub_dir.is_dir() else {}
    if telemetry.get("undefined_refs_or_cites"):
        blockers.append(
            {"category": "tex_log", "issue": f"Undefined refs/cites: {telemetry['undefined_refs_or_cites'][:5]}"}
        )
    if telemetry.get("missing_graphics"):
        blockers.append({"category": "tex_log", "issue": f"Missing graphics: {telemetry['missing_graphics']}"})
    if telemetry.get("overfull_hbox_gt_2pt"):
        warnings.append(
            {"category": "tex_log", "issue": f"{len(telemetry['overfull_hbox_gt_2pt'])} Overfull \\hbox > 2pt warnings"}
        )

    # Double-blind scan across submission/*.tex and submission/sections/*.tex (body + % comments)
    state_data, _ = load_json_checked(ws / "paper_state.json")
    sub_mode = (state_data or {}).get("venue", {}).get("submission_mode", "double-blind")
    if sub_mode == "double-blind" and sub_dir.is_dir():
        tex_files = list(sub_dir.glob("*.tex")) + (list(tex_sec_dir.glob("*.tex")) if tex_sec_dir.is_dir() else [])
        path_leak_re = re.compile(r"(?:/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|C:\\\\Users\\\\[A-Za-z0-9._-]+)")
        gh_leak_re = re.compile(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.I)
        for tf in tex_files:
            content = tf.read_text(encoding="utf-8", errors="replace")
            if path_leak_re.search(content):
                blockers.append({"category": "anonymity", "issue": f"Local user path leak in {tf.name}"})
            if gh_leak_re.search(content):
                blockers.append({"category": "anonymity", "issue": f"Non-anonymous GitHub URL in {tf.name}"})
            if tf.name == "main.tex":
                if re.search(r"^\s*\\iclrfinalcopy\b", content, re.MULTILINE):
                    blockers.append({"category": "anonymity", "issue": "main.tex enables \\iclrfinalcopy in double-blind mode"})
                if re.search(r"\\usepackage\{cvpr\}", content):
                    blockers.append({"category": "anonymity", "issue": "main.tex uses camera-ready \\usepackage{cvpr} in double-blind mode"})

    result = {
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "warnings": warnings,
        "telemetry": telemetry,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="po_tools.py", description="PaperOEGM zero-dependency verification helper.")
    sub = p.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("state-sync", help="Validate paper_state.json, detect digest drift, regenerate STATUS.md.")
    p_sync.add_argument("--workspace", required=True, help="Path to paper workspace directory.")
    p_sync.add_argument("--stage", help="Stage key to update (e.g., po-draft, po-literature:early).")
    p_sync.add_argument("--status", default="approved", help="Stage status to write.")
    p_sync.add_argument("--inputs", help="Comma-separated workspace-relative input file paths.")
    p_sync.add_argument("--outputs", help="Comma-separated workspace-relative output file paths.")
    p_sync.add_argument("--probe", action="store_true", help="Refresh environment toolchain probe.")
    p_sync.add_argument("--check-only", action="store_true", help="Check digest drift without modifying files.")

    p_ro = sub.add_parser("check-readonly", help="Snapshot or verify tracked files inside <paper_workspace>/ only.")
    p_ro.add_argument("--workspace", required=True, help="Path to paper workspace directory.")
    p_ro.add_argument("--snapshot", required=True, help="Path to snapshot JSON file.")
    grp = p_ro.add_mutually_exclusive_group(required=True)
    grp.add_argument("--create", action="store_true", help="Create baseline SHA-256 snapshot.")
    grp.add_argument("--verify", action="store_true", help="Verify workspace against snapshot.")

    p_pre = sub.add_parser("review-preflight", help="Deterministic citation, synthetic/dirty, and inline run-metric audit.")
    p_pre.add_argument("--workspace", required=True, help="Path to paper workspace directory.")

    p_fmt = sub.add_parser("format-verify", help="Zip Slip, TeX shell-pipe, .md<->.tex parity, TeX .log, and double-blind scan.")
    p_fmt.add_argument("--workspace", required=True, help="Path to paper workspace directory.")
    p_fmt.add_argument("--archive", help="Optional fetched template archive (.zip/.tar*) to validate.")
    p_fmt.add_argument("--check-tex-dir", help="Optional directory of .tex/.sty/.cls files to scan for shell pipes.")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "state-sync":
        return cmd_state_sync(args)
    if args.command == "check-readonly":
        return cmd_check_readonly(args)
    if args.command == "review-preflight":
        return cmd_review_preflight(args)
    if args.command == "format-verify":
        return cmd_format_verify(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
