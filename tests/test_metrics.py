import numpy as np
import pytest

from synthsel.dynamics import grow_concentric
from synthsel.evaluation import (
    dice,
    lesion_count,
    lesion_volumes,
    per_lesion_volume_change,
)
from synthsel.synthesis import ellipsoid_mask

SHAPE = (40, 40, 40)


def two_lesions():
    return ellipsoid_mask(SHAPE, (10, 20, 20), (3, 3, 3)) | ellipsoid_mask(
        SHAPE, (30, 20, 20), (3, 3, 3)
    )


def test_dice():
    a = two_lesions()
    assert dice(a, a) == 1.0
    assert dice(a, np.zeros_like(a)) == 0.0
    assert dice(np.zeros_like(a), np.zeros_like(a)) == 1.0


def test_count_and_volumes():
    mask = two_lesions()
    assert lesion_count(mask) == 2
    vols = lesion_volumes(mask, voxel_volume=2.0)
    assert set(vols) == {1, 2}
    assert sum(vols.values()) == pytest.approx(2.0 * mask.sum())


def test_per_lesion_change_detects_growth():
    base = two_lesions()
    lesion_a = ellipsoid_mask(SHAPE, (10, 20, 20), (3, 3, 3))
    follow = (base & ~lesion_a) | grow_concentric(lesion_a, 2)
    change = per_lesion_volume_change(base, follow)
    assert change[1]["rel_change"] > 0.5  # grown lesion
    assert change[2]["rel_change"] == pytest.approx(0.0)  # stable lesion


def test_per_lesion_change_disappearing_lesion():
    base = two_lesions()
    change = per_lesion_volume_change(base, np.zeros_like(base))
    assert all(c["rel_change"] == -1.0 for c in change.values())
