import numpy as np

from app.backend.src.ai.simulation import build_multi_boundary_ignition_mask


def test_single_fire_matches_expected_cell():
    H, W = 60, 60
    bounds = (28.0, -26.0, 28.5, -25.5)  # min_lon, min_lat, max_lon, max_lat
    cell_size_m = 15.0

    # place a fire exactly at the grid's geographic center
    center_lat = -25.75
    center_lng = 28.25

    mask = build_multi_boundary_ignition_mask(
        H,
        W,
        cell_size_m,
        fires=[(center_lat, center_lng, 100.0)],
        grid_bounds=bounds,
    )

    assert mask.shape == (H, W)
    assert mask[H // 2, W // 2] == True  # noqa: E712 - clarity over style here
    assert mask.sum() > 0


def test_two_separated_fires_produce_two_disjoint_blobs():
    H, W = 100, 100
    bounds = (28.0, -26.0, 29.0, -25.0)
    cell_size_m = 15.0

    fire_1 = (-25.2, 28.2, 50.0)  # near the top of the grid
    fire_2 = (-25.8, 28.8, 50.0)  # near the bottom

    mask = build_multi_boundary_ignition_mask(
        H, W, cell_size_m, fires=[fire_1, fire_2], grid_bounds=bounds
    )

    # two separate ignition blobs, not touching, given how far apart they are
    from scipy.ndimage import label

    labeled, n_components = label(mask)
    assert n_components == 2


def test_overlapping_fires_merge_into_one_blob():
    H, W = 100, 100
    bounds = (28.0, -26.0, 29.0, -25.0)
    cell_size_m = 15.0

    # close enough together that their radii should touch
    fire_1 = (-25.5, 28.5, 300.0)
    fire_2 = (-25.5, 28.502, 300.0)

    mask = build_multi_boundary_ignition_mask(
        H, W, cell_size_m, fires=[fire_1, fire_2], grid_bounds=bounds
    )

    from scipy.ndimage import label

    labeled, n_components = label(mask)
    assert n_components == 1


def test_fire_outside_grid_bounds_produces_empty_or_partial_mask():
    H, W = 50, 50
    bounds = (28.0, -26.0, 28.5, -25.5)
    cell_size_m = 15.0

    # fire center is outside the grid entirely
    mask = build_multi_boundary_ignition_mask(
        H,
        W,
        cell_size_m,
        fires=[(-30.0, 30.0, 100.0)],
        grid_bounds=bounds,
    )

    # should not crash, and shouldn't ignite anything inside this grid
    assert mask.shape == (H, W)
    assert mask.sum() == 0
