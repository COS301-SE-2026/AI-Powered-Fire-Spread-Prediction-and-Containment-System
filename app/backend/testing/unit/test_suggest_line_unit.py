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


