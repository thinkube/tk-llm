# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

import pytest


@pytest.fixture
def backend_url():
    return "http://test-backend:8000"


@pytest.fixture
def gateway_url():
    return "http://test-gateway:8080"
