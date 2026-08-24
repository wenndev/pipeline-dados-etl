"""
Esse arquivo centraliza a gravação de dados em formato Parquet.

A função salvar_parquet recebe dados em formatos comuns no projeto, como
lista de dicionários, dicionário único ou DataFrame, converte para
DataFrame quando necessário e salva em disco.

Parquet é usado na camada Bronze porque é um formato eficiente para
pipelines de dados: ocupa menos espaço que CSV e preserva melhor os tipos
das colunas para leituras futuras.
"""

from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from logger import obter_logger

logger = obter_logger("parquet")


def salvar_parquet(dados: Any, caminho: str | Path) -> Path:
    caminho_saida = Path(caminho)

    if caminho_saida.suffix != ".parquet":
        caminho_saida = caminho_saida.with_suffix(".parquet")

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(dados, pd.DataFrame):
        dataframe = dados
    elif isinstance(dados, dict):
        dataframe = pd.DataFrame([dados])
    else:
        dataframe = pd.DataFrame(dados)

    caminho_temporario = caminho_saida.with_name(
        f".{caminho_saida.stem}.{uuid4().hex}.tmp.parquet"
    )

    try:
        dataframe.to_parquet(caminho_temporario, index=False)
        caminho_temporario.replace(caminho_saida)
    finally:
        if caminho_temporario.exists():
            caminho_temporario.unlink()

    logger.info("Parquet salvo em %s", caminho_saida)

    return caminho_saida
