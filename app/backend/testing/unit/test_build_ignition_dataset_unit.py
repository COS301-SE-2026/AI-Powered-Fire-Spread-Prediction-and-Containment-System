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


# OpenMeteo Tests


def test_open_meteo_provider_raises_if_fetch_before_prepare():
    provider = bid.OpenMeteoWeatherProvider()
    with pytest.raises(RuntimeError, match="prepare_for_fire"):
        provider.fetch(0, 0, 1, 1, pd.Timestamp("2024-01-01"), (4, 4))


def test_open_meteo_provider_raises_on_empty_fetch_result():
    event = bid.FireEvent(
        fire_id=1,
        detection=pd.DataFrame(),
        min_lon=0,
        min_lat=0,
        max_lon=1,
        max_lat=1,
        ticks=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
    )
    provider = bid.OpenMeteoWeatherProvider()
    with patch(
        "app.datasets.scripts.fetch_historical_weather.fetch_historical_weather",
        return_value=pd.DataFrame(),
    ):
        with pytest.raises(RuntimeError, match="no data"):
            provider.prepare_for_fire(event, target_shape=(4, 4))


def test_open_meteo_provider_caches_per_fire_and_delegates_fetch():
    event = bid.FireEvent(
        fire_id=2,
        detection=pd.DataFrame(),
        min_lon=0,
        min_lat=0,
        max_lon=1,
        max_lat=1,
        ticks=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
    )
    fake_df = pd.DataFrame({"datetime": [pd.Timestamp("2024-01-01")]})
    provider = bid.OpenMeteoWeatherProvider()

    with patch(
        "app.datasets.scripts.fetch_historical_weather.fetch_historical_weather",
        return_value=fake_df,
    ) as mock_fetch:
        provider.prepare_for_fire(event, target_shape=(4, 4))
        mock_fetch.assert_called_once()
        assert provider._current_fire_id == 2
        assert provider._df_by_fire[2] is fake_df

    expected_grids = {
        "wind_u": np.zeros((4, 4)),
        "wind_v": np.zeros((4, 4)),
        "temperature": np.zeros((4, 4)),
        "rel_humidity": np.zeros((4, 4)),
    }
    with patch(
        "app.datasets.scripts.fetch_historical_weather.get_weather_at_timestamp",
        return_value=expected_grids,
    ) as mock_get:
        result = provider.fetch(0, 0, 1, 1, pd.Timestamp("2024-01-01"), (4, 4))
        mock_get.assert_called_once()
        assert result is expected_grids


# Satic sources tests:


def test_static_source_manifest_from_csv_converts_nan_to_none(tmp_path):
    csv_path = tmp_path / "manifest.csv"
    csv_path.write_text("fire_id,dem_path,scl_path\n1,/data/dem1.tif,\n")
    manifest = bid.StaticSourceManifest.from_csv(csv_path)
    row = manifest.get(1)
    assert row["dem_path"] == "/data/dem1.tif"
    assert row["scl_path"] is None


def test_static_source_manifest_get_missing_fire_id_raises_keyerror(tmp_path):
    csv_path = tmp_path / "manifest.csv"
    csv_path.write_text("fire_id,dem_path\n1,/data/dem1.tif\n")
    manifest = bid.StaticSourceManifest.from_csv(csv_path)
    with pytest.raises(KeyError, match="fire_id=99"):
        manifest.get(99)


# Static grid loading


def test_load_static_grids_for_fire_falls_back_to_computing_aspect_sin_cos():
    manifest_row = {
        "b04_path": "b04.tif",
        "b08_path": "b08.tif",
        "b11_path": "b11.tif",
        "dem_path": "dem.tif",
        "scl_path": None,
        "worldcover_path": None,
    }
    fake_veg = {"fuel_load": np.full((2, 2), 0.5), "dryness": np.full((2, 2), 0.3)}
    fake_terrain = {
        "elevation": np.full((2, 2), 100.0),
        "slope": np.full((2, 2), 5.0),
        "aspect": np.full((2, 2), 90.0),  # only raw aspect given, no sin/cos
    }
    with patch(
        "app.backend.ml.features.fuel_load.process_sentinal2_and_worldcover",
        return_value=fake_veg,
    ), patch(
        "app.backend.ml.features.terrain.extract_terrain_features",
        return_value=fake_terrain,
    ):
        grids = bid.load_static_grids_for_fire(manifest_row, 0, 0, 1, 1, (2, 2))

    assert set(grids.keys()) == {
        "elevation",
        "slope",
        "aspect_sin",
        "aspect_cos",
        "fuel_load",
        "dryness",
    }
    assert grids["aspect_sin"] == pytest.approx(np.sin(np.radians(90.0)))
    assert grids["aspect_cos"] == pytest.approx(np.cos(np.radians(90.0)), abs=1e-6)
