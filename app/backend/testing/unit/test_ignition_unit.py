import json
from unittest.mock import MagicMock, mock_open, patch
import numpy as np
import pytest
import xgboost as xgb

from ai.ignition import IgnitionScorer
from ai.schema import FEATURES, SCHEMA_VERSION, UNBURNED, BURNING, BURNED


class TestIgnitionScorerInit:
    def test_init_with_explicit_metadata(self):
        mock_booster = MagicMock(spec=xgb.Booster)
        metadata = {"version": "v1.0", "author": "team"}

        scorer = IgnitionScorer(booster=mock_booster, metadata=metadata)

        assert scorer.booster is mock_booster
        assert scorer.metadata == metadata
        mock_booster.set_param.assert_called_once_with({"nthread": 2, "device": "cpu"})

    def test_init_with_none_metadata(self):
        mock_booster = MagicMock(spec=xgb.Booster)

        scorer = IgnitionScorer(booster=mock_booster, metadata=None)

        assert scorer.booster is mock_booster
        assert scorer.metadata == {}
        mock_booster.set_param.assert_called_once_with({"nthread": 2, "device": "cpu"})


class TestIgnitionScorerLoad:
    @patch("ai.ignition.artifact_store.resolve")
    def test_load_schema_mismatch_features_raises_runtime_error(self, mock_resolve, tmp_path):
        metadata_file = tmp_path / "metadata.json"
        metadata = {
            "version": "v0.1",
            "features": ["wrong_feature_1", "wrong_feature_2"],
            "schema_version": SCHEMA_VERSION,
        }
        metadata_file.write_text(json.dumps(metadata))
        mock_resolve.return_value = tmp_path

        with pytest.raises(RuntimeError, match="Schema mismatch"):
            IgnitionScorer.load("v0.1")

    @patch("ai.ignition.artifact_store.resolve")
    def test_load_schema_mismatch_schema_version_raises_runtime_error(self, mock_resolve, tmp_path):
        metadata_file = tmp_path / "metadata.json"
        metadata = {
            "version": "v0.1",
            "features": FEATURES,
            "schema_version": SCHEMA_VERSION + 999,
        }
        metadata_file.write_text(json.dumps(metadata))
        mock_resolve.return_value = tmp_path

        with pytest.raises(RuntimeError, match="Schema mismatch"):
            IgnitionScorer.load("v0.1")

    @patch("ai.ignition.xgb.Booster")
    @patch("ai.ignition.artifact_store.resolve")
    def test_load_success(self, mock_resolve, mock_booster_cls, tmp_path):
        metadata_file = tmp_path / "metadata.json"
        metadata = {
            "version": "v1.0.0",
            "features": FEATURES,
            "schema_version": SCHEMA_VERSION,
        }
        metadata_file.write_text(json.dumps(metadata))
        mock_resolve.return_value = tmp_path

        mock_booster_instance = mock_booster_cls.return_value

        scorer = IgnitionScorer.load("v1.0.0")

        mock_resolve.assert_called_once_with("ignition", "v1.0.0")
        mock_booster_instance.load_model.assert_called_once_with(str(tmp_path / "model.json"))
        mock_booster_instance.set_param.assert_called_once_with({"nthread": 2, "device": "cpu"})
        assert scorer.booster is mock_booster_instance
        assert scorer.metadata == metadata


class TestIgnitionScorerScoreGrid:
    @patch("ai.ignition.grid_to_fmatrix")
    @patch("ai.ignition.xgb.DMatrix")
    def test_score_grid(self, mock_dmatrix, mock_grid_to_fmatrix):
        mock_booster = MagicMock(spec=xgb.Booster)
        scorer = IgnitionScorer(booster=mock_booster)

        H, W = 3, 3
        weather = {"temp": np.zeros((H, W), dtype=np.float32)}
        static = {"elevation": np.zeros((H, W), dtype=np.float32)}

        burn_state = np.array([
            [UNBURNED, BURNING, BURNED],
            [UNBURNED, UNBURNED, BURNING],
            [BURNED, UNBURNED, UNBURNED],
        ], dtype=np.int32)

        mock_grid_to_fmatrix.return_value = np.zeros((H * W, len(FEATURES)), dtype=np.float32)
        dummy_dmatrix = MagicMock()
        mock_dmatrix.return_value = dummy_dmatrix

        mock_booster.predict.return_value = np.full(H * W, 0.8, dtype=np.float32)

        p = scorer.score_grid(weather, static, burn_state)

        mock_grid_to_fmatrix.assert_called_once_with(weather, static, burn_state)
        mock_dmatrix.assert_called_once_with(mock_grid_to_fmatrix.return_value, feature_names=FEATURES)
        mock_booster.predict.assert_called_once_with(dummy_dmatrix)

        assert p.shape == (H, W)
        assert p.dtype == np.float32

        assert p[0, 0] == pytest.approx(0.8)
        assert p[1, 0] == pytest.approx(0.8)
        assert p[1, 1] == pytest.approx(0.8)
        assert p[2, 1] == pytest.approx(0.8)
        assert p[2, 2] == pytest.approx(0.8)

        assert p[0, 1] == 0.0
        assert p[0, 2] == 0.0
        assert p[1, 2] == 0.0
        assert p[2, 0] == 0.0