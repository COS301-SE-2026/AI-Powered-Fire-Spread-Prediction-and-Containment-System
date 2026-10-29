import numpy as np
from app.backend.src.ai.geo import bbox_from_fire, touch_edge
from app.backend.src.ai.sim_constants import TICKS_PER_HOUR, MAX_SPREAD_PER_HOUR


class TestBboxFromFire:
    def test_bbox_from_fire_spread_headroom(self):
        lat = -25.7479
        lng = 28.2293
        boundary_radius = 500.0
        n_steps = 120

        min_lon, min_lat, max_lon, max_lat = bbox_from_fire(
            lat=lat,
            lng=lng,
            boundary_radius_m=boundary_radius,
            n_steps=n_steps,
        )

        assert min_lon < lng < max_lon
        assert min_lat < lat < max_lat


    def test_bbox_from_fire_min_extent_fallback(self):
        lat = 0.0
        lng = 0.0
        min_lon, min_lat, max_lon, max_lat = bbox_from_fire(
            lat=lat,
            lng=lng,
            boundary_radius_m=10.0,
            n_steps=0,
            min_extent_radius_m=300.0,
        )

        assert min_lon < lng < max_lon
        assert min_lat < lat < max_lat


class TestTouchEdge:
    def test_touch_edge_empty_grid_line_50(self):
        empty_grid = np.zeros((0, 0), dtype=int)
        assert touch_edge(empty_grid, burning_val=1, burned_val=2) is False


    def test_touch_edge_no_touch(self):
        grid = np.zeros((5, 5), dtype=int)
        grid[2, 2] = 1
        assert touch_edge(grid, burning_val=1, burned_val=2) is False


    def test_touch_edge_top_boundary(self):
        grid = np.zeros((5, 5), dtype=int)
        grid[0, 2] = 1
        assert touch_edge(grid, burning_val=1, burned_val=2) is True


    def test_touch_edge_bottom_boundary(self):
        grid = np.zeros((5, 5), dtype=int)
        grid[-1, 2] = 2
        assert touch_edge(grid, burning_val=1, burned_val=2) is True


    def test_touch_edge_left_boundary(self):
        grid = np.zeros((5, 5), dtype=int)
        grid[2, 0] = 1
        assert touch_edge(grid, burning_val=1, burned_val=2) is True


    def test_touch_edge_right_boundary(self):
        grid = np.zeros((5, 5), dtype=int)
        grid[2, -1] = 2
        assert touch_edge(grid, burning_val=1, burned_val=2) is True