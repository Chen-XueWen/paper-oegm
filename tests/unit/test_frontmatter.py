"""Validate YAML frontmatter across all 10 skills, 5 root agents, and 5 Claude adapters."""

from pathlib import Path
import yaml

EXPECTED_SKILLS = {
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
}

EXPECTED_AGENTS = {
    "po-peer-reviewer",
    "po-evidence-auditor",
    "po-citation-auditor",
    "po-visual-format-critic",
    "po-clarity-reader",
}


def parse_frontmatter(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    assert raw.startswith("---\n"), f"{path} must start with YAML frontmatter"
    parts = raw.split("---", 2)
    assert len(parts) >= 3, f"{path} has unclosed YAML frontmatter"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), f"{path} frontmatter must parse as a mapping"
    return data


def test_skill_frontmatter(discovered_skills: list[Path]) -> None:
    found = {p.name for p in discovered_skills}
    assert found == EXPECTED_SKILLS
    for skill_dir in discovered_skills:
        fm = parse_frontmatter(skill_dir / "SKILL.md")
        assert fm.get("name") == skill_dir.name
        assert fm.get("license") == "Apache-2.0"
        assert fm.get("disable-model-invocation") is True
        desc = fm.get("description", "")
        assert isinstance(desc, str) and len(desc.strip()) >= 20


def test_root_and_claude_agent_frontmatter(repo_root: Path) -> None:
    root_agents = sorted((repo_root / "agents").glob("*.md"))
    claude_agents = sorted((repo_root / ".claude-plugin/agents").glob("*.md"))

    assert {p.stem for p in root_agents} == EXPECTED_AGENTS
    assert {p.stem for p in claude_agents} == EXPECTED_AGENTS

    for p in root_agents:
        fm = parse_frontmatter(p)
        assert fm.get("name") == p.stem
        assert isinstance(fm.get("description"), str) and fm["description"].strip()
        for claude_only in ("tools", "omitClaudeMd", "memory", "model"):
            assert claude_only not in fm, f"Root agent {p.name} must not declare {claude_only}"

    for p in claude_agents:
        fm = parse_frontmatter(p)
        assert fm.get("name") == p.stem
        assert isinstance(fm.get("description"), str) and fm["description"].strip()
        assert set(fm.get("tools", [])) == {"Read", "Grep", "Glob"}
        assert fm.get("model") == "inherit"
        assert fm.get("omitClaudeMd") is True
        assert "memory" not in fm
