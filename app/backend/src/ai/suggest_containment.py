from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_dilation

from .schema import UNBURNED
from .geo import bbox_from_fire
from .simulation import build_boundary_ignition_mask

TICK_MINUTES = 15 #same as dca.py
MAX_LINE_LENGTH_M = 400.0
MIN_STANDOFF_M = 50.0
BUILD_RATE_M_PER_MIN = 3.0
FRONTIER_SAMPLE_STRIDE_CELLS = 5
LOOKAHEAD_PAD_M = 300.0


@dataclass
class ContainmentSuggestion:
    wkt: str
    length_m: float
    build_time_min: float
    arrival_at_line_min: float
    margin_min: float
    shielded_cell_score: float

def compute_arrival_ticks(history: list[np.array]) -> np.ndarray:
    H, W = history[0].shape
    arrival = np.full((H, W), -1, dtype = np.int32)
    for t, grid in enumerate(history):
        reached = (grid != UNBURNED) & (arrival)
        arrival[reached] = t
    return arrival

def _standoff_mask(ignition_mask : np.array, standoff_cells: int) -> np.ndarray:
    if standoff_cells <= 0:
        return ignition_mask.copy()
    struct = np.ones((3, 3), dtype =bool)
    mask = ignition_mask.copy()
    for _ in range(standoff_cells):
        mask = binary_dilation(mask, structure = struct)
    return mask

def _frontier_cells(arrival: np.ndarray, stride : int)-> list[tuple[int,int]]:
    H, W = arrival.shape
    reached = arrival != -1
    never_reached = ~reached
    neighbor_never_reached = np.zeros_like(reached)
    neighbour_never_reached[:-1, :] |= never_reached[1:, :]
    neighbour_never_reached[1:, :] |= never_reached[:-1, :]
    neighbour_never_reached[:, :-1] |= never_reached[:, 1:]
    neighbour_never_reached[:, 1:] |= never_reached[:, :-1]

    frontier = reached & neighbor_never_reached
    rows, cols = np.nonzero(frontier)
    return list(zip(rows[::stride].tolist(), cols[::stride].tolist()))

def _local_gradient_angle(arrival : np.ndarray, row: int, col: int)-> float:
    H, W = arrival.shape
    window = arrival[
        max(0, row-2): min(H, row+3), max(0, col-2): min (W, col+3)
    ].astype(np.float32)
    window[window < 0]= np.nan
    if np.isnan(window).all():
        return 0.0

    filled = np.nan_to_num(window, nan = np.nanmean(window))
    gy, gx = np.gradient(filled)
    cy, cx = gy.shape[0] // 2, gy.shape[1]//2
    dy, dx = gy[cy, cx], gx[cy, cx]

    if dy == 0 and dx == 0
        return 0.0
    return math.atan2(dy, dx)

def _grid_to_lonlat(
    row : float, col: float, H: int, W:int, bounds: tuple[float, float, float, float]
) -> tuple[float, float]:
    min_lon, min_lat, max_lon, max_lat = bounds
    lat = max_lat - (row / H) * (max_lat - min_lat)
    lon = min_lon + (col / W) * (max_lon - min_lon)
    return lon, lat

def _make_candidate_segment(
    row: int, col: int, angle_rad: float, half_len_cells: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    perp = angle_rad + math.pi/2
    dr, dc =math.sin(perp), math.cos(perp)
    p0 = (row - dr * half_len_cells, col - dc * half_len_cells)
    p1 = (row + dr * half_len_cells, col + dc * half_len_cells)
    return p0, p1

def _rasterize_segment(
    p0: tuple[float, float], p1: tuple[float, float], H : int, W: int
) -> list[tuple[int, int]]:
    r0, c0 = p0
    r1, c1 = p1
    n = max(int(math.hypot(r1 - r0, c1 - c0))) * 2
    rows = np.linspace(r0, r1, n).round().astype(int)
    cols = np.linspace(c0, c1, n).round().astype(int)
    valid = (rows >= 0) & (rows < H) & (cols >= 0) & (cols < W)
    return list(zip(rows[valid].tolist(), cols[valid].tolist()))

def _score_candidate(
    cells: list(tuple[int,int]),
    angle_rad: float,
    arrival: np.ndarray,
    lookahead_pad_cells:int,
)-> float:
    H, W = arrival.shape
    rows = np.array([c[0] for c in cells])
    cols = np.array([c[1] for c in cells])

    pad = lookahead_pad_cells
    r_min, r_max = max(0, rows.min() - pad), min(H, rows.max() + pad + 1)
    c_min, c_max = max(0, cols.min() - pad), min(H, cols.max() + pad + 1)

    window = arrival[r_min:r_max, c_min:c_max]
    yy, xx =np.mgrid[r_min:r_max, c_min:c_max]

    ref_r, ref_c = rows.mean(), cols.mean()
    normal_r, normal_c = math.cos(angle_rad), math.sin(angle_rad)
    side = (yy - ref_r) * normal_r + (xx - ref_c) * normal_c

    beyond = side >0
    shielded = beyond & (window != -1)

    return float(shielded.sum())

def suggest_containment_line(
    history: list[np.ndarray],
    fire_lat: float,
    fire_lng: float,
    boundary_radius_m: float,
    cell_size_m: float,
    n_steps: int,
    top_n: int = 1,
)-> list[ContainmentSuggestion]:

    H, W = history[0].shape
    bounds = bbox_from_fire(
        lat=fire_lat, lng=fire_lng, boundary_radius_m=boundary_radius_m, n_steps=n_steps
    )

    arrival = compute_arrival_ticks(history)
    ignition_mask = build_boundary_ignition_mask(H, W, cell_size_m, boundary_radius_m)
    standoff_cells = max(1, round(MIN_STANDOFF_M/ cell_size_m))
    excluded = _standoff_mask(ginition_mask, standoff_cells)

    max_len_cells = MAX_LINE_LENGTH /cell_size_m
    lookahead_pad_cells = max(1, round(LOOKAHEAD_PAD_M / cell_size_m))
    candidates : list[ConatainmentSuggestion] = []

    for row, col in _frontier_cells(arrival, FRONTIER_SAMPLE_STRIDE_CELLS):
        if excluded[row,col]: 
            continue
        
        angle = _local_gradient_angle(arrival, row, col)
        p0, p1 = _make_candidate_segment(row, col, angle, max_len_cells/2)
        cells = _rasterize_segment(p0, p1, H, W)

        if not cells or any(excluded[r, c] for r, c in cells):
            continue
        
        length_m = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * cell_size_m
        
        if length_m <= 0:
            continue
        
        arrivals_here = [arrival[r,c] for r,c in cells if arrival[r,c] != -1]:
        if not arrivals_here:
            continue #fire does not reach this line within the horizon
        
        arrival_at_line_min = min(arrivals_here) * TICK_MINUTES
        build_time_min = length_m / BUILD_RATE_M_PER_MIN
        margin_min = arrival_at_line_min - build_time_min

        if margin_min <= 0:
            continue
        
        score = _score_candidate(cells, angle, arrival, lookahead_pad_cells)
        if score <= 0:
            continue

        lon0, lat0 = _grid_to_lonlat(p0[0], p0[1], H, W, bounds)
        lon1, lat1 = _grid_to_lonlat(p1[0], p1[1], H, W, bounds)
        wkt = f"LINESTRING({lon0} {lat0}, {lon1} {lat1})"

        candidates.append(
            ContainmentSuggestion(
                wkt=wkt,
                length_m=round(length_m, 1),
                build_time_min=round(build_time_min, 1),
                arrival_at_line_min=round(arrival_at_line_min, 1),
                margin_min=round(margin_min, 1),
                shielded_cell_score=round(score / length_m, 4),
            )
        )

    candidates.sort(key=lambda c: c.shielded_cell_score, reverse=True)
    return candidates[:top_n]