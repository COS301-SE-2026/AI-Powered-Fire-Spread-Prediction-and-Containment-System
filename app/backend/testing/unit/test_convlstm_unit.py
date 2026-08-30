import pytest
import torch
from app.ml.training.losses import SmoothL1DeltaLoss
from app.ml.traing.metrics import MetricTracker
#First I test the loss function, then the metrics
def test_smooth_l1_delta_loss_initialization():
    """ Tests default and custom beta initialization"""
    #test defualt
    loss_default = SmoothL1DeltaLoss()
    assert loss_default.loss_fn.beta == 1.0
    #test custom
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
    loss_fn =SmoothL1DeltaLoss(beta)
    #we make the error be 0.5<beta
    pred = torch.tensor([1.5])
    target =torch.tensor([1.0])
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
    variables =["temp", "humid" ]
    num_steps = 3
    tracker =MetricTracker(variables =variables, num_steps = num_steps)
    assert tracker.variables ==variables
    assert tracker.num_steps ==num_steps
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