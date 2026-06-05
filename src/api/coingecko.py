import random
import time
from typing import Any

import requests

from config import Settings, get_settings
from logger import get_logger

logger = get_logger("coingecko")


class CoinGeckoClientError(RuntimeError):
    """Raised when the CoinGecko client cannot return a successful response."""


class CoinGeckoClient:
    def __init__(
        self,
        settings: Settings | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.session = session or requests.Session()

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:
        url = f"{self.settings.api_url}/{endpoint.lstrip('/')}"
        headers = self._headers()

        for attempt in range(1, retries + 1):
            try:
                logger.info("GET %s attempt=%s", endpoint, attempt)
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.settings.request_timeout,
                )

                if response.status_code == 200:
                    return response.json()

                if response.status_code not in {429, 500, 502, 503, 504}:
                    raise CoinGeckoClientError(
                        f"CoinGecko returned {response.status_code}: {response.text}"
                    )

                logger.warning("Retryable CoinGecko error: %s", response.status_code)
                self._sleep_before_retry(response, attempt)

            except requests.RequestException as exc:
                if attempt == retries:
                    raise CoinGeckoClientError("CoinGecko request failed") from exc

                logger.warning("Connection error: %s", exc)
                self._sleep_before_retry(None, attempt)

        raise CoinGeckoClientError(f"Failed to fetch {endpoint} after {retries} retries")

    def _headers(self) -> dict[str, str]:
        if not self.settings.api_key:
            return {}

        return {"x-cg-demo-api-key": self.settings.api_key}

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

