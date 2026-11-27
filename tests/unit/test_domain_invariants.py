"""PaperOEGM domain invariants: read-only critic neutrality, zero legacy leaks, and starter template checks."""

import re
from pathlib import Path

FORBIDDEN_LEGACY_STRINGS = (
    "SEMANTIC_SCHOLAR_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "PaperBanana",
    "UNIVERSAL_NO_LEAKAGE_PROMPT",
    "Never explicitly state a limitation",
    "Ambitious AI Researcher",
    "paper_writing_cli.py",
)


def test_root_agents_harness_neutral_and_readonly(repo_root: Path) -> None:
    for agent_md in sorted((repo_root / "agents").glob("po-*.md")):
        text = agent_md.read_text(encoding="utf-8")
        assert "invoke_subagent" not in text, f"{agent_md.name} must stay harness-neutral (no invoke_subagent)"
        assert "Never" in text and "read-only" in text.lower()
        non_prohibition = "\n".join(l for l in text.splitlines() if "never" not in l.lower())
        assert not re.search(r"\b(?:run|execute)\s+(?:bash|shell)\s+commands\b", non_prohibition, re.I)
        assert not re.search(r"\b(?:write_file|edit_file|run_command)\b", text)


def test_skills_never_invoke_claude_skill_tool(discovered_skills: list[Path]) -> None:
    for skill_dir in discovered_skills:
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert not re.search(r"\bSkill\s*\(", text), f"{skill_dir.name} must not call Skill(...)"
        assert not re.search(r"(?<!Never )invoke\s+Claude's\s+`Skill`\s+tool", text)


def test_zero_legacy_strings_in_shipped_files(repo_root: Path) -> None:
    scan_files: list[Path] = []
    for folder in ("skills", "agents", "resources"):
        scan_files.extend(p for p in (repo_root / folder).rglob("*") if p.is_file())
    # Top-level bundled docs/*.md only (explicitly excluding docs/designs/)
    scan_files.extend(sorted((repo_root / "docs").glob("*.md")))
    scan_files.append(repo_root / "README.md")

    for fp in scan_files:
        if fp.suffix.lower() in {".png", ".svg"}:
            continue
        text = fp.read_text(encoding="utf-8", errors="ignore")
        for bad in FORBIDDEN_LEGACY_STRINGS:
            assert bad not in text, f"Forbidden legacy string '{bad}' found in {fp.relative_to(repo_root)}"


def test_starter_templates_invariants(repo_root: Path) -> None:
    tpl_root = repo_root / "resources/templates"
    for venue in ("cvpr2025", "iclr2025"):
        assert (tpl_root / venue / "template.tex").is_file()
        assert (tpl_root / venue / "guidelines.md").is_file()
        assert (tpl_root / venue / "references.bib").is_file()

    cvpr_tex = (tpl_root / "cvpr2025/template.tex").read_text(encoding="utf-8")
    assert "\\usepackage[review]{cvpr}" in cvpr_tex
    assert "12345678" not in cvpr_tex

    # Obsolete/non-redistributable standard TeX Live files must be absent
    all_names = {p.name for p in tpl_root.rglob("*") if p.is_file()}
    assert "natbib.sty" not in all_names
    assert "fancyhdr.sty" not in all_names
