"""
DAG responsável por orquestrar a ingestão Bronze de mercados da CoinGecko.

Conceitos importantes:
- DAG é o fluxo/pipeline que o Airflow agenda e monitora.
- task é uma etapa dentro da DAG.
- schedule define quando a DAG roda automaticamente.
- catchup=False evita que o Airflow tente executar datas antigas em massa.
"""

from __future__ import annotations

import pendulum
from airflow.decorators import dag, task


@dag(
    dag_id="coingecko_markets_bronze",
    description="Extrai o Top N moedas da CoinGecko e salva a camada Bronze em Parquet.",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 8, 3, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["coingecko", "bronze", "markets"],
)
def coingecko_markets_bronze_dag():
    @task(task_id="extrair_mercados_bronze")
    def extrair_mercados_bronze() -> str:
        from ingestion.markets import executar_ingestao_mercados

        caminho_saida = executar_ingestao_mercados()
        return str(caminho_saida)

    extrair_mercados_bronze()


coingecko_markets_bronze_dag()
