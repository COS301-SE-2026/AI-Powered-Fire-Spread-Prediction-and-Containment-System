import pytest
import torch
from app.ml.training.losses import SmoothL1DeltaLoss
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
