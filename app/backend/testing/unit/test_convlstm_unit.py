import pytest
import torch
import numpy as np
import math
import torch.nn as nn
from app.ml.training.train_convlstm import tf_p_for_epoch, TrainConfig, Trainer
from app.ml.training.losses import SmoothL1DeltaLoss
from app.ml.training.metrics import MetricTracker
from app.ml.training.dataset import (
    WeatherDatasetSplitConfig,
    WeatherRolloutDataset,
    _hour_angle,
    attach_static_and_time,
)


# First I test the loss function, then the metrics
def test_smooth_l1_delta_loss_initialization():
    """Tests default and custom beta initialization"""
    # test defualt
    loss_default = SmoothL1DeltaLoss()
    assert loss_default.loss_fn.beta == 1.0
    # test custom
    loss_custom = SmoothL1DeltaLoss(beta=0.5)
    assert loss_custom.loss_fn.beta == 0.5


def test_smooth_l1_delta_loss_perfect_match():
    """tests that identical tensors yield zero loss"""
    loss_fn = SmoothL1DeltaLoss()
    pred = torch.tensor([1.0, 2.0, 3.0])
    target = torch.tensor([1.0, 2.0, 3.0])

    loss = loss_fn(pred, target)
    assert loss.item() == 0.0


def test_smooth_l1_delta_loss_l2_region():
    """Teststhe l2 (MSE) part of the function where
    absolute error is less than beta"""
    beta = 1.0
    loss_fn = SmoothL1DeltaLoss(beta)
    # we make the error be 0.5<beta
    pred = torch.tensor([1.5])
    target = torch.tensor([1.0])
    loss = loss_fn(pred, target)
    assert pytest.approx(loss.item(), 0.0001) == 0.125


def test_smooth_l1_delta_loss_l1_region():
    """Test the L1 (MAE) region where absolute error is greater than beta."""
    beta = 1.0
    loss_fn = SmoothL1DeltaLoss(beta=beta)

    # Error is 2.0, which is > beta (1.0).
    # Formula: |err| - 0.5 * beta = 2.0 - 0.5 = 1.5
    pred = torch.tensor([3.0])
    target = torch.tensor([1.0])

    loss = loss_fn(pred, target)
    assert pytest.approx(loss.item(), 0.0001) == 1.5


def test_smooth_l1_delta_loss_multidimensional():
    """Test that the loss handles 4D tensors (Batch, Channel, H, W) correctly."""
    loss_fn = SmoothL1DeltaLoss()

    # Simulating a batch size of 2, 4 weather variables, 10x10 map grid
    pred = torch.randn(2, 4, 10, 10)
    target = torch.randn(2, 4, 10, 10)

    loss = loss_fn(pred, target)

    # By default, PyTorch's SmoothL1Loss reduces the output to a single scalar mean
    assert loss.dim() == 0
    assert loss.item() >= 0


def test_metric_tracker_initialization():
    """Test that the tracker initializes with correct shapes and zeroes"""
    variables = ["temp", "humid"]
    num_steps = 3
    tracker = MetricTracker(variables=variables, num_steps=num_steps)
    assert tracker.variables == variables
    assert tracker.num_steps == num_steps
    assert tracker._sq_err_model.shape == (2, 3)
    assert tracker._sq_err_persistence.shape == (2, 3)
    assert tracker._count.shape == (2, 3)
    assert np.all(tracker._count == 0)


def test_metric_tracker_update_accumulation():
    """Test that errors and counts accumulate correctly across multiple batches."""
    tracker = MetricTracker(variables=["wind_u"], num_steps=1)

    pred = np.full((2, 1, 1, 2, 2), 2.0)
    target = np.full((2, 1, 1, 2, 2), 1.0)
    persistence = np.full((2, 1, 1, 2, 2), 0.0)
    # Model error = (2-1)^2 = 1.0 per pixel.
    # Persistence error = (0-1)^2 = 1.0 per pixel.
    # Total pixels evaluated = 2 (batch) * 2 * 2 (spatial) = 8.
    tracker.update(pred, target, persistence)

    assert tracker._count[0, 0] == 8
    assert tracker._sq_err_model[0, 0] == 8.0
    assert tracker._sq_err_persistence[0, 0] == 8.0

    # Run a second identical batch to verify continuous accumulation
    tracker.update(pred, target, persistence)
    assert tracker._count[0, 0] == 16
    assert tracker._sq_err_model[0, 0] == 16.0


def test_metric_tracker_compute_perfect_model():
    """Test compute when the model perfectly predicts the target."""
    tracker = MetricTracker(variables=["wind_u"], num_steps=1)

    pred = np.full((1, 1, 1, 1, 1), 5.0)
    target = np.full((1, 1, 1, 1, 1), 5.0)
    persistence = np.full((1, 1, 1, 1, 1), 0.0)

    tracker.update(pred, target, persistence)
    results = tracker.compute()

    assert "wind_u" in results
    assert 1 in results["wind_u"]

    metrics = results["wind_u"][1]
    assert metrics["model_rmse"] == 0.0
    assert metrics["persistence_rmse"] == 5.0
    assert metrics["skill"] == 1.0  # Formula: 1.0 - (0.0 / 5.0)


def test_metric_tracker_compute_negative_skill():
    """Test compute when the model performs worse than the persistence baseline."""
    tracker = MetricTracker(variables=["wind_u"], num_steps=1)

    pred = np.full((1, 1, 1, 1, 1), 10.0)
    target = np.full((1, 1, 1, 1, 1), 5.0)
    persistence = np.full((1, 1, 1, 1, 1), 4.0)

    tracker.update(pred, target, persistence)
    metrics = tracker.compute()["wind_u"][1]

    # Model RMSE = 5.0, Persistence RMSE = 1.0
    # Skill = 1.0 - (5.0 / 1.0) = -4.0
    assert metrics["model_rmse"] == 5.0
    assert metrics["persistence_rmse"] == 1.0
    assert metrics["skill"] == -4.0


def test_metric_tracker_zero_persistence():
    """Test compute gracefully handles zero persistence error by returning NaN skill."""
    tracker = MetricTracker(variables=["wind_u"], num_steps=1)

    pred = np.full((1, 1, 1, 1, 1), 5.0)
    target = np.full((1, 1, 1, 1, 1), 5.0)
    persistence = np.full((1, 1, 1, 1, 1), 5.0)

    tracker.update(pred, target, persistence)
    metrics = tracker.compute()["wind_u"][1]

    assert metrics["persistence_rmse"] == 0.0
    assert math.isnan(metrics["skill"])


# now I test the dataset.py
class DummyNormalizer:
    """mock normalizer for unit tests"""

    def transform(self, frame: np.ndarray) -> np.ndarray:
        return frame


@pytest.fixture
def dummy_static_tensor():
    """Generates a 4-channel static tensor (Elevation, Slope, SinAspect, CosAspect)."""
    return np.zeros((4, 10, 10), dtype=np.float32)


@pytest.fixture
def dummy_npz_file(tmp_path):
    """Creates a temporary .npz dataset file with 24 hourly timestamps."""
    npz_path = tmp_path / "weather_tensors_2026.npz"

    T, H, W = 24, 10, 10
    hourly_tensor = np.ones((T, 4, H, W), dtype=np.float32)
    hourly_deltas = np.full((T, 4, H, W), 0.1, dtype=np.float32)

    # timestamps are in Jan
    timestamps = [
        f"2026-01-01T{h:02d}:00:00" if h < 24 else f"2026-01-02T{h-24:02d}:00:00"
        for h in range(T)
    ]

    np.savez_compressed(
        npz_path,
        hourly_tensor=hourly_tensor,
        hourly_timestamps=np.array(timestamps, dtype="U19"),
        hourly_deltas=hourly_deltas,
    )
    return str(npz_path)


# 1. the follwoning tests are just to check that the utility funcitons work
def test_hour_angle_midnight_and_noon_returns_expected_trig_values():
    """Test _hour_angle converts midnight to (0, 1) and noon to (0, -1)
    since this is how polar cordinates work"""
    timestamps = ["2026-01-01T00:00:00", "2026-01-01T12:00:00"]
    sin_vals, cos_vals = _hour_angle(timestamps)

    # Midnight (00:00): sin(0) = 0.0, cos(0) = 1.0
    assert pytest.approx(sin_vals[0], abs=1e-4) == 0.0
    assert pytest.approx(cos_vals[0], abs=1e-4) == 1.0

    # Noon (12:00): sin(pi) = 0.0, cos(pi) = -1.0
    assert pytest.approx(sin_vals[1], abs=1e-4) == 0.0
    assert pytest.approx(cos_vals[1], abs=1e-4) == -1.0


def test_attach_static_and_time_3d_dynamic_returns_concatenated_shape(
    dummy_static_tensor,
):
    """Test 3D dynamic tensor (4 channels) attaches static (4) and time (2) -> 10 channels."""
    dynamic_3d = np.zeros((4, 10, 10), dtype=np.float32)
    result = attach_static_and_time(
        dynamic_3d, dummy_static_tensor, hour_sin=0.0, hour_cos=1.0
    )

    # Shape: (4 dynamic + 4 static + 1 sin + 1 cos, H=10, W=10) = (10, 10, 10)
    assert result.shape == (10, 10, 10)


def test_attach_static_and_time_4d_dynamic_returns_concatenated_shape(
    dummy_static_tensor,
):
    """Test 4D dynamic tensor sequence (T, 4, H, W) attaches static and time correctly."""
    T, H, W = 6, 10, 10
    dynamic_4d = np.zeros((T, 4, H, W), dtype=np.float32)
    hour_sin = np.zeros(T, dtype=np.float32)
    hour_cos = np.ones(T, dtype=np.float32)

    result = attach_static_and_time(dynamic_4d, dummy_static_tensor, hour_sin, hour_cos)

    # Shape: (T=6, 10 channels, H=10, W=10)
    assert result.shape == (6, 10, H, W)


def test_attach_static_and_time_invalid_ndim_raises_value_error(dummy_static_tensor):
    """Test passing invalid tensor dimensions (e.g. 2D) raises ValueError."""
    invalid_dynamic = np.zeros((10, 10), dtype=np.float32)
    with pytest.raises(ValueError, match="Unexpected dynamic tensor ndim"):
        attach_static_and_time(invalid_dynamic, dummy_static_tensor, 0.0, 1.0)


# 2 the following tests check indexing and dataset mechanics


def test_weather_rollout_dataset_len_valid_indices(dummy_npz_file, dummy_static_tensor):
    """Test dataset length matches valid sliding window count based on T, input_hours, rollout_steps."""
    split_cfg = WeatherDatasetSplitConfig(input_hours=6, rollout_steps=4)
    dataset = WeatherRolloutDataset(
        npz_paths=[dummy_npz_file],
        static_tensor=dummy_static_tensor,
        raw_normalizer=DummyNormalizer(),
        delta_normalizer=DummyNormalizer(),
        cfg=split_cfg,
    )

    # Total timestamps = 24.
    # Valid indices: input_hours - 1 (5) to T - 1 - rollout_steps + 1 (20)
    # Expected samples = 24 - 6 - 4 + 1 = 15.
    assert len(dataset) == 15


def test_weather_rollout_dataset_getitem_returns_correct_tensor_shapes_and_types(
    dummy_npz_file, dummy_static_tensor
):
    """Test __getitem__ returns correctly formatted PyTorch Tensors with accurate window shapes."""
    split_cfg = WeatherDatasetSplitConfig(input_hours=6, rollout_steps=4)
    dataset = WeatherRolloutDataset(
        npz_paths=[dummy_npz_file],
        static_tensor=dummy_static_tensor,
        raw_normalizer=DummyNormalizer(),
        delta_normalizer=DummyNormalizer(),
        cfg=split_cfg,
    )

    sample = dataset[0]

    assert isinstance(sample["input_seq"], torch.Tensor)
    assert sample["input_seq"].shape == (
        6,
        10,
        10,
        10,
    )  # (InputHours=6, Channels=10, H=10, W=10)

    assert isinstance(sample["anchor_dynamic_raw"], torch.Tensor)
    assert sample["anchor_dynamic_raw"].shape == (
        4,
        10,
        10,
    )  # Anchor frame (4 weather vars)

    assert isinstance(sample["future_dynamic_raw"], torch.Tensor)
    assert sample["future_dynamic_raw"].shape == (
        4,
        4,
        10,
        10,
    )  # (Rollout=4, Vars=4, H=10, W=10)

    assert isinstance(sample["future_deltas_norm"], torch.Tensor)
    assert sample["future_deltas_norm"].shape == (4, 4, 10, 10)

    assert sample["future_hour_sin"].shape == (4,)
    assert sample["future_hour_cos"].shape == (4,)


def test_weather_rollout_dataset_split_by_month_invalid_month_raises_error(
    dummy_npz_file, dummy_static_tensor
):
    """Test split_by_month raises ValueError when requesting a month not present in dataset."""
    dataset = WeatherRolloutDataset(
        npz_paths=[dummy_npz_file],
        static_tensor=dummy_static_tensor,
        raw_normalizer=DummyNormalizer(),
        delta_normalizer=DummyNormalizer(),
    )

    # Data is only in January. Requesting month 12 should fail.
    with pytest.raises(ValueError, match="matched no samples"):
        dataset.split_by_month(val_months={12})


def test_tf_p_for_epoch_start_returns_start_value():
    """Test that at epoch 0, the teacher forcing probability is exactly tf_p_start."""
    cfg = TrainConfig(tf_p_start=1.0, tf_p_end=0.0, tf_p_anneal_epochs=10)
    result = tf_p_for_epoch(0, cfg)
    assert pytest.approx(result, abs=1e-4) == 1.0


def test_tf_p_for_epoch_midpoint_returns_interpolated_value():
    """Test that halfway through the anneal schedule, the probability is perfectly split."""
    cfg = TrainConfig(tf_p_start=1.0, tf_p_end=0.0, tf_p_anneal_epochs=10)
    result = tf_p_for_epoch(5, cfg)
    assert pytest.approx(result, abs=1e-4) == 0.5


def test_tf_p_for_epoch_after_anneal_returns_end_value():
    """Test that after the anneal epochs have passed, the probability clamps to tf_p_end."""
    cfg = TrainConfig(tf_p_start=1.0, tf_p_end=0.0, tf_p_anneal_epochs=10)
    result = tf_p_for_epoch(15, cfg)
    assert pytest.approx(result, abs=1e-4) == 0.0


class DummyWeatherDeltaModel(nn.Module):
    """dummy model to test the training loop without loading ConvLSTM."""

    def __init__(self):
        super().__init__()
        # single trainable parameter so we can check backpropagation
        self.dummy_layer = nn.Linear(1, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C, H, W = x.shape
        # Return a tensor matching the expected future deltas shape: (B, 4, H, W)
        base_output = torch.zeros((B, 4, H, W), device=x.device)
        return base_output + self.dummy_layer(torch.zeros(1, device=x.device))[0]


class DummyStats:
    def __init__(self, channels: int):
        self.mean = np.zeros(channels, dtype=np.float32)
        self.std = np.ones(channels, dtype=np.float32)


class DummyNorm:
    def __init__(self, channels: int):
        self.stats = DummyStats(channels)


@pytest.fixture
def dummy_train_batch():
    """Generates a perfectly shaped tensor payload imitating a DataLoader batch."""
    B, T, H, W = 2, 6, 8, 8
    return {
        "input_seq": torch.zeros((B, T, 10, H, W), dtype=torch.float32),
        "anchor_dynamic_raw": torch.zeros((B, 4, H, W), dtype=torch.float32),
        "future_dynamic_raw": torch.zeros(
            (B, 4, 4, H, W), dtype=torch.float32
        ),  # (B, Rollout, Vars, H, W)
        "future_deltas_norm": torch.zeros((B, 4, 4, H, W), dtype=torch.float32),
        "future_hour_sin": torch.zeros((B, 4), dtype=torch.float32),
        "future_hour_cos": torch.zeros((B, 4), dtype=torch.float32),
    }


def test_trainer_train_epoch_updates_model_parameters(dummy_train_batch):
    """Test that running a training epoch successfully executes backpropagation and updates weights."""
    cfg = TrainConfig(device="cpu", rollout_steps=4, epochs=1)
    model = DummyWeatherDeltaModel()
    static_tensor = np.zeros((4, 8, 8), dtype=np.float32)

    # Mock data loaders that yield exactly one batch
    train_loader = [dummy_train_batch]
    val_loader = []

    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        static_tensor=static_tensor,
        raw_normalizer=DummyNorm(channels=10),  # FIX: 10 channels for raw inputs
        delta_normalizer=DummyNorm(channels=4),  # FIX: 4 channels for deltas
        cfg=cfg,
    )
    # Capture the weight of the dummy parameter before training
    param_before = model.dummy_layer.weight.clone()
    # We modify the target slightly so the loss isn't zero (forcing a gradient)
    dummy_train_batch["future_deltas_norm"] += 1.0
    loss = trainer.train_epoch(epoch=0)
    # Capture the weight after training
    param_after = model.dummy_layer.weight.clone()
    assert loss > 0.0
    # If backprop was successful, the optimizer should have shifted the weights
    assert not torch.equal(param_before, param_after)


def test_trainer_validate_epoch_computes_metrics_without_crashing(dummy_train_batch):
    """Test that the validation loop correctly executes inference and returns metric dictionaries."""
    cfg = TrainConfig(device="cpu", rollout_steps=4, epochs=1)
    model = DummyWeatherDeltaModel()
    static_tensor = np.zeros((4, 8, 8), dtype=np.float32)

    train_loader = []
    val_loader = [dummy_train_batch]  # Inject the batch into the validation loader

    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        static_tensor=static_tensor,
        raw_normalizer=DummyNorm(channels=10),  # FIX: 10 channels for raw inputs
        delta_normalizer=DummyNorm(channels=4),  # FIX: 4 channels for deltas
        cfg=cfg,
    )
    val_loss, val_metrics = trainer.validate_epoch()

    assert val_loss >= 0.0
    # Validate the dictionary structure returned by MetricTracker
    assert isinstance(val_metrics, dict)
    assert "wind_u" in val_metrics
