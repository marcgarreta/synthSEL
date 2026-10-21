import numpy as np
import pytest

from synthsel.io import load_nifti, save_nifti, voxel_spacing, voxel_volume


def test_roundtrip(tmp_path):
    data = np.arange(24, dtype=np.float32).reshape(2, 3, 4)
    affine = np.diag([1.0, 1.0, 2.0, 1.0])
    path = save_nifti(data, affine, tmp_path / "sub" / "img.nii.gz")
    loaded, loaded_affine = load_nifti(path)
    np.testing.assert_array_equal(loaded, data)
    np.testing.assert_array_equal(loaded_affine, affine)


def test_bool_saved_as_uint8(tmp_path):
    mask = np.zeros((4, 4, 4), dtype=bool)
    mask[1, 1, 1] = True
    loaded, _ = load_nifti(save_nifti(mask, np.eye(4), tmp_path / "m.nii.gz"))
    assert loaded.sum() == 1


def test_spacing_and_volume():
    affine = np.diag([0.5, 1.0, 3.0, 1.0])
    assert voxel_spacing(affine) == (0.5, 1.0, 3.0)
    assert voxel_volume(affine) == pytest.approx(1.5)
