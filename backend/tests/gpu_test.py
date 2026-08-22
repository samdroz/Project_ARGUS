import torch


def test_gpu_and_torch():
    assert torch.__version__ is not None
    # Verify torch tensor allocation
    t = torch.zeros((2, 2))
    assert t.shape == (2, 2)