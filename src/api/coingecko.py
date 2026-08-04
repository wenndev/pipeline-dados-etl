"""
Esse arquivo concentra a comunicação com a API da CoinGecko.

A classe ClienteCoinGecko monta a URL final, envia requisições GET,
passa parâmetros de consulta, aplica timeout e tenta novamente quando
acontecem falhas temporárias, como rate limit ou erro de servidor.

Ter esse código isolado evita espalhar chamadas HTTP pelo projeto. Assim,
os arquivos de ingestão só precisam pedir os dados, sem conhecer detalhes
de retry, headers, timeout ou tratamento de erro.
"""

import random
import time
from typing import Any

import requests

from config import Configuracoes, obter_configuracoes
from logger import obter_logger

logger = obter_logger("coingecko")


class ErroClienteCoinGecko(RuntimeError):
    """Erro disparado quando o cliente da CoinGecko não consegue retornar sucesso."""


class ClienteCoinGecko:
    def __init__(
        self,
        configuracoes: Configuracoes | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.configuracoes = configuracoes or obter_configuracoes()
        self.session = session or requests.Session()

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:
        url = f"{self.configuracoes.api_url}/{endpoint.lstrip('/')}"
        headers = self._headers()

        for attempt in range(1, retries + 1):
            try:
                logger.info("GET %s attempt=%s", endpoint, attempt)
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.configuracoes.request_timeout,
                )

                if response.status_code == 200:
                    return response.json()

                if response.status_code not in {429, 500, 502, 503, 504}:
                    raise ErroClienteCoinGecko(
                        f"CoinGecko returned {response.status_code}: {response.text}"
                    )

                logger.warning("Retryable CoinGecko error: %s", response.status_code)
                self._sleep_before_retry(response, attempt)

            except requests.RequestException as exc:
                if attempt == retries:
                    raise ErroClienteCoinGecko("CoinGecko request failed") from exc

                logger.warning("Connection error: %s", exc)
                self._sleep_before_retry(None, attempt)

        raise ErroClienteCoinGecko(f"Failed to fetch {endpoint} after {retries} retries")

    def _headers(self) -> dict[str, str]:
        if not self.configuracoes.api_key:
            return {}

        return {"x-cg-demo-api-key": self.configuracoes.api_key}

    def _sleep_before_retry(
        self,
        response: requests.Response | None,
        attempt: int,
    ) -> None:
        retry_after = response.headers.get("Retry-After") if response else None

        if retry_after and retry_after.isdigit():
            sleep_time = float(retry_after)
        else:
            backoff = 2 ** (attempt - 1)
            jitter = random.uniform(0, backoff * 0.5)
            sleep_time = backoff + jitter

        logger.info("Waiting %.2fs before retry", sleep_time)
        time.sleep(sleep_time)
