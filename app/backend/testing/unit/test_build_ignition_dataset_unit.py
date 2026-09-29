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
    dist = bid.haversine_km(np.array([-25.75]), np.array([28.23]), np.array([-25.75]), np.array([28.23]))
    assert dist[0] == pytest.approx(0.0, abs=1e-9)

def test_haversine_km_is_symmetric():
    a = bid.haversine_km(np.array([1.0]), np.array([2.0]), np.array([3.0]), np.array([4.0]))
    b = bid.haversine_km(np.array([3.0]), np.array([4.0]), np.array([1.0]), np.array([2.0]))
    assert a[0] == pytest.approx(b[0])

# CLuster fire events

def _detections(rows):
    """
    rows: list of lat, lon and timestamps, -> dataframe matching load_detections's output
    """
    return pd.DataFrame(rows, columns = ["lat", "lon", "timestamp"]).assign(
        timestamp = lambda d: pd.to_datetime(d["timestamp"])
    )

def test_cluster_fire_events_merges_close_points_in_space_and_time():
    df = _detections([
        (-25.750, 28.230, "2024-01-01 00:00"),
        (-25.751, 28.231, "2024-01-01 00:30"),  # ~150m away, 30 min later
    ])
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] == fire_ids[1]


def test_cluster_fire_events_splits_points_far_apart_in_space():
    df = _detections([
        (-25.750, 28.230, "2024-01-01 00:00"),
        (-26.750, 29.230, "2024-01-01 00:00"),  # >100km away
    ])
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] != fire_ids[1]


def test_cluster_fire_events_splits_points_far_apart_in_time():
    df = _detections([
        (-25.750, 28.230, "2024-01-01 00:00"),
        (-25.750, 28.230, "2024-02-01 00:00"),  # same spot, 31 days later
    ])
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] != fire_ids[1]
 

def test_cluster_fire_events_is_transitive_across_a_chain():
    df = _detections([
        (-25.7500, 28.2300, "2024-01-01 00:00"),  # A
        (-25.7540, 28.2340, "2024-01-01 00:30"),  # B, close to A
        (-25.7580, 28.2380, "2024-01-01 01:00"),  # C, close to B, farther from A
    ])
    fire_ids = bid.cluster_fire_events(df, max_gap_km=5.0, max_gap_days=4.0)
    assert fire_ids[0] == fire_ids[1] == fire_ids[2]


def test_cluster_fire_events_single_point_gets_its_own_cluster():
    df = _detections([(-25.75, 28.23, "2024-01-01 00:00")])
    fire_ids = bid.cluster_fire_events(df)
    assert len(fire_ids) == 1
