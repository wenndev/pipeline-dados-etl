"""Cria conexoes com o banco usado pelo pipeline."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import Configuracoes, obter_configuracoes


def criar_engine_postgres(configuracoes: Configuracoes | None = None) -> Engine:
    configuracoes = configuracoes or obter_configuracoes()

    if not configuracoes.database_url:
        raise ValueError("DATABASE_URL precisa estar configurada para acessar o banco")

    return create_engine(configuracoes.database_url)
