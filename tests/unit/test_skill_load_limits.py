"""Enforce whole-file load-size ceilings for all skills and root agents."""

from pathlib import Path

MAX_SKILL_BYTES = 12_000
MAX_SKILL_LINES = 250
MAX_AGENT_BYTES = 6_000


def test_skill_whole_file_limits(discovered_skills: list[Path]) -> None:
    assert len(discovered_skills) == 10
    for skill_dir in discovered_skills:
        skill_md = skill_dir / "SKILL.md"
        raw = skill_md.read_text(encoding="utf-8")
        byte_size = len(raw.encode("utf-8"))
        line_count = len(raw.splitlines())
        assert byte_size <= MAX_SKILL_BYTES, f"{skill_md} is {byte_size} bytes (> {MAX_SKILL_BYTES})"
        assert line_count <= MAX_SKILL_LINES, f"{skill_md} has {line_count} lines (> {MAX_SKILL_LINES})"


def test_root_agent_whole_file_limits(repo_root: Path) -> None:
    agents = sorted((repo_root / "agents").glob("*.md"))
    assert len(agents) == 5
    for agent_md in agents:
        byte_size = len(agent_md.read_text(encoding="utf-8").encode("utf-8"))
        assert byte_size <= MAX_AGENT_BYTES, f"{agent_md} is {byte_size} bytes (> {MAX_AGENT_BYTES})"
