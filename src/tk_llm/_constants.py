# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

DEFAULT_GATEWAY_URL = (
    "http://thinkube-control-llm-proxy.thinkube-control.svc.cluster.local:8080"
)
DEFAULT_BACKEND_URL = "http://backend.thinkube-control.svc.cluster.local:8000"

ENV_GATEWAY_URL = "LLM_GATEWAY_URL"
ENV_API_TOKEN = "THINKUBE_API_TOKEN"

MANAGEMENT_API_PREFIX = "/api/v1/llm"
DEFAULT_TIMEOUT = 30.0
