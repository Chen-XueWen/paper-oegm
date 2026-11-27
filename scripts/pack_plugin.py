#!/usr/bin/env python3
# Copyright 2026 Chen-XueWen
# Adapted from Google's Elephant-Goldfish Model (EGM) pack_plugin.py (Apache-2.0).
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
"""Build deterministic PaperOEGM runtime folders and ZIPs without development files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

SKILLS = (
    "po-start",
    "po-exp-design",
    "po-exp-code",
    "po-outline",
    "po-literature",
    "po-visuals",
    "po-draft",
    "po-review",
    "po-resolve",
    "po-format",
)

AGENTS = (
    "po-peer-reviewer",
    "po-evidence-auditor",
    "po-citation-auditor",
    "po-visual-format-critic",
    "po-clarity-reader",
)

PROTOCOLS = (
    "workspace_contract.md",
    "experiment_safety.md",
    "citation_provenance.md",
    "visual_standards.md",
    "markdown_manuscript.md",
    "formatting_and_build.md",
)

REVIEW_STANDARDS = (
    "peer-review-standard.md",
    "evidence-audit-standard.md",
    "citation-audit-standard.md",
    "visual-format-standard.md",
    "clarity-standard.md",
)

REQUIRED_SHARED = (
    "plugin.json",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "README.md",
    "assets/icon.svg",
    "docs/assets/readme-header.svg",
    "docs/assets/workflow-overview.svg",
    "docs/harnesses.md",
    "docs/claude.md",
    "docs/codex.md",
    "docs/privacy.md",
    "resources/README.md",
    "resources/execution_instructions.md",
    "resources/scripts/po_tools.py",
) + tuple(
    f"skills/{skill}/{name}"
    for skill in SKILLS
    for name in ("SKILL.md", "agents/openai.yaml", "assets/icon.svg")
) + tuple(f"agents/{agent}.md" for agent in AGENTS) + tuple(
    f"resources/protocols/{p}" for p in PROTOCOLS
) + tuple(f"resources/review_standards/{s}" for s in REVIEW_STANDARDS)

OPTIONAL_SHARED = (
    "skills/po-*/references/*",
    "resources/templates/*/*.tex",
    "resources/templates/*/*.sty",
    "resources/templates/*/*.bst",
    "resources/templates/*/*.cls",
    "resources/templates/*/*.bib",
    "resources/templates/*/*.md",
)

HOST = {
    "antigravity": (),
    "claude": (
        ".claude-plugin/plugin.json",
        ".claude-plugin/icon.png",
        ".claude-plugin/agents/po-*.md",
    ),
    "openai": (".codex-plugin/plugin.json",),
}

HOST_REQUIRED = {
    "antigravity": ("plugin.json",),
    "claude": (".claude-plugin/plugin.json", ".claude-plugin/icon.png")
    + tuple(f".claude-plugin/agents/{a}.md" for a in AGENTS),
    "openai": (".codex-plugin/plugin.json",),
}


def _readme_local_images(root: Path) -> list[str]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    refs: list[str] = []
    for m in re.finditer(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', readme, flags=re.I):
        refs.append(m.group(1))
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        refs.append(m.group(1).split()[0])
    return [r for r in refs if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", r)]


def build(root: Path, target: str, output: Path) -> tuple[Path, Path]:
    """Write a new runtime folder and reproducible ZIP; refuse unsafe inputs or overwrites."""
    if target not in HOST:
        raise ValueError(f"Unsupported target: {target}")
    root = root.resolve()
    output = output.resolve()
    folder = output / f"paper-oegm-{target}"
    archive = folder.with_suffix(".zip")

    if any(p.exists() or p.is_symlink() for p in (folder, archive)):
        raise ValueError(f"Output folder or ZIP already exists: {folder}")
    if folder == root or root.is_relative_to(folder):
        raise ValueError("Output must not contain the source tree")

    files: set[Path] = set()
    patterns = REQUIRED_SHARED + OPTIONAL_SHARED + HOST[target]
    for pattern in patterns:
        for path in root.glob(pattern):
            relative = path.relative_to(root)
            if any(
                (root / Path(*relative.parts[:i])).is_symlink()
                for i in range(1, len(relative.parts) + 1)
            ):
                raise ValueError(f"Symlink in runtime path: {relative}")
            if not path.resolve().is_relative_to(root):
                raise ValueError(f"Path escapes source tree: {relative}")
            if path.is_file():
                files.add(relative)

    for name in REQUIRED_SHARED + HOST_REQUIRED[target]:
        if Path(name) not in files:
            raise ValueError(f"Missing required file: {name}")

    manifest_rel = HOST_REQUIRED[target][0]
    manifest = json.loads((root / manifest_rel).read_text(encoding="utf-8"))
    portable = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    openai_ext = portable.get("extensions", {}).get("com.openai", {})

    for metadata in (manifest, portable, openai_ext):
        if metadata.get("hooks"):
            raise ValueError("Directory packages cannot contain hooks")
        for forbidden_key in ("mcpServers", "mcp", "apps"):
            if metadata.get(forbidden_key):
                raise ValueError(f"Runtime builder rejects unsupported key: {forbidden_key}")

    references: list[str] = []
    agents = manifest.get("agents", [])
    if not isinstance(agents, (str, list)):
        raise ValueError(f"Invalid manifest agents: {agents!r}")
    references.extend([agents] if isinstance(agents, str) else list(agents))

    if target == "openai":
        interfaces = [manifest.get("interface", {})]
        if "interface" in openai_ext:
            interfaces.append(openai_ext["interface"])
        for interface in interfaces:
            for key in ("composerIcon", "logo"):
                if not interface.get(key):
                    raise ValueError(f"Missing OpenAI interface reference: {key}")
                references.append(interface[key])
    elif target == "claude":
        references.append(manifest.get("icon", "./.claude-plugin/icon.png"))
    else:
        if portable.get("logo"):
            references.append(portable["logo"])

    references.extend(_readme_local_images(root))

    for ref in references:
        p = Path(ref)
        if p.is_absolute() or ".." in p.parts or p not in files:
            raise ValueError(f"Unbundled manifest or README reference: {ref}")

    output.mkdir(parents=True, exist_ok=True)
    folder.mkdir()
    with tempfile.TemporaryDirectory(prefix=".paper-oegm-", dir=output) as temporary:
        staged = Path(temporary) / archive.name
        with zipfile.ZipFile(staged, "x", zipfile.ZIP_DEFLATED) as bundle:
            for relative in sorted(files):
                data = (root / relative).read_bytes()
                destination = folder / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                destination.chmod(0o644)
                info = zipfile.ZipInfo(relative.as_posix(), (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, data)
        archive.hardlink_to(staged)

    return folder, archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        required=True,
        choices=(*HOST.keys(), "all"),
        help="Runtime target to build (or 'all').",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output directory.")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    targets = tuple(HOST.keys()) if args.target == "all" else (args.target,)
    try:
        for t in targets:
            runtime, bundle = build(root, t, args.output)
            print(f"[{t}] Runtime: {runtime}\n[{t}] ZIP: {bundle}")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
