from pathlib import Path


def test_project_structure_has_core_files():
    root = Path(__file__).resolve().parents[1]

    assert (root / "pyproject.toml").exists()
    assert (root / "docker-compose.yml").exists()
    assert (root / "src").exists()
