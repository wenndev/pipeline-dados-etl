import pandas as pd
import pytest

from quality.markets import (
    ErroQualidadeDados,
    validar_arquivo_mercados_bronze,
    validar_dataframe_mercados,
    validar_mercados,
)


def mercado_valido():
    return {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 100,
        "market_cap": 1000,
        "market_cap_rank": 1,
        "total_volume": 500,
    }


def test_validar_mercados_aceita_dados_validos():
    validar_mercados([mercado_valido()], limite_esperado=20)


def test_validar_mercados_rejeita_lista_vazia():
    with pytest.raises(ErroQualidadeDados, match="lista vazia"):
        validar_mercados([], limite_esperado=20)


def test_validar_mercados_rejeita_quantidade_acima_do_limite():
    dados = [mercado_valido(), mercado_valido()]

    with pytest.raises(ErroQualidadeDados, match="acima do limite"):
        validar_mercados(dados, limite_esperado=1)


def test_validar_mercados_rejeita_campo_obrigatorio_ausente():
    registro = mercado_valido()
    registro.pop("market_cap")

    with pytest.raises(ErroQualidadeDados, match="campos obrigatórios"):
        validar_mercados([registro], limite_esperado=20)


def test_validar_mercados_rejeita_campo_obrigatorio_nulo():
    registro = mercado_valido()
    registro["current_price"] = None

    with pytest.raises(ErroQualidadeDados, match="nulos"):
        validar_mercados([registro], limite_esperado=20)


def test_validar_mercados_rejeita_valor_numerico_negativo():
    registro = mercado_valido()
    registro["total_volume"] = -1

    with pytest.raises(ErroQualidadeDados, match="negativo"):
        validar_mercados([registro], limite_esperado=20)


def test_validar_dataframe_mercados_aceita_dataframe_valido():
    dataframe = pd.DataFrame([mercado_valido()])

    validar_dataframe_mercados(dataframe, limite_esperado=20)


def test_validar_dataframe_mercados_rejeita_coluna_ausente():
    dataframe = pd.DataFrame([mercado_valido()]).drop(columns=["current_price"])

    with pytest.raises(ErroQualidadeDados, match="colunas obrigatórias"):
        validar_dataframe_mercados(dataframe, limite_esperado=20)


def test_validar_dataframe_mercados_rejeita_id_duplicado():
    dataframe = pd.DataFrame([mercado_valido(), mercado_valido()])

    with pytest.raises(ErroQualidadeDados, match="duplicadas por id"):
        validar_dataframe_mercados(dataframe, limite_esperado=20)


def test_validar_dataframe_mercados_rejeita_texto_vazio():
    registro = mercado_valido()
    registro["symbol"] = " "
    dataframe = pd.DataFrame([registro])

    with pytest.raises(ErroQualidadeDados, match="symbol vazio"):
        validar_dataframe_mercados(dataframe, limite_esperado=20)


def test_validar_arquivo_mercados_bronze_retorna_total_registros(tmp_path):
    caminho = tmp_path / "mercados_2026-08-03.parquet"
    pd.DataFrame([mercado_valido()]).to_parquet(caminho, index=False)

    total_registros = validar_arquivo_mercados_bronze(caminho, limite_esperado=20)

    assert total_registros == 1
