from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from tk_llm._base import BaseClient
from tk_llm.models import (
    BackendsListResponse,
    GPUStatusResponse,
    LoadOptionsResponse,
    ModelLoadResponse,
    ModelResolveResponse,
    ModelState,
    ModelStatusResponse,
    ModelTier,
    ModelsListResponse,
    RefreshResponse,
)

if TYPE_CHECKING:
    import openai


class LLMClient(BaseClient):
    """Synchronous client for the thinkube LLM gateway."""

    def __init__(
        self,
        gateway_url: str | None = None,
        backend_url: str | None = None,
        api_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(gateway_url, backend_url, api_token, timeout)
        self._http = httpx.Client(timeout=self._timeout, headers=self._auth_headers())

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> LLMClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # -- Models --

    def list_models(
        self,
        state: ModelState | str | None = None,
        server_type: str | None = None,
    ) -> ModelsListResponse:
        """List all models in the registry."""
        params: dict[str, str] = {}
        if state is not None:
            params["state"] = str(state)
        if server_type is not None:
            params["server_type"] = server_type
        resp = self._http.get(self._management_url("/models/"), params=params)
        self._raise_for_status(resp)
        return ModelsListResponse.model_validate(resp.json())

    def get_model_status(self, model_id: str) -> ModelStatusResponse:
        """Get detailed status of a specific model."""
        resp = self._http.get(self._management_url(f"/models/{model_id}/status"))
        self._raise_for_status(resp)
        return ModelStatusResponse.model_validate(resp.json())

    def resolve_model(
        self,
        model: str,
        tier: ModelTier | str | None = None,
    ) -> ModelResolveResponse:
        """Resolve a model alias to its backend URL."""
        params: dict[str, str] = {"model": model}
        if tier is not None:
            params["tier"] = str(tier)
        resp = self._http.get(self._management_url("/models/resolve"), params=params)
        self._raise_for_status(resp)
        return ModelResolveResponse.model_validate(resp.json())

    def get_load_options(self, model_id: str) -> LoadOptionsResponse:
        """Get compatible backends and GPU info for loading a model."""
        resp = self._http.get(self._management_url(f"/models/{model_id}/load-options"))
        self._raise_for_status(resp)
        return LoadOptionsResponse.model_validate(resp.json())

    def load_model(
        self,
        model_id: str,
        *,
        tier: ModelTier | str | None = None,
        keep_alive: str | None = None,
        backend: str | None = None,
        node: str | None = None,
        max_context_length: int | None = None,
    ) -> ModelLoadResponse:
        """Load a model onto a backend."""
        body: dict[str, Any] = {}
        if tier is not None:
            body["tier"] = str(tier)
        if keep_alive is not None:
            body["keep_alive"] = keep_alive
        if backend is not None:
            body["backend"] = backend
        if node is not None:
            body["node"] = node
        if max_context_length is not None:
            body["max_context_length"] = max_context_length
        resp = self._http.post(self._management_url(f"/models/{model_id}/load"), json=body)
        self._raise_for_status(resp)
        return ModelLoadResponse.model_validate(resp.json())

    def unload_model(
        self,
        model_id: str,
        *,
        force: bool = False,
    ) -> ModelLoadResponse:
        """Unload a model from its backend."""
        resp = self._http.post(
            self._management_url(f"/models/{model_id}/unload"),
            json={"force": force},
        )
        self._raise_for_status(resp)
        return ModelLoadResponse.model_validate(resp.json())

    # -- Backends --

    def list_backends(self) -> BackendsListResponse:
        """List all registered backends."""
        resp = self._http.get(self._management_url("/backends/"))
        self._raise_for_status(resp)
        return BackendsListResponse.model_validate(resp.json())

    # -- GPU --

    def gpu_status(self) -> GPUStatusResponse:
        """Get GPU resource status across all nodes."""
        resp = self._http.get(self._management_url("/gpu/status/"))
        self._raise_for_status(resp)
        return GPUStatusResponse.model_validate(resp.json())

    # -- Refresh --

    def refresh(self) -> RefreshResponse:
        """Force re-discovery of models and backends."""
        resp = self._http.post(self._management_url("/refresh/"))
        self._raise_for_status(resp)
        return RefreshResponse.model_validate(resp.json())

    # -- OpenAI convenience --

    def openai_client(
        self,
        tier: ModelTier | str | None = None,
        **kwargs: Any,
    ) -> openai.OpenAI:
        """Return an openai.OpenAI client pre-configured for the gateway."""
        from tk_llm.openai import get_openai_client

        return get_openai_client(
            gateway_url=self._gateway_url,
            api_token=self._api_token,
            tier=tier,
            **kwargs,
        )


class AsyncLLMClient(BaseClient):
    """Asynchronous client for the thinkube LLM gateway."""

    def __init__(
        self,
        gateway_url: str | None = None,
        backend_url: str | None = None,
        api_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(gateway_url, backend_url, api_token, timeout)
        self._http = httpx.AsyncClient(timeout=self._timeout, headers=self._auth_headers())

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncLLMClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    # -- Models --

    async def list_models(
        self,
        state: ModelState | str | None = None,
        server_type: str | None = None,
    ) -> ModelsListResponse:
        """List all models in the registry."""
        params: dict[str, str] = {}
        if state is not None:
            params["state"] = str(state)
        if server_type is not None:
            params["server_type"] = server_type
        resp = await self._http.get(self._management_url("/models/"), params=params)
        self._raise_for_status(resp)
        return ModelsListResponse.model_validate(resp.json())

    async def get_model_status(self, model_id: str) -> ModelStatusResponse:
        """Get detailed status of a specific model."""
        resp = await self._http.get(self._management_url(f"/models/{model_id}/status"))
        self._raise_for_status(resp)
        return ModelStatusResponse.model_validate(resp.json())

    async def resolve_model(
        self,
        model: str,
        tier: ModelTier | str | None = None,
    ) -> ModelResolveResponse:
        """Resolve a model alias to its backend URL."""
        params: dict[str, str] = {"model": model}
        if tier is not None:
            params["tier"] = str(tier)
        resp = await self._http.get(self._management_url("/models/resolve"), params=params)
        self._raise_for_status(resp)
        return ModelResolveResponse.model_validate(resp.json())

    async def get_load_options(self, model_id: str) -> LoadOptionsResponse:
        """Get compatible backends and GPU info for loading a model."""
        resp = await self._http.get(self._management_url(f"/models/{model_id}/load-options"))
        self._raise_for_status(resp)
        return LoadOptionsResponse.model_validate(resp.json())

    async def load_model(
        self,
        model_id: str,
        *,
        tier: ModelTier | str | None = None,
        keep_alive: str | None = None,
        backend: str | None = None,
        node: str | None = None,
        max_context_length: int | None = None,
    ) -> ModelLoadResponse:
        """Load a model onto a backend."""
        body: dict[str, Any] = {}
        if tier is not None:
            body["tier"] = str(tier)
        if keep_alive is not None:
            body["keep_alive"] = keep_alive
        if backend is not None:
            body["backend"] = backend
        if node is not None:
            body["node"] = node
        if max_context_length is not None:
            body["max_context_length"] = max_context_length
        resp = await self._http.post(self._management_url(f"/models/{model_id}/load"), json=body)
        self._raise_for_status(resp)
        return ModelLoadResponse.model_validate(resp.json())

    async def unload_model(
        self,
        model_id: str,
        *,
        force: bool = False,
    ) -> ModelLoadResponse:
        """Unload a model from its backend."""
        resp = await self._http.post(
            self._management_url(f"/models/{model_id}/unload"),
            json={"force": force},
        )
        self._raise_for_status(resp)
        return ModelLoadResponse.model_validate(resp.json())

    # -- Backends --

    async def list_backends(self) -> BackendsListResponse:
        """List all registered backends."""
        resp = await self._http.get(self._management_url("/backends/"))
        self._raise_for_status(resp)
        return BackendsListResponse.model_validate(resp.json())

    # -- GPU --

    async def gpu_status(self) -> GPUStatusResponse:
        """Get GPU resource status across all nodes."""
        resp = await self._http.get(self._management_url("/gpu/status/"))
        self._raise_for_status(resp)
        return GPUStatusResponse.model_validate(resp.json())

    # -- Refresh --

    async def refresh(self) -> RefreshResponse:
        """Force re-discovery of models and backends."""
        resp = await self._http.post(self._management_url("/refresh/"))
        self._raise_for_status(resp)
        return RefreshResponse.model_validate(resp.json())

    # -- OpenAI convenience --

    def openai_client(
        self,
        tier: ModelTier | str | None = None,
        **kwargs: Any,
    ) -> openai.AsyncOpenAI:
        """Return an openai.AsyncOpenAI client pre-configured for the gateway."""
        from tk_llm.openai import get_async_openai_client

        return get_async_openai_client(
            gateway_url=self._gateway_url,
            api_token=self._api_token,
            tier=tier,
            **kwargs,
        )
