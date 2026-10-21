"""Heuristic lesion insertion (Chard / Battaglini style baseline).

The lesion is painted into the image with a target intensity and a Gaussian
soft edge so it blends with the surrounding tissue. It is the simplest
level-1 baseline against which CarveMix or diffusion models are compared.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


def insert_lesion(
    image: np.ndarray,
    lesion_mask: np.ndarray,
    intensity: float,
    sigma: float = 1.0,
    noise_std: float = 0.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Return a copy of ``image`` with a hyperintense lesion inside ``lesion_mask``.

    Args:
        image: normalised FLAIR volume.
        lesion_mask: boolean mask of the lesion.
        intensity: target lesion intensity (same scale as ``image``).
        sigma: Gaussian blur (voxels) applied to the mask edge; 0 gives a hard edge.
        noise_std: std of Gaussian texture noise added inside the lesion.
        rng: random generator for the noise.
    """
    weight = lesion_mask.astype(np.float32)
    if sigma > 0:
        weight = np.clip(gaussian_filter(weight, sigma), 0.0, 1.0)

    lesion = np.full_like(image, intensity, dtype=np.float32)
    if noise_std > 0:
        rng = rng or np.random.default_rng()
        lesion += rng.normal(0.0, noise_std, size=image.shape).astype(np.float32)

    return (1.0 - weight) * image + weight * lesion
