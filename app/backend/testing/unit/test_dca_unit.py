from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import torch

from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.schema import UNBURNED


@pytest.fixture
def base_grids():
    h, w = 6, 6
    static = {
        "elevation": np.zeros((h, w), dtype=np.float32),
        "slope": np.zeros((h, w), dtype=np.float32),
        "aspect_sin": np.zeros((h, w), dtype=np.float32),
        "aspect_cos": np.ones((h, w), dtype=np.float32),
        "fuel_load": np.ones((h, w), dtype=np.float32),
        "dryness": np.full((h, w), 0.5, dtype=np.float32),
    }
    weather = {
        "wind_u": np.zeros((h, w), dtype=np.float32),
        "wind_v": np.zeros((h, w), dtype=np.float32),
        "rel_humidity": np.full((h, w), 40.0, dtype=np.float32),
        "temperature": np.full((h, w), 25.0, dtype=np.float32),
    }
    return static, weather


def test_run_dca_exceeds_max_steps(base_grids):
    static, weather = base_grids
    with pytest.raises(ValueError, match="exceeds max steps"):
        run_dca(
            weather_grids=weather,
            static_grids=static,
            cell_size_m=30.0,
            n_steps=999999,
        )


@patch("app.backend.src.ai.dca.WildfireModel")
@patch("app.backend.src.ai.dca.convert_containment_line")
@patch("app.backend.src.ai.dca.build_env_data")
@patch("app.backend.src.ai.dca.state_to_burn_state")
def test_run_dca_with_ignition_mask(
    mock_state_to_burn,
    mock_build_env,
    mock_convert_containment,
    mock_model_cls,
    base_grids,
):
    static, weather = base_grids
    h, w = static["elevation"].shape

    mock_convert_containment.return_value = np.zeros((h, w), dtype=bool)
    mock_build_env.return_value = {}
    mock_state_to_burn.return_value = np.zeros((h, w), dtype=np.int64)

    mock_model_instance = MagicMock()
    mock_model_instance.state = torch.zeros((1, h, w), dtype=torch.float32)
    mock_model_instance.to.return_value = mock_model_instance
    mock_model_cls.return_value = mock_model_instance

    ignition_mask = np.zeros((h, w), dtype=bool)
    ignition_mask[2, 2] = True

    with patch("torch.cuda.is_available", return_value=False):
        history = run_dca(
            weather_grids=weather,
            static_grids=static,
            cell_size_m=30.0,
            n_steps=2,
            ignition_mask=ignition_mask,
        )

    assert len(history) == 3
    mock_model_instance.to.assert_called_with("cpu")
    mock_model_cls.assert_called_once()
    assert mock_model_instance.compute.call_count == 2


@patch("app.backend.src.ai.dca.WildfireModel")
@patch("app.backend.src.ai.dca.convert_containment_line")
@patch("app.backend.src.ai.dca.build_verified_reports_mask")
@patch("app.backend.src.ai.dca.binary_dilation")
@patch("app.backend.src.ai.dca.build_env_data")
@patch("app.backend.src.ai.dca.state_to_burn_state")
@patch("app.backend.src.ai.dca.update_model_tensors")
def test_run_dca_hourly_weather_and_containment_dilation(
    mock_update_tensors,
    mock_state_to_burn,
    mock_build_env,
    mock_binary_dilation,
    mock_verified_mask,
    mock_convert_containment,
    mock_model_cls,
    base_grids,
):
    static, weather = base_grids
    h, w = static["elevation"].shape

    static_with_nonburnable = static.copy()
    static_with_nonburnable["nonburnable"] = np.zeros((h, w), dtype=bool)

    raw_containment = np.zeros((h, w), dtype=bool)
    raw_containment[1, 1] = True
    mock_convert_containment.return_value = raw_containment
    mock_binary_dilation.return_value = raw_containment

    mock_verified_mask.return_value = np.zeros((h, w), dtype=bool)
    mock_build_env.return_value = {}
    mock_state_to_burn.return_value = np.zeros((h, w), dtype=np.int64)

    mock_model_instance = MagicMock()
    mock_model_instance.state = torch.zeros((1, h, w), dtype=torch.float32)
    mock_model_instance.to.return_value = mock_model_instance
    mock_model_cls.return_value = mock_model_instance

    weather_list = [weather, weather]

    with patch("torch.cuda.is_available", return_value=False):
        history = run_dca(
            weather_grids=weather_list,
            static_grids=static_with_nonburnable,
            cell_size_m=30.0,
            n_steps=3,
            ignition_points=[(2, 2)],
            containment_lines=["LINESTRING(0 0, 1 1)"],
        )

    assert len(history) == 4
    mock_model_instance.to.assert_called_with("cpu")
    mock_binary_dilation.assert_called_once()
    mock_verified_mask.assert_called_once_with(h, w, [(2, 2)])
    assert mock_update_tensors.call_count == 3


@patch("app.backend.src.ai.dca.WildfireModel")
@patch("app.backend.src.ai.dca.IgnitionScorer.load")
@patch("app.backend.src.ai.dca.pick_ignition_points")
@patch("app.backend.src.ai.dca.convert_containment_line")
@patch("app.backend.src.ai.dca.build_env_data")
@patch("app.backend.src.ai.dca.state_to_burn_state")
def test_run_dca_ignition_scorer_fallback_and_no_state_tensor(
    mock_state_to_burn,
    mock_build_env,
    mock_convert_containment,
    mock_pick_ignition,
    mock_scorer_load,
    mock_model_cls,
    base_grids,
):
    static, weather = base_grids
    h, w = static["elevation"].shape

    mock_convert_containment.return_value = np.zeros((h, w), dtype=bool)
    mock_scorer = MagicMock()
    mock_scorer.score_grid.return_value = np.ones((h, w), dtype=np.float32)
    mock_scorer_load.return_value = mock_scorer
    mock_pick_ignition.return_value = np.zeros((h, w), dtype=bool)

    mock_model_instance = MagicMock()

    mock_model_instance.state = "not_a_tensor"
    mock_model_instance.to.return_value = mock_model_instance
    mock_model_cls.return_value = mock_model_instance
    mock_state_to_burn.return_value = np.zeros((h, w), dtype=np.int64)

    with patch("torch.cuda.is_available", return_value=False):
        history = run_dca(
            weather_grids=weather,
            static_grids=static,
            cell_size_m=30.0,
            n_steps=1,
            n_ignition_points=2,
        )

    assert len(history) == 2
    mock_scorer.score_grid.assert_called_once()
    mock_pick_ignition.assert_called_once()
    mock_model_instance.compute.assert_called_once()


@patch("app.backend.src.ai.dca.torch.from_numpy")
@patch("app.backend.src.ai.dca.WildfireModel")
@patch("app.backend.src.ai.dca.convert_containment_line")
@patch("app.backend.src.ai.dca.build_env_data")
@patch("app.backend.src.ai.dca.state_to_burn_state")
def test_run_dca_cuda_device_branch(
    mock_state_to_burn,
    mock_build_env,
    mock_convert_containment,
    mock_model_cls,
    mock_from_numpy,
    base_grids,
):
    static, weather = base_grids
    h, w = static["elevation"].shape

    mock_convert_containment.return_value = np.zeros((h, w), dtype=bool)
    mock_build_env.return_value = {}
    mock_state_to_burn.return_value = np.zeros((h, w), dtype=np.int64)

    mock_tensor = MagicMock()
    mock_tensor.to.return_value = mock_tensor
    mock_from_numpy.return_value = mock_tensor

    mock_model_instance = MagicMock()
    mock_model_instance.to.return_value = mock_model_instance
    mock_model_instance.state = torch.zeros((1, h, w), dtype=torch.float32)
    mock_model_cls.return_value = mock_model_instance

    ignition_mask = np.zeros((h, w), dtype=bool)

    with patch("torch.cuda.is_available", return_value=True):
        history = run_dca(
            weather_grids=weather,
            static_grids=static,
            cell_size_m=30.0,
            n_steps=1,
            ignition_mask=ignition_mask,
        )

    assert len(history) == 2
    mock_model_instance.to.assert_called_with("cuda")
    mock_tensor.to.assert_called_with("cuda")