from __future__ import annotations

import asyncio
import base64
import json
import zlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.ai import simulation_api as sim
from app.backend.src.ai.simulation_api import (
    ClusterSimRequest,
    cluster_fires_by_bbox_overlap,
    decode_history,
    grid_dimensions_for_extent,
    router,
    run_cluster_simulation,
    run_simulation_job,
    simulate_fire_cluster,
    simulate_single_fire,
    wait_for_result,
)
from app.backend.src.dependencies.auth import get_current_user


class DummyFireReport:
    def __init__(self, id: str, reference_number: str, lat: float, lng: float, boundary_radius: float):
        self.id = id
        self.reference_number = reference_number
        self.lat = lat
        self.lng = lng
        self.boundary_radius = boundary_radius


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "test-user", "role": "admin"}
    return app


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def client(test_app, mock_db):
    test_app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(test_app) as c:
        yield c
    test_app.dependency_overrides.clear()


def test_decode_history_variations():
    arr = np.ones((2, 5, 5), dtype=np.int8)
    compressed = base64.b64encode(zlib.compress(arr.tobytes())).decode("utf-8")
    res_z = decode_history({"history_z": compressed, "history_shape": [2, 5, 5]}, 5, 5)
    np.testing.assert_array_equal(res_z, arr)

    res_empty = decode_history({"history": []}, 5, 5)
    assert res_empty.shape == (0, 5, 5)

    raw_3d = np.ones((2, 3, 3), dtype=np.int8).tolist()
    res_3d = decode_history({"history": raw_3d}, 3, 3)
    assert res_3d.shape == (2, 3, 3)

    raw_flat = [np.ones((9,), dtype=np.int8).tolist()]
    res_flat = decode_history({"history": raw_flat}, 3, 3)
    assert res_flat.shape == (1, 3, 3)


def test_grid_dimensions_large_extent_scale_factor():
    h, w = grid_dimensions_for_extent(1.5, 1.5, -34.0, target_cell_size_m=30.0)
    assert sim.MIN_GRID_DIMENSION <= h <= sim.MAX_GRID_DIMENSION
    assert sim.MIN_GRID_DIMENSION <= w <= sim.MAX_GRID_DIMENSION


def test_cluster_fires_empty_and_path_compression():
    assert cluster_fires_by_bbox_overlap([], 10) == []

    f1 = DummyFireReport("1", "F1", -34.000, 18.500, 0.5)
    f2 = DummyFireReport("2", "F2", -34.002, 18.502, 0.5)
    f3 = DummyFireReport("3", "F3", -34.004, 18.504, 0.5)
    clusters = cluster_fires_by_bbox_overlap([f1, f2, f3], 10)
    assert len(clusters) == 1
    assert len(clusters[0]) == 3


@pytest.mark.asyncio
async def test_wait_for_result_branches(tmp_path, monkeypatch):
    monkeypatch.setattr(sim, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(sim, "RESULT_POLL_TIMEOUT_S", 0.05)
    monkeypatch.setattr(sim, "RESULT_POLL_INTERVAL_S", 0.01)

    bad_file = tmp_path / "bad.json"
    bad_file.write_text("invalid json")

    class DynamicNoSuchKey(Exception):
        pass

    mock_s3 = MagicMock()
    mock_s3.exceptions = SimpleNamespace(NoSuchKey=DynamicNoSuchKey)
    mock_s3.get_object.side_effect = DynamicNoSuchKey("Missing")
    monkeypatch.setattr(sim, "s3_client", mock_s3)

    res = await wait_for_result("bad")
    assert res is None

    mock_s3.get_object.side_effect = RuntimeError("S3 error")
    res_err = await wait_for_result("err")
    assert res_err is None


@pytest.mark.asyncio
async def test_run_simulation_job_volunteer_and_cloud(monkeypatch):
    job = {"job_id": "test-job"}

    monkeypatch.setattr(sim, "has_active_volunteer_workers", lambda: True)
    monkeypatch.setattr(
        sim,
        "dispatch_simulation_task",
        AsyncMock(return_value={"status": "completed", "result": 1}),
    )
    res_vol = await run_simulation_job(job)
    assert res_vol == {"status": "completed", "result": 1}

    monkeypatch.setattr(
        sim,
        "dispatch_simulation_task",
        AsyncMock(return_value={"status": "failed"}),
    )
    monkeypatch.setattr(sim.sqs, "send_message", MagicMock())
    monkeypatch.setattr(sim, "wait_for_result", AsyncMock(return_value={"cloud": "done"}))
    monkeypatch.setattr(sim, "set_sim_progress", MagicMock())
    monkeypatch.setattr(sim, "clear_sim_progress", MagicMock())

    res_cloud = await run_simulation_job(job, progress_key="pk")
    assert res_cloud == {"cloud": "done"}


@pytest.mark.asyncio
async def test_simulate_single_fire_cache_and_timeout(monkeypatch):
    fire = DummyFireReport("id-1", "F1", -34.0, 18.5, 0.4)
    semaphore = asyncio.Semaphore(1)

    cached_payload = {
        "ref": "F1",
        "lat": -34.0,
        "lng": 18.5,
        "history": [[0]],
        "burned_cells": 0,
        "radius_m": 0.0,
        "truncated": False,
        "lat_extent_deg": 0.01,
        "lon_extent_deg": 0.01,
        "grid_h": 10,
        "grid_w": 10,
        "cell_size_m": 30.0,
    }

    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: cached_payload)
    pred_early = await simulate_single_fire(fire, 10, semaphore)
    assert pred_early.ref == "F1"

    calls = [None, cached_payload]
    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: calls.pop(0))
    pred_inner = await simulate_single_fire(fire, 10, semaphore)
    assert pred_inner.ref == "F1"

    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=None))
    with pytest.raises(HTTPException) as exc:
        await simulate_single_fire(fire, 10, semaphore)
    assert exc.value.status_code == 504


@pytest.mark.asyncio
async def test_simulate_fire_cluster_cache_and_timeout(monkeypatch):
    fires = [
        DummyFireReport("id-1", "F1", -34.0, 18.5, 0.4),
        DummyFireReport("id-2", "F2", -34.001, 18.501, 0.4),
    ]
    semaphore = asyncio.Semaphore(1)

    cached_cluster = {
        "fire_refs": ["F1", "F2"],
        "lat": -34.0,
        "lng": 18.5,
        "history": [[0]],
        "burned_cells": 0,
        "radius_m": 0.0,
        "truncated": False,
        "lat_extent_deg": 0.01,
        "lon_extent_deg": 0.01,
        "grid_h": 10,
        "grid_w": 10,
        "cell_size_m": 30.0,
    }

    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: cached_cluster)
    cp_early = await simulate_fire_cluster(fires, 10, semaphore)
    assert cp_early.fire_refs == ["F1", "F2"]

    calls = [None, cached_cluster]
    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: calls.pop(0))
    cp_inner = await simulate_fire_cluster(fires, 10, semaphore)
    assert cp_inner.fire_refs == ["F1", "F2"]

    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: None)
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=None))
    with pytest.raises(HTTPException) as exc:
        await simulate_fire_cluster(fires, 10, semaphore)
    assert exc.value.status_code == 504


def test_api_simulate_empty_fires(client, mock_db):
    mock_db.query.return_value.filter.return_value.all.return_value = []

    response = client.post("/api/simulate", json={"n_steps": 2, "containment_lines": []})
    assert response.status_code == 200
    assert response.json() == {"predictions": [], "cluster_predictions": [], "n_steps_run": 0}


def test_api_simulate_mixed_groups(client, mock_db, monkeypatch):
    f1 = DummyFireReport("id-1", "FIRE-1", -33.900, 18.420, 0.5)
    f2 = DummyFireReport("id-2", "FIRE-2", -33.901, 18.421, 0.5)
    f_isolated = DummyFireReport("id-3", "FIRE-3", -30.000, 25.000, 0.2)

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [f1, f2, f_isolated],
        [("id-1", "LINESTRING(18.42 -33.90, 18.43 -33.90)")],
    ]

    h, w = 10, 10
    sim_output = {
        "status": "completed",
        "history": [np.zeros((h, w), dtype=np.int8).tolist()],
        "weather_by_hour": [{"hour": 0, "temperature_c": 22.0, "rel_humidity_pct": 45.0, "wind_speed_kmh": 12.0, "wind_dir_deg": 180.0}],
        "forecast_source": "open-meteo",
        "forecast_model": {"mean_skill": 0.88, "val_years": ["2023"], "skill_by_channel": {}},
    }

    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: None)
    monkeypatch.setattr(sim, "cache_prediction", MagicMock())
    monkeypatch.setattr(sim, "cache_cluster_prediction", MagicMock())
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=sim_output))

    response = client.post(
        "/api/simulate", 
        json={"n_steps": 2, "containment_lines": ["LINESTRING(18.41 -33.91, 18.44 -33.91)"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == 1
    assert len(data["cluster_predictions"]) == 1
    assert data["n_steps_run"] == 1


def test_api_simulate_single_fire_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    response = client.post("/api/simulate/fire/UNKNOWN", json={"n_steps": 10})
    assert response.status_code == 404


def test_api_simulate_single_fire_success_with_containment_and_cache(client, mock_db, monkeypatch):
    fire = DummyFireReport("id-10", "F-SINGLE", -34.0, 18.5, 0.4)
    mock_db.query.return_value.filter.return_value.first.return_value = fire
    mock_db.query.return_value.filter.return_value.all.return_value = [("LINESTRING(18.50 -34.00, 18.51 -34.01)",)]

    h, w = 54, 54
    sim_output = {
        "status": "completed",
        "history": [np.zeros((h, w), dtype=np.int8).tolist()],
        "weather_by_hour": [],
        "forecast_source": "test",
    }

    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
    monkeypatch.setattr(sim, "cache_prediction", MagicMock())
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=sim_output))

    response = client.post(
        "/api/simulate/fire/F-SINGLE",
        json={"n_steps": 10, "containment_lines": ["LINESTRING(18.49 -34.00, 18.52 -34.00)"]}
    )
    assert response.status_code == 200
    assert response.json()["ref"] == "F-SINGLE"


def test_api_simulate_single_fire_worker_timeout_504(client, mock_db, monkeypatch):
    fire = DummyFireReport("id-10", "F-TIMEOUT", -34.0, 18.5, 0.4)
    mock_db.query.return_value.filter.return_value.first.return_value = fire
    mock_db.query.return_value.filter.return_value.all.return_value = []

    monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=None))

    response = client.post("/api/simulate/fire/F-TIMEOUT", json={"n_steps": 10})
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]


def test_api_simulate_cluster_fewer_than_two_distinct_refs(client):
    response = client.post(
        "/api/simulate/fires",
        json={"fire_refs": ["F1", "F1"], "n_steps": 10}
    )
    assert response.status_code == 422
    assert "at least two distinct fires" in response.json()["detail"]


def test_api_simulate_cluster_missing_fires(client, mock_db):
    f1 = DummyFireReport("id-1", "F1", -34.0, 18.5, 0.5)
    mock_db.query.return_value.filter.return_value.all.return_value = [f1]

    response = client.post(
        "/api/simulate/fires",
        json={"fire_refs": ["F1", "F2"], "n_steps": 10}
    )
    assert response.status_code == 404
    assert "F2" in response.json()["detail"]


def test_api_simulate_cluster_too_far_apart_422(client, mock_db):
    f1 = DummyFireReport("id-1", "F1", -34.0, 18.5, 0.01)
    f2 = DummyFireReport("id-2", "F2", -30.0, 28.0, 0.01)
    mock_db.query.return_value.filter.return_value.all.return_value = [f1, f2]

    response = client.post(
        "/api/simulate/fires",
        json={"fire_refs": ["F1", "F2"], "n_steps": 1}
    )
    assert response.status_code == 422
    assert "too far apart" in response.json()["detail"]


def test_api_simulate_cluster_success(client, mock_db, monkeypatch):
    f1 = DummyFireReport("id-1", "F1", -34.000, 18.500, 0.5)
    f2 = DummyFireReport("id-2", "F2", -34.001, 18.501, 0.5)

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [f1, f2],
        [("id-1", "LINESTRING(18.50 -34.00, 18.51 -34.01)")],
    ]

    expected_h, expected_w = 70, 70
    sim_output = {
        "status": "completed",
        "history": [np.zeros((expected_h, expected_w), dtype=np.int8).tolist()],
        "weather_by_hour": [],
        "forecast_source": "test",
    }

    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: None)
    monkeypatch.setattr(sim, "cache_cluster_prediction", MagicMock())
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=sim_output))

    response = client.post(
        "/api/simulate/fires",
        json={
            "fire_refs": ["F1", "F2"],
            "n_steps": 10,
            "containment_lines": ["LINESTRING(18.49 -34.00, 18.52 -34.00)"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fire_refs"] == ["F1", "F2"]
    assert data["grid_h"] == expected_h
    assert data["grid_w"] == expected_w


def test_api_simulate_cluster_empty_containment_rows_branch(client, mock_db, monkeypatch):
    f1 = DummyFireReport("id-1", "F1", -34.000, 18.500, 0.5)
    f2 = DummyFireReport("id-2", "F2", -34.001, 18.501, 0.5)

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [f1, f2],
        [],
    ]

    sim_output = {
        "status": "completed",
        "history": [np.zeros((70, 70), dtype=np.int8).tolist()],
    }

    monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: None)
    monkeypatch.setattr(sim, "cache_cluster_prediction", MagicMock())
    monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=sim_output))

    response = client.post(
        "/api/simulate/fires",
        json={"fire_refs": ["F1", "F2"], "n_steps": 10}
    )
    assert response.status_code == 200
    assert response.json()["fire_refs"] == ["F1", "F2"]


@pytest.mark.asyncio
async def test_run_cluster_simulation_empty_fire_ids_branch_740(monkeypatch):
    db = MagicMock()
    f1 = DummyFireReport("id-1", "F1", -34.0, 18.5, 0.5)
    f2 = DummyFireReport("id-2", "F2", -34.001, 18.501, 0.5)

    class FiresSequence(list):
        def __init__(self, items):
            super().__init__(items)
            self._iter_count = 0

        def __iter__(self):
            self._iter_count += 1
            if self._iter_count >= 3:
                return iter([])
            return super().__iter__()

    fires_mock = FiresSequence([f1, f2])
    db.query.return_value.filter.return_value.all.return_value = fires_mock

    dummy_pred = sim.ClusterPrediction(
        fire_refs=["F1", "F2"],
        lat=-34.0,
        lng=18.5,
        history=[[0]],
        burned_cells=0,
        radius_m=0.0,
        truncated=False,
        lat_extent_deg=0.01,
        lon_extent_deg=0.01,
        grid_h=10,
        grid_w=10,
        cell_size_m=30.0,
    )
    monkeypatch.setattr(sim, "simulate_fire_cluster", AsyncMock(return_value=dummy_pred))

    req = ClusterSimRequest(fire_refs=["F1", "F2"], n_steps=10)
    res = await run_cluster_simulation(req, db)
    assert res.fire_refs == ["F1", "F2"]