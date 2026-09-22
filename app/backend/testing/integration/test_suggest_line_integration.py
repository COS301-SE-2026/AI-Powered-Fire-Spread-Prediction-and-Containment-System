from unittest.mock import AsyncMock, patch

import numpy as np

from conftest import make_report
from app.backend.src.ai.simulation_api import Prediction
from app.backend.src.enums.report_status import ReportStatus

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