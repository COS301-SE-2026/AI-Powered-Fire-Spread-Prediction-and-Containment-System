import threading
from datetime import datetime, timedelta, timezone

import pytest
import redis
from starlette.websockets import WebSocketDisconnect

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.workers import WorkerNode
from app.backend.src.services import workers as worker_service
from app.backend.src.routes import workers as worker_routes
from app.backend.testing.integration.conftest import make_user

WS_path = "/api/v1/workers/connect"

@pytest.fixture
def test_valkey(monkeypatch):
    client = redis.Redis(host="localhost", port=6380, db=0, decode_responses=True)
    client.flushdb()
    monkeypatch.setattr(worker_service, "valkey_client", client)
    yield client
    client.flushdb()

@pytest.fixture
def user_headers(db):
    user = make_user(db)
    token = create_access_token({"user_id": user.id})
    return user, {"Authorization": f"Bearer {token}"}

def payload(key, vram_mb=8192):
    return {
        "registration_key": key,
        "label": "test_rig",
        "gpu_name": "RTX 5070",
        "vram_mb": vram_mb,
        "driver_version": "12.8",
        "cuda_capable": True 
    }

def new_key(client, headers):
    resp = client.post("/api/v1/workers/keys", headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()["registration_key"]

def register(client, headers):
    resp = client.post("/api/v1/workers/register", json=payload(new_key(client, headers)))
    assert resp.status_code == 200, resp.text
    return resp.json()

def ws_headers(jwt):
    return {"Authorization": f"Bearer {jwt}"}

class TestKeysAndRegistration:
    def test_keys_requires_auth(self, client, test_valkey):
        assert client.post("/api/v1/workers/keys").status_code == 401

    def test_stored_keys_against_user(self, client, test_valkey, user_headers):
        user, headers = user_headers
        key = new_key(client, headers)
        assert test_valkey.get(f"worker:reg:{key}") == user.id

    def test_register_creates_node_user(self, client, db, test_valkey, user_headers):
        user, headers = user_headers
        body = register(client, headers)

        node = db.query(WorkerNode).filter(WorkerNode.id == body["worker_id"]).first()
        assert node is not None
        assert node.user_id == user.id
        assert node.status == "active"
        assert body["access_token"]

    def test_low_vram_reject_key_survival(self, client, test_valkey, user_headers):
        _, headers = user_headers
        key = new_key(client, headers)

        rejected = client.post("/api/v1/workers/register", json=payload(key, vram_mb=2048))
        assert rejected.status_code == 400

        retried = client.post("/api/v1/workers/register", json=payload(key))
        assert retried.status_code == 200

    def test_key_single_use(self, client, test_valkey, user_headers):
        _, headers = user_headers
        key = new_key(client, headers)

        assert client.post("/api/v1/workers/register", json=payload(key)).status_code == 200
        assert client.post("/api/v1/workers/register", json=payload(key)).status_code == 401