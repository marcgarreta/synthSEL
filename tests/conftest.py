import numpy as np
import pytest


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.fixture
def phantom():
    """32^3 toy 'brain': a sphere of intensity 0.5 with a smaller 'WM' core."""
    shape = (32, 32, 32)
    grid = np.indices(shape) - 15.5
    radius = np.sqrt((grid**2).sum(axis=0))
    brain = radius < 14
    wm = radius < 9
    image = np.where(brain, 0.5, 0.0).astype(np.float32)
    return image, brain, wm
