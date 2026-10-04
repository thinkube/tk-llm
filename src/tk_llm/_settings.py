# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os

from tk_llm.exceptions import ConfigurationError


def required(explicit: str | None, env_name: str, argument: str) -> str:
    """The value passed as ``argument``, else the environment variable ``env_name``.

    Thinkube sets both variables in code-server and in the notebook servers;
    an application deployed from a template receives the token as a secret.
    """
    value = explicit or os.environ.get(env_name)
    if not value:
        raise ConfigurationError(
            f"{env_name} is not set. Set it in the environment or pass {argument}=."
        )
    return value
