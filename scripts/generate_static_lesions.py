"""Exp001: insert heuristic ellipsoid lesions into a FLAIR volume.

Usage:
    uv run python scripts/generate_static_lesions.py configs/exp001_static_spheres.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from synthsel.config import load_config
from synthsel.io import load_nifti, save_nifti, voxel_spacing
from synthsel.preprocessing import normalize_intensity
from synthsel.synthesis import ellipsoid_mask, insert_lesion, sample_center


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    cfg = load_config(parser.parse_args().config)
    rng = np.random.default_rng(cfg["seed"])

    image, affine = load_nifti(cfg["input"]["flair"])
    region, _ = load_nifti(cfg["input"]["region_mask"])
    region = region > 0
    spacing = voxel_spacing(affine)
    image = normalize_intensity(image, mask=region)

    lcfg = cfg["lesions"]
    lesion_mask = np.zeros(image.shape, dtype=bool)
    for _ in range(lcfg["n"]):
        radii = rng.uniform(lcfg["radius_mm"][0], lcfg["radius_mm"][1], size=3)
        mask = ellipsoid_mask(image.shape, sample_center(region, rng), radii, spacing) & region
        image = insert_lesion(image, mask, lcfg["intensity"], lcfg["sigma"], lcfg["noise_std"], rng)
        lesion_mask |= mask

    out = Path(cfg["output_dir"]) / cfg["name"]
    save_nifti(image, affine, out / "flair_synth.nii.gz")
    save_nifti(lesion_mask, affine, out / "lesion_mask.nii.gz")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
