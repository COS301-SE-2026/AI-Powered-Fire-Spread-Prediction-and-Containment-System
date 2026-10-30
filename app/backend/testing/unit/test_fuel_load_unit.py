import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from app.backend.ml.features import fuel_load as fl
from app.backend.ml.features.fuel_load import (
    DEFAULT_SCL_MASKED_CLASSES,
    FUEL_BASE_WEIGHTS,
    NONBURNABLE_WORLDCOVER_CLASSES,
    SCL_WATER,
    _dn_to_reflectance,
    _read_window_single,
    _read_worldcover_window,
    _resample_to_shape,
    load_fuel_base_weights,
    process_sentinal2_and_worldcover,
    worldcover_s3_urls_for_bbox,
    worldcover_tile_id,
)


class TestLoadFuelBaseWeights:
    def test_load_weights_file_not_exists(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda self: False)
        weights = load_fuel_base_weights()
        assert weights == FUEL_BASE_WEIGHTS

    def test_load_weights_valid_json(self, monkeypatch):
        fake_data = {"10": 0.85, "20": 0.55}
        monkeypatch.setattr(Path, "exists", lambda self: True)
        with patch("builtins.open", mock_open(read_data=json.dumps(fake_data))):
            weights = load_fuel_base_weights()
        assert weights == {10: 0.85, 20: 0.55}

    def test_load_weights_corrupt_json_fallback(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda self: True)
        with patch("builtins.open", mock_open(read_data="invalid json")):
            weights = load_fuel_base_weights()
        assert weights == FUEL_BASE_WEIGHTS


class TestWorldCoverTilesAndUrls:
    def test_worldcover_tile_id_quadrants(self):
        assert worldcover_tile_id(1.5, 2.5) == "N00E000"
        assert worldcover_tile_id(35.2, 140.1) == "N33E138"
        assert worldcover_tile_id(-33.9, 18.4) == "S36E018"
        assert worldcover_tile_id(-12.4, -77.1) == "S15W078"

    def test_worldcover_s3_urls_invalid_year_raises(self):
        with pytest.raises(ValueError, match="No known WorldCover version for year=1999"):
            worldcover_s3_urls_for_bbox(0.0, 0.0, 1.0, 1.0, year=1999)

    def test_worldcover_s3_urls_valid_crossing_tiles(self):
        urls = worldcover_s3_urls_for_bbox(17.9, -34.1, 18.2, -33.9, year=2021)
        assert len(urls) >= 1
        assert all(u.startswith("s3://esa-worldcover/v200/2021/map/") for u in urls)


class TestResampleAndRasterWindows:
    def test_resample_to_shape_2d_and_3d(self):
        transform = from_origin(18.0, -33.0, 0.01, 0.01)
        crs = CRS.from_epsg(4326)

        arr_2d = np.ones((10, 10), dtype=np.float32)
        res_2d = _resample_to_shape(arr_2d, transform, crs, (5, 5), Resampling.nearest)
        assert res_2d.shape == (5, 5)

        arr_3d = np.ones((1, 10, 10), dtype=np.float32)
        res_3d = _resample_to_shape(arr_3d, transform, crs, (6, 6), Resampling.bilinear)
        assert res_3d.shape == (6, 6)

    def test_read_window_single_epsg4326(self):
        profile = {
            "driver": "GTiff",
            "height": 10,
            "width": 10,
            "count": 1,
            "dtype": "uint8",
            "crs": "EPSG:4326",
            "transform": from_origin(0.0, 10.0, 1.0, 1.0),
        }
        with MemoryFile() as mem:
            with mem.open(**profile) as dst:
                dst.write(np.ones((10, 10), dtype=np.uint8), 1)

            with patch("rasterio.open", side_effect=lambda *args, **kwargs: mem.open()):
                res = _read_window_single("dummy.tif", 0.0, 0.0, 4.0, 4.0, (4, 4), Resampling.nearest)
                assert res.shape == (4, 4)

    def test_read_window_single_none_crs_branch(self):
        mock_ds = MagicMock()
        mock_ds.crs = None
        mock_ds.transform = from_origin(0.0, 10.0, 1.0, 1.0)
        mock_ds.read.return_value = np.zeros((4, 4), dtype=np.uint8)

        mock_enter = MagicMock()
        mock_enter.__enter__.return_value = mock_ds
        mock_enter.__exit__.return_value = None

        with patch("rasterio.open", return_value=mock_enter):
            res = _read_window_single("dummy_none.tif", 0.0, 0.0, 2.0, 2.0, (4, 4), Resampling.nearest)
            assert res.shape == (4, 4)

    def test_read_window_single_projected_crs(self):
        mock_ds = MagicMock()
        mock_crs = MagicMock()
        mock_crs.to_epsg.return_value = 3857
        mock_ds.crs = mock_crs
        mock_ds.transform = from_origin(0.0, 10.0, 1.0, 1.0)
        mock_ds.read.return_value = np.zeros((4, 4), dtype=np.uint8)

        mock_enter = MagicMock()
        mock_enter.__enter__.return_value = mock_ds
        mock_enter.__exit__.return_value = None

        with patch("rasterio.open", return_value=mock_enter), \
             patch("app.backend.ml.features.fuel_load.transform_bounds", return_value=(0.0, 0.0, 100.0, 100.0)):
            res = _read_window_single("dummy_proj.tif", 0.0, 0.0, 1.0, 1.0, (4, 4), Resampling.nearest)
            assert res.shape == (4, 4)

    def test_read_worldcover_window_local_map_path(self):
        with patch("app.backend.ml.features.fuel_load.stream_cropped_raster") as mock_stream:
            mock_stream.return_value = np.full((10, 10), 10, dtype=np.uint8)
            res = _read_worldcover_window("/tmp/map.tif", 18.0, -34.0, 19.0, -33.0, (10, 10))
            assert res.shape == (10, 10)
            mock_stream.assert_called_once()

    def test_read_worldcover_window_s3_merge_exact_and_resampled(self):
        mock_ds = MagicMock()
        mock_ds.crs = CRS.from_epsg(4326)

        mosaic_exact = np.zeros((1, 8, 8), dtype=np.uint8)
        with patch("rasterio.open", return_value=mock_ds), \
             patch("app.backend.ml.features.fuel_load.rio_merge", return_value=(mosaic_exact, "mock_transform")):
            res = _read_worldcover_window(None, 18.0, -34.0, 19.0, -33.0, (8, 8), worldcover_year=2021)
            assert res.shape == (8, 8)
            mock_ds.close.assert_called()

        mosaic_diff = np.zeros((1, 16, 16), dtype=np.uint8)
        with patch("rasterio.open", return_value=mock_ds), \
             patch("app.backend.ml.features.fuel_load.rio_merge", return_value=(mosaic_diff, "mock_transform")), \
             patch("app.backend.ml.features.fuel_load._resample_to_shape", return_value=np.zeros((8, 8), dtype=np.uint8)) as mock_resample:
            res_resampled = _read_worldcover_window(None, 18.0, -34.0, 19.0, -33.0, (8, 8), worldcover_year=2021)
            assert res_resampled.shape == (8, 8)
            mock_resample.assert_called_once()


class TestDnToReflectance:
    def test_dn_to_reflectance_scaling_and_nodata(self):
        dn = np.array([0, 1000, 2000], dtype=np.int32)
        refl = _dn_to_reflectance(dn, scale=0.0001, offset=-0.1, nodata=0)
        assert np.isnan(refl[0])
        assert np.isclose(refl[1], 1000 * 0.0001 - 0.1)
        assert np.isclose(refl[2], 2000 * 0.0001 - 0.1)

    def test_dn_to_reflectance_nodata_none(self):
        dn = np.array([0, 1000], dtype=np.int32)
        refl = _dn_to_reflectance(dn, scale=0.0001, offset=0.0, nodata=None)
        assert not np.isnan(refl[0])
        assert refl[0] == 0.0


class TestProcessSentinal2AndWorldcover:
    def test_process_sentinal2_and_worldcover_without_scl(self):
        h, w = 10, 10
        fake_wc = np.full((h, w), 10, dtype=np.uint8)
        fake_wc[0, 0] = NONBURNABLE_WORLDCOVER_CLASSES[0]

        fake_b04_dn = np.full((h, w), 2000, dtype=np.int32)
        fake_b08_dn = np.full((h, w), 4000, dtype=np.int32)
        fake_b11_dn = np.full((h, w), 1500, dtype=np.int32)

        def mock_stream(path, *args, **kwargs):
            if "b04" in path:
                return fake_b04_dn
            if "b08" in path:
                return fake_b08_dn
            return fake_b11_dn

        with patch("app.backend.ml.features.fuel_load._read_worldcover_window", return_value=fake_wc), \
             patch("app.backend.ml.features.fuel_load.stream_cropped_raster", side_effect=mock_stream):
            result = process_sentinal2_and_worldcover(
                b04_path="b04.tif",
                b08_path="b08.tif",
                b11_path="b11.tif",
                min_lon=18.0,
                min_lat=-34.0,
                max_lon=18.5,
                max_lat=-33.5,
                target_shape=(h, w),
                scl_path=None,
            )

        assert result["fuel_load"].shape == (h, w)
        assert result["dryness"].shape == (h, w)
        assert result["valid_mask"].shape == (h, w)
        assert bool(result["valid_mask"].all()) is True
        assert bool(result["nonburnable"][0, 0]) is True
        assert bool(result["nonburnable"][1, 1]) is False

    def test_process_sentinal2_and_worldcover_with_scl_cloud_and_water(self):
        h, w = 10, 10
        fake_wc = np.full((h, w), 30, dtype=np.uint8)
        fake_b04_dn = np.full((h, w), 2000, dtype=np.int32)
        fake_b08_dn = np.full((h, w), 4000, dtype=np.int32)
        fake_b11_dn = np.full((h, w), 1500, dtype=np.int32)

        fake_scl = np.full((h, w), 4, dtype=np.uint8)
        cloud_class = list(DEFAULT_SCL_MASKED_CLASSES)[0]
        fake_scl[0, 0] = cloud_class
        fake_scl[1, 1] = SCL_WATER

        def mock_stream(path, *args, **kwargs):
            if "b04" in path:
                return fake_b04_dn
            if "b08" in path:
                return fake_b08_dn
            if "b11" in path:
                return fake_b11_dn
            return fake_scl

        with patch("app.backend.ml.features.fuel_load._read_worldcover_window", return_value=fake_wc), \
             patch("app.backend.ml.features.fuel_load.stream_cropped_raster", side_effect=mock_stream):
            result = process_sentinal2_and_worldcover(
                b04_path="b04.tif",
                b08_path="b08.tif",
                b11_path="b11.tif",
                min_lon=18.0,
                min_lat=-34.0,
                max_lon=18.5,
                max_lat=-33.5,
                target_shape=(h, w),
                scl_path="scl.tif",
            )

        assert result["valid_mask"][0, 0] == False
        assert result["valid_mask"][2, 2] == True
        assert result["nonburnable"][1, 1] == True
        assert not np.isnan(result["fuel_load"]).any()
        assert not np.isnan(result["dryness"]).any()

    def test_process_sentinal2_and_worldcover_all_cloud_fallback(self):
        h, w = 6, 6
        fake_wc = np.full((h, w), 20, dtype=np.uint8)
        fake_b04_dn = np.full((h, w), 2000, dtype=np.int32)
        fake_b08_dn = np.full((h, w), 4000, dtype=np.int32)
        fake_b11_dn = np.full((h, w), 1500, dtype=np.int32)

        cloud_class = list(DEFAULT_SCL_MASKED_CLASSES)[0]
        all_clouds = np.full((h, w), cloud_class, dtype=np.uint8)

        def mock_stream(path, *args, **kwargs):
            if "b04" in path:
                return fake_b04_dn
            if "b08" in path:
                return fake_b08_dn
            if "b11" in path:
                return fake_b11_dn
            return all_clouds

        with patch("app.backend.ml.features.fuel_load._read_worldcover_window", return_value=fake_wc), \
             patch("app.backend.ml.features.fuel_load.stream_cropped_raster", side_effect=mock_stream):
            result = process_sentinal2_and_worldcover(
                b04_path="b04.tif",
                b08_path="b08.tif",
                b11_path="b11.tif",
                min_lon=18.0,
                min_lat=-34.0,
                max_lon=18.5,
                max_lat=-33.5,
                target_shape=(h, w),
                scl_path="scl.tif",
            )

        assert result["valid_mask"].sum() == 0
        assert np.all(result["fuel_load"] == 0.0)
        assert np.all(result["dryness"] == 0.0)