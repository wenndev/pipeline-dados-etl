from pipeline_dados.config import get_settings


def test_get_settings_has_safe_defaults(monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)
    monkeypatch.delenv("COIN_TOP_N", raising=False)

    settings = get_settings()

    assert settings.api_url == "https://api.coingecko.com/api/v3"
    assert settings.api_key is None
    assert settings.request_timeout == 10
    assert settings.coin_top_n == 20

