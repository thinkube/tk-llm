# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

import os
from unittest.mock import patch

import pytest


def test_get_openai_client_explicit_args():
    from tk_llm.openai import get_openai_client

    client = get_openai_client(
        gateway_url="http://my-gateway:8080",
        api_token="tk_mytoken",
        tier="performance",
    )
    assert str(client.base_url) == "http://my-gateway:8080/v1/"
    assert client.api_key == "tk_mytoken"


def test_get_openai_client_from_env():
    from tk_llm.openai import get_openai_client

    with patch.dict(os.environ, {"LLM_GATEWAY_URL": "http://env-gw:9090", "THINKUBE_API_TOKEN": "tk_env"}):
        client = get_openai_client()
    assert str(client.base_url) == "http://env-gw:9090/v1/"
    assert client.api_key == "tk_env"


def test_get_openai_client_defaults():
    from tk_llm.openai import get_openai_client

    with patch.dict(os.environ, {}, clear=True):
        # Remove env vars if they exist
        os.environ.pop("LLM_GATEWAY_URL", None)
        os.environ.pop("THINKUBE_API_TOKEN", None)
        client = get_openai_client()
    assert "/v1/" in str(client.base_url)
    assert client.api_key == "not-needed"


def test_get_async_openai_client():
    from tk_llm.openai import get_async_openai_client

    client = get_async_openai_client(
        gateway_url="http://my-gateway:8080",
        api_token="tk_mytoken",
    )
    assert str(client.base_url) == "http://my-gateway:8080/v1/"


def test_openai_import_error():
    """Verify helpful error when openai is not installed."""
    import importlib
    import sys

    # Temporarily hide the openai module
    openai_mod = sys.modules.get("openai")
    sys.modules["openai"] = None  # type: ignore[assignment]
    try:
        # Reimport to trigger the ImportError path
        import tk_llm.openai as mod
        importlib.reload(mod)
        with pytest.raises(ImportError, match="pip install tk-llm"):
            mod.get_openai_client()
    finally:
        if openai_mod is not None:
            sys.modules["openai"] = openai_mod
        else:
            sys.modules.pop("openai", None)
