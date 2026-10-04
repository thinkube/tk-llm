# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import httpx

from tk_llm._constants import (
    DEFAULT_BACKEND_URL,
    DEFAULT_TIMEOUT,
    ENV_API_TOKEN,
    ENV_GATEWAY_URL,
    MANAGEMENT_API_PREFIX,
)
from tk_llm._settings import required
from tk_llm.exceptions import AuthError, GatewayError, LLMError, NotFoundError


class BaseClient:
    """Shared logic for sync and async clients."""

    def __init__(
        self,
        gateway_url: str | None = None,
        backend_url: str | None = None,
        api_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._gateway_url = required(gateway_url, ENV_GATEWAY_URL, "gateway_url").rstrip("/")
        self._backend_url = (backend_url or DEFAULT_BACKEND_URL).rstrip("/")
        self._api_token = required(api_token, ENV_API_TOKEN, "api_token")
        self._timeout = timeout

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_token}"}

    def _management_url(self, path: str) -> str:
        return f"{self._backend_url}{MANAGEMENT_API_PREFIX}{path}"

    def _proxy_url(self, path: str) -> str:
        return f"{self._gateway_url}{path}"

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        status = response.status_code
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        if status in (401, 403):
            raise AuthError(str(detail), status_code=status)
        if status == 404:
            raise NotFoundError(str(detail), status_code=status)
        if status >= 500:
            raise GatewayError(str(detail), status_code=status)
        raise LLMError(str(detail), status_code=status)
