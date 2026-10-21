"""Overlap, lesion-count and per-lesion volume-change metrics."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import generate_binary_structure, label

# 26-connectivity, the usual choice for counting 3D lesions
_STRUCTURE = generate_binary_structure(3, 3)


def dice(a: np.ndarray, b: np.ndarray) -> float:
    """Dice coefficient; 1.0 when both masks are empty."""
    a, b = a.astype(bool), b.astype(bool)
    total = a.sum() + b.sum()
    if total == 0:
        return 1.0
    return float(2.0 * np.logical_and(a, b).sum() / total)


def label_lesions(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Connected components of a binary lesion mask."""
    labels, n = label(mask.astype(bool), structure=_STRUCTURE)
    return labels, int(n)


def lesion_count(mask: np.ndarray) -> int:
    return label_lesions(mask)[1]


def lesion_volumes(mask: np.ndarray, voxel_volume: float = 1.0) -> dict[int, float]:
    """Volume (mm^3) of each connected lesion, keyed by label."""
    labels, n = label_lesions(mask)
    counts = np.bincount(labels.ravel(), minlength=n + 1)
    return {i: float(counts[i] * voxel_volume) for i in range(1, n + 1)}


def per_lesion_volume_change(
    baseline: np.ndarray, followup: np.ndarray, voxel_volume: float = 1.0
) -> dict[int, dict[str, float]]:
    """Volume change of each baseline lesion at follow-up.

    Each baseline lesion is matched to every follow-up component it overlaps.
    Note that under confluence several baseline lesions share the same
    follow-up component; for synthetic data the true identity is known and
    should be preferred.
    """
    base_labels, n = label_lesions(baseline)
    follow_labels, _ = label_lesions(followup)
    result: dict[int, dict[str, float]] = {}
    for i in range(1, n + 1):
        region = base_labels == i
        v0 = float(region.sum() * voxel_volume)
        matched = np.unique(follow_labels[region])
        matched = matched[matched > 0]
        v1 = float(np.isin(follow_labels, matched).sum() * voxel_volume)
        result[i] = {"v0": v0, "v1": v1, "abs_change": v1 - v0, "rel_change": (v1 - v0) / v0}
    return result
