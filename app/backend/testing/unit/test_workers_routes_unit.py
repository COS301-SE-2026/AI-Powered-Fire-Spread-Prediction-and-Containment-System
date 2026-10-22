"""Unit Tests for the helper logic in the worker routes"""

import asyncio
import json

import fakeredis
import pytest
from fastapi import HTTPException
from jose import jwt

from app.backend.src.routes import workers as worker_routes
from app.backend.src.services import workers as worker_service

SECRET = "unit-test-secret"
FALLBACK = {"dispatched_to": "cloud_fallback", "status": "queued"}

class BrokenValkey:
    """Every call raises like a valkey that is down"""
    def __getattr__(self, name):
        def fail(*args, **kwargs):
            raise ConnectionError("valkey down")
        return fail

@pytest.fixture
def valkey(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(worker_service, "valkey_client", fake)
    return fake

@pytest.fixture
def broken_valkey(monkeypatch):
    monkeypatch.setattr(worker_service, "valkey_client", BrokenValkey())

@pytest.fixture
def secret(monkeypatch):
    monkeypatch.setattr(worker_routes, "JWT_SECRET_KEY", SECRET)

def stored(valkey, key):
    return json.loads(valkey.get(f"sim:progress:{key}"))

def worker_token(key=SECRET, **claims):
    body = {"sub": "worker-1", "role": "worker_node", "type": "worker_device"}
    body.update(claims)
    return jwt.encode({k: v for k, v in body.items() if v is not None}, key, algorithm="HS256")

class TestSimProgress:
    def test_set_stores_stage_with_ttl(self, valkey):
        worker_routes.set_sim_progress("FR-1", "received", "Job picked up")
        assert stored(valkey, "FR-1") == {"stage": "received", "message": "Job picked up"}
        assert 0 < valkey.ttl("sim:progress:FR-1") <= worker_routes.PROGRESS_TTL_SECONDS

    def test_set_without_key_is_noop(self, valkey):
        worker_routes.set_sim_progress(None, "received", "x")
        assert not valkey.keys()

    def test_set_swallows_valkey_errors(self, broken_valkey):
        worker_routes.set_sim_progress("FR-1", "received", "x")

    def test_clear_removes_stage(self, valkey):
        worker_routes.set_sim_progress("FR-1", "received", "x")
        worker_routes.clear_sim_progress("FR-1")
        assert valkey.get("sim:progress:FR-1") is None

    def test_clear_without_key_is_noop(self, valkey):
        worker_routes.clear_sim_progress(None)

    def test_clear_swallows_valkey_errors(self, broken_valkey):
        worker_routes.clear_sim_progress("FR-1")

    def test_cloud_fallback_marks_cloud_stage(self, valkey):
        assert worker_routes.cloud_fallback("FR-1") == FALLBACK
        assert stored(valkey, "FR-1")["stage"] == "cloud"

class TestHasActiveVolunteerWorkers:
    def test_idle_worker_with_live_connection(self, valkey, monkeypatch):
        valkey.sadd("worker:pool:idle", "w1")
        monkeypatch.setattr(worker_routes, "active_worker_connections", {"w1": object()})
        assert worker_routes.has_active_volunteer_workers() is True

    def test_idle_set_but_no_connections(self, valkey, monkeypatch):
        valkey.sadd("worker:pool:idle", "w1")
        monkeypatch.setattr(worker_routes, "active_worker_connections", {})
        assert worker_routes.has_active_volunteer_workers() is False

    def test_connections_but_none_idle(self, valkey, monkeypatch):
        monkeypatch.setattr(worker_routes, "active_worker_connections", {"w1": object()})
        assert worker_routes.has_active_volunteer_workers() is False

    def test_falls_back_to_connections_when_valkey_down(self, broken_valkey, monkeypatch):
            monkeypatch.setattr(worker_routes, "active_worker_connections", {"w1": object()})
            assert worker_routes.has_active_volunteer_workers() is True

class TestVerifyWorkerToken:
    def test_valid_worker_token_returns_worker_id(self, secret):
        assert asyncio.run(worker_routes.verify_worker_token(worker_token())) == "worker-1"

    @pytest.mark.parametrize("claims", [{"role": "user"}, {"type": "access"}, {"sub": None}])
    def test_wrong_scope_is_rejected(self, secret, claims):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(worker_routes.verify_worker_token(worker_token(**claims)))
        assert exc.value.status_code == 401

    def test_forged_signature_is_rejected(self, secret):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(worker_routes.verify_worker_token(worker_token(key="someone-else")))
        assert exc.value.status_code == 401

    def test_garbage_is_rejected(self, secret):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(worker_routes.verify_worker_token("not-a-jwt"))
        assert exc.value.status_code == 401

class TestDispatchWithoutUsableWorker:
    """Paths that return before touching DB"""
    def test_no_idle_worker_falls_back_to_cloud(self, valkey):
        result = asyncio.run(
            worker_routes.dispatch_simulation_task({"job_id": "j1"}, db=object(), progress_key="FR-1")
        )
        assert result == FALLBACK
        assert stored(valkey, "FR-1")["stage"] == "cloud"

    def test_idle_entry_without_connection_is_dropped(self, valkey, monkeypatch):
        valkey.sadd("worker:pool:idle", "ghost")
        monkeypatch.setattr(worker_routes, "active_worker_connections", {})
        result = asyncio.run(
            worker_routes.dispatch_simulation_task({"job_id": "j1"}, db=object(), progress_key="FR-1")
        )
        assert result == FALLBACK
        assert not valkey.sismember("worker:pool:idle", "ghost")

    