import numpy as np
import pytest

from synthsel.preprocessing import normalize_intensity


def test_range_is_unit(rng):
    image = rng.normal(100, 20, size=(10, 10, 10)).clip(1)
    out = normalize_intensity(image)
    assert out.min() == 0.0 and out.max() == 1.0


def test_uses_mask():
    image = np.zeros((4, 4, 4))
    image[:2] = np.arange(32).reshape(2, 4, 4) + 1.0
    image[2:] = 1000.0  # outlier region outside the mask
    mask = np.zeros_like(image)
    mask[:2] = 1
    out = normalize_intensity(image, mask=mask)
    assert np.all(out[2:] == 1.0)


def test_constant_image_returns_zeros():
    assert not normalize_intensity(np.ones((3, 3, 3))).any()


def test_empty_raises():
    with pytest.raises(ValueError):
        normalize_intensity(np.zeros((3, 3, 3)))
