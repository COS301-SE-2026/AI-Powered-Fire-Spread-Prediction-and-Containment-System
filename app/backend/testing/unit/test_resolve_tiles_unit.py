from datetime import datetime, timezone
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


class TestDemTileId:
    def test_southern_eastern_coordinates(self):
        tile = dem_tile_id(-25.9, 28.1)
        assert tile == "S26_00_E028_00"

    def test_northern_western_coordinates(self):
        tile = dem_tile_id(12.4, -15.6)
        assert tile == "N12_00_W016_00"

    def test_exact_zero_coordinates(self):
        tile = dem_tile_id(0.0, 0.0)
        assert tile == "N00_00_E000_00"


class TestResolveDemPath:
    def test_single_cell_bounding_box(self):
        paths = resolve_dem_path(28.1, -25.9, 28.3, -25.8)
        assert len(paths) == 1
        expected_tile = "S26_00_E028_00"
        assert f"/vsis3/{COPERNICUS_DEM_BUCKET}/Copernicus_DSM_COG_10_{expected_tile}_DEM/" in paths[0]

    def test_multi_cell_bounding_box(self):
        paths = resolve_dem_path(10.2, 5.1, 11.4, 6.2)
        assert len(paths) == 4
        for p in paths:
            assert p.startswith(f"/vsis3/{COPERNICUS_DEM_BUCKET}/")
            assert p.endswith(".tif")


class TestResolveSentinel2Bands:
    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_success(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        mock_item = MagicMock()
        mock_item.id = "S2A_TEST_SCENE"
        mock_item.datetime = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        mock_item.properties = {"eo:cloud_cover": 4.5}
        mock_item.assets = {
            "red": MagicMock(href="s3://sentinel-s2-l2a/red.jp2"),
            "nir": MagicMock(href="s3://sentinel-s2-l2a/nir.jp2"),
            "swir16": MagicMock(href="s3://sentinel-s2-l2a/swir16.jp2"),
            "scl": MagicMock(href="s3://sentinel-s2-l2a/scl.jp2"),
        }

        mock_search = MagicMock()
        mock_search.items.return_value = [mock_item]
        mock_catalog.search.return_value = mock_search

        result = resolve_sentinel2_bands(
            min_lon=28.0,
            min_lat=-26.0,
            max_lon=28.5,
            max_lat=-25.5,
            when=datetime(2026, 5, 11, tzinfo=timezone.utc),
        )

        assert isinstance(result, ResolvedTiles)
        assert result.b04_path == "s3://sentinel-s2-l2a/red.jp2"
        assert result.b08_path == "s3://sentinel-s2-l2a/nir.jp2"
        assert result.b11_path == "s3://sentinel-s2-l2a/swir16.jp2"
        assert result.scl_path == "s3://sentinel-s2-l2a/scl.jp2"
        assert result.s2_item_id == "S2A_TEST_SCENE"
        assert result.s2_cloud_cover == 4.5

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_missing_scl_and_none_datetime(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        mock_item = MagicMock()
        mock_item.id = "S2B_NO_SCL"
        mock_item.datetime = None
        mock_item.properties = {"eo:cloud_cover": 8.0}
        mock_item.assets = {
            "red": MagicMock(href="s3://sentinel-s2-l2a/red.jp2"),
            "nir": MagicMock(href="s3://sentinel-s2-l2a/nir.jp2"),
            "swir16": MagicMock(href="s3://sentinel-s2-l2a/swir16.jp2"),
        }

        mock_search = MagicMock()
        mock_search.items.return_value = [mock_item]
        mock_catalog.search.return_value = mock_search

        result = resolve_sentinel2_bands(
            min_lon=28.0,
            min_lat=-26.0,
            max_lon=28.5,
            max_lat=-25.5,
            when=None,
        )

        assert result.scl_path is None
        assert result.s2_item_id == "S2B_NO_SCL"

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_no_items_raises_error(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        mock_search = MagicMock()
        mock_search.items.return_value = []
        mock_catalog.search.return_value = mock_search

        with pytest.raises(FileNotFoundError, match="No sentinel2 scene found"):
            resolve_sentinel2_bands(28.0, -26.0, 28.5, -25.5)

    @patch("app.backend.src.ai.resolve_tiles.Client.open")
    def test_resolve_sentinel2_bands_missing_required_bands_raises_error(self, mock_client_open):
        mock_catalog = MagicMock()
        mock_client_open.return_value = mock_catalog

        mock_item = MagicMock()
        mock_item.id = "S2A_CORRUPT"
        mock_item.datetime = datetime.now(timezone.utc)
        mock_item.properties = {"eo:cloud_cover": 2.0}
        mock_item.assets = {
            "red": MagicMock(href="s3://sentinel-s2-l2a/red.jp2"),
        }

        mock_search = MagicMock()
        mock_search.items.return_value = [mock_item]
        mock_catalog.search.return_value = mock_search

        with pytest.raises(FileNotFoundError, match="missing required bands"):
            resolve_sentinel2_bands(28.0, -26.0, 28.5, -25.5)


class TestResolveTilePaths:
    @patch("app.backend.src.ai.resolve_tiles.resolve_sentinel2_bands")
    @patch("app.backend.src.ai.resolve_tiles.resolve_dem_path")
    def test_resolve_tile_paths_single_dem(self, mock_resolve_dem, mock_resolve_s2):
        dummy_s2 = ResolvedTiles(
            b04_path="b04",
            b08_path="b08",
            b11_path="b11",
            dem_path="",
        )
        mock_resolve_s2.return_value = dummy_s2
        mock_resolve_dem.return_value = ["/path/dem_single.tif"]

        result = resolve_tile_paths(10.0, 20.0, 10.5, 20.5)

        assert result.dem_path == "/path/dem_single.tif"
        mock_resolve_s2.assert_called_once()
        mock_resolve_dem.assert_called_once()

    @patch("builtins.print")
    @patch("app.backend.src.ai.resolve_tiles.resolve_sentinel2_bands")
    @patch("app.backend.src.ai.resolve_tiles.resolve_dem_path")
    def test_resolve_tile_paths_multi_dem_warning(self, mock_resolve_dem, mock_resolve_s2, mock_print):
        dummy_s2 = ResolvedTiles(
            b04_path="b04",
            b08_path="b08",
            b11_path="b11",
            dem_path="",
        )
        mock_resolve_s2.return_value = dummy_s2
        mock_resolve_dem.return_value = ["/path/dem_1.tif", "/path/dem_2.tif"]

        result = resolve_tile_paths(10.0, 20.0, 11.5, 21.5)

        assert result.dem_path == "/path/dem_1.tif"
        mock_print.assert_called_once()
        printed_msg = mock_print.call_args[0][0]
        assert "WARNING: bbox spans 2 DEM tiles" in printed_msg