"""Validate relative Markdown links, #anchors, and ${CLAUDE_PLUGIN_ROOT} paths across repo and packed bundles."""

import re
import subprocess
import sys
from pathlib import Path

FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CLAUDE_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`'\"()]+)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def slugify_heading(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def check_markdown_tree(base: Path, md_files: list[Path]) -> None:
    for md in md_files:
        raw = md.read_text(encoding="utf-8")
        no_code = FENCED_RE.sub("", raw)
        no_inline_code = re.sub(r"`[^`]*`", "", no_code)
        headings = {slugify_heading(h) for h in HEADING_RE.findall(no_code)}

        for target in MD_LINK_RE.findall(no_inline_code):
            target = target.strip().split()[0]
            if re.match(r"^(?:https?|mailto|file):", target, re.I):
                continue
            if target.startswith("#"):
                anchor = target[1:].lower()
                assert anchor in headings, f"{md}: broken intra-doc anchor #{anchor}"
                continue
            rel_part, _, frag = target.partition("#")
            if rel_part.startswith("${CLAUDE_PLUGIN_ROOT}/"):
                resolved = (base / rel_part.removeprefix("${CLAUDE_PLUGIN_ROOT}/")).resolve()
            else:
                resolved = (md.parent / rel_part).resolve()
            assert resolved.exists(), f"{md}: broken relative link '{target}' -> {resolved}"
            if frag and resolved.suffix == ".md":
                t_no_code = FENCED_RE.sub("", resolved.read_text(encoding="utf-8"))
                t_headings = {slugify_heading(h) for h in HEADING_RE.findall(t_no_code)}
                assert frag.lower() in t_headings, f"{md}: broken target anchor '{target}'"

        for rel in CLAUDE_ROOT_RE.findall(no_code):
            if "*" in rel or "<" in rel or rel.endswith("/"):
                continue
            assert (base / rel).exists(), f"{md}: missing ${{CLAUDE_PLUGIN_ROOT}}/{rel}"


def test_repo_link_integrity(repo_root: Path) -> None:
    md_files = [
        p
        for p in sorted(repo_root.rglob("*.md"))
        if ".git" not in p.parts
        and ".pytest_cache" not in p.parts
        and "tests" not in p.parts
        and not (p.parent.name == "designs" and "docs" in p.parts)
    ]
    assert len(md_files) >= 25
    check_markdown_tree(repo_root, md_files)


def test_packed_bundle_link_integrity(repo_root: Path, tmp_path: Path) -> None:
    res = subprocess.run(
        [sys.executable, str(repo_root / "scripts/pack_plugin.py"), "--target", "all", "--output", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr
    for target in ("antigravity", "claude", "openai"):
        bundle_dir = tmp_path / f"paper-oegm-{target}"
        md_files = sorted(bundle_dir.rglob("*.md"))
        check_markdown_tree(bundle_dir, md_files)
