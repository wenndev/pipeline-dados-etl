from pathlib import Path


def test_project_structure_has_core_files():
    root = Path(__file__).resolve().parents[1]

    assert (root / "pyproject.toml").exists()
    assert (root / "docker-compose.yml").exists()
    assert (root / "src" / "config.py").exists()
    assert (root / "src" / "logger.py").exists()
    assert (root / "src" / "api" / "coingecko.py").exists()
    assert (root / "src" / "database" / "connection.py").exists()
    assert (root / "src" / "ingestion" / "markets.py").exists()
    assert (root / "src" / "loading" / "markets.py").exists()
    assert (root / "src" / "storage" / "parquet.py").exists()
