from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from app.backend.src.ai.resolve_tiles import (
    COPERNICUS_DEM_BUCKET,
    ResolvedTiles,
    dem_tile_id,
    resolve_dem_path,
    resolve_sentinel2_bands,
    resolve_tile_paths,
)


class TestDemCoordinateCalculations:
    def test_dem_tile_id_quadrants(self):
        assert dem_tile_id(-25.9, 28.1) == "S26_00_E028_00"
        assert dem_tile_id(12.4, -15.6) == "N12_00_W016_00"
        assert dem_tile_id(0.0, 0.0) == "N00_00_E000_00"
        assert dem_tile_id(-0.5, -0.2) == "S01_00_W001_00"

    def test_resolve_dem_path_single_and_multi_cell(self):
        single_paths = resolve_dem_path(28.1, -25.9, 28.3, -25.8)
        assert len(single_paths) == 1
        expected_uri = (
            f"/vsis3/{COPERNICUS_DEM_BUCKET}/Copernicus_DSM_COG_10_S26_00_E028_00_DEM/"
            f"Copernicus_DSM_COG_10_S26_00_E028_00_DEM.tif"
        )
        assert single_paths[0] == expected_uri

        multi_paths = resolve_dem_path(10.2, 5.1, 11.4, 6.2)
        assert len(multi_paths) == 4
        for p in multi_paths:
            assert p.startswith(f"/vsis3/{COPERNICUS_DEM_BUCKET}/")
            assert p.endswith(".tif")


class TestResolveSentinel2Bands:
    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_success_with_timestamp(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        item_best = SimpleNamespace(
            id="S2_BEST_SCENE",
            datetime=datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc),
            properties={"eo:cloud_cover": 3.2},
            assets={
                "red": SimpleNamespace(href="s3://s2-bucket/b04.tif"),
                "nir": SimpleNamespace(href="s3://s2-bucket/b08.tif"),
                "swir16": SimpleNamespace(href="s3://s2-bucket/b11.tif"),
                "scl": SimpleNamespace(href="s3://s2-bucket/scl.tif"),
            },
        )
        item_older = SimpleNamespace(
            id="S2_OLDER_SCENE",
            datetime=datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc),
            properties={"eo:cloud_cover": 8.0},
            assets=item_best.assets,
        )

        search_result = MagicMock()
        search_result.items.return_value = [item_older, item_best]
        mock_catalog.search.return_value = search_result

        target_time = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
        resolved = resolve_sentinel2_bands(
            min_lon=28.0,
            min_lat=-26.0,
            max_lon=28.5,
            max_lat=-25.5,
            when=target_time,
            time_window=10,
            max_cloud_coverage=5.0,
        )

        assert isinstance(resolved, ResolvedTiles)
        assert resolved.s2_item_id == "S2_BEST_SCENE"
        assert resolved.b04_path == "s3://s2-bucket/b04.tif"
        assert resolved.b08_path == "s3://s2-bucket/b08.tif"
        assert resolved.b11_path == "s3://s2-bucket/b11.tif"
        assert resolved.scl_path == "s3://s2-bucket/scl.tif"
        assert resolved.s2_cloud_cover == 3.2

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_fallback_to_higher_cloud_limit_and_none_datetime(
        self, mock_client_open
    ):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        item_cloudy = SimpleNamespace(
            id="S2_FALLBACK_SCENE",
            datetime=None,  # Tests item.datetime is None branch in score()
            properties={"eo:cloud_cover": 25.0},
            assets={
                "red": SimpleNamespace(href="s3://s2-bucket/b04.tif"),
                "nir": SimpleNamespace(href="s3://s2-bucket/b08.tif"),
                "swir16": SimpleNamespace(href="s3://s2-bucket/b11.tif"),
            },
        )

        search_tier1 = MagicMock()
        search_tier1.items.return_value = []

        search_tier2 = MagicMock()
        search_tier2.items.return_value = [item_cloudy]

        mock_catalog.search.side_effect = [search_tier1, search_tier2]

        resolved = resolve_sentinel2_bands(
            min_lon=28.0,
            min_lat=-26.0,
            max_lon=28.5,
            max_lat=-25.5,
            when=None,  # Tests when = None branch
        )

        assert resolved.s2_item_id == "S2_FALLBACK_SCENE"
        assert resolved.scl_path is None
        assert resolved.s2_cloud_cover == 25.0

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_exhausted_clouds_raises_filenotfound(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        empty_search = MagicMock()
        empty_search.items.return_value = []
        mock_catalog.search.return_value = empty_search

        with pytest.raises(FileNotFoundError, match="No sentinel2 scene found"):
            resolve_sentinel2_bands(18.0, -34.0, 18.5, -33.5)

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_missing_required_bands_raises_filenotfound(
        self, mock_client_open
    ):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        item_incomplete = SimpleNamespace(
            id="S2_INCOMPLETE",
            datetime=datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
            properties={"eo:cloud_cover": 1.0},
            assets={
                "red": SimpleNamespace(href="s3://s2-bucket/b04.tif"),
            },
        )

        search_res = MagicMock()
        search_res.items.return_value = [item_incomplete]
        mock_catalog.search.return_value = search_res

        with pytest.raises(FileNotFoundError, match="is missing required bands"):
            resolve_sentinel2_bands(18.0, -34.0, 18.5, -33.5)


class TestResolveTilePathsIntegration:
    @patch("app.backend.src.ai.resolve_tiles.resolve_sentinel2_bands")
    def test_resolve_tile_paths_single_dem(self, mock_resolve_s2):
        dummy_s2 = ResolvedTiles(
            b04_path="b04",
            b08_path="b08",
            b11_path="b11",
            dem_path="",
        )
        mock_resolve_s2.return_value = dummy_s2

        result = resolve_tile_paths(
            min_lon=28.1,
            min_lat=-25.9,
            max_lon=28.3,
            max_lat=-25.8,
        )

        assert result.dem_path.endswith("Copernicus_DSM_COG_10_S26_00_E028_00_DEM.tif")

    @patch("builtins.print")
    @patch("app.backend.src.ai.resolve_tiles.resolve_sentinel2_bands")
    def test_resolve_tile_paths_multi_dem_logs_warning(self, mock_resolve_s2, mock_print):
        dummy_s2 = ResolvedTiles(
            b04_path="b04",
            b08_path="b08",
            b11_path="b11",
            dem_path="",
        )
        mock_resolve_s2.return_value = dummy_s2

        result = resolve_tile_paths(
            min_lon=10.2,
            min_lat=5.1,
            max_lon=11.4,
            max_lat=6.2,
        )

        assert result.dem_path.startswith(f"/vsis3/{COPERNICUS_DEM_BUCKET}/")
        mock_print.assert_called_once()
        log_text = mock_print.call_args[0][0]
        assert "WARNING: bbox spans 4 DEM tiles" in log_text