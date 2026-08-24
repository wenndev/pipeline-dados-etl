"""
DAG responsável por orquestrar diariamente a ingestão Bronze
de mercados da CoinGecko.

Fluxo:
1. Extrai os dados da API da CoinGecko e salva em Parquet.
2. Valida a qualidade dos dados (Data Quality).
3. Carrega os dados validados no PostgreSQL.

Conceitos do Airflow:
- DAG: representa o fluxo/pipeline que será orquestrado.
- Task: representa uma etapa executável dentro da DAG.
- schedule="@daily": agenda a execução da DAG uma vez por dia.
- start_date: define a partir de quando o agendamento é considerado
  pelo Airflow. Não representa necessariamente a data dos dados.
- catchup=False: evita que o Airflow crie automaticamente execuções
  para os períodos anteriores desde a start_date.
- XCom: permite passar pequenos valores entre tasks. Nesta DAG,
  é utilizado para passar o caminho do arquivo Parquet entre as tasks.

Fluxo da DAG:
Extração -> Validação -> Carga no PostgreSQL
"""

from __future__ import annotations

import pendulum
from airflow.decorators import dag, task


@dag(
    dag_id="coingecko_markets_bronze",
    description="Extrai mercados da CoinGecko, salva Bronze em Parquet e carrega no Postgres.",
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

    @task(task_id="carregar_mercados_bronze_postgres")
    def carregar_mercados_bronze_postgres(caminho_parquet: str) -> int:
        from loading.markets import carregar_mercados_bronze_postgres as carregar

        return carregar(caminho_parquet)

    @task(task_id="validar_mercados_bronze")
    def validar_mercados_bronze(caminho_parquet: str) -> str:
        from config import obter_configuracoes
        from quality.markets import validar_arquivo_mercados_bronze

        configuracoes = obter_configuracoes()
        validar_arquivo_mercados_bronze(
            caminho_parquet,
            limite_esperado=configuracoes.coin_top_n,
        )
        return caminho_parquet

    caminho_mercados = extrair_mercados_bronze()
    caminho_validado = validar_mercados_bronze(caminho_mercados)
    carregar_mercados_bronze_postgres(caminho_validado)


coingecko_markets_bronze_dag()
