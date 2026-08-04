"""
Esse arquivo guarda as configurações do projeto (URLs, senha do banco,
pastas de dados/logs etc.), tudo num lugar só.

A função obter_configuracoes() pega esses valores do arquivo .env e devolve
prontos pra usar no resto do código.

A maioria dos valores tem um "valor padrão" (se não achar no .env, usa
esse). A URL do banco (DATABASE_URL) fica opcional por enquanto, porque
a etapa atual ainda grava a camada Bronze em Parquet local.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Configuracoes:
    api_url: str
    api_key: str | None
    request_timeout: int
    coin_top_n: int
    data_dir: Path
    log_dir: Path
    database_url: str | None


def obter_configuracoes() -> Configuracoes:
    return Configuracoes(
        api_url=os.getenv("API_URL", "https://api.coingecko.com/api/v3").rstrip("/"),
        api_key=os.getenv("API_KEY") or None,
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
        coin_top_n=int(os.getenv("COIN_TOP_N", "20")),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        log_dir=Path(os.getenv("LOG_DIR", "logs")),
        database_url=os.getenv("DATABASE_URL") or None,
    )
