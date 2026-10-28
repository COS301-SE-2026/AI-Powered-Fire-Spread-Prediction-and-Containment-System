from unittest.mock import AsyncMock, patch

import numpy as np

from conftest import make_report
from app.backend.src.ai.simulation_api import Prediction
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.ai.geo import bbox_from_fire
from app.backend.src.ai.simulation import convert_containment_line
from app.backend.src.ai.suggest_containment import (
    ContainmentSuggestion,
    _frontier_cells,
    _longest_land_run,
    compute_arrival_ticks,
    suggest_containment_line,
)
def make_radial_history(H=60, W=60, n_steps=40, speed_cells_per_tick=1.0):
    cy, cx = H / 2, W / 2
    yy, xx = np.ogrid[0:H, 0:W]
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    history = []
    for t in range(n_steps + 1):
        radius = t * speed_cells_per_tick
        grid = np.full((H, W), 0, dtype=np.int64)
        grid[dist <= radius] = 2
        grid[(dist > radius) & (dist <= radius + 1.5)] = 1
        history.append(grid)
    return history
def test_suggest_endpoint_returns_line(client, db):
    fire = make_report(
        db,
        lat=-25.7479,
        lng=28.2293,
        status=ReportStatus.verified,
        boundary_radius=0.06,
    )
    fake_history = make_radial_history(speed_cells_per_tick=0.5)
    fake_prediction = Prediction(
        ref=fire.reference_number,
        lat=fire.lat if hasattr(fire, "lat") else 0.0,
        lng=fire.lng if hasattr(fire, "lng") else 0.0,
        history=[g.ravel().tolist() for g in fake_history],
        burned_cells=100,
        radius_m=200.0,
        truncated=False,
        lat_extent_deg=0.05,
        lon_extent_deg=0.05,
        grid_h=fake_history[0].shape[0],
        grid_w=fake_history[0].shape[1],
        cell_size_m=15.0,
    )

    with patch(
        "app.backend.src.services.firefighter.containment_lines.simulate_single_fire",
        new=AsyncMock(return_value=fake_prediction),
    ):
        resp = client.get(
            f"/api/firefighter/suggest-containment-line/{fire.reference_number}"
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 0
    if body["total"] > 0:
        assert "wkt" in body["data"][0]


H = W = 200
CELL_M = 30.0
LAT, LNG = -25.7, 28.2
BOUNDARY_M = 600.0
N_TICKS = 60


def _history():
    yy, xx = np.ogrid[0:H, 0:W]
    dist = np.sqrt((yy - H / 2) ** 2 + (xx - W / 2) ** 2)
    ticks = []
    for t in range(N_TICKS):
        grid = np.zeros((H, W), dtype=np.int64)   # 0 == UNBURNED
        grid[dist <= 20 + 0.5 * t] = 2            # burned
        ticks.append(grid)
    return ticks


def _water_block():
    water = np.zeros((H, W), dtype=bool)
    water[:, 135:] = True    # a "lake" along the east side, in the fire's path
    return water


def test_longest_land_run_splits_on_water():
    water = np.zeros((5, 5), dtype=bool)
    water[2, 1] = True                       # runs: [(2,0)] and [(2,2),(2,3),(2,4)]
    cells = [(2, c) for c in range(5)]
    assert _longest_land_run(cells, water) == [(2, 2), (2, 3), (2, 4)]


def test_longest_land_run_all_water_and_all_land():
    water = np.zeros((1, 3), dtype=bool)
    cells = [(0, 0), (0, 1), (0, 2)]
    assert _longest_land_run(cells, water) == cells        # no water: untouched
    assert _longest_land_run(cells, np.ones((1, 3), dtype=bool)) == []

def test_frontier_ignores_shoreline():
    history = _history()
    water = _water_block()
    arrival = compute_arrival_ticks(history)
    for r, c in _frontier_cells(arrival, water):
        # no frontier cell may exist only because it touches water
        nbrs = [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
        assert any(
            0 <= rr < H and 0 <= cc < W and arrival[rr, cc] == -1 and not water[rr, cc]
            for rr, cc in nbrs
        )


def test_suggestions_stay_off_water():
    history = _history()
    water = _water_block()

    suggestions = suggest_containment_line(
        history=history,
        fire_lat=LAT,
        fire_lng=LNG,
        boundary_radius_m=BOUNDARY_M,
        cell_size_m=CELL_M,
        n_steps=N_TICKS,
        top_n=10,
        nonburnable=water,
    )
    assert all(isinstance(s, ContainmentSuggestion) for s in suggestions)

    bounds = bbox_from_fire(LAT, LNG, BOUNDARY_M, N_TICKS)
    for s in suggestions:
        mask = convert_containment_line([s.wkt], H, W, bounds)
        assert mask.any()
        assert not (mask & water).any(), f"line touches water: {s.wkt}"


def test_no_mask_is_backwards_compatible():
    kwargs = dict(
        history=_history(), fire_lat=LAT, fire_lng=LNG,
        boundary_radius_m=BOUNDARY_M, cell_size_m=CELL_M,
        n_steps=N_TICKS, top_n=3,
    )
    assert suggest_containment_line(**kwargs) == suggest_containment_line(
        **kwargs, nonburnable=None
    )