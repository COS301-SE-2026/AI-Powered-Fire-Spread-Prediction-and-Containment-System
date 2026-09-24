import threading
from datetime import datetime, timedelta, timezone

import os
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
    host = os.getenv("VALKEY_HOST", "localhost")
    port = int(os.getenv("VALKEY_PORT", "6380"))
    client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
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

class TestWebSocketControl:
    def test_connect_joins_idle_pool_and_answers_ping(self, client, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_path, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "ping"})
            assert ws.receive_json() == {"type": "pong"}
            assert test_valkey.sismember("worker:pool:idle", body["worker_id"])

        #disconnect to clean up pool
        assert not test_valkey.sismember("worker:pool:idle", body["worker_id"])

    def test_invalid_token_reject(self, client, test_valkey):
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(WS_path, headers=ws_headers("not-a-jwt")):
                pass
        assert exc.value.code == 1008

    def test_user_token_cannot_conn_as_worker(self, client, test_valkey, user_headers):
        _, headers = user_headers
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(WS_path, headers=headers):
                pass
        assert exc.value.code == 1008

class TestQuarantine:
    def quaratine(self, db, worker_id, until):
        node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
        node.status = "quarantined"
        node.quarantine_until = until
        db.commit()
        return node

    def test_active_quarantine_blocks_reconn(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        self.quaratine(db, body["worker_id"], datetime.now(timezone.utc) + timedelta(minutes=15))

        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(WS_path, headers=ws_headers(body["access_token"])):
                pass
        assert exc.value.code == 1008

    def test_expired_quarantined_allows_reconn(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        node = self.quaratine(db, body["worker_id"], datetime.now(timezone.utc) - timedelta(minutes=1))

        with client.websocket_connect(WS_path, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "ping"})
            assert ws.receive_json() == {"type": "pong"}
            db.refresh(node)
            assert node.status == "active"

class TestDispatch:
    def test_no_volunteer_worker_fallback(self, client, db, test_valkey):
        result = client.portal.call(worker_routes.dispatch_simulation_task, {"job_id": "j0"}, db)
        assert result == {"dispatched_to": "cloud_fallback", "status": "queued"}

    def test_job_delivered_result_gotten(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        job = {
            "job_id": "job-int-1",
            "grid_h": 5,
            "grid_w": 5,
            "n_steps": 1
        }
        holder = {}

        with client.websocket_connect(WS_path, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "ping"})
            ws.receive_json() # handshake hence a worker is idel

            t = threading.Thread(target=lambda: holder.update(result=client.portal.call(worker_routes.dispatch_simulation_task, job, db)))
            t.start()

            msg = ws.receive_json()
            assert msg["type"] == "simulation_job"
            assert msg["payload"]["job_id"] == "job-int-1"

            ws.send_json({
                "type": "simulation_result",
                "job_id": "job-int-1",
                "payload": {"job_id": "job-int-1", "status": "completed", "history": [[0] * 25]},
            })
            t.join(timeout=10)

        assert holder["result"]["status"] == "completed"
        assert holder["result"]["history"] == [[0] * 25]

    def test_worker_error_quarantines_node(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_path, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "simulation_error", "job_id": "bad-job", "error": "boom"})
            ws.send_json({"type": "ping"})
            ws.receive_json() # handshake hence a worker is idel

        node = db.query(WorkerNode).filter(WorkerNode.id == body["worker_id"]).first()
        db.refresh(node)
        assert node.status == "quarantined"
        assert node.consecutive_failures == 1
        assert node.quarantine_until > datetime.now(timezone.utc)