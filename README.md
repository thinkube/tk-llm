# tk-llm

Python client for the Thinkube LLM gateway.

## What it does

- `get_openai_client()` and `get_async_openai_client()` return an OpenAI
  client (`openai.OpenAI` / `openai.AsyncOpenAI`) whose base URL is the
  gateway's `/v1`. Chat, completions and embeddings then go through the
  gateway to whichever backend serves the model.
- `LLMClient` and `AsyncLLMClient` call the model management API of
  thinkube-control (`/api/v1/llm`): list models, see load options, load
  and unload models, list backends, read GPU status, refresh discovery.
- A tier (`flexible` or `performance`) is sent to the gateway as the
  `X-LLM-Tier` header.
- HTTP errors become typed exceptions: `AuthError`, `NotFoundError`,
  `GatewayError`, all subclasses of `LLMError`. A missing gateway address or
  token raises `ConfigurationError`.

## How it reaches a user

tk-llm is a package in the platform's own package index. The Thinkube
installer builds it from this repository and publishes it to the
platform's DevPI index (`core/thinkube-control/16_publish_packages.yaml` in
[thinkube](https://github.com/thinkube/thinkube)). Every JupyterHub
environment already has `tk-llm[openai]` (`core/jupyterhub/venv-packages.txt`).
It is not on PyPI and is not installed on its own.

## Install

To add it to an app or another environment on the platform, use the
platform's index:

```bash
pip install --extra-index-url https://packages-api.<your-domain>/root/stable/+simple/ tk-llm            # core (httpx + pydantic)
pip install --extra-index-url https://packages-api.<your-domain>/root/stable/+simple/ "tk-llm[openai]"  # + OpenAI client convenience
```

## Quick start

```python
from tk_llm import get_openai_client

client = get_openai_client()
response = client.chat.completions.create(
    model="qwen3:8b",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

You can pass values explicitly:

```python
client = get_openai_client(
    gateway_url="https://llm.yourdomain.com",
    api_token="tk_your_token_here",
    tier="performance",
)
```

## Embeddings

```python
from tk_llm import get_openai_client

client = get_openai_client()
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="The quick brown fox jumps over the lazy dog",
)
print(f"Dimension: {len(response.data[0].embedding)}")
```

## Management

```python
from tk_llm import LLMClient

llm = LLMClient()

# List available models
models = llm.list_models(state="available")
for m in models.models:
    print(f"{m.id} [{m.state}] {m.params_b or '?'}B params")

# Filter by backend type
ollama_models = llm.list_models(server_type="ollama")

# Check load options before loading
options = llm.get_load_options("Qwen/Qwen3-8B")
print(f"Estimated memory: {options.estimated_memory_gb:.1f} GB")
for backend in options.compatible_backends:
    print(f"  Backend: {backend.name} ({backend.type}) - {backend.status}")

# Load a model
result = llm.load_model("Qwen/Qwen3-8B", tier="flexible")
print(result.message)

# Check GPU resources
gpu = llm.gpu_status()
print(f"GPU memory: {gpu.used_memory_gb:.1f}/{gpu.total_memory_gb:.1f} GB")
print(f"Can load more: {gpu.can_accept_new_model}")
for node in gpu.nodes:
    print(f"  {node.name}: {node.gpu_product} - {node.available_slots}/{node.total_slots} slots")

# List inference backends
backends = llm.list_backends()
for b in backends.backends:
    print(f"{b.name} ({b.type}) on {b.node} - {b.status}")

# Unload when done
llm.unload_model("Qwen/Qwen3-8B")

# Force re-discovery of models and backends
llm.refresh()
```

## Async

```python
from tk_llm import AsyncLLMClient

async with AsyncLLMClient() as llm:
    models = await llm.list_models()
    gpu = await llm.gpu_status()
    await llm.load_model("Qwen/Qwen3-8B")
```

## Configuration

| Env var | Description |
|---------|-------------|
| `LLM_GATEWAY_URL` | LLM gateway URL. Required. |
| `THINKUBE_API_TOKEN` | API token (`tk_...`) or JWT. Required. |

Thinkube sets both in code-server and in the notebook servers. An application
deployed from a template receives the token as a secret you add on the Secrets
page of thinkube-control. When one is missing, the clients raise
`ConfigurationError` naming the variable.

The management calls of `LLMClient` and `AsyncLLMClient` go to
`http://backend.thinkube-control.svc.cluster.local:8000`, or to the
`backend_url` argument. The request timeout is 30 seconds, or the
`timeout` argument.

All settings can also be passed directly to `LLMClient()`, `AsyncLLMClient()`, or `get_openai_client()`.

## API reference

### Client methods

| Method | Description | Returns |
|--------|-------------|---------|
| `list_models(state?, server_type?, task?)` | List all models, optionally filtered | `ModelsListResponse` |
| `get_model_status(model_id)` | Detailed status of a model | `ModelStatusResponse` |
| `resolve_model(model, tier?)` | Resolve model alias to backend URL | `ModelResolveResponse` |
| `get_load_options(model_id)` | Compatible backends and GPU info | `LoadOptionsResponse` |
| `load_model(model_id, tier?, backend?, node?, ...)` | Load a model | `ModelLoadResponse` |
| `unload_model(model_id, force?)` | Unload a model | `ModelLoadResponse` |
| `list_backends()` | List inference backends | `BackendsListResponse` |
| `gpu_status()` | GPU resources across all nodes | `GPUStatusResponse` |
| `refresh()` | Force re-discovery of models and backends | `RefreshResponse` |
| `openai_client(tier?)` | Get a pre-configured OpenAI client | `openai.OpenAI` |

### Convenience functions

| Function | Description | Returns |
|----------|-------------|---------|
| `get_openai_client(gateway_url?, api_token?, tier?)` | Pre-configured OpenAI client | `openai.OpenAI` |
| `get_async_openai_client(gateway_url?, api_token?, tier?)` | Pre-configured async OpenAI client | `openai.AsyncOpenAI` |

### Exceptions

| Exception | When |
|-----------|------|
| `LLMError` | Base exception for all SDK errors |
| `ConfigurationError` | `LLM_GATEWAY_URL` or `THINKUBE_API_TOKEN` is not set |
| `AuthError` | Authentication failed (401/403) |
| `NotFoundError` | Model or resource not found (404) |
| `GatewayError` | Backend or gateway error (5xx) |

## Working on it

```bash
git clone https://github.com/thinkube/tk-llm.git
cd tk-llm
pip install -e ".[dev,openai]"
pytest
mypy src
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
