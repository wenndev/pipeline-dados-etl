"""Carrega dados Bronze de mercados para o Postgres."""

from __future__ import annotations

import json
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pandas_types
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from config import obter_configuracoes
from database.connection import criar_engine_postgres
from logger import obter_logger
from quality.markets import validar_arquivo_mercados_bronze

logger = obter_logger("carregar_mercados")

PADRAO_DATA_ARQUIVO = re.compile(r"mercados_(\d{4}-\d{2}-\d{2})\.parquet$")
PADRAO_IDENTIFICADOR_SQL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def extrair_data_referencia(caminho_parquet: str | Path) -> date:
    caminho = Path(caminho_parquet)
    resultado = PADRAO_DATA_ARQUIVO.match(caminho.name)

    if not resultado:
        raise ValueError(
            "Nome do arquivo deve seguir o padrão mercados_YYYY-MM-DD.parquet"
        )

    return date.fromisoformat(resultado.group(1))


def preparar_dataframe_mercados(
    dataframe: pd.DataFrame,
    caminho_parquet: str | Path,
) -> pd.DataFrame:
    dados = dataframe.copy()

    for coluna in dados.columns:
        dados[coluna] = dados[coluna].map(_serializar_valor_complexo)

    dados["data_referencia"] = extrair_data_referencia(caminho_parquet)
    dados["arquivo_origem"] = str(caminho_parquet)
    dados["carregado_em"] = datetime.now(UTC)

    return dados


def carregar_mercados_bronze_postgres(
    caminho_parquet: str | Path,
    engine: Engine | None = None,
    schema: str = "bronze",
    tabela: str = "coingecko_mercados",
) -> int:
    caminho = Path(caminho_parquet)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo Parquet não encontrado: {caminho}")

    configuracoes = obter_configuracoes()
    validar_arquivo_mercados_bronze(
        caminho,
        limite_esperado=configuracoes.coin_top_n,
    )

    dataframe = pd.read_parquet(caminho)
    dataframe = preparar_dataframe_mercados(dataframe, caminho)
    data_referencia = extrair_data_referencia(caminho)
    engine = engine or criar_engine_postgres()

    with engine.begin() as conexao:
        if schema:
            conexao.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

        _remover_particao_existente(
            conexao=conexao,
            schema=schema,
            tabela=tabela,
            data_referencia=data_referencia,
        )
        _adicionar_colunas_ausentes(
            conexao=conexao,
            dataframe=dataframe,
            schema=schema,
            tabela=tabela,
        )

        dataframe.to_sql(
            name=tabela,
            con=conexao,
            schema=schema or None,
            if_exists="append",
            index=False,
        )

    total_registros = len(dataframe)
    logger.info(
        "Carregados %s registros em %s.%s",
        total_registros,
        schema,
        tabela,
    )

    return total_registros


def _serializar_valor_complexo(valor: Any) -> Any:
    if isinstance(valor, dict | list):
        return json.dumps(valor, ensure_ascii=False)

    return valor


def _remover_particao_existente(
    conexao: Any,
    schema: str,
    tabela: str,
    data_referencia: date,
) -> None:
    nome_tabela = _nome_tabela_sql(schema=schema, tabela=tabela)
    tabela_existe = inspect(conexao).has_table(tabela, schema=schema or None)

    if tabela_existe:
        conexao.execute(
            text(f"DELETE FROM {nome_tabela} WHERE data_referencia = :data_referencia"),
            {"data_referencia": data_referencia},
        )


def _adicionar_colunas_ausentes(
    conexao: Any,
    dataframe: pd.DataFrame,
    schema: str,
    tabela: str,
) -> None:
    inspetor = inspect(conexao)

    if not inspetor.has_table(tabela, schema=schema or None):
        return

    colunas_existentes = {
        coluna["name"] for coluna in inspetor.get_columns(tabela, schema=schema or None)
    }
    nome_tabela = _nome_tabela_sql(schema=schema, tabela=tabela)

    for coluna in dataframe.columns:
        if coluna in colunas_existentes:
            continue

        tipo_sql = _tipo_sql_coluna(dataframe[coluna])
        conexao.execute(
            text(f"ALTER TABLE {nome_tabela} ADD COLUMN {_identificador_sql(coluna)} {tipo_sql}")
        )


def _tipo_sql_coluna(coluna: pd.Series) -> str:
    if pandas_types.is_integer_dtype(coluna):
        return "BIGINT"

    if pandas_types.is_float_dtype(coluna):
        return "DOUBLE PRECISION"

    if pandas_types.is_bool_dtype(coluna):
        return "BOOLEAN"

    if pandas_types.is_datetime64_any_dtype(coluna):
        return "TIMESTAMP"

    return "TEXT"


def _nome_tabela_sql(schema: str, tabela: str) -> str:
    if schema:
        return f"{_identificador_sql(schema)}.{_identificador_sql(tabela)}"

    return _identificador_sql(tabela)


def _identificador_sql(valor: str) -> str:
    if not PADRAO_IDENTIFICADOR_SQL.fullmatch(valor):
        raise ValueError(f"Identificador SQL inválido: {valor}")

    return f'"{valor}"'
