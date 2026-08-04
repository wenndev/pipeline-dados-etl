import pytest

from quality.markets import ErroQualidadeDados, validar_mercados


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
