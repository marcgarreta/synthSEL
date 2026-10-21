"""Intensity preprocessing for FLAIR volumes."""

from __future__ import annotations

import numpy as np


def normalize_intensity(
    image: np.ndarray,
    mask: np.ndarray | None = None,
    lower: float = 1.0,
    upper: float = 99.0,
) -> np.ndarray:
    """Percentile-based min-max normalisation to [0, 1].

    Percentiles are computed inside ``mask`` (or on non-zero voxels if no mask
    is given), which avoids the background dominating the statistics.
    """
    values = image[mask > 0] if mask is not None else image[image > 0]
    if values.size == 0:
        raise ValueError("No voxels available to compute normalisation statistics.")
    lo, hi = np.percentile(values, [lower, upper])
    if hi <= lo:
        return np.zeros_like(image, dtype=np.float32)
    return np.clip((image - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)
