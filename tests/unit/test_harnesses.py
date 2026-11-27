"""Verify cross-manifest parity, icon invariants, harness docs, and backticked plugin paths."""

import json
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

SHARED_FIELDS = ("name", "version", "description", "author", "homepage", "repository", "license")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_five_manifests_synchronized(repo_root: Path) -> None:
    root_m = load_json(repo_root / "plugin.json")
    claude_m = load_json(repo_root / ".claude-plugin/plugin.json")
    claude_mkt = load_json(repo_root / ".claude-plugin/marketplace.json")
    codex_m = load_json(repo_root / ".codex-plugin/plugin.json")
    codex_mkt = load_json(repo_root / ".agents/plugins/marketplace.json")

    assert "$schema" not in root_m
    assert root_m["name"] == "paper-oegm"
    assert root_m["displayName"] == "PaperOEGM"
    assert len(root_m["displayName"]) <= 30
    assert root_m["author"]["name"] == "Chen-XueWen"

    for field in SHARED_FIELDS:
        assert claude_m[field] == root_m[field], f"Claude mismatch on {field}"
        assert codex_m[field] == root_m[field], f"Codex mismatch on {field}"

    assert claude_m["displayName"] == root_m["displayName"]
    assert claude_mkt["name"] == "paper-oegm"
    assert claude_mkt["owner"]["name"] == "Chen-XueWen"
    assert claude_mkt["plugins"][0]["name"] == "paper-oegm"
    assert claude_mkt["plugins"][0]["source"] == "./"

    openai_ext = root_m["extensions"]["com.openai"]
    assert openai_ext["requires_local_executor"] is True
    assert codex_m["requires_local_executor"] is True
    assert codex_m["skills"] == "./skills/"
    assert codex_m["interface"] == openai_ext["interface"]

    iface = codex_m["interface"]
    assert len(iface["displayName"]) <= 30
    assert len(iface["shortDescription"]) <= 30
    assert len(iface["longDescription"]) <= 4000
    assert iface["developerName"] == "Chen-XueWen"
    for url_key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        assert iface[url_key].startswith("https://")
    for url_key in ("documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl"):
        assert claude_m[url_key].startswith("https://")

    assert codex_mkt["name"] == "paper-oegm"
    assert codex_mkt["interface"]["displayName"] == "PaperOEGM"
    assert codex_mkt["plugins"][0]["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}

    for m in (root_m, claude_m, codex_m, openai_ext):
        for forbidden in ("hooks", "mcpServers", "mcp", "apps"):
            assert forbidden not in m


def test_icons_valid(repo_root: Path) -> None:
    svg_path = repo_root / "assets/icon.svg"
    assert svg_path.stat().st_size <= 5 * 1024 * 1024
    tree = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    w = int(tree.attrib["width"])
    h = int(tree.attrib["height"])
    assert w == h >= 48

    png_bytes = (repo_root / ".claude-plugin/icon.png").read_bytes()
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    pw, ph = struct.unpack(">II", png_bytes[16:24])
    assert (pw, ph) == (512, 512)


def test_skill_harness_links_and_backticked_paths(repo_root: Path, discovered_skills: list[Path]) -> None:
    path_re = re.compile(r"`((?:resources|agents|docs|skills)/[A-Za-z0-9_.\-/]+)`")
    for skill_dir in discovered_skills:
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert "[Codex integration](../../docs/codex.md)" in text
        assert "${CLAUDE_PLUGIN_ROOT}/docs/claude.md" in text
        for rel in path_re.findall(text):
            if "*" in rel or "<" in rel or rel.endswith("/"):
                continue
            assert (repo_root / rel).exists(), f"{skill_dir.name}/SKILL.md references missing path: {rel}"

    for agent_md in (repo_root / "agents").glob("*.md"):
        text = agent_md.read_text(encoding="utf-8")
        for rel in path_re.findall(text):
            if "*" in rel or "<" in rel or rel.endswith("/"):
                continue
            assert (repo_root / rel).exists(), f"{agent_md.name} references missing path: {rel}"


def test_harness_docs_override_and_verification_labels(repo_root: Path) -> None:
    for doc in ("docs/harnesses.md", "docs/claude.md", "docs/codex.md"):
        text = (repo_root / doc).read_text(encoding="utf-8")
        assert "PaperOEGM artifact directory:" in text
        assert "symbolic links" in text.lower()

    for doc in ("docs/harnesses.md", "TESTING.md"):
        text = (repo_root / doc).read_text(encoding="utf-8")
        assert "Live-verified upon implementation" in text
        assert "Packaged and structurally verified via offline `pytest`" in text
