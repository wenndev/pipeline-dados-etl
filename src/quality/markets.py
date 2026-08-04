"""Validações de qualidade para dados de mercado da CoinGecko."""

from typing import Any


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
