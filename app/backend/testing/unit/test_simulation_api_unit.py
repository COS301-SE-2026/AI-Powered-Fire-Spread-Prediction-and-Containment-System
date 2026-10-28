
from __future__ import annotations

import asyncio
import base64
import json
import zlib
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from fastapi import HTTPException

from app.backend.src.ai import simulation_api as sim
from app.backend.src.ai.simulation_api import (
    ClusterSimRequest,
    OnDemandSimRequest,
    _bboxes_overlap,
    burned_area_radius_m,
    cluster_fires_by_bbox_overlap,
    decode_history,
    grid_dimensions_for_extent,
    run_cluster_simulation,
    run_simulation,
    run_simulation_job,
    run_single_fire_simulation,
    simulate_fire_cluster,
    simulate_single_fire,
    wait_for_result,
)

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


class TestDecodeHistoryAndHelpers:
    def test_decode_history_compressed(self):
        arr = np.ones((2, 4, 4), dtype=np.int8)
        compressed = base64.b64encode(zlib.compress(arr.tobytes())).decode("utf-8")
        raw = {"history_z": compressed, "history_shape": [2, 4, 4]}
        decoded = decode_history(raw, 4, 4)
        np.testing.assert_array_equal(decoded, arr)

    def test_decode_history_legacy_empty(self):
        decoded = decode_history({"history": []}, 5, 5)
        assert decoded.shape == (0, 5, 5)
        assert decoded.dtype == np.int8

    def test_decode_history_legacy_3d(self):
        legacy = np.ones((2, 3, 3), dtype=np.int8).tolist()
        decoded = decode_history({"history": legacy}, 3, 3)
        assert decoded.shape == (2, 3, 3)

    def test_decode_history_legacy_flattened(self):
        legacy = [np.ones((9,), dtype=np.int8).tolist()]
        decoded = decode_history({"history": legacy}, 3, 3)
        assert decoded.shape == (1, 3, 3)

    def test_grid_dimensions_large_extent_scale_factor(self):
        h, w = grid_dimensions_for_extent(1.5, 1.5, -34.0, target_cell_size_m=30.0)
        assert h <= sim.MAX_GRID_DIMENSION
        assert w <= sim.MAX_GRID_DIMENSION
        assert h >= sim.MIN_GRID_DIMENSION

    def test_burned_area_radius_zero(self):
        assert burned_area_radius_m(0, 10, 10, 0.1, 0.1, -34.0) == 0.0


class TestWaitForResult:
    @pytest.mark.asyncio
    async def test_wait_for_result_local_file_success(self, fake_results_dir):
        job_id = "test-job-local"
        file_path = fake_results_dir / f"{job_id}.json"
        file_path.write_text(json.dumps({"status": "completed", "history": []}))
        res = await wait_for_result(job_id)
        assert res is not None
        assert res["status"] == "completed"

    @pytest.mark.asyncio
    async def test_wait_for_result_local_file_read_error_fallback(self, fake_results_dir, fake_s3, monkeypatch):
        job_id = "test-job-corrupt"
        file_path = fake_results_dir / f"{job_id}.json"
        file_path.write_text("invalid json string {")
        fake_s3.put(f"results/{job_id}.json", {"status": "s3-success"})
        monkeypatch.setattr(sim, "RESULT_POLL_TIMEOUT_S", 0.05)
        monkeypatch.setattr(sim, "RESULT_POLL_INTERVAL_S", 0.01)

        res = await wait_for_result(job_id)
        assert res == {"status": "s3-success"}

    @pytest.mark.asyncio
    async def test_wait_for_result_s3_exception_logged(self, fake_results_dir, monkeypatch):
        job_id = "test-job-s3-fail"
        mock_s3 = MagicMock()
        mock_s3.exceptions = SimpleNamespace(NoSuchKey=FakeNoSuchKey)
        mock_s3.get_object.side_effect = RuntimeError("S3 read timeout")
        monkeypatch.setattr(sim, "s3_client", mock_s3)
        monkeypatch.setattr(sim, "RESULT_POLL_TIMEOUT_S", 0.03)
        monkeypatch.setattr(sim, "RESULT_POLL_INTERVAL_S", 0.01)

        res = await wait_for_result(job_id)
        assert res is None


class TestClusterBboxOverlap:
    def test_cluster_fires_empty(self):
        assert cluster_fires_by_bbox_overlap([], 10) == []

    def test_cluster_fires_union_and_find_branches(self):
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        f2 = FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5)
        f3 = FakeFire(id="3", reference_number="F3", lat=-34.002, lng=18.502, boundary_radius=0.5)
        f_far = FakeFire(id="4", reference_number="F4", lat=-30.0, lng=25.0, boundary_radius=0.1)

        clusters = cluster_fires_by_bbox_overlap([f1, f2, f3, f_far], 10)
        assert len(clusters) == 2


class TestRunSimulationJob:
    @pytest.mark.asyncio
    async def test_volunteer_worker_success(self, monkeypatch):
        monkeypatch.setattr(sim, "has_active_volunteer_workers", lambda: True)
        mock_dispatch = AsyncMock(return_value={"status": "completed", "history": []})
        monkeypatch.setattr(sim, "dispatch_simulation_task", mock_dispatch)

        res = await run_simulation_job({"job_id": "job-vol-ok"})
        assert res == {"status": "completed", "history": []}

    @pytest.mark.asyncio
    async def test_volunteer_worker_failed_and_fallback_to_cloud(
        self, monkeypatch, fake_sqs, fake_results_dir
    ):
        monkeypatch.setattr(sim, "has_active_volunteer_workers", lambda: True)
        mock_dispatch = AsyncMock(return_value={"status": "failed"})
        monkeypatch.setattr(sim, "dispatch_simulation_task", mock_dispatch)
        monkeypatch.setattr(sim, "set_sim_progress", MagicMock())
        monkeypatch.setattr(sim, "clear_sim_progress", MagicMock())

        (fake_results_dir / "job-fallback.json").write_text(json.dumps({"status": "completed", "history": []}))

        res = await run_simulation_job({"job_id": "job-fallback"})
        assert res == {"status": "completed", "history": []}
        assert len(fake_sqs.sent_messages) == 1

    @pytest.mark.asyncio
    async def test_volunteer_worker_exception_fallback(
        self, monkeypatch, fake_sqs, fake_results_dir
    ):
        monkeypatch.setattr(sim, "has_active_volunteer_workers", lambda: True)
        mock_dispatch = AsyncMock(side_effect=Exception("Connection reset"))
        monkeypatch.setattr(sim, "dispatch_simulation_task", mock_dispatch)
        monkeypatch.setattr(sim, "set_sim_progress", MagicMock())
        monkeypatch.setattr(sim, "clear_sim_progress", MagicMock())

        (fake_results_dir / "job-err.json").write_text(json.dumps({"status": "completed", "history": []}))

        res = await run_simulation_job({"job_id": "job-err"})
        assert res == {"status": "completed", "history": []}


class TestSimulateSingleAndCluster:
    @pytest.mark.asyncio
    async def test_simulate_single_fire_cached_early(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        cached_payload = {
            "ref": "F1",
            "lat": -34.0,
            "lng": 18.5,
            "history": [[0]],
            "burned_cells": 1,
            "radius_m": 10.0,
            "truncated": False,
            "lat_extent_deg": 0.01,
            "lon_extent_deg": 0.01,
            "grid_h": 10,
            "grid_w": 10,
            "cell_size_m": 30.0,
        }
        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: cached_payload)
        pred = await simulate_single_fire(fire, 10, asyncio.Semaphore(1))
        assert pred.ref == "F1"

    @pytest.mark.asyncio
    async def test_simulate_single_fire_cached_inside_semaphore(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        cached_payload = {
            "ref": "F1",
            "lat": -34.0,
            "lng": 18.5,
            "history": [[0]],
            "burned_cells": 1,
            "radius_m": 10.0,
            "truncated": False,
            "lat_extent_deg": 0.01,
            "lon_extent_deg": 0.01,
            "grid_h": 10,
            "grid_w": 10,
            "cell_size_m": 30.0,
        }
        calls = [None, cached_payload]
        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: calls.pop(0))

        pred = await simulate_single_fire(fire, 10, asyncio.Semaphore(1))
        assert pred.ref == "F1"

    @pytest.mark.asyncio
    async def test_simulate_single_fire_timeout_raises_504(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=None))

        with pytest.raises(HTTPException) as exc_info:
            await simulate_single_fire(fire, 10, asyncio.Semaphore(1))
        assert exc_info.value.status_code == 504

    @pytest.mark.asyncio
    async def test_simulate_single_fire_full_flow(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
        monkeypatch.setattr(sim, "cache_prediction", MagicMock())

        h, w = 10, 10
        raw_result = {
            "history": [np.zeros((h, w), dtype=np.int8).tolist()],
            "weather_by_hour": [{"hour": 0, "temperature_c": 20.0, "rel_humidity_pct": 50.0, "wind_speed_kmh": 10.0, "wind_dir_deg": 90.0}],
            "forecast_source": "open-meteo",
            "forecast_model": {"mean_skill": 0.85, "val_years": ["2022"], "skill_by_channel": {}},
        }
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=raw_result))

        pred = await simulate_single_fire(fire, 10, asyncio.Semaphore(1))
        assert pred.ref == "F1"
        assert pred.forecast_source == "open-meteo"
        assert pred.forecast_model.mean_skill == 0.85

    @pytest.mark.asyncio
    async def test_simulate_fire_cluster_cached_early(self, monkeypatch):
        fires = [FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)]
        cached_payload = {
            "fire_refs": ["F1"],
            "lat": -34.0,
            "lng": 18.5,
            "history": [[0]],
            "burned_cells": 1,
            "radius_m": 10.0,
            "truncated": False,
            "lat_extent_deg": 0.01,
            "lon_extent_deg": 0.01,
            "grid_h": 10,
            "grid_w": 10,
            "cell_size_m": 30.0,
        }
        monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: cached_payload)
        cp = await simulate_fire_cluster(fires, 10, asyncio.Semaphore(1))
        assert cp.fire_refs == ["F1"]

    @pytest.mark.asyncio
    async def test_simulate_fire_cluster_timeout_raises_504(self, monkeypatch):
        fires = [
            FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5),
            FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5),
        ]
        monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: None)
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=None))

        with pytest.raises(HTTPException) as exc_info:
            await simulate_fire_cluster(fires, 10, asyncio.Semaphore(1))
        assert exc_info.value.status_code == 504

    @pytest.mark.asyncio
    async def test_simulate_fire_cluster_full_flow(self, monkeypatch):
        fires = [
            FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5),
            FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5),
        ]
        calls = [None, None]
        monkeypatch.setattr(sim, "get_cached_cluster_prediction", lambda k: calls.pop(0) if calls else None)
        monkeypatch.setattr(sim, "cache_cluster_prediction", MagicMock())

        h, w = 12, 12
        raw_result = {"history": [np.zeros((h, w), dtype=np.int8).tolist()]}
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=raw_result))

        cp = await simulate_fire_cluster(fires, 10, asyncio.Semaphore(1), containment_lines_by_fire={"F1": ["LINESTRING(0 0, 1 1)"]})
        assert cp.fire_refs == ["F1", "F2"]


class TestFastAPIEndpoints:
    @pytest.mark.asyncio
    async def test_run_simulation_empty_fires(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        req = OnDemandSimRequest(n_steps=10)
        resp = await run_simulation(req, db)
        assert resp.predictions == []
        assert resp.cluster_predictions == []
        assert resp.n_steps_run == 0

    @pytest.mark.asyncio
    async def test_run_simulation_mixed_single_and_cluster(self, monkeypatch):
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.1)
        f2 = FakeFire(id="2", reference_number="F2", lat=-33.0, lng=19.0, boundary_radius=0.1)
        f3 = FakeFire(id="3", reference_number="F3", lat=-33.001, lng=19.001, boundary_radius=0.1)

        db = MagicMock()
        db.query.return_value.filter.return_value.all.side_effect = [
            [f1, f2, f3],
            [("1", "LINESTRING(18.5 -34.0, 18.51 -34.01)")],
        ]

        dummy_pred = sim.Prediction(
            ref="F1", lat=-34.0, lng=18.5, history=[[0]], burned_cells=0,
            radius_m=0.0, truncated=False, lat_extent_deg=0.01, lon_extent_deg=0.01,
            grid_h=10, grid_w=10, cell_size_m=30.0
        )
        dummy_cluster_pred = sim.ClusterPrediction(
            fire_refs=["F2", "F3"], lat=-33.0, lng=19.0, history=[[0], [0]], burned_cells=0,
            radius_m=0.0, truncated=False, lat_extent_deg=0.01, lon_extent_deg=0.01,
            grid_h=10, grid_w=10, cell_size_m=30.0
        )

        monkeypatch.setattr(sim, "simulate_single_fire", AsyncMock(return_value=dummy_pred))
        monkeypatch.setattr(sim, "simulate_fire_cluster", AsyncMock(return_value=dummy_cluster_pred))

        req = OnDemandSimRequest(n_steps=10, containment_lines=["LINESTRING(18.0 -34.0, 18.1 -34.0)"])
        resp = await run_simulation(req, db)
        assert len(resp.predictions) == 1
        assert len(resp.cluster_predictions) == 1
        assert resp.n_steps_run == 2

    @pytest.mark.asyncio
    async def test_run_single_fire_simulation_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await run_single_fire_simulation("UNKNOWN", OnDemandSimRequest(n_steps=10), db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_run_single_fire_simulation_success(self, monkeypatch):
        f = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.1)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = f
        db.query.return_value.filter.return_value.all.return_value = [("LINESTRING(0 0, 1 1)",)]

        dummy_pred = sim.Prediction(
            ref="F1", lat=-34.0, lng=18.5, history=[[0]], burned_cells=0,
            radius_m=0.0, truncated=False, lat_extent_deg=0.01, lon_extent_deg=0.01,
            grid_h=10, grid_w=10, cell_size_m=30.0
        )
        monkeypatch.setattr(sim, "simulate_single_fire", AsyncMock(return_value=dummy_pred))

        res = await run_single_fire_simulation("F1", OnDemandSimRequest(n_steps=10), db)
        assert res.ref == "F1"

    @pytest.mark.asyncio
    async def test_run_cluster_simulation_fewer_than_two_distinct_refs(self):
        db = MagicMock()
        req = ClusterSimRequest(fire_refs=["F1", "F1"], n_steps=10)
        with pytest.raises(HTTPException) as exc_info:
            await run_cluster_simulation(req, db)
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_run_cluster_simulation_missing_fires(self):
        db = MagicMock()
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.1)
        db.query.return_value.filter.return_value.all.return_value = [f1]

        req = ClusterSimRequest(fire_refs=["F1", "F2"], n_steps=10)
        with pytest.raises(HTTPException) as exc_info:
            await run_cluster_simulation(req, db)
        assert exc_info.value.status_code == 404
        assert "F2" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_run_cluster_simulation_disjoint_clusters_raises_422(self):
        db = MagicMock()
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        f2 = FakeFire(id="2", reference_number="F2", lat=-30.0, lng=28.0, boundary_radius=0.01)
        db.query.return_value.filter.return_value.all.return_value = [f1, f2]

        req = ClusterSimRequest(fire_refs=["F1", "F2"], n_steps=1)
        with pytest.raises(HTTPException) as exc_info:
            await run_cluster_simulation(req, db)
        assert exc_info.value.status_code == 422
        assert "too far apart" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_run_cluster_simulation_success(self, monkeypatch):
        db = MagicMock()
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        f2 = FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5)

        db.query.return_value.filter.return_value.all.side_effect = [
            [f1, f2],
            [("1", "LINESTRING(18.5 -34.0, 18.51 -34.01)")],
        ]

        dummy_cluster_pred = sim.ClusterPrediction(
            fire_refs=["F1", "F2"], lat=-34.0, lng=18.5, history=[[0]], burned_cells=0,
            radius_m=0.0, truncated=False, lat_extent_deg=0.01, lon_extent_deg=0.01,
            grid_h=10, grid_w=10, cell_size_m=30.0
        )
        monkeypatch.setattr(sim, "simulate_fire_cluster", AsyncMock(return_value=dummy_cluster_pred))

        req = ClusterSimRequest(fire_refs=["F1", "F2"], n_steps=10)
        res = await run_cluster_simulation(req, db)
        assert res.fire_refs == ["F1", "F2"]

class TestMissingBranchesSimulationApi:
    @pytest.mark.asyncio
    async def test_wait_for_result_nosuchkey_exception(self, monkeypatch):

        class DynamicNoSuchKey(Exception):
            pass

        mock_s3 = MagicMock()
        mock_s3.exceptions = SimpleNamespace(NoSuchKey=FakeNoSuchKey)
        mock_s3.get_object.side_effect = FakeNoSuchKey("Key not found")

        monkeypatch.setattr(sim, "s3_client", mock_s3)
        monkeypatch.setattr(sim, "RESULT_POLL_TIMEOUT_S", 0.02)
        monkeypatch.setattr(sim, "RESULT_POLL_INTERVAL_S", 0.01)

        res = await wait_for_result("test-missing-key-job")
        assert res is None

    @pytest.mark.asyncio
    async def test_simulate_single_fire_cache_miss_branch(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)

        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
        monkeypatch.setattr(sim, "cache_prediction", MagicMock())

        h, w = 10, 10
        raw_result = {
            "history": [np.zeros((h, w), dtype=np.int8).tolist()],
            "weather_by_hour": [],
            "forecast_source": "test",
        }
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=raw_result))

        semaphore = asyncio.Semaphore(1)
        res = await simulate_single_fire(fire, 10, semaphore)
        assert res.ref == "F1"

    def test_cluster_fires_path_compression(self):
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.000, lng=18.500, boundary_radius=0.5)
        f2 = FakeFire(id="2", reference_number="F2", lat=-34.002, lng=18.502, boundary_radius=0.5)
        f3 = FakeFire(id="3", reference_number="F3", lat=-34.004, lng=18.504, boundary_radius=0.5)

        clusters = cluster_fires_by_bbox_overlap([f1, f2, f3], 10)
        assert len(clusters) == 1
        assert len(clusters[0]) == 3

    @pytest.mark.asyncio
    async def test_simulate_fire_cluster_cached_inside_semaphore(self, monkeypatch):
        fires = [
            FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5),
            FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5),
        ]
        cached_payload = {
            "fire_refs": ["F1", "F2"],
            "lat": -34.0,
            "lng": 18.5,
            "history": [[0]],
            "burned_cells": 1,
            "radius_m": 10.0,
            "truncated": False,
            "lat_extent_deg": 0.01,
            "lon_extent_deg": 0.01,
            "grid_h": 10,
            "grid_w": 10,
            "cell_size_m": 30.0,
        }
        calls = [None, cached_payload]
        monkeypatch.setattr(
            sim, "get_cached_cluster_prediction", lambda k: calls.pop(0) if calls else cached_payload
        )

        res = await simulate_fire_cluster(fires, 10, asyncio.Semaphore(1))
        assert res.fire_refs == ["F1", "F2"]

    @pytest.mark.asyncio
    async def test_simulate_single_fire_cache_miss_branch(self, monkeypatch):
        fire = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        monkeypatch.setattr(sim, "get_cached_prediction", lambda k: None)
        monkeypatch.setattr(sim, "cache_prediction", MagicMock())

        h, w = 10, 10
        raw_result = {"history": [np.zeros((h, w), dtype=np.int8).tolist()]}
        monkeypatch.setattr(sim, "run_simulation_job", AsyncMock(return_value=raw_result))

        res = await simulate_single_fire(fire, 10, asyncio.Semaphore(1))
        assert res.ref == "F1"

    @pytest.mark.asyncio
    async def test_run_cluster_simulation_fire_ids_empty_branch(self, monkeypatch):
        db = MagicMock()
        f1 = FakeFire(id="1", reference_number="F1", lat=-34.0, lng=18.5, boundary_radius=0.5)
        f2 = FakeFire(id="2", reference_number="F2", lat=-34.001, lng=18.501, boundary_radius=0.5)
        db.query.return_value.filter.return_value.all.return_value = [f1, f2]

        class FiresContainer(list):
            def __init__(self, items):
                super().__init__(items)
                self._iter_count = 0

            def __iter__(self):
                self._iter_count += 1
                if self._iter_count >= 3:
                    return iter([])
                return super().__iter__()

        fires_mock = FiresContainer([f1, f2])
        db.query.return_value.filter.return_value.all.return_value = fires_mock

        dummy_cluster_pred = sim.ClusterPrediction(
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
        monkeypatch.setattr(sim, "simulate_fire_cluster", AsyncMock(return_value=dummy_cluster_pred))

        req = ClusterSimRequest(fire_refs=["F1", "F2"], n_steps=10)
        res = await run_cluster_simulation(req, db)
        assert res.fire_refs == ["F1", "F2"]