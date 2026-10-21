"""Mask-level lesion dynamics.

SELs expand concentrically and at a constant rate (Elliott et al., 2019), so
growth is modelled as an isotropic dilation measured in mm with a Euclidean
distance transform, which respects anisotropic voxel spacing.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.ndimage import distance_transform_edt


def grow_concentric(
    mask: np.ndarray,
    distance_mm: float,
    spacing: Sequence[float] = (1.0, 1.0, 1.0),
    constraint: np.ndarray | None = None,
) -> np.ndarray:
    """Expand ``mask`` by ``distance_mm`` in every direction.

    ``constraint`` (e.g. a white-matter mask) limits where the lesion may grow.
    """
    mask = mask.astype(bool)
    if distance_mm <= 0 or not mask.any():
        return mask.copy()
    dist = distance_transform_edt(~mask, sampling=spacing)
    grown = mask | (dist <= distance_mm)
    if constraint is not None:
        grown &= constraint.astype(bool) | mask
    return grown


def shrink(
    mask: np.ndarray, distance_mm: float, spacing: Sequence[float] = (1.0, 1.0, 1.0)
) -> np.ndarray:
    """Erode ``mask`` by ``distance_mm`` (lesion reduction)."""
    mask = mask.astype(bool)
    if distance_mm <= 0:
        return mask.copy()
    return distance_transform_edt(mask, sampling=spacing) > distance_mm


def sel_trajectory(
    mask: np.ndarray,
    rate_mm: float,
    n_steps: int,
    spacing: Sequence[float] = (1.0, 1.0, 1.0),
    constraint: np.ndarray | None = None,
) -> list[np.ndarray]:
    """Masks for a SEL growing ``rate_mm`` per time step; index 0 is the baseline."""
    return [grow_concentric(mask, rate_mm * t, spacing, constraint) for t in range(n_steps + 1)]
