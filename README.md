# tk-llm

Python SDK for the thinkube LLM gateway.

## Install

```bash
pip install tk-llm            # core (httpx + pydantic)
pip install tk-llm[openai]    # + OpenAI client convenience
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

## Management

```python
from tk_llm import LLMClient

llm = LLMClient()

# List available models
models = llm.list_models(state="available")
for m in models.models:
    print(f"{m.id} [{m.state}] {m.params_b or '?'}B params")

# Load a model
result = llm.load_model("Qwen/Qwen3-8B", tier="flexible")

# Check GPU resources
gpu = llm.gpu_status()
print(f"{gpu.used_memory_gb}/{gpu.total_memory_gb} GB used")

# Unload when done
llm.unload_model("Qwen/Qwen3-8B")
```

## Async

```python
from tk_llm import AsyncLLMClient

async with AsyncLLMClient() as llm:
    models = await llm.list_models()
    status = await llm.gpu_status()
```

## Configuration

| Env var | Description | Default |
|---------|-------------|---------|
| `LLM_GATEWAY_URL` | LLM proxy URL | `http://thinkube-control-llm-proxy.thinkube-control.svc.cluster.local:8080` |
| `THINKUBE_API_TOKEN` | API token (`tk_...`) or JWT | — |

All settings can also be passed directly to `LLMClient()` or `get_openai_client()`.
