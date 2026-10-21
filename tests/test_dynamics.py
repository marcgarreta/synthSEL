import numpy as np

from synthsel.dynamics import grow_concentric, sel_trajectory, shrink
from synthsel.synthesis import ellipsoid_mask

SHAPE = (40, 40, 40)
CENTER = (20, 20, 20)


def test_grow_matches_larger_sphere():
    # tiny spheres suffer from voxel discretisation, so use a reasonably sized one
    grown = grow_concentric(ellipsoid_mask(SHAPE, CENTER, (8, 8, 8)), 3.0)
    target = ellipsoid_mask(SHAPE, CENTER, (11, 11, 11))
    assert abs(int(grown.sum()) - int(target.sum())) / target.sum() < 0.1


def test_grow_contains_original():
    mask = ellipsoid_mask(SHAPE, CENTER, (4, 4, 4))
    assert np.all(grow_concentric(mask, 1.5)[mask])


def test_grow_noop_cases():
    mask = ellipsoid_mask(SHAPE, CENTER, (4, 4, 4))
    np.testing.assert_array_equal(grow_concentric(mask, 0), mask)
    assert not grow_concentric(np.zeros(SHAPE, bool), 3).any()


def test_grow_constraint():
    mask = ellipsoid_mask(SHAPE, CENTER, (4, 4, 4))
    constraint = np.zeros(SHAPE, bool)
    constraint[:, :, :20] = True
    grown = grow_concentric(mask, 3, constraint=constraint)
    assert not (grown & ~constraint & ~mask).any()


def test_shrink():
    mask = ellipsoid_mask(SHAPE, CENTER, (6, 6, 6))
    small = shrink(mask, 2)
    assert small.sum() < mask.sum()
    assert np.all(mask[small])
    np.testing.assert_array_equal(shrink(mask, 0), mask)


def test_sel_trajectory_monotonic():
    traj = sel_trajectory(ellipsoid_mask(SHAPE, CENTER, (3, 3, 3)), rate_mm=1.0, n_steps=3)
    volumes = [m.sum() for m in traj]
    assert len(traj) == 4
    assert all(a < b for a, b in zip(volumes, volumes[1:], strict=False))
