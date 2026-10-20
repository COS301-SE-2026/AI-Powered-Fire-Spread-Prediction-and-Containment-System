"""Integration tests for the worker management, progress, and dispatch paths in worker route"""
import functools
import json
import threading
import os

import pytest
import redis
from starlette.websockets import WebSocketDisconnect

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.workers import WorkerNode
from app.backend.src.routes import workers as worker_routes
from app.backend.src.services import workers as worker_service
from app.backend.testing.integration.conftest import make_user
 
WS_PATH = "/api/v1/workers/connect"
FALLBACK = {"dispatched_to": "cloud_fallback", "status": "queued"}

@pytest.fixture
def test_valkey(monkeypatch):
    host = os.getenv("VALKEY_HOST", "localhost")
    port = int(os.getenv("VALKEY_PORT", "6380"))
    client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
    client.flushdb()
    monkeypatch.setattr(worker_service, "valkey_client", client)
    yield client
    client.flushdb()

def auth_headers(user):
    return {"Authorization": f"Bearer {create_access_token({'user_id': user.id})}"}

@pytest.fixture
def user_headers(db):
    user = make_user(db)
    return user, auth_headers(user)

def register(client, headers):
    key_resp = client.post(
         "/api/v1/workers/keys", headers=headers, json={"label": "test-worker", "gpu_name": "Test GPU"}
    )
    assert key_resp.status_code == 201, key_resp.text
    resp = client.post(
        "/api/v1/workers/register",
        json={
            "registration_key": key_resp.json()["registration_key"],
            "label": "test_rig",
            "gpu_name": "RTX 5070",
            "vram_mb": 8192,
            "driver_version": "12.8",
            "cuda_capable": True,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()

def ws_headers(jwt):
    return {"Authorization": f"Bearer {jwt}"}

def fresh_node(db, worker_id):
    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    db.refresh(node)
    return node

def sync(ws):
    ws.send_json({"type": "ping"})
    assert ws.receive_json() == {"type": "pong"}

def start_dispatch(client, db, job_id, progress_key=None):
    holder = {}
    call = functools.partial(worker_routes.dispatch_simulation_task, {"job_id": job_id}, db, progress_key)
    thread = threading.Thread(target=lambda: holder.update(result=client.portal.call(call)))
    thread.start()
    return thread, holder

def progress(test_valkey, key):
    raw = test_valkey.get(f"sim:progress:{key}")
    return json.loads(raw) if raw else None

class TestProgressRoute:
    def test_requires_auth(self, client, test_valkey):
        assert client.get("/api/v1/workers/progress/FR-1").status_code == 401

    def test_empty_when_nothing_recorded(self, client, test_valkey, user_headers):
        _, headers = user_headers
        resp = client.get("/api/v1/workers/progress/FR-1", headers=headers)
        assert resp.json() == {"stage": None, "message": None}

    def test_returns_latest_stage(self, client, test_valkey, user_headers):
        _, headers = user_headers
        worker_routes.set_sim_progress("FR-1", "running_model", "Running fire spread model")
        resp = client.get("/api/v1/workers/progress/FR-1", headers=headers)
        assert resp.json() == {"stage": "running_model", "message": "Running fire spread model"}

    def test_cluster_key_with_plus_sign(self, client, test_valkey, user_headers):
        _, headers = user_headers
        worker_routes.set_sim_progress("FR-1+FR-2", "queued", "Finding an available GPU")
        resp = client.get("/api/v1/workers/progress/FR-1%2BFR-2", headers=headers)
        assert resp.json()["stage"] == "queued"

class TestWorkerProgressMessages:
    def test_progress_is_stored_under_the_jobs_progress_key(self, client, test_valkey, user_headers, monkeypatch):
        _, headers = user_headers
        body = register(client, headers)
        monkeypatch.setitem(worker_routes.job_progress_keys, "job-p1", "FR-9")

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "progress", "job_id": "job-p1", "stage": "fetching_weather", "message": "Fetching weather data"})
            sync(ws)

        assert progress(test_valkey, "FR-9") == {"stage": "fetching_weather", "message": "Fetching weather data"}

    def test_progress_for_unknown_job_is_ignored(self, client, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            ws.send_json({"type": "progress", "job_id": "nobody", "stage": "received", "message": "x"})
            sync(ws)
        assert not test_valkey.keys("sim:progress:*")

class TestDispatchPaths:
    def test_success_reports_dispatched_then_clears_and_frees_worker(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            sync(ws)
            thread, holder = start_dispatch(client, db, "job-ok", progress_key="FR-7")

            assert ws.receive_json()["type"] == "simulation_job"
            assert progress(test_valkey, "FR-7")["stage"] == "dispatched"

            ws.send_json({"type": "simulation_result", "job_id": "job-ok", "payload": {"status": "completed"}})
            thread.join(timeout=10)
            sync(ws)

            assert holder["result"] == {"status": "completed"}
            assert progress(test_valkey, "FR-7") is None
            assert fresh_node(db, body["worker_id"]).status == "active"
            assert test_valkey.sismember("worker:pool:idle", body["worker_id"])

    def test_worker_error_falls_back_to_cloud_and_quarantines(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            sync(ws)
            thread, holder = start_dispatch(client, db, "job-bad", progress_key="FR-8")
            ws.receive_json()
            ws.send_json({"type": "simulation_error", "job_id": "job-bad", "error": "boom"})
            thread.join(timeout=10)

        assert holder["result"] == FALLBACK
        assert progress(test_valkey, "FR-8")["stage"] == "cloud"
        assert fresh_node(db, body["worker_id"]).status == "quarantined"

    def test_data_source_error_does_not_quarantine(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            sync(ws)
            thread, holder = start_dispatch(client, db, "job-meteo")
            ws.receive_json()
            ws.send_json({
                "type": "simulation_error",
                "job_id": "job-meteo",
                "error": "Upstream data source unavailable",
                "error_kind": "data_source",
            })
            thread.join(timeout=10)
            sync(ws)

            node = fresh_node(db, body["worker_id"])
            assert holder["result"] == FALLBACK
            assert node.status == "active"
            assert node.consecutive_failures == 0
            assert test_valkey.sismember("worker:pool:idle", body["worker_id"])

    def test_disconnect_mid_job_falls_back(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        
        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            sync(ws)
            thread, holder = start_dispatch(client, db, "job-drop")
            ws.receive_json()
        thread.join(timeout=10)
        
        assert holder["result"] == FALLBACK
        assert fresh_node(db, body["worker_id"]).status == "offline"

    def test_timeout_quarantine_worker(self, client, db, test_valkey, user_headers, monkeypatch):
        monkeypatch.setattr(worker_routes, "JOB_TIMEOUT_SECONDS", 1.0)
        _, headers = user_headers
        body = register(client, headers)

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            sync(ws)
            thread, holder = start_dispatch(client, db, "job-slow")
            ws.receive_json()
            thread.join(timeout=10)

            node = fresh_node(db, body["worker_id"])
            assert holder["result"] == FALLBACK
            assert node.status == "quarantined"
            assert node.consecutive_failures == 1

class TestWorkerManagement:
    def test_deactivate_then_activate(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        worker_id = register(client, headers)["worker_id"]

        resp = client.post(f"/api/v1/workers/{worker_id}/deactivate", headers=headers)
        assert resp.status_code == 200
        assert fresh_node(db, worker_id).status == "deactivated"
        assert not test_valkey.sismember("worker:pool:idle", worker_id)

        resp = client.post(f"/api/v1/workers/{worker_id}/activate", headers=headers)
        assert resp.status_code == 200
        assert fresh_node(db, worker_id).status == "active"
        assert test_valkey.sismember("worker:pool:idle", worker_id)

    def test_other_user_cannot_deactivate(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        worker_id = register(client, headers)["worker_id"]
        stranger = make_user(db)

        resp = client.post(f"/api/v1/workers/{worker_id}/deactivate", headers=auth_headers(stranger))
        assert resp.status_code == 403

    def test_deactivate_worker_cannot_connect(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        client.post(f"/api/v1/workers/{body['worker_id']}/deactivate", headers=headers)

        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])):
                pass
        assert exc.value.code == 1008

    def test_removed_worker_gets_credentials_rejected(self, client, db, test_valkey, user_headers):
        _, headers = user_headers
        body = register(client, headers)
        resp = client.post(f"/api/v1/workers/{body['worker_id']}/remove", headers=headers, json={"reason": "new machine"})

        assert resp.status_code == 200
        assert fresh_node(db, body["worker_id"]).status == "removed"

        with client.websocket_connect(WS_PATH, headers=ws_headers(body["access_token"])) as ws:
            with pytest.raises(WebSocketDisconnect) as exc:
                ws.receive_text()
        assert exc.value.code == 4401

    def test_run_command_has_no_key_and_pulls(self, client, test_valkey, user_headers):
        _, headers = user_headers
        worker_id = register(client, headers)["worker_id"]

        resp = client.get(f"/api/v1/workers/{worker_id}/command", headers=headers)
        assert resp.status_code == 200
        command = resp.json()["docker_command"]
        assert "--pull always" in command
        assert "fireaway-worker-data:/data" in command
        assert "REGISTRATION_KEY" not in command

    def test_command_for_removed_worker_is_conflict(self, client, test_valkey, user_headers):
        _, headers = user_headers
        worker_id = register(client, headers)["worker_id"]
        client.post(f"/api/v1/workers/{worker_id}/remove", headers=headers, json={"reason": "gone"})

        assert client.get(f"/api/v1/workers/{worker_id}/command", headers=headers).status_code == 409

    def test_reset_key_issues_fresh_key_for_owner(self, client, test_valkey, user_headers):
        user, headers = user_headers
        worker_id = register(client, headers)["worker_id"]

        resp = client.post(f"/api/v1/workers/{worker_id}/reset-key", headers=headers)
        assert resp.status_code == 201

        key = resp.json()["registration_key"]
        assert key in resp.json()["docker_command"]
        assert test_valkey.get(f"worker:reg:{key}") == user.id

    def test_compute_distribution_counts_registerd_worker(self, client, test_valkey, user_headers):
        _, headers = user_headers
        register(client, headers)

        body = client.get("/api/v1/workers/compute-distribution").json()
        assert body["active"] >= 1
        assert body["total"] == body["active"] + body["busy"] + body["quarantined"] + body["offline"]
