# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations


class LLMError(Exception):
    """Base exception for all tk-llm errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class AuthError(LLMError):
    """Authentication failed (401/403)."""


class NotFoundError(LLMError):
    """Resource not found (404)."""


class GatewayError(LLMError):
    """Gateway or backend error (5xx)."""


class ConfigurationError(LLMError):
    """A required setting is missing."""
