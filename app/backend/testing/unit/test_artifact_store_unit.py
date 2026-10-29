import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from app.backend.src.ai.artifact_store import (
    gpu_name,
    list_versions,
    new_version_name,
    promote_version,
    publish,
    resolve,
    store_root,
)


@pytest.fixture
def temp_store(tmp_path, monkeypatch):
    store_dir = tmp_path / "test_artifact_store"
    monkeypatch.setenv("FIRE_ARTIFACT_STORE", str(store_dir))
    return store_dir


class TestStoreRootAndNames:
    def test_store_root_creates_directory(self, temp_store):
        root = store_root()
        assert root == temp_store
        assert root.is_dir()

    def test_new_version_name_format(self):
        v = new_version_name()
        assert v.startswith("v")
        assert "_" in v


class TestGpuName:
    @patch("subprocess.run")
    def test_gpu_name_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="NVIDIA RTX 4090\n")
        assert gpu_name() == "NVIDIA RTX 4090"

    @patch("subprocess.run")
    def test_gpu_name_subprocess_exception_fallback(self, mock_run):
        mock_run.side_effect = subprocess.SubprocessError("Command not found")
        assert gpu_name() == "none/cpu"

    @patch("subprocess.run")
    def test_gpu_name_nonzero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert gpu_name() == "none/cpu"


class TestPublishAndPromote:
    def test_publish_without_promotion(self, temp_store, tmp_path):
        dummy_model = tmp_path / "temp_model.json"
        dummy_model.write_text(json.dumps({"weights": [1, 2, 3]}))

        version = publish(
            model_family="xgboost",
            model_path=dummy_model,
            metadata={"loss": 0.05},
            promote=False,
        )

        vdir = temp_store / "xgboost" / version
        assert vdir.is_dir()
        assert (vdir / "model.json").exists()
        assert (vdir / "metadata.json").exists()

        meta = json.loads((vdir / "metadata.json").read_text())
        assert meta["version"] == version
        assert meta["loss"] == 0.05
        assert "published_utc" in meta

        assert not (temp_store / "xgboost" / "LATEST").exists()

    def test_publish_with_promotion(self, temp_store, tmp_path):
        dummy_model = tmp_path / "temp_model.json"
        dummy_model.write_text(json.dumps({"weights": [4, 5, 6]}))

        version = publish(
            model_family="convlstm",
            model_path=dummy_model,
            metadata={"epoch": 10},
            promote=True,
        )

        latest_pointer = temp_store / "convlstm" / "LATEST"
        assert latest_pointer.exists()
        assert latest_pointer.read_text().strip() == version

    def test_promote_nonexistent_version_raises_error(self, temp_store):
        (temp_store / "xgboost").mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError, match="No such version to promote"):
            promote_version("xgboost", "v99999999-missing_host")


class TestResolve:
    def test_resolve_latest_missing_pointer_raises_error(self, temp_store):
        (temp_store / "xgboost").mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError, match="No LATEST pointer"):
            resolve("xgboost", version="LATEST")

    def test_resolve_latest_success(self, temp_store, tmp_path):
        dummy_model = tmp_path / "m.json"
        dummy_model.write_text("{}")
        version = publish("xgboost", dummy_model, {}, promote=True)

        resolved_dir = resolve("xgboost", version="LATEST")
        assert resolved_dir == temp_store / "xgboost" / version

    def test_resolve_specific_version_success(self, temp_store, tmp_path):
        dummy_model = tmp_path / "m.json"
        dummy_model.write_text("{}")
        version = publish("xgboost", dummy_model, {}, promote=False)

        resolved_dir = resolve("xgboost", version=version)
        assert resolved_dir == temp_store / "xgboost" / version

    def test_resolve_specific_version_missing_raises_error(self, temp_store):
        (temp_store / "xgboost").mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError, match="Artifact version not found"):
            resolve("xgboost", version="v00000000-none_host")


class TestListVersions:
    def test_list_versions_empty_when_no_family_dir(self, temp_store):
        assert list_versions("nonexistent_family") == []

    def test_list_versions_returns_sorted_list(self, temp_store, tmp_path):
        dummy_model = tmp_path / "m.json"
        dummy_model.write_text("{}")

        v1 = publish("xgboost", dummy_model, {})
        v2 = publish("xgboost", dummy_model, {})

        (temp_store / "xgboost" / "ignore_dir").mkdir()
        (temp_store / "xgboost" / "LATEST").write_text(v2)

        versions = list_versions("xgboost")
        assert versions == sorted([v1, v2])