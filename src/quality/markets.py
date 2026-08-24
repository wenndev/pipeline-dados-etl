"""Validações de qualidade para dados de mercado da CoinGecko."""

from pathlib import Path
from typing import Any

import pandas as pd


class ErroQualidadeDados(ValueError):
    """Erro disparado quando os dados não passam nas regras de qualidade."""


CAMPOS_OBRIGATORIOS_MERCADOS = {
    "id",
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "market_cap_rank",
    "total_volume",
}


def validar_mercados(dados: list[dict[str, Any]], limite_esperado: int) -> None:
    if not dados:
        raise ErroQualidadeDados("A extração de mercados retornou uma lista vazia")

    if len(dados) > limite_esperado:
        raise ErroQualidadeDados(
            f"A extração retornou {len(dados)} registros, acima do limite "
            f"esperado de {limite_esperado}"
        )

    for indice, registro in enumerate(dados):
        _validar_campos_obrigatorios(registro, indice)
        _validar_valores_numericos(registro, indice)


def validar_arquivo_mercados_bronze(
    caminho_parquet: str | Path,
    limite_esperado: int,
) -> int:
    caminho = Path(caminho_parquet)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo Bronze não encontrado: {caminho}")

    dataframe = pd.read_parquet(caminho)
    validar_dataframe_mercados(dataframe, limite_esperado=limite_esperado)

    return len(dataframe)


def validar_dataframe_mercados(
    dataframe: pd.DataFrame,
    limite_esperado: int,
) -> None:
    if dataframe.empty:
        raise ErroQualidadeDados("O arquivo Bronze de mercados está vazio")

    if len(dataframe) > limite_esperado:
        raise ErroQualidadeDados(
            f"O arquivo Bronze possui {len(dataframe)} registros, acima do limite "
            f"esperado de {limite_esperado}"
        )

    campos_ausentes = CAMPOS_OBRIGATORIOS_MERCADOS - set(dataframe.columns)
    if campos_ausentes:
        campos = ", ".join(sorted(campos_ausentes))
        raise ErroQualidadeDados(f"Arquivo Bronze sem colunas obrigatórias: {campos}")

    campos_nulos = [
        campo
        for campo in CAMPOS_OBRIGATORIOS_MERCADOS
        if dataframe[campo].isna().any()
    ]
    if campos_nulos:
        campos = ", ".join(sorted(campos_nulos))
        raise ErroQualidadeDados(f"Arquivo Bronze possui colunas com nulos: {campos}")

    _validar_colunas_texto(dataframe)
    _validar_colunas_numericas(dataframe)
    _validar_unicidade(dataframe)


def _validar_campos_obrigatorios(registro: dict[str, Any], indice: int) -> None:
    campos_ausentes = CAMPOS_OBRIGATORIOS_MERCADOS - set(registro)

    if campos_ausentes:
        campos = ", ".join(sorted(campos_ausentes))
        raise ErroQualidadeDados(
            f"Registro {indice} não possui campos obrigatórios: {campos}"
        )

    campos_nulos = [
        campo
        for campo in CAMPOS_OBRIGATORIOS_MERCADOS
        if registro.get(campo) is None
    ]

    if campos_nulos:
        campos = ", ".join(sorted(campos_nulos))
        raise ErroQualidadeDados(
            f"Registro {indice} possui campos obrigatórios nulos: {campos}"
        )


def _validar_valores_numericos(registro: dict[str, Any], indice: int) -> None:
    for campo in ("current_price", "market_cap", "market_cap_rank", "total_volume"):
        valor = registro[campo]

        if not isinstance(valor, int | float):
            raise ErroQualidadeDados(
                f"Registro {indice} possui {campo} com tipo inválido: {type(valor)}"
            )

        if valor < 0:
            raise ErroQualidadeDados(
                f"Registro {indice} possui {campo} negativo: {valor}"
            )


def _validar_colunas_texto(dataframe: pd.DataFrame) -> None:
    for campo in ("id", "symbol", "name"):
        valores_vazios = dataframe[campo].astype(str).str.strip().eq("")

        if valores_vazios.any():
            raise ErroQualidadeDados(f"Arquivo Bronze possui {campo} vazio")


def _validar_colunas_numericas(dataframe: pd.DataFrame) -> None:
    for campo in ("current_price", "market_cap", "market_cap_rank", "total_volume"):
        if not pd.api.types.is_numeric_dtype(dataframe[campo]):
            raise ErroQualidadeDados(
                f"Arquivo Bronze possui {campo} com tipo não numérico"
            )

        if dataframe[campo].lt(0).any():
            raise ErroQualidadeDados(f"Arquivo Bronze possui {campo} negativo")


def _validar_unicidade(dataframe: pd.DataFrame) -> None:
    if dataframe["id"].duplicated().any():
        raise ErroQualidadeDados("Arquivo Bronze possui moedas duplicadas por id")

    if dataframe["market_cap_rank"].duplicated().any():
        raise ErroQualidadeDados(
            "Arquivo Bronze possui ranking de capitalização duplicado"
        )
