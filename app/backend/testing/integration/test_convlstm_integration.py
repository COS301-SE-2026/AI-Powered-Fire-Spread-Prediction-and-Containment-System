import json
from pathlib import Path

import numpy as np
import pytest
from torch.utils.data import DataLoader

from app.backend.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.backend.ml.training.dataset import WeatherDatasetSplitConfig, WeatherRolloutDataset
from app.backend.ml.training.train_convlstm import TrainConfig, Trainer, build_normalizers


@pytest.fixture
def integration_env(tmp_path):
    """Sets up a temporary filesystem with dummy .npz weather data and static terrain."""
    tensors_dir = tmp_path / "weather_tensors"
    tensors_dir.mkdir()
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    # 1.tiny weather tensor file (12 hours total, just enough for 6 input + 4 rollout)
    T, H, W = 12, 8, 8
    hourly_tensor = np.ones((T, 4, H, W), dtype=np.float32)
    hourly_deltas = np.full((T, 4, H, W), 0.1, dtype=np.float32)
    timestamps = [f"2026-01-01T{h:02d}:00:00" for h in range(T)]

    npz_path = tensors_dir / "weather_tensors_2026.npz"
    np.savez_compressed(
        npz_path,
        hourly_tensor=hourly_tensor,
        hourly_timestamps=np.array(timestamps, dtype="U19"),
        hourly_deltas=hourly_deltas,
    )

    # 2.static tensor (4 channels: elevation, slope, aspect_sin, aspect_cos)
    static_tensor = np.zeros((4, H, W), dtype=np.float32)
    static_path = static_dir / "static_tensor.npz"
    np.savez_compressed(static_path, static_tensor=static_tensor)

    return {
        "tensors_dir": str(tensors_dir),
        "static_path": str(static_path),
        "artifacts_dir": str(artifacts_dir),
        "npz_paths": [str(npz_path)],
        "static_tensor": static_tensor,
    }


def test_convlstm_training_pipeline_integration(integration_env, monkeypatch):
    """Tests the end-to-end integration of the Dataset, Normalizers, Model, and Trainer."""

    # intercept the save path so the trainer writes to our temp directory instead of the artifact store
    def mock_path(path_str):
        if "artifact_store" in str(path_str):
            return Path(integration_env["artifacts_dir"])
        return Path(path_str)

    monkeypatch.setattr("app.backend.ml.training.train_convlstm.Path", mock_path)

    # build normalizers using the data
    raw_norm, delta_norm = build_normalizers(
        integration_env["npz_paths"], integration_env["static_tensor"]
    )

    # init Dataset and DataLoader
    split_cfg = WeatherDatasetSplitConfig(input_hours=6, rollout_steps=4)
    dataset = WeatherRolloutDataset(
        npz_paths=integration_env["npz_paths"],
        static_tensor=integration_env["static_tensor"],
        raw_normalizer=raw_norm,
        delta_normalizer=delta_norm,
        cfg=split_cfg,
    )

    # ensure our sliding window math successfully captured at least one sequence
    assert len(dataset) > 0
    loader = DataLoader(dataset, batch_size=2, shuffle=False)

    # init ConvLSTM Model (using tiny layers to keep tests fast on CPU)
    model_cfg = WeatherDeltaModelConfig(hidden_dims=[8, 8], kernel_size=3)
    model = WeatherDeltaModel(model_cfg)

    # init trainer
    train_cfg = TrainConfig(
        device="cpu",
        rollout_steps=4,
        epochs=2,  # Run 2 epochs to guarantee we trigger the "is_best" save logic
        lr=1e-3,
    )

    trainer = Trainer(
        model=model,
        train_loader=loader,
        val_loader=loader,  # We reuse the loader for validation in this tiny test
        static_tensor=integration_env["static_tensor"],
        raw_normalizer=raw_norm,
        delta_normalizer=delta_norm,
        cfg=train_cfg,
    )

    assert trainer.best_val_loss == float("inf")

    # fit model
    trainer.fit(num_epochs=train_cfg.epochs)

    assert trainer.best_val_loss < float(
        "inf"
    ), "Validation loss should have decreased and updated"

    artifacts_path = Path(integration_env["artifacts_dir"])
    assert (
        artifacts_path / "model.pt"
    ).exists(), "Model weights were not saved to disk"
    assert (
        artifacts_path / "metadata.json"
    ).exists(), "Metadata JSON was not saved to disk"

    # verify JSON structure
    with open(artifacts_path / "metadata.json", "r") as f:
        metadata = json.load(f)
        assert "val_loss" in metadata
        assert "val_metrics" in metadata
        assert "wind_u" in metadata["val_metrics"], "Metrics tracker output is missing"
