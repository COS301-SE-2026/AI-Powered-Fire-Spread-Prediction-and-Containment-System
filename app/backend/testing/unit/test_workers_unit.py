import os
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("AWS_REGION", "us-east-1")

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi import HTTPException

from app.backend.src.schemas.workers import WorkerRegisterRequest
from app.backend.src.services import workers as worker_service

class TestGenerateWorkerKey:
    def test_key_format_and_ttl(self):
        fake_valkey = MagicMock()
        with patch.object(worker_service, "valkey_client", fake_valkey):
            result = worker_service.generate_worker_key("usr_01")

        key = result["registration_key"]
        assert key.startswith("REG-")
        assert len(key) == len("REG-") + 16
        assert result["expires_in_seconds"] == worker_service.REGISTRATION_KEY_TTL

        fake_valkey.setex.assert_called_once_with(
            f"worker:reg:{key}", worker_service.REGISTRATION_KEY_TTL, "usr_01"
        )

    def test_docker_command_contains_key(self):
        with patch.object(worker_service, "valkey_client", MagicMock()):
            result = worker_service.generate_worker_key("usr_01")
        assert result["registration_key"] in result["docker_command"]
        assert result["docker_command"].startswith("docker run")