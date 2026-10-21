"""NIfTI input/output helpers."""

from __future__ import annotations

from pathlib import Path

import nibabel as nib
import numpy as np


def load_nifti(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a NIfTI volume and return ``(data, affine)``."""
    img = nib.load(str(path))
    return np.asarray(img.get_fdata(dtype=np.float32)), img.affine


def save_nifti(data: np.ndarray, affine: np.ndarray, path: str | Path) -> Path:
    """Save ``data`` as NIfTI, creating parent folders if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if data.dtype == bool:
        data = data.astype(np.uint8)
    nib.save(nib.Nifti1Image(data, affine), str(path))
    return path


def voxel_spacing(affine: np.ndarray) -> tuple[float, float, float]:
    """Voxel size in mm along each axis."""
    return tuple(float(s) for s in np.linalg.norm(affine[:3, :3], axis=0))


def voxel_volume(affine: np.ndarray) -> float:
    """Voxel volume in mm^3."""
    return float(abs(np.linalg.det(affine[:3, :3])))
