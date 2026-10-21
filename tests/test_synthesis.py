import numpy as np
import pytest

from synthsel.synthesis import ellipsoid_mask, insert_lesion, sample_center


def test_ellipsoid_volume_close_to_analytic():
    mask = ellipsoid_mask((40, 40, 40), (20, 20, 20), (8, 6, 4))
    expected = 4 / 3 * np.pi * 8 * 6 * 4
    assert mask.sum() == pytest.approx(expected, rel=0.05)


def test_ellipsoid_respects_spacing():
    iso = ellipsoid_mask((40, 40, 40), (20, 20, 20), (6, 6, 6))
    aniso = ellipsoid_mask((40, 40, 40), (20, 20, 20), (6, 6, 6), spacing=(1, 1, 2))
    assert aniso.sum() == pytest.approx(iso.sum() / 2, rel=0.1)


def test_sample_center_inside_region(phantom, rng):
    _, _, wm = phantom
    for _ in range(20):
        assert wm[sample_center(wm, rng)]


def test_sample_center_empty_raises(rng):
    with pytest.raises(ValueError):
        sample_center(np.zeros((3, 3, 3), bool), rng)


def test_insert_lesion_hard_edge(phantom):
    image, _, _ = phantom
    mask = ellipsoid_mask(image.shape, (16, 16, 16), (3, 3, 3))
    out = insert_lesion(image, mask, intensity=0.9, sigma=0)
    np.testing.assert_allclose(out[mask], 0.9)
    np.testing.assert_array_equal(out[~mask], image[~mask])


def test_insert_lesion_soft_edge_is_hyperintense(phantom, rng):
    image, _, _ = phantom
    mask = ellipsoid_mask(image.shape, (16, 16, 16), (4, 4, 4))
    out = insert_lesion(image, mask, intensity=0.9, sigma=1.0, noise_std=0.01, rng=rng)
    assert out[mask].mean() > image[mask].mean()
    assert out[0, 0, 0] == pytest.approx(image[0, 0, 0])  # far voxels untouched
    assert image.max() == 0.5  # input not modified in place
