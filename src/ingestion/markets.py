"""Extrai dados atuais de mercado da CoinGecko para a camada Bronze."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from api.coingecko import ClienteCoinGecko
from config import Configuracoes, obter_configuracoes
from logger import obter_logger
from quality.markets import validar_mercados
from storage.parquet import salvar_parquet

logger = obter_logger("mercados")

ENDPOINT_MERCADOS = "/coins/markets"
FONTE_MERCADOS = "coingecko"


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
    fuso_horario = ZoneInfo(configuracoes.timezone)
    data_atual = data_execucao or datetime.now(fuso_horario)
    data_atual = data_atual.astimezone(fuso_horario)
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
        ENDPOINT_MERCADOS,
        params=montar_parametros_mercados(configuracoes),
    )

    if not isinstance(dados, list):
        raise TypeError("A resposta de mercados da CoinGecko deve ser uma lista")

    return dados


def adicionar_metadados_mercados(
    dados: list[dict[str, Any]],
    configuracoes: Configuracoes,
    data_execucao: datetime | None = None,
) -> list[dict[str, Any]]:
    fuso_horario = ZoneInfo(configuracoes.timezone)
    data_atual = data_execucao or datetime.now(fuso_horario)
    data_processamento = data_atual.astimezone(fuso_horario).date().isoformat()
    ingestion_timestamp = datetime.now(UTC).isoformat()

    return [
        {
            **registro,
            "source": FONTE_MERCADOS,
            "endpoint": ENDPOINT_MERCADOS,
            "processing_date": data_processamento,
            "ingestion_timestamp": ingestion_timestamp,
        }
        for registro in dados
    ]


def executar_ingestao_mercados(
    cliente: ClienteCoinGecko | None = None,
    configuracoes: Configuracoes | None = None,
    data_execucao: datetime | None = None,
) -> Path:
    configuracoes = configuracoes or obter_configuracoes()
    dados = extrair_mercados(cliente=cliente, configuracoes=configuracoes)
    validar_mercados(dados, limite_esperado=configuracoes.coin_top_n)
    dados_com_metadados = adicionar_metadados_mercados(
        dados,
        configuracoes=configuracoes,
        data_execucao=data_execucao,
    )
    caminho_saida = montar_caminho_saida_mercados(
        configuracoes,
        data_execucao=data_execucao,
    )

    logger.info("Salvando %s registros de mercado em %s", len(dados), caminho_saida)
    return salvar_parquet(dados_com_metadados, caminho_saida)


if __name__ == "__main__":
    caminho = executar_ingestao_mercados()
    print(caminho)
