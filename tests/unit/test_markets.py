from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from config import Configuracoes
from ingestion.markets import (
    executar_ingestao_mercados,
    extrair_mercados,
    montar_caminho_saida_mercados,
    montar_parametros_mercados,
)


class ClienteCoinGeckoFalso:
    def __init__(self, resposta):
        self.resposta = resposta
        self.chamadas = []

    def get(self, endpoint, params=None):
        self.chamadas.append({"endpoint": endpoint, "params": params})
        return self.resposta


def criar_configuracoes(tmp_path: Path) -> Configuracoes:
    return Configuracoes(
        api_url="https://api.coingecko.com/api/v3",
        api_key=None,
        request_timeout=10,
        coin_top_n=20,
        data_dir=tmp_path,
        log_dir=tmp_path / "logs",
        database_url=None,
        timezone="America/Sao_Paulo",
    )


def test_montar_parametros_mercados_usa_padroes_do_projeto(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)

    parametros = montar_parametros_mercados(configuracoes)

    assert parametros == {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d,1y",
    }


def test_montar_caminho_saida_mercados_usa_particao_de_data(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)
    data_execucao = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)

    caminho_saida = montar_caminho_saida_mercados(
        configuracoes,
        data_execucao=data_execucao,
    )

    assert caminho_saida == (
        tmp_path
        / "bronze"
        / "coingecko"
        / "mercados"
        / "mercados_2026-07-28.parquet"
    )


def test_montar_caminho_saida_mercados_converte_para_timezone_do_projeto(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)
    data_execucao = datetime(2026, 8, 4, 2, 0, tzinfo=UTC)

    caminho_saida = montar_caminho_saida_mercados(
        configuracoes,
        data_execucao=data_execucao,
    )

    assert caminho_saida.name == "mercados_2026-08-03.parquet"


def test_extrair_mercados_chama_endpoint_da_coingecko(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)
    cliente = ClienteCoinGeckoFalso([{"id": "bitcoin"}])

    dados = extrair_mercados(cliente=cliente, configuracoes=configuracoes)

    assert dados == [{"id": "bitcoin"}]
    assert cliente.chamadas == [
        {
            "endpoint": "/coins/markets",
            "params": montar_parametros_mercados(configuracoes),
        }
    ]


def test_extrair_mercados_rejeita_resposta_inesperada(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)
    cliente = ClienteCoinGeckoFalso({"id": "bitcoin"})

    with pytest.raises(TypeError, match="deve ser uma lista"):
        extrair_mercados(cliente=cliente, configuracoes=configuracoes)


def test_executar_ingestao_mercados_salva_parquet(tmp_path):
    configuracoes = criar_configuracoes(tmp_path)
    cliente = ClienteCoinGeckoFalso(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 100,
                "market_cap": 1000,
                "market_cap_rank": 1,
                "total_volume": 500,
            }
        ]
    )
    data_execucao = datetime(2026, 7, 28, tzinfo=UTC)

    caminho_saida = executar_ingestao_mercados(
        cliente=cliente,
        configuracoes=configuracoes,
        data_execucao=data_execucao,
    )

    assert caminho_saida.exists()

    dataframe = pd.read_parquet(caminho_saida)
    assert dataframe.to_dict(orient="records") == [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 100,
            "market_cap": 1000,
            "market_cap_rank": 1,
            "total_volume": 500,
        }
    ]
