from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def discovered_skills(repo_root: Path) -> list[Path]:
    return sorted(p for p in (repo_root / "skills").iterdir() if p.is_dir())
