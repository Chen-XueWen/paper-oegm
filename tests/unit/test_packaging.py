"""Test scripts/pack_plugin.py across antigravity, claude, and openai targets plus edge cases."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest
import yaml

PALETTE = {
    "#1b6ef3": {"#1b6ef3", "#7cacf8"},
    "#e86e00": {"#e86e00", "#ff8d41"},
}

FORBIDDEN_PREFIXES = (
    "tests/",
    "scripts/",
    "docs/designs/",
    ".agents/",
    ".git/",
)

FORBIDDEN_FILES = {
    "TESTING.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "AGENTS.md",
    "pyproject.toml",
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
}


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_packer(repo_root: Path, target: str, out_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(repo_root / "scripts/pack_plugin.py"), "--target", target, "--output", str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_deterministic_builds_all_targets(repo_root: Path, tmp_path: Path) -> None:
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    r1 = run_packer(repo_root, "all", out1)
    r2 = run_packer(repo_root, "all", out2)
    assert r1.returncode == 0, r1.stderr
    assert r2.returncode == 0, r2.stderr

    for target in ("antigravity", "claude", "openai"):
        z1 = out1 / f"paper-oegm-{target}.zip"
        z2 = out2 / f"paper-oegm-{target}.zip"
        assert z1.is_file() and z2.is_file()
        assert sha256_bytes(z1) == sha256_bytes(z2), f"Non-reproducible ZIP for {target}"

        with zipfile.ZipFile(z1) as zf:
            names = set(zf.namelist())
            for info in zf.infolist():
                assert info.date_time == (1980, 1, 1, 0, 0, 0)

        # Required shared runtime assets
        assert "plugin.json" in names
        assert "LICENSE" in names
        assert "NOTICE" in names
        assert "THIRD_PARTY_NOTICES.md" in names
        assert "README.md" in names
        assert "resources/scripts/po_tools.py" in names
        assert "docs/assets/readme-header.svg" in names
        assert "docs/assets/workflow-overview.svg" in names
        assert "resources/templates/cvpr2025/cvpr.sty" in names
        assert "resources/templates/cvpr2025/ieeenat_fullname.bst" in names
        assert "resources/templates/cvpr2025/references.bib" in names
        assert "resources/templates/cvpr2025/template.tex" in names
        assert "resources/templates/cvpr2025/guidelines.md" in names
        assert "resources/templates/iclr2025/iclr2025_conference.sty" in names
        assert "resources/templates/iclr2025/iclr2025_conference.bst" in names
        assert "resources/templates/iclr2025/references.bib" in names
        assert "resources/templates/iclr2025/template.tex" in names
        assert "resources/templates/iclr2025/guidelines.md" in names

        # 10 skills and 5 root agents
        assert len([n for n in names if re.fullmatch(r"skills/po-[^/]+/SKILL\.md", n)]) == 10
        assert len([n for n in names if re.fullmatch(r"agents/po-[^/]+\.md", n)]) == 5

        # Host-specific inclusions/exclusions
        if target == "claude":
            assert ".claude-plugin/plugin.json" in names
            assert ".claude-plugin/icon.png" in names
            assert ".codex-plugin/plugin.json" not in names
        elif target == "openai":
            assert ".codex-plugin/plugin.json" in names
            assert ".claude-plugin/plugin.json" not in names
        else:
            assert ".claude-plugin/plugin.json" not in names
            assert ".codex-plugin/plugin.json" not in names

        # Forbidden dev/test/design files excluded
        for n in names:
            assert n not in FORBIDDEN_FILES, f"Forbidden file bundled: {n}"
            assert not any(n.startswith(p) for p in FORBIDDEN_PREFIXES), f"Forbidden prefix bundled: {n}"
            assert not n.endswith(("TEST.md", "test_scenarios.yaml"))


def test_openai_yaml_and_skill_icon_palettes(discovered_skills: list[Path]) -> None:
    hex_re = re.compile(r"#[0-9a-fA-F]{6}")
    for skill_dir in discovered_skills:
        oy = yaml.safe_load((skill_dir / "agents/openai.yaml").read_text(encoding="utf-8"))["interface"]
        desc = oy["short_description"]
        assert 25 <= len(desc) <= 64, f"{skill_dir.name}: len={len(desc)}"
        brand = oy["brand_color"].lower()
        assert brand in PALETTE

        svg_text = (skill_dir / "assets/icon.svg").read_text(encoding="utf-8")
        tree = ET.fromstring(svg_text)
        assert tree.attrib.get("viewBox") == "0 0 24 24"
        titles = [el.text for el in tree.iter() if el.tag.endswith("title") and el.text]
        assert titles, f"{skill_dir.name}/assets/icon.svg missing <title>"
        colors = {c.lower() for c in hex_re.findall(svg_text)}
        assert colors == PALETTE[brand], f"{skill_dir.name}: SVG colors {colors} != {PALETTE[brand]}"


def test_packager_refuses_overwrite(repo_root: Path, tmp_path: Path) -> None:
    assert run_packer(repo_root, "claude", tmp_path).returncode == 0
    second = run_packer(repo_root, "claude", tmp_path)
    assert second.returncode == 1
    assert "already exists" in second.stderr


def test_packager_refuses_symlink_and_hooks(repo_root: Path, tmp_path: Path) -> None:
    clone = tmp_path / "repo_copy"
    shutil.copytree(
        repo_root,
        clone,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "dist", "paper_workspace"),
    )

    # 1. Inject hooks into plugin.json -> must reject
    pjson = clone / "plugin.json"
    data = json.loads(pjson.read_text(encoding="utf-8"))
    data["hooks"] = {"PreToolUse": []}
    pjson.write_text(json.dumps(data, indent=2), encoding="utf-8")
    r_hooks = run_packer(clone, "claude", tmp_path / "out_hooks")
    assert r_hooks.returncode == 1
    assert "hooks" in r_hooks.stderr.lower()

    # Restore plugin.json, replace NOTICE with a symlink -> must reject
    pjson.write_text((repo_root / "plugin.json").read_text(encoding="utf-8"), encoding="utf-8")
    notice = clone / "NOTICE"
    notice.unlink()
    notice.symlink_to(clone / "LICENSE")
    r_sym = run_packer(clone, "antigravity", tmp_path / "out_sym")
    assert r_sym.returncode == 1
    assert "symlink" in r_sym.stderr.lower()
