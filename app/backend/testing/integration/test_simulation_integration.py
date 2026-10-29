from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest
import torch

from app.backend.src.ai import simulation as sim
from app.backend.src.ai.schema import BURNED, BURNING, UNBURNED


class TestSimulationIntegration:
    def test_pick_ignition_points_success_and_all_zero_error(self):
        zero_grid = np.zeros((4, 4), dtype=np.float32)
        with pytest.raises(ValueError, match="No ignition-prone cells"):
            sim.pick_ignition_points(zero_grid, n_points=1)

        p_ignite = np.zeros((3, 3), dtype=np.float32)
        p_ignite[1, 1] = 1.0

        rng = np.random.default_rng(seed=42)
        mask_custom = sim.pick_ignition_points(p_ignite, n_points=1, rng=rng)
        assert mask_custom.shape == (3, 3)
        assert bool(mask_custom[1, 1]) is True

        mask_default = sim.pick_ignition_points(p_ignite, n_points=1, rng=None)
        assert mask_default.shape == (3, 3)
        assert bool(mask_default[1, 1]) is True

    def test_build_verified_reports_mask_in_and_out_of_bounds(self):
        H, W = 6, 6
        points = [
            (2, 2),    # Valid inside
            (0, 0),    # Valid inside
            (-1, 2),   # Out of bounds: row < 0
            (7, 2),    # Out of bounds: row >= H
            (2, -1),   # Out of bounds: col < 0
            (2, 7),    # Out of bounds: col >= W
        ]
        mask = sim.build_verified_reports_mask(H, W, points)
        assert mask.shape == (H, W)
        assert bool(mask[2, 2]) is True
        assert bool(mask[0, 0]) is True
        assert mask.sum() == 2

    def test_build_boundary_ignition_mask(self):
        H, W = 10, 10
        cell_size = 10.0
        boundary_radius = 25.0

        mask = sim.build_boundary_ignition_mask(H, W, cell_size, boundary_radius)
        assert mask.shape == (10, 10)
        assert bool(mask[5, 5]) is True
        assert bool(mask[0, 0]) is False

    def test_build_multi_boundary_ignition_mask_lines_69_to_82(self):
        H, W = 20, 20
        cell_size_m = 10.0
        grid_bounds = (18.40, -34.00, 18.60, -33.80)  # min_lon, min_lat, max_lon, max_lat
        fires = [
            (-33.90, 18.50, 30.0),  # Fire 1 in center
            (-33.85, 18.45, 20.0),  # Fire 2
        ]

        mask = sim.build_multi_boundary_ignition_mask(H, W, cell_size_m, fires, grid_bounds)
        assert mask.shape == (H, W)
        assert mask.dtype == bool
        assert mask.sum() > 0

    def test_compute_wind_components(self):
        u_np = np.array([[3.0]], dtype=np.float32)
        v_np = np.array([[4.0]], dtype=np.float32)
        vel, deg = sim.compute_wind_components(u_np, v_np)
        assert torch.is_tensor(vel)
        assert torch.is_tensor(deg)
        assert pytest.approx(vel.item(), rel=1e-3) == 5.0

        u_t = torch.tensor([[0.0]])
        v_t = torch.tensor([[10.0]])
        vel_t, deg_t = sim.compute_wind_components(u_t, v_t)
        assert pytest.approx(vel_t.item(), rel=1e-3) == 10.0

    def test_build_env_data_with_and_without_nonburnable(self):
        weather_grids = {
            "wind_u": np.ones((5, 5), dtype=np.float32),
            "wind_v": np.zeros((5, 5), dtype=np.float32),
        }
        static_grids_with_nb = {
            "elevation": np.zeros((5, 5), dtype=np.float32),
            "fuel_load": np.full((5, 5), 0.8, dtype=np.float32),
            "dryness": np.full((5, 5), 0.5, dtype=np.float32),
            "nonburnable": np.array([
                [True, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
            ], dtype=bool),
        }
        initial_mask = np.zeros((5, 5), dtype=bool)
        initial_mask[2, 2] = True

        # Branch 121->128: nonburnable is not None
        env_nb = sim.build_env_data(
            weather_grids, static_grids_with_nb, initial_mask, cell_size_m=30.0
        )
        assert env_nb["p_veg"][0, 0].item() == -1.0
        assert env_nb["p_veg"][0, 1].item() == pytest.approx(0.8, rel=1e-3)

        # Nonburnable is None
        static_grids_no_nb = {
            "elevation": np.zeros((5, 5), dtype=np.float32),
            "fuel_load": np.full((5, 5), 0.8, dtype=np.float32),
            "dryness": np.full((5, 5), 0.5, dtype=np.float32),
            "nonburnable": None,
        }
        env_no_nb = sim.build_env_data(
            weather_grids, static_grids_no_nb, initial_mask, cell_size_m=30.0
        )
        assert env_no_nb["p_veg"][0, 0].item() == pytest.approx(0.8, rel=1e-3)

    def test_update_model_tensors(self):
        class DummyModel:
            def __init__(self):
                self.wind_velocity = torch.zeros((1, 1), dtype=torch.float32)
                self.wind_towards_direction = torch.zeros((1, 1), dtype=torch.float32)

        model = DummyModel()
        weather = {
            "wind_u": np.array([[5.0]], dtype=np.float32),
            "wind_v": np.array([[0.0]], dtype=np.float32),
        }
        sim.update_model_tensors(model, weather, device="cpu")
        assert model.wind_velocity[0, 0].item() == pytest.approx(5.0, rel=1e-3)

    def test_state_to_burn_state(self):
        state = torch.zeros((2, 3, 3), dtype=torch.bool)
        state[0, 1, 1] = True  # burning
        state[1, 0, 0] = True  # burned

        burn_grid = sim.state_to_burn_state(state)
        assert burn_grid.shape == (3, 3)
        assert burn_grid[1, 1] == BURNING
        assert burn_grid[0, 0] == BURNED
        assert burn_grid[2, 2] == UNBURNED

    def test_convert_containment_line_all_branches(self):
        H, W = 10, 10

        empty_mask = sim.convert_containment_line([], H, W)
        assert empty_mask.shape == (H, W)
        assert empty_mask.sum() == 0

        point_mask = sim.convert_containment_line(["POINT(18.5 -33.9)"], H, W)
        assert point_mask.sum() == 0

        empty_line_mask = sim.convert_containment_line(["LINESTRING EMPTY"], H, W)
        assert empty_line_mask.sum() == 0

        malformed_mask = sim.convert_containment_line(["INVALID_WKT_STRING(abc)"], H, W)
        assert malformed_mask.sum() == 0

        direct_wkt = "LINESTRING(1 1, 8 8)"
        direct_mask = sim.convert_containment_line([direct_wkt], H, W, bounds=None)
        assert bool(direct_mask[1, 1]) is True
        assert bool(direct_mask[8, 8]) is True

        bounds = (18.40, -34.00, 18.60, -33.80)
        geo_wkt = "LINESTRING(18.45 -33.95, 18.55 -33.85)"
        geo_mask = sim.convert_containment_line([geo_wkt], H, W, bounds=bounds)
        assert geo_mask.sum() > 0