import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_url: str
    api_key: str | None
    request_timeout: int
    coin_top_n: int
    data_dir: Path
    log_dir: Path


def get_settings() -> Settings:
    return Settings(
        api_url=os.getenv("API_URL", "https://api.coingecko.com/api/v3").rstrip("/"),
        api_key=os.getenv("API_KEY") or None,
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
        coin_top_n=int(os.getenv("COIN_TOP_N", "20")),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        log_dir=Path(os.getenv("LOG_DIR", "logs")),
    )

