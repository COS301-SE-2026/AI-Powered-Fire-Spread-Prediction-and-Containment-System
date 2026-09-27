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

class TestRegisterWorkerNode:
    def _req(self, vram_mb):
        return WorkerRegisterRequest(
            registration_key="REG-AAAABBBBCCCCDDDD",
            label="test-rig",
            gpu_name="Test GPU",
            vram_mb=vram_mb,
            driver_version="12.8",
            cuda_capable=True
        )

    def test_low_vram_rejected_without_burning_key(self):
        fake_valkey = MagicMock()
        with patch.object(worker_service, "valkey_client", fake_valkey):
            with pytest.raises(HTTPException) as exc:
                worker_service.register_worker_node(MagicMock, self._req(2048))
        assert exc.value.status_code == 400
        fake_valkey.pipeline.assert_not_called()

    def test_unknown_key_raises_401(self):
        fake_valkey = MagicMock()
        fake_valkey.pipeline.return_value.execute.return_value = [None, 0]
        with patch.object(worker_service, "valkey_client", fake_valkey):
            with pytest.raises(HTTPException) as exc:
                worker_service.register_worker_node(MagicMock, self._req(8192))
        assert exc.value.status_code == 401

class TestPreFlightCheck:
    @staticmethod
    def _props(name, total_bytes):
        props = MagicMock()
        props.name = name
        props.total_memory = total_bytes
        return props

    def test_passes_with_good_gpu(self):
        import gpu_worker.client_worker as cw
        cuda = cw.torch.cuda
        with patch.object(cuda, "is_available", return_value=True), \
             patch.object(cuda, "device_count", return_value=1), \
             patch.object(cuda, "get_device_properties", return_value=self._props("RTX 5070", 12 * 1024**3)), \
             patch.object(cuda, "synchronize"), \
             patch.object(cuda, "empty_cache"), \
             patch.object(cuda, "is_available", return_value=True), \
             patch.object(cw.torch, "randn", return_value=MagicMock()), \
             patch.object(cw.torch, "matmul", return_value=MagicMock()), \
             patch.object(cw, "BENCHMARK_DURATION_SECONDS", 0.01):
            passed, name, vram = cw.run_pre_flight_check()
        assert passed is True
        assert name == "RTX 5070"
        assert vram == 12 * 1024

    def test_failes_without_cuda(self):
        import gpu_worker.client_worker as cw
        with patch.object(cw.torch.cuda, "is_available", return_value=False):
            passed, _, vram = cw.run_pre_flight_check()
        assert passed is False
        assert vram == 0

    def test_failes_below_vram_minimum(self):
            import gpu_worker.client_worker as cw
            cuda = cw.torch.cuda
            with patch.object(cuda, "is_available", return_value=True), \
                         patch.object(cuda, "device_count", return_value=1), \
                         patch.object(cuda, "get_device_properties", return_value=self._props("Weak GPU", 2 * 1024**3)):
                passed, _, vram = cw.run_pre_flight_check()
            assert passed is False
            assert vram == 2 * 1024

class TestExecutePipelineTask:
    def test_weather_tensor_shape_and_channel_order(self, small_grids):
        """
        Canonical order:
            [
                wind_u,
                wind_v,
                temperature,
                rel_humidity
            ]
            -> [1,T,4,H,W]
        """

        import gpu_worker.client_worker as cw
        weather, static, _ =small_grids(H=5, W=5)
        T = 6
        captured = {}

        def fake_run(**kwargs):
            captured["weather"] = kwargs["weather_history"]
            return [np.zeros((5, 5), dtype=np.int8)]

        payload = {
            "job_id": "unit-1", 
            "grid_h": 5,
            "grid_w": 5,
            "cell_size_m": 15.0,
            "boundary_radius_m": 500.0,
            "n_steps": 1,
            "grid_bounds": [0, 0, 1, 1]
        }

        with patch.object(cw, "fetch_weather_history", return_value=[dict(weather)] * T), \
             patch.object(cw, "fetch_static_grids", return_value=static), \
             patch.object(cw, "build_boundary_ignition_mask", return_value=np.zeros((5,5), bool)), \
             patch.object(cw, "run_convlstm_dca", side_effect=fake_run):
            result = cw.execute_pipeline_task(MagicMock(), payload)

        wt = captured["weather"]
        assert tuple(wt.shape) == (1, T, 4, 5, 5)
        assert float(wt[0, 0, 0].mean()) == pytest.approx(3.0) # wind u
        assert float(wt[0, 0, 2].mean()) == pytest.approx(25.0) # temp 
        assert float(wt[0, 0, 3].mean()) == pytest.approx(30.0) # humidity
        assert result == {"job_id": "unit-1", "status": "completed", "history": [np.zeros((5,5)).tolist()]}
