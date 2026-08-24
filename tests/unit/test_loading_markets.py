from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine

from loading.markets import (
    carregar_mercados_bronze_postgres,
    extrair_data_referencia,
    preparar_dataframe_mercados,
)


def criar_parquet_mercados(tmp_path: Path) -> Path:
    caminho = tmp_path / "mercados_2026-08-03.parquet"
    dataframe = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 100,
                "market_cap": 1000,
                "market_cap_rank": 1,
                "total_volume": 500,
                "roi": {"times": 2},
                "source": "coingecko",
                "endpoint": "/coins/markets",
                "processing_date": "2026-08-03",
                "ingestion_timestamp": "2026-08-03T12:00:00+00:00",
            }
        ]
    )
    dataframe.to_parquet(caminho, index=False)

    return caminho


def test_extrair_data_referencia_usa_nome_do_arquivo():
    data_referencia = extrair_data_referencia("mercados_2026-08-03.parquet")

    assert data_referencia.isoformat() == "2026-08-03"


def test_extrair_data_referencia_rejeita_nome_fora_do_padrao():
    with pytest.raises(ValueError, match="mercados_YYYY-MM-DD"):
        extrair_data_referencia("arquivo.parquet")


def test_preparar_dataframe_mercados_adiciona_colunas_de_auditoria(tmp_path):
    caminho = tmp_path / "mercados_2026-08-03.parquet"
    dataframe = pd.DataFrame([{"id": "bitcoin", "roi": {"times": 2}}])

    resultado = preparar_dataframe_mercados(dataframe, caminho)

    assert resultado.loc[0, "data_referencia"].isoformat() == "2026-08-03"
    assert resultado.loc[0, "arquivo_origem"] == str(caminho)
    assert resultado.loc[0, "roi"] == '{"times": 2}'
    assert "carregado_em" in resultado.columns


def test_carregar_mercados_bronze_postgres_grava_sem_duplicar_rerun(tmp_path):
    caminho = criar_parquet_mercados(tmp_path)
    engine = create_engine(f"sqlite:///{tmp_path / 'teste.db'}")

    total_primeira_carga = carregar_mercados_bronze_postgres(
        caminho,
        engine=engine,
        schema="",
        tabela="coingecko_mercados",
    )
    total_segunda_carga = carregar_mercados_bronze_postgres(
        caminho,
        engine=engine,
        schema="",
        tabela="coingecko_mercados",
    )

    with engine.connect() as conexao:
        resultado = pd.read_sql_query("SELECT * FROM coingecko_mercados", conexao)

    assert total_primeira_carga == 1
    assert total_segunda_carga == 1
    assert len(resultado) == 1
    assert resultado.loc[0, "id"] == "bitcoin"


def test_carregar_mercados_bronze_postgres_adiciona_colunas_ausentes(tmp_path):
    caminho = criar_parquet_mercados(tmp_path)
    engine = create_engine(f"sqlite:///{tmp_path / 'teste.db'}")

    with engine.begin() as conexao:
        conexao.execute(
            """
            CREATE TABLE coingecko_mercados (
                id TEXT,
                symbol TEXT,
                name TEXT,
                current_price FLOAT,
                market_cap BIGINT,
                market_cap_rank BIGINT,
                total_volume BIGINT,
                data_referencia DATE
            )
            """
        )

    total = carregar_mercados_bronze_postgres(
        caminho,
        engine=engine,
        schema="",
        tabela="coingecko_mercados",
    )

    with engine.connect() as conexao:
        resultado = pd.read_sql_query("SELECT * FROM coingecko_mercados", conexao)

    assert total == 1
    assert resultado.loc[0, "source"] == "coingecko"
    assert resultado.loc[0, "endpoint"] == "/coins/markets"
