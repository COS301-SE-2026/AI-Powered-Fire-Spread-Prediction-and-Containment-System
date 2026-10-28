from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import torch

from app.backend.src.ai.schema import BURNED, BURNING, UNBURNED
from app.backend.src.ai.simulation import(
    build_boundary_ignition_mask,
    build_env_data,
    build_multi_boundary_ignition_mask,
    build_verified_reports_mask,
    compute_wind_components,
    convert_containment_line,
    pick_ignition_points,
    state_to_burn_state,
    update_model_tensors,
)

class TestPickIgnitionPoints:
    def test_pick_ignition_points_success_with_rng(self):
        p_ignite = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        rng = np.random.default_rng(seed=42)
        mask = pick_ignition_points(p_ignite, n_points=2, rng=rng)

        assert mask.shape == (2, 2)
        assert mask.dtype == bool
        assert mask.sum() == 2


    def test_pick_ignition_points_default_rng(self):
        p_ignite = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=np.float32)
        mask = pick_ignition_points(p_ignite, n_points=1, rng=None)

        assert mask.shape == (2, 2)
        assert bool(mask[0, 1]) is True
        assert mask.sum() == 1


    def test_pick_ignition_points_all_zero_raises_error(self):
        p_ignite = np.zeros((3, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="No ignition-prone cells"):
            pick_ignition_points(p_ignite)


class TestBuildReportMasks:
    def test_build_verified_reports_mask(self):
        H, W = 5, 5
        points =[(0, 0), (2, 3), (-1, 2), (5, 2), (2, -1), (2, 5)]
        mask = build_verified_reports_mask(H, W, points)

        assert mask.shape == (5, 5)
        assert bool(mask[0, 0]) is True
        assert bool(mask[2, 3]) is True
        assert mask.sum() == 2

    def test_build_boundary_ignition_mask(self):
        H, W = 10, 10
        cell_size = 10.0
        boundary_radius = 20.0

        mask  = build_boundary_ignition_mask(H, W, cell_size, boundary_radius)

        assert mask.shape == (10, 10)
        assert bool(mask[5, 5]) is True
        assert bool(mask[0, 0]) is False

    def test_build_multi_boundary_ignition_mask(self):
        H, W = 20, 20
        cell_size = 10.0
        grid_bounds = (18.0, -34.0, 19.0, -33.0)
        fires = [
            (-33.5, 18.5, 20.0),
            (-33.2, 18.8, 15.0),
        ]

        mask = build_multi_boundary_ignition_mask(H, W, cell_size, fires, grid_bounds)

        assert mask.shape == (20, 20)
        assert mask.dtype == bool
        assert mask.sum() > 0


class TestWindAndEnvironment:
    def test_compute_wind_components_numpy(self):
        wind_u = np.array([3.0, 0.0])
        wind_v = np.array([4.0, 2.0])

        velocity, direction = compute_wind_components(wind_u, wind_v)

        assert isinstance(velocity, torch.Tensor)
        assert isinstance(direction, torch.Tensor)
        assert torch.isclose(velocity[0], torch.tensor(5.0))
        expected_deg = torch.rad2deg(torch.atan2(torch.tensor(4.0), torch.tensor(3.0))) % 360
        assert torch.isclose(direction[0], expected_deg)


    def test_compute_wind_components_tensor(self):
        u = torch.tensor([-2.0])
        v = torch.tensor([0.0])

        velocity, direction = compute_wind_components(u, v)

        assert torch.isclose(velocity[0], torch.tensor(2.0))
        assert torch.isclose(direction[0], torch.tensor(180.0))


    @patch("app.backend.src.ai.simulation.calculate_slope")
    def test_build_env_data_with_nonburnable(self, mock_slope):
        mock_slope.return_value = torch.zeros((4, 4), dtype=torch.float32)

        weather_grids = {
            "wind_u": np.ones((4, 4), dtype=np.float32),
            "wind_v": np.zeros((4, 4), dtype=np.float32),
        }
        static_grids = {
            "elevation": np.full((4, 4), 100.0, dtype=np.float32),
            "fuel_load": np.full((4, 4), 0.8, dtype=np.float32),
            "dryness": np.full((4, 4), 0.5, dtype=np.float32),
            "nonburnable": np.array([
                [True, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
                [False, False, False, False],
            ]),
        }
        initial_mask = np.zeros((4, 4), dtype=bool)
        initial_mask[2, 2] = True

        env_dict = build_env_data(weather_grids, static_grids, initial_mask, cell_size_m=30.0)

        assert "p_veg" in env_dict
        assert "p_den" in env_dict
        assert "wind_velocity" in env_dict
        assert "wind_towards_direction" in env_dict
        assert "slope" in env_dict
        assert "initial_ignition" in env_dict

        # nonburnable cell must be overridden to -1.0
        assert env_dict["p_veg"][0, 0].item() == -1.0
        assert env_dict["p_veg"][0, 1].item() == pytest.approx(0.8)


    @patch("app.backend.src.ai.simulation.calculate_slope")
    def test_build_env_data_without_nonburnable(self, mock_slope):
        mock_slope.return_value = torch.zeros((3, 3), dtype=torch.float32)

        weather_grids = {
            "wind_u": np.zeros((3, 3), dtype=np.float32),
            "wind_v": np.zeros((3, 3), dtype=np.float32),
        }
        static_grids = {
            "elevation": np.full((3, 3), 50.0, dtype=np.float32),
            "fuel_load": np.full((3, 3), 0.6, dtype=np.float32),
            "dryness": np.full((3, 3), 0.3, dtype=np.float32),
        }
        initial_mask = np.zeros((3, 3), dtype=bool)

        env_dict = build_env_data(weather_grids, static_grids, initial_mask, cell_size_m=20.0)

        assert env_dict["p_veg"][0, 0].item() == pytest.approx(0.6)


    def test_update_model_tensors(self):
        class DummyModel:
            def __init__(self):
                self.wind_velocity = torch.zeros((2, 2), dtype=torch.float32)
                self.wind_towards_direction = torch.zeros((2, 2), dtype=torch.float32)

        model = DummyModel()
        current_weather = {
            "wind_u": np.full((2, 2), 3.0, dtype=np.float32),
            "wind_v": np.full((2, 2), 0.0, dtype=np.float32),
        }

        update_model_tensors(model, current_weather, device="cpu")

        assert torch.allclose(model.wind_velocity, torch.full((2, 2), 3.0))
        assert torch.allclose(model.wind_towards_direction, torch.zeros((2, 2)))


class TestStateConversion:
    def test_state_to_burn_state(self):
        state = torch.zeros((2, 3, 3), dtype=torch.bool)
        state[0, 1, 1] = True  
        state[1, 0, 0] = True  

        grid = state_to_burn_state(state)

        assert grid.shape == (3, 3)
        assert grid[0, 0] == BURNED
        assert grid[1, 1] == BURNING
        assert grid[2, 2] == UNBURNED


class TestContainmentLineConversion:
    def test_convert_containment_line_empty_list(self):
        mask = convert_containment_line([], 10, 10)
        assert mask.shape == (10, 10)
        assert mask.sum() == 0


    def test_convert_containment_line_with_bounds(self):
        bounds = (18.0, -34.0, 19.0, -33.0)
        line_wkt = "LINESTRING(18.2 -33.2, 18.8 -33.8)"
        mask = convert_containment_line([line_wkt], 20, 20, bounds=bounds)

        assert mask.shape == (20, 20)
        assert mask.sum() > 0


    def test_convert_containment_line_without_bounds(self):
        line_wkt = "LINESTRING(2 2, 8 8)"
        mask = convert_containment_line([line_wkt], 15, 15, bounds=None)

        assert mask.shape == (15, 15)
        assert bool(mask[2, 2]) is True
        assert bool(mask[8, 8]) is True


    def test_convert_containment_line_skips_invalid_geometries(self):
        lines = [
            "POINT(18.5 -33.5)",                 
            "LINESTRING(18.5 -33.5)",             
            "INVALID WKT STRING",    
            "LINESTRING(100 100, 200 200)",
        ]
        mask = convert_containment_line(lines, 10, 10, bounds=None)

        assert mask.shape == (10, 10)
        assert mask.sum() == 0


    def test_convert_containment_line_empty_linestring(self):
        mask = convert_containment_line(["LINESTRING EMPTY"], 10, 10, bounds=None)

        assert mask.shape == (10, 10)
        assert mask.sum() == 0









