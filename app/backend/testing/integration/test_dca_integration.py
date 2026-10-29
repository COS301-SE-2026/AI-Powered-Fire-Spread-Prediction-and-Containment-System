from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import torch

from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.schema import UNBURNED, BURNING, BURNED
from app.backend.src.ai.sim_constants import MAXSTEPS

@pytest.fixture
def base_dca_environment():
    """Builds a realistic 10x10 synthetic geospatial grid environment."""
    h, w = 10, 10
    static_grids = {
        "elevation": np.full((h, w), 250.0, dtype=np.float32),
        "slope": np.full((h, w), 5.0, dtype=np.float32),
        "aspect_sin": np.zeros((h, w), dtype=np.float32),
        "aspect_cos": np.ones((h, w), dtype=np.float32),
        "fuel_load": np.full((h, w), 0.8, dtype=np.float32),
        "dryness": np.full((h, w), 0.7, dtype=np.float32),
    }

    weather_grid = {
        "wind_u": np.full((h, w), 2.5, dtype=np.float32),
        "wind_v": np.full((h, w), 1.0, dtype=np.float32),
        "rel_humidity": np.full((h, w), 30.0, dtype=np.float32),
        "temperature": np.full((h, w), 28.0, dtype=np.float32),
    }

    return static_grids, weather_grid


def test_dca_exceeds_max_steps_raises_value_error(base_dca_environment):
    """Verifies bounds checking against MAXSTEPS."""
    static_grids, weather_grid = base_dca_environment
    with pytest.raises(ValueError, match="exceeds max steps"):
        run_dca(
            weather_grids=weather_grid,
            static_grids=static_grids,
            cell_size_m=30.0,
            n_steps=MAXSTEPS + 1,
        )


def test_dca_integration_with_explicit_ignition_mask(base_dca_environment):
    """Tests simulation execution with a direct binary ignition mask and static weather."""
    static_grids, weather_grid = base_dca_environment
    h, w = static_grids["elevation"].shape

    ignition_mask = np.zeros((h, w), dtype=bool)
    ignition_mask[5, 5] = True

    history = run_dca(
        weather_grids=weather_grid,
        static_grids=static_grids,
        cell_size_m=30.0,
        n_steps=3,
        ignition_mask=ignition_mask,
    )

    assert len(history) == 4
    for grid in history:
        assert isinstance(grid, np.ndarray)
        assert grid.shape == (h, w)
        assert grid.dtype == np.int64


def test_dca_integration_with_verified_ignition_points_and_containment(base_dca_environment):
    """Tests simulation execution with verified ignition coordinates and containment lines."""
    static_grids, weather_grid = base_dca_environment
    h, w = static_grids["elevation"].shape

    containment_wkt = ["LINESTRING(18.4 34.0, 18.5 34.1)"]
    grid_bounds = (18.3, 33.9, 18.6, 34.2)
    ignition_points = [(3, 3), (4, 4)]

    history = run_dca(
        weather_grids=weather_grid,
        static_grids=static_grids,
        cell_size_m=30.0,
        n_steps=2,
        ignition_points=ignition_points,
        containment_lines=containment_wkt,
        grid_bounds=grid_bounds,
    )

    assert len(history) == 3
    for step_state in history:
        assert np.all(np.isin(step_state, [UNBURNED, BURNING, BURNED]))


def test_dca_integration_hourly_weather_list_and_existing_nonburnable(base_dca_environment):
    """Tests hourly weather sequence updates and pre-existing nonburnable terrain."""
    static_grids, weather_grid = base_dca_environment
    h, w = static_grids["elevation"].shape

    static_with_nonburnable = static_grids.copy()
    existing_nonburnable = np.zeros((h, w), dtype=bool)
    existing_nonburnable[0, :] = True
    static_with_nonburnable["nonburnable"] = existing_nonburnable

    weather_hourly = [weather_grid, weather_grid, weather_grid]

    ignition_mask = np.zeros((h, w), dtype=bool)
    ignition_mask[2, 2] = True

    history = run_dca(
        weather_grids=weather_hourly,
        static_grids=static_with_nonburnable,
        cell_size_m=30.0,
        n_steps=3,
        ignition_mask=ignition_mask,
    )

    assert len(history) == 4


def test_dca_integration_scorer_fallback():
    """Tests fallback to IgnitionScorer when neither points nor mask are passed."""
    h, w = 8, 8
    static_grids = {
        "elevation": np.zeros((h, w), dtype=np.float32),
        "slope": np.zeros((h, w), dtype=np.float32),
        "aspect_sin": np.zeros((h, w), dtype=np.float32),
        "aspect_cos": np.ones((h, w), dtype=np.float32),
        "fuel_load": np.ones((h, w), dtype=np.float32),
        "dryness": np.full((h, w), 0.5, dtype=np.float32),
    }
    weather_grid = {
        "wind_u": np.zeros((h, w), dtype=np.float32),
        "wind_v": np.zeros((h, w), dtype=np.float32),
        "rel_humidity": np.full((h, w), 40.0, dtype=np.float32),
        "temperature": np.full((h, w), 25.0, dtype=np.float32),
    }

    synthetic_prob = np.zeros((h, w), dtype=np.float32)
    synthetic_prob[3, 3] = 0.99

    mock_scorer = MagicMock()
    mock_scorer.score_grid.return_value = synthetic_prob

    with patch("app.backend.src.ai.dca.IgnitionScorer.load", return_value=mock_scorer):
        history = run_dca(
            weather_grids=weather_grid,
            static_grids=static_grids,
            cell_size_m=30.0,
            n_steps=1,
            n_ignition_points=1,
        )

    assert len(history) == 2
    mock_scorer.score_grid.assert_called_once()


def test_dca_cuda_branch_handling(base_dca_environment):
    """Tests the CUDA code path safely by mocking device tensors."""
    static_grids, weather_grid = base_dca_environment
    h, w = static_grids["elevation"].shape
    ignition_mask = np.zeros((h, w), dtype=bool)
    ignition_mask[2, 2] = True

    called_to = []

    from torch.nn import Module
    orig_module_to = Module.to

    def fake_module_to(self, *args, **kwargs):
        if (args and args[0] == "cuda") or kwargs.get("device") == "cuda":
            called_to.append("model_cuda")
            return self
        return orig_module_to(self, *args, **kwargs)

    orig_tensor_to = torch.Tensor.to

    def fake_tensor_to(self, *args, **kwargs):
        if (args and args[0] == "cuda") or kwargs.get("device") == "cuda":
            called_to.append("tensor_cuda")
            return self
        return orig_module_to(self, *args, **kwargs)

    with patch("torch.cuda.is_available", return_value=True), \
        patch.object(Module, "to", fake_module_to), \
        patch.object(torch.Tensor, "to", fake_tensor_to):
        history = run_dca(
            weather_grids=weather_grid,
            static_grids=static_grids,
            cell_size_m=30.0,
            n_steps=1,
            ignition_mask=ignition_mask,
        )

    assert len(history) == 2
    assert "model_cuda" in called_to
    assert "tensor_cuda" in called_to