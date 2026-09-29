from __future__ import annotations
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from app.backend.src.ai import build_ignition_dataset as bid
from app.backend.src.ai.schema import BURNED, UNBURNED, FEATURES, BURNING


def test_haversine_km_one_degree_longitude_at_equator():
    """
    Haversine stuff
    """
    dist = bid.haversine_km(
        np.array([0.0]), np.array([0.0]), np.array([0.0]), np.array([1.0])
    )
    assert dist[0] == pytest.approx(111.19, abs=0.5)


def test_haversine_km_zero_distance_for_identical_points():
    dist = bid.haversine_km(
        np.array([-25.75]), np.array([28.23]), np.array([-25.75]), np.array([28.23])
    )
    assert dist[0] == pytest.approx(0.0, abs=1e-9)


def test_haversine_km_is_symmetric():
    a = bid.haversine_km(
        np.array([1.0]), np.array([2.0]), np.array([3.0]), np.array([4.0])
    )
    b = bid.haversine_km(
        np.array([3.0]), np.array([4.0]), np.array([1.0]), np.array([2.0])
    )
    assert a[0] == pytest.approx(b[0])


# CLuster fire events


def _detections(rows):
    """
    rows: list of lat, lon and timestamps, -> dataframe matching load_detections's output
    """
    return pd.DataFrame(rows, columns=["lat", "lon", "timestamp"]).assign(
        timestamp=lambda d: pd.to_datetime(d["timestamp"])
    )


def test_cluster_fire_events_merges_close_points_in_space_and_time():
    df = _detections(
        [
            (-25.750, 28.230, "2024-01-01 00:00"),
            (-25.751, 28.231, "2024-01-01 00:30"),  # ~150m away, 30 min later
        ]
    )
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] == fire_ids[1]


def test_cluster_fire_events_splits_points_far_apart_in_space():
    df = _detections(
        [
            (-25.750, 28.230, "2024-01-01 00:00"),
            (-26.750, 29.230, "2024-01-01 00:00"),  # >100km away
        ]
    )
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] != fire_ids[1]


def test_cluster_fire_events_splits_points_far_apart_in_time():
    df = _detections(
        [
            (-25.750, 28.230, "2024-01-01 00:00"),
            (-25.750, 28.230, "2024-02-01 00:00"),  # same spot, 31 days later
        ]
    )
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] != fire_ids[1]


def test_cluster_fire_events_is_transitive_across_a_chain():
    df = _detections(
        [
            (-25.7500, 28.2300, "2024-01-01 00:00"),  # A
            (-25.7540, 28.2340, "2024-01-01 00:30"),  # B, close to A
            (-25.7580, 28.2380, "2024-01-01 01:00"),  # C, close to B, farther from A
        ]
    )
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] == fire_ids[1] == fire_ids[2]


def test_cluster_fire_events_single_point_gets_its_own_cluster():
    df = _detections([(-25.75, 28.23, "2024-01-01 00:00")])
    fire_ids = bid.cluster_fire_events(df)
    assert len(fire_ids) == 1


# build fire events


def test_build_fire_events_applies_bbox_buffer_and_sorts_ticks():
    df = _detections(
        [
            (0.0, 0.0, "2024-01-02"),
            (0.01, 0.02, "2024-01-01"),  # earlier day, should sort first
        ]
    )
    fire_ids = np.array([0, 0])
    events = bid.build_fire_events(df, fire_ids, bbox_buffer_km=2.0)

    assert len(events) == 1
    ev = events[0]
    buf_deg = 2.0 / 111.0
    assert ev.min_lon == pytest.approx(0.0 - buf_deg)
    assert ev.max_lat == pytest.approx(0.01 + buf_deg)
    assert ev.ticks[0] < ev.ticks[1]


def test_build_fire_events_splits_by_fire_id():
    df = _detections(
        [
            (0.0, 0.0, "2024-01-01"),
            (10.0, 10.0, "2024-01-01"),
        ]
    )
    fire_ids = np.array([0, 1])
    events = bid.build_fire_events(df, fire_ids)
    assert {e.fire_id for e in events} == {0, 1}
    assert all(len(e.detection) == 1 for e in events)


# rasterize tick


def _make_event(min_lon, min_lat, max_lon, max_lat):
    return bid.FireEvent(
        fire_id=0,
        detection=pd.DataFrame(),
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        ticks=[],
    )


def test_rasterize_tick_empty_detections_returns_all_false():
    event = _make_event(0, 0, 3, 3)
    hit = bid.rasterize_tick(
        pd.DataFrame(columns=["lat", "lon"]), event, height=3, width=3
    )
    assert hit.shape == (3, 3)
    assert not hit.any()


def test_rasterize_tick_places_point_in_expected_cell():
    event = _make_event(0, 0, 3, 3)
    detections = pd.DataFrame({"lat": [2.5], "lon": [0.5]})
    hit = bid.rasterize_tick(detections, event, height=3, width=3)
    assert hit[0, 0]  # near top-left: high lat -> row 0, low lon -> col 0
    assert hit.sum() == 1


def test_rasterize_tick_clips_out_of_range_points_into_bounds():
    event = _make_event(0, 0, 3, 3)
    # point exactly on the max corner would otherwise index out of bounds
    detections = pd.DataFrame({"lat": [0.0], "lon": [3.0]})
    hit = bid.rasterize_tick(detections, event, height=3, width=3)
    assert hit.shape == (3, 3)
    assert hit.sum() == 1  # clipped, not dropped or crashed


def test_rasterize_tick_degenerate_bbox_does_not_crash():
    event = _make_event(5.0, 5.0, 5.0, 5.0)
    detections = pd.DataFrame({"lat": [5.0], "lon": [5.0]})
    hit = bid.rasterize_tick(detections, event, height=3, width=3)
    assert hit.shape == (3, 3)
    assert hit.sum() == 1


# step_burn_state


def test_step_burn_state_unburned_to_burning_on_detection():
    prev = np.array([[UNBURNED]])
    detected = np.array([[True]])
    new = bid.step_burn_state(prev, detected)
    assert new[0, 0] == BURNING


def test_step_burn_state_burning_to_burned_when_no_longer_detected():
    prev = np.array([[BURNING]])
    detected = np.array([[False]])
    new = bid.step_burn_state(prev, detected)
    assert new[0, 0] == BURNED


def test_step_burn_state_burning_stays_burning_while_detected():
    prev = np.array([[BURNING]])
    detected = np.array([[True]])
    new = bid.step_burn_state(prev, detected)
    assert new[0, 0] == BURNING


def test_step_burn_state_burned_is_terminal():
    prev = np.array([[BURNED]])
    detected = np.array([[True]])
    new = bid.step_burn_state(prev, detected)
    assert new[0, 0] == BURNED
