import httpx
import pytest
import respx

from tk_llm import AsyncLLMClient, LLMClient
from tk_llm.exceptions import AuthError, NotFoundError
from tk_llm.models import ModelState

BACKEND = "http://test-backend:8000"
GATEWAY = "http://test-gateway:8080"
API = f"{BACKEND}/api/v1/llm"


MODELS_LIST_PAYLOAD = {
    "models": [
        {
            "id": "Qwen/Qwen3-8B",
            "name": "Qwen3 8B",
            "server_type": ["ollama"],
            "state": "available",
            "task": "text-generation",
        }
    ],
    "total": 1,
    "available": 1,
    "deployable": 0,
    "registered": 0,
    "installed_backend_types": ["ollama"],
}

MODEL_STATUS_PAYLOAD = {
    "model": {
        "id": "Qwen/Qwen3-8B",
        "name": "Qwen3 8B",
        "server_type": ["ollama"],
        "state": "available",
        "task": "text-generation",
    },
    "backends": ["ollama-node1"],
}

RESOLVE_PAYLOAD = {
    "backend_url": "http://10.0.0.1:11434",
    "api_path": "/v1",
    "model_id": "Qwen/Qwen3-8B",
    "serving_name": "qwen3:8b",
    "model_state": "available",
    "tier": "flexible",
}

LOAD_OPTIONS_PAYLOAD = {
    "model_id": "Qwen/Qwen3-8B",
    "compatible_backends": [
        {"id": "ollama-node1", "name": "Ollama Node1", "type": "ollama", "status": "healthy"}
    ],
    "gpu_nodes": [
        {
            "name": "node1",
            "total_slots": 4,
            "available_slots": 2,
            "total_memory_gb": 48.0,
            "used_memory_gb": 16.0,
        }
    ],
    "estimated_memory_gb": 6.5,
    "context_length": 32768,
}

LOAD_RESPONSE_PAYLOAD = {
    "model_id": "Qwen/Qwen3-8B",
    "state": "available",
    "message": "Model loaded successfully",
    "backend_id": "ollama-node1",
}

BACKENDS_PAYLOAD = {
    "backends": [
        {
            "id": "ollama-node1",
            "name": "Ollama Node1",
            "url": "http://10.0.0.1:11434",
            "type": "ollama",
            "status": "healthy",
        }
    ],
    "total": 1,
    "healthy": 1,
}

GPU_STATUS_PAYLOAD = {
    "nodes": [
        {
            "name": "node1",
            "gpu_product": "NVIDIA RTX 4090",
            "total_slots": 4,
            "available_slots": 2,
            "total_memory_gb": 48.0,
            "used_memory_gb": 16.0,
        }
    ],
    "total_memory_gb": 48.0,
    "used_memory_gb": 16.0,
    "memory_threshold": 0.85,
    "can_accept_new_model": True,
}

REFRESH_PAYLOAD = {
    "models_refreshed": 5,
    "backends_refreshed": 2,
    "message": "ok",
}


class TestLLMClientSync:
    def _client(self) -> LLMClient:
        return LLMClient(gateway_url=GATEWAY, backend_url=BACKEND, api_token="tk_test")

    @respx.mock
    def test_list_models(self):
        respx.get(f"{API}/models/").mock(
            return_value=httpx.Response(200, json=MODELS_LIST_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.list_models()
        assert result.total == 1
        assert result.models[0].id == "Qwen/Qwen3-8B"
        assert result.models[0].state == ModelState.available

    @respx.mock
    def test_list_models_with_filters(self):
        route = respx.get(f"{API}/models/").mock(
            return_value=httpx.Response(200, json=MODELS_LIST_PAYLOAD)
        )
        with self._client() as llm:
            llm.list_models(state="available", server_type="ollama")
        assert "state=available" in str(route.calls[0].request.url)
        assert "server_type=ollama" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_model_status(self):
        respx.get(f"{API}/models/Qwen/Qwen3-8B/status").mock(
            return_value=httpx.Response(200, json=MODEL_STATUS_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.get_model_status("Qwen/Qwen3-8B")
        assert result.model.id == "Qwen/Qwen3-8B"
        assert "ollama-node1" in result.backends

    @respx.mock
    def test_resolve_model(self):
        respx.get(f"{API}/models/resolve").mock(
            return_value=httpx.Response(200, json=RESOLVE_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.resolve_model("qwen3:8b", tier="flexible")
        assert result.serving_name == "qwen3:8b"
        assert result.model_state == ModelState.available

    @respx.mock
    def test_get_load_options(self):
        respx.get(f"{API}/models/Qwen/Qwen3-8B/load-options").mock(
            return_value=httpx.Response(200, json=LOAD_OPTIONS_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.get_load_options("Qwen/Qwen3-8B")
        assert result.estimated_memory_gb == 6.5
        assert len(result.compatible_backends) == 1

    @respx.mock
    def test_load_model(self):
        respx.post(f"{API}/models/Qwen/Qwen3-8B/load").mock(
            return_value=httpx.Response(200, json=LOAD_RESPONSE_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.load_model("Qwen/Qwen3-8B", tier="flexible")
        assert result.state == ModelState.available
        assert result.backend_id == "ollama-node1"

    @respx.mock
    def test_unload_model(self):
        payload = {**LOAD_RESPONSE_PAYLOAD, "state": "deployable", "message": "Model unloaded"}
        respx.post(f"{API}/models/Qwen/Qwen3-8B/unload").mock(
            return_value=httpx.Response(200, json=payload)
        )
        with self._client() as llm:
            result = llm.unload_model("Qwen/Qwen3-8B")
        assert result.state == ModelState.deployable

    @respx.mock
    def test_list_backends(self):
        respx.get(f"{API}/backends/").mock(
            return_value=httpx.Response(200, json=BACKENDS_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.list_backends()
        assert result.total == 1
        assert result.healthy == 1

    @respx.mock
    def test_gpu_status(self):
        respx.get(f"{API}/gpu/status/").mock(
            return_value=httpx.Response(200, json=GPU_STATUS_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.gpu_status()
        assert result.can_accept_new_model is True
        assert result.nodes[0].gpu_product == "NVIDIA RTX 4090"

    @respx.mock
    def test_refresh(self):
        respx.post(f"{API}/refresh/").mock(
            return_value=httpx.Response(200, json=REFRESH_PAYLOAD)
        )
        with self._client() as llm:
            result = llm.refresh()
        assert result.models_refreshed == 5

    @respx.mock
    def test_auth_error(self):
        respx.get(f"{API}/models/").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid token"})
        )
        with self._client() as llm:
            with pytest.raises(AuthError):
                llm.list_models()

    @respx.mock
    def test_not_found_error(self):
        respx.get(f"{API}/models/nonexistent/status").mock(
            return_value=httpx.Response(404, json={"detail": "Model not found"})
        )
        with self._client() as llm:
            with pytest.raises(NotFoundError):
                llm.get_model_status("nonexistent")

    @respx.mock
    def test_auth_header_sent(self):
        route = respx.get(f"{API}/models/").mock(
            return_value=httpx.Response(200, json=MODELS_LIST_PAYLOAD)
        )
        with self._client() as llm:
            llm.list_models()
        assert route.calls[0].request.headers["authorization"] == "Bearer tk_test"


class TestAsyncLLMClient:
    def _client(self) -> AsyncLLMClient:
        return AsyncLLMClient(gateway_url=GATEWAY, backend_url=BACKEND, api_token="tk_test")

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_models(self):
        respx.get(f"{API}/models/").mock(
            return_value=httpx.Response(200, json=MODELS_LIST_PAYLOAD)
        )
        async with self._client() as llm:
            result = await llm.list_models()
        assert result.total == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_load_model(self):
        respx.post(f"{API}/models/Qwen/Qwen3-8B/load").mock(
            return_value=httpx.Response(200, json=LOAD_RESPONSE_PAYLOAD)
        )
        async with self._client() as llm:
            result = await llm.load_model("Qwen/Qwen3-8B")
        assert result.state == ModelState.available

    @respx.mock
    @pytest.mark.asyncio
    async def test_gpu_status(self):
        respx.get(f"{API}/gpu/status/").mock(
            return_value=httpx.Response(200, json=GPU_STATUS_PAYLOAD)
        )
        async with self._client() as llm:
            result = await llm.gpu_status()
        assert result.can_accept_new_model is True
