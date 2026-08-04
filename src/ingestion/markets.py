"""Extrai dados atuais de mercado da CoinGecko para a camada Bronze."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from api.coingecko import ClienteCoinGecko
from config import Configuracoes, obter_configuracoes
from logger import obter_logger
from storage.parquet import salvar_parquet

logger = obter_logger("mercados")


def montar_parametros_mercados(configuracoes: Configuracoes) -> dict[str, Any]:
    return {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": configuracoes.coin_top_n,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d,1y",
    }


def montar_caminho_saida_mercados(
    configuracoes: Configuracoes,
    data_execucao: datetime | None = None,
) -> Path:
    data_atual = data_execucao or datetime.now(UTC)
    particao_data = data_atual.strftime("%Y-%m-%d")

    return (
        configuracoes.data_dir
        / "bronze"
        / "coingecko"
        / "mercados"
        / f"mercados_{particao_data}.parquet"
    )


def extrair_mercados(
    cliente: ClienteCoinGecko | None = None,
    configuracoes: Configuracoes | None = None,
) -> list[dict[str, Any]]:
    configuracoes = configuracoes or obter_configuracoes()
    cliente = cliente or ClienteCoinGecko(configuracoes=configuracoes)

    dados = cliente.get(
        "/coins/markets",
        params=montar_parametros_mercados(configuracoes),
    )

    if not isinstance(dados, list):
        raise TypeError("A resposta de mercados da CoinGecko deve ser uma lista")

    return dados


def executar_ingestao_mercados(
    cliente: ClienteCoinGecko | None = None,
    configuracoes: Configuracoes | None = None,
    data_execucao: datetime | None = None,
) -> Path:
    configuracoes = configuracoes or obter_configuracoes()
    dados = extrair_mercados(cliente=cliente, configuracoes=configuracoes)
    caminho_saida = montar_caminho_saida_mercados(
        configuracoes,
        data_execucao=data_execucao,
    )

    logger.info("Salvando %s registros de mercado em %s", len(dados), caminho_saida)
    return salvar_parquet(dados, caminho_saida)
