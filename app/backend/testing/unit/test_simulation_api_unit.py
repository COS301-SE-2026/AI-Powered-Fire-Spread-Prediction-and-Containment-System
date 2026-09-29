
from __future__ import annotations

import base64
import json
import zlib
from dataclasses import dataclass, field
from types import SimpleNamespace
from unittest.mock import AsyncMock

import numpy as np
import pytest

from app.backend.src.ai import simulation_api as sim


# Fakes

class FakeNoSuchKey(Exception):
    pass


class FakeS3Client:

    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.exceptions = SimpleNamespace(NoSuchKey=FakeNoSuchKey)

    def put(self, key: str, payload: dict) -> None:
        self.objects[key] = json.dumps(payload).encode("utf-8")

    def get_object(self, Bucket: str, Key: str):
        if Key not in self.objects:
            raise self.exceptions.NoSuchKey()
        body = self.objects[Key]

        class _Body:
            def read(self_inner):
                return body

        return {"Body": _Body()}


class FakeSQSClient:

    def __init__(self):
        self.sent_messages: list[dict] = []

    def send_message(self, QueueUrl: str, MessageBody: str):
        self.sent_messages.append({"QueueUrl": QueueUrl, "MessageBody": MessageBody})
        return {"MessageId": "fake-message-id"}


@dataclass
class FakeFire:
    id: str
    reference_number: str
    lat: float
    lng: float
    boundary_radius: float


# Fixtures

@pytest.fixture
def fake_s3(monkeypatch):
    client = FakeS3Client()
    monkeypatch.setattr(sim, "s3_client", client)
    return client


@pytest.fixture
def fake_sqs(monkeypatch):
    client = FakeSQSClient()
    monkeypatch.setattr(sim, "sqs", client)
    return client


@pytest.fixture
def fake_results_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(sim, "RESULTS_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def no_volunteers(monkeypatch):
    monkeypatch.setattr(sim, "has_active_volunteer_workers", lambda: False)


@pytest.fixture
def fast_polling(monkeypatch):
    """Shrinks the poll loop so timeout-path tests don't actually take 6 minutes."""
    monkeypatch.setattr(sim, "RESULT_POLL_TIMEOUT_S", 0.05)
    monkeypatch.setattr(sim, "RESULT_POLL_INTERVAL_S", 0.01)

