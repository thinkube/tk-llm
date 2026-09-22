# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tk_llm._constants import ENV_API_TOKEN, ENV_GATEWAY_URL
from tk_llm._settings import required
from tk_llm.models import ModelTier

if TYPE_CHECKING:
    import openai


def get_openai_client(
    gateway_url: str | None = None,
    api_token: str | None = None,
    tier: ModelTier | str | None = None,
    **kwargs: Any,
) -> openai.OpenAI:
    """Create an openai.OpenAI client pre-configured for the thinkube LLM gateway.

    Usage::

        from tk_llm import get_openai_client

        client = get_openai_client()
        response = client.chat.completions.create(
            model="qwen3:8b",
            messages=[{"role": "user", "content": "Hello"}],
        )
    """
    try:
        import openai as _openai
    except ImportError:
        raise ImportError(
            "openai package required. Install with: pip install tk-llm[openai]"
        ) from None

    url = required(gateway_url, ENV_GATEWAY_URL, "gateway_url").rstrip("/")
    token = required(api_token, ENV_API_TOKEN, "api_token")

    default_headers: dict[str, str] = {}
    if tier is not None:
        default_headers["X-LLM-Tier"] = str(tier)

    return _openai.OpenAI(
        base_url=f"{url}/v1",
        api_key=token,
        default_headers=default_headers or None,
        **kwargs,
    )


def get_async_openai_client(
    gateway_url: str | None = None,
    api_token: str | None = None,
    tier: ModelTier | str | None = None,
    **kwargs: Any,
) -> openai.AsyncOpenAI:
    """Create an openai.AsyncOpenAI client pre-configured for the thinkube LLM gateway."""
    try:
        import openai as _openai
    except ImportError:
        raise ImportError(
            "openai package required. Install with: pip install tk-llm[openai]"
        ) from None

    url = required(gateway_url, ENV_GATEWAY_URL, "gateway_url").rstrip("/")
    token = required(api_token, ENV_API_TOKEN, "api_token")

    default_headers: dict[str, str] = {}
    if tier is not None:
        default_headers["X-LLM-Tier"] = str(tier)

    return _openai.AsyncOpenAI(
        base_url=f"{url}/v1",
        api_key=token,
        default_headers=default_headers or None,
        **kwargs,
    )
