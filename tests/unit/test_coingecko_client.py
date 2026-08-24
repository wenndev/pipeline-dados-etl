import pytest

from api.coingecko import ClienteCoinGecko, ErroClienteCoinGecko
from config import Configuracoes


class RespostaJSONInvalido:
    status_code = 200
    headers = {}
    text = "not json"

    def json(self):
        raise ValueError("invalid json")


class SessaoFalsa:
    def get(self, url, params=None, headers=None, timeout=None):
        return RespostaJSONInvalido()


def criar_configuracoes(tmp_path):
    return Configuracoes(
        api_url="https://api.coingecko.com/api/v3",
        api_key=None,
        request_timeout=10,
        coin_top_n=20,
        data_dir=tmp_path,
        log_dir=tmp_path / "logs",
        database_url=None,
        timezone="America/Sao_Paulo",
    )


def test_cliente_coingecko_rejeita_json_invalido(tmp_path):
    cliente = ClienteCoinGecko(
        configuracoes=criar_configuracoes(tmp_path),
        session=SessaoFalsa(),
    )

    with pytest.raises(ErroClienteCoinGecko, match="invalid JSON"):
        cliente.get("/ping")
