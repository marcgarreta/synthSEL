"""Prescribed lesion masks (shape and position control)."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def ellipsoid_mask(
    shape: Sequence[int],
    center: Sequence[float],
    radii: Sequence[float],
    spacing: Sequence[float] = (1.0, 1.0, 1.0),
) -> np.ndarray:
    """Boolean ellipsoid of ``radii`` (mm) centred at ``center`` (voxel coords)."""
    grids = np.ogrid[tuple(slice(0, s) for s in shape)]
    dist = sum(
        ((g - c) * sp / r) ** 2 for g, c, r, sp in zip(grids, center, radii, spacing, strict=True)
    )
    return dist <= 1.0


def sample_center(region: np.ndarray, rng: np.random.Generator) -> tuple[int, ...]:
    """Pick a random voxel inside ``region`` (e.g. a white-matter mask)."""
    candidates = np.argwhere(region)
    if len(candidates) == 0:
        raise ValueError("Region mask is empty; cannot sample a lesion centre.")
    return tuple(int(v) for v in candidates[rng.integers(len(candidates))])
