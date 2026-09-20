import numpy as np
import pytest
from shapely import wkt as shapely_wkt

from app.backend.src.ai.suggest_containment import (
    compute_arrival_ticks,
    suggest_containment_line,
)

from app.backend.src.ai.schema import UNBURNED, BURNING, BURNED

def make_radial_history(H=60, W=60, n_steps=40, speed_cells_per_tick=1.0):
    cy, cx = H / 2, W / 2
    yy, xx = np.ogrid[0:H, 0:W]
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)

    history = []
    for t in range(n_steps + 1):
        radius = t * speed_cells_per_tick
        grid = np.full((H, W), UNBURNED, dtype=np.int64)
        grid[dist <= radius] = BURNED
        grid[(dist > radius) & (dist <= radius + 1.5)] = BURNING
        history.append(grid)
    return history

def test_arrival_ticks_monotonic_outward():
    history = make_radial_history()
    from app.backend.src.ai.suggest_containment import compute_arrival_ticks
    arrival = compute_arrival_ticks(history)
    print("arrival center:", arrival[30, 30])
    print("unique arrival values:", np.unique(arrival))
    arrival =  compute_arrival_ticks(history)

    H, W = arrival.shape
    cy, cx = H // 2, W // 2

    assert arrival[cy, cx] == 0
    assert arrival[cy, cx + 25] == -1 or arrival[cy, cx + 25] > arrival[cy, cx + 5]

def  test_suggest_returns_feasible_line():
    history = make_radial_history(speed_cells_per_tick = 0.5)
    suggestions = suggest_containment_line(
        history=history,
        fire_lat=-25.0,
        fire_lng=28.0,
        boundary_radius_m=60.0,
        cell_size_m=15.0,
        n_steps=len(history) - 1,
        top_n=1,
    )

    assert len(suggestions) == 1
    s = suggestions[0]

    assert s.margin_min > 0
    assert s.length_m >0
    assert s.shielded_cell_score > 0

    geom = shapely_wkt.loads(s.wkt)

    assert geom.geom_type == "LineString"

def test_no_suggestion_when_fire_too_fast():
    # fire reaches every cell almost immediately -> no line can be built in time
    history = make_radial_history(speed_cells_per_tick=50.0, n_steps=3)
    suggestions = suggest_containment_line(
        history=history,
        fire_lat=-25.0,
        fire_lng=28.0,
        boundary_radius_m=300.0,
        cell_size_m=15.0,
        n_steps=len(history) - 1,
        top_n=1,
    )
    assert suggestions == []