from config import obter_configuracoes


def test_obter_configuracoes_tem_valores_padrao_seguros(monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)
    monkeypatch.delenv("COIN_TOP_N", raising=False)

    configuracoes = obter_configuracoes()

    assert configuracoes.api_url == "https://api.coingecko.com/api/v3"
    assert configuracoes.api_key is None
    assert configuracoes.request_timeout == 10
    assert configuracoes.coin_top_n == 20
    assert configuracoes.database_url is None
