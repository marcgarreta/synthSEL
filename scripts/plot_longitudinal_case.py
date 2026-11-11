"""Figure: baseline vs follow-up 3D FLAIR of one MSSEG2 patient with new lesions highlighted.

Rows are axial / coronal / sagittal slices through the centroid of the largest new lesion.
The default layout shows baseline and follow-up, with arrowheads on the new lesions in the
follow-up;
``--layout overlay`` fills the ground truth in red on the follow-up instead;
``--layout full`` adds the follow-up with the new-lesion contour and the follow-up minus
baseline difference.

Usage:
    uv run --extra viz python scripts/plot_longitudinal_case.py --patient 069
    uv run --extra viz python scripts/plot_longitudinal_case.py --patient 069 --layout overlay
    uv run --extra viz python scripts/plot_longitudinal_case.py --patient 069 --layout full
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap, Normalize
from scipy import ndimage

from synthsel.preprocessing import normalize_intensity

LESION_COLOR = "#F76707"
ARROW_COLOR = "#FCC419"
GT_FILL = ListedColormap(["#E03131"])
# Diverging blue-black-red: dark midpoint so unchanged tissue blends with the black figure.
DIFF_CMAP = plt.get_cmap("berlin").with_extremes(bad="black")
DIFF_NORM = Normalize(vmin=-0.5, vmax=0.5)
VIEWS = ("Axial", "Coronal", "Sagittal")


def load_canonical(path: Path) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Load a volume reoriented to RAS so slicing axes match anatomical views."""
    img = nib.as_closest_canonical(nib.load(str(path)))
    return np.asarray(img.get_fdata(dtype=np.float32)), tuple(img.header.get_zooms()[:3])


def take_slice(vol: np.ndarray, view: int, center: np.ndarray) -> np.ndarray:
    """Slice through ``center`` and rotate so anterior/superior point up."""
    if view == 0:
        sl = vol[:, :, center[2]]
    elif view == 1:
        sl = vol[:, center[1], :]
    else:
        sl = vol[center[0], :, :]
    return np.rot90(sl)


def view_aspect(view: int, zooms: tuple[float, float, float]) -> float:
    """Pixel aspect (row spacing / column spacing) of a rotated slice."""
    rows, cols = {0: (1, 0), 1: (2, 0), 2: (2, 1)}[view]
    return zooms[rows] / zooms[cols]


def head_mask(image: np.ndarray, threshold: float = 0.08) -> np.ndarray:
    """Rough foreground mask: smoothed threshold, largest component, holes filled."""
    mask = ndimage.gaussian_filter(image, sigma=2) > threshold
    labels, n = ndimage.label(mask)  # type: ignore[misc]
    if n > 1:
        sizes = ndimage.sum(mask, labels, range(1, n + 1))
        mask = labels == int(np.argmax(sizes)) + 1
    return np.asarray(ndimage.binary_fill_holes(mask), dtype=bool)


def add_arrows(ax: Axes, mask2d: np.ndarray, aspect: float, min_area: int = 10) -> None:
    """Point an arrowhead at each lesion in the slice, coming from outside the brain.

    The tip stops just short of the lesion edge so the lesion itself stays unobscured.
    Distances are computed in display units (rows are stretched by ``aspect``).
    """
    labels, n = ndimage.label(mask2d)  # type: ignore[misc]
    img_center = np.array([mask2d.shape[0] * aspect, mask2d.shape[1]]) / 2
    for lab in range(1, n + 1):
        comp = labels == lab
        area = comp.sum()
        if area < min_area:
            continue
        r, c = (float(v) for v in ndimage.center_of_mass(comp))
        pos = np.array([r * aspect, c])
        direction = pos - img_center
        norm = np.linalg.norm(direction)
        u = direction / norm if norm > 0 else np.array([-1.0, -1.0]) / np.sqrt(2)
        reach = np.sqrt(area * aspect / np.pi) + 4
        tip_row, tip_col = (pos + u * reach) / np.array([aspect, 1.0])
        ax.annotate(
            "",
            xy=(tip_col, tip_row),
            xytext=(u[1] * 22, -u[0] * 22),
            textcoords="offset points",
            arrowprops={"arrowstyle": "-|>", "color": ARROW_COLOR, "lw": 1.6, "mutation_scale": 12},
        )


def brain_bbox(mask2d: np.ndarray, pad: int = 6) -> tuple[slice, slice]:
    rr, cc = np.nonzero(mask2d)
    return (
        slice(max(rr.min() - pad, 0), rr.max() + pad + 1),
        slice(max(cc.min() - pad, 0), cc.max() + pad + 1),
    )


def style_axis(ax: Axes) -> None:
    ax.set_facecolor("black")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def plot_per_lesion(
    t1: np.ndarray,
    t2: np.ndarray,
    gt: np.ndarray,
    head: np.ndarray,
    labels: np.ndarray,
    n_lesions: int,
    zooms: tuple[float, float, float],
):
    """One column per new lesion (largest first): axial slice where that lesion is largest."""
    sizes = ndimage.sum(gt, labels, range(1, n_lesions + 1))
    order = np.argsort(sizes)[::-1] + 1
    voxel_mm3 = float(np.prod(zooms))
    aspect = view_aspect(0, zooms)

    fig, axes = plt.subplots(
        2, n_lesions, figsize=(3.2 * n_lesions, 6.6), facecolor="black", squeeze=False
    )
    for col, lab in enumerate(order):
        comp = labels == lab
        z = int(np.argmax(comp.sum(axis=(0, 1))))
        center = np.array([0, 0, z])
        crop = brain_bbox(take_slice(head, 0, center))
        b, f = take_slice(t1, 0, center)[crop], take_slice(t2, 0, center)[crop]
        m = take_slice(gt, 0, center)[crop]
        axes[0, col].imshow(b, cmap="gray", vmin=0, vmax=1, aspect=aspect)
        axes[1, col].imshow(f, cmap="gray", vmin=0, vmax=1, aspect=aspect)
        axes[1, col].imshow(np.ma.masked_where(~m, m), cmap=GT_FILL, alpha=0.85, aspect=aspect)
        axes[0, col].set_title(
            f"Lesion {col + 1} · {comp.sum() * voxel_mm3:.0f} mm³", color="white", fontsize=11
        )
        for ax in axes[:, col]:
            style_axis(ax)
    axes[0, 0].set_ylabel("Baseline (t1)", color="white", fontsize=11)
    axes[1, 0].set_ylabel("Follow-up (t2)", color="white", fontsize=11)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patient", default="069")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw/MSSEG2/training-v2"))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--layout",
        choices=("arrows", "overlay", "lesions", "full"),
        default="arrows",
        help=(
            "arrows: baseline | follow-up with arrowheads; overlay: follow-up with the"
            " ground truth filled in red; lesions: one axial slice per new lesion, red"
            " ground truth; full: adds contour and difference"
        ),
    )
    parser.add_argument(
        "--orientation",
        choices=("horizontal", "vertical"),
        default="horizontal",
        help="horizontal: one row per timepoint; vertical: one row per anatomical view",
    )
    args = parser.parse_args()

    case = args.data_dir / args.patient
    t1, zooms = load_canonical(case / "flair_time01_on_middle_space.nii.gz")
    t2, _ = load_canonical(case / "flair_time02_on_middle_space.nii.gz")
    gt, _ = load_canonical(case / "ground_truth.nii.gz")
    gt = gt > 0

    t1 = normalize_intensity(t1, mask=(t1 > 0) & (t2 > 0))
    t2 = normalize_intensity(t2, mask=(t1 > 0) & (t2 > 0))
    head = head_mask(t1) & head_mask(t2)
    diff = np.where(head, t2 - t1, np.nan)

    labels, n_lesions = ndimage.label(gt)  # type: ignore[misc]
    if n_lesions == 0:
        # Stable patient: no new lesions, so slice through the centre of the head instead.
        print(f"Patient {args.patient} has no new lesions; slicing through the head centre.")
        center = np.round(ndimage.center_of_mass(head)).astype(int)
    else:
        sizes = ndimage.sum(gt, labels, range(1, n_lesions + 1))
        largest = int(np.argmax(sizes)) + 1
        center = np.round(ndimage.center_of_mass(labels == largest)).astype(int)

    suffix = {"arrows": "", "overlay": "_overlay", "lesions": "_lesions", "full": "_full"}
    default_out = Path("thesis/figures") / (
        f"msseg2_{args.patient}_longitudinal{suffix[args.layout]}.png"
    )
    out = args.out or default_out
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.layout == "lesions":
        if n_lesions == 0:
            raise ValueError(f"Patient {args.patient} has no new lesions to show.")
        fig = plot_per_lesion(t1, t2, gt, head, labels, n_lesions, zooms)
        fig.savefig(out, dpi=300, facecolor="black", bbox_inches="tight")
        fig.savefig(out.with_suffix(".pdf"), facecolor="black", bbox_inches="tight")
        print(f"Saved to {out} (+ .pdf)")
        return

    full = args.layout == "full"
    horizontal = args.orientation == "horizontal"
    n_panels = 4 if full else 2
    if horizontal:
        fig, axes = plt.subplots(n_panels, 3, figsize=(9.6, 3.3 * n_panels), facecolor="black")
        axes = axes.T  # index as [view, panel] in both orientations
    else:
        fig, axes = plt.subplots(3, n_panels, figsize=(3 * n_panels, 9.6), facecolor="black")
    titles = ("Baseline (t1)", "Follow-up (t2)", "Follow-up + new lesions", "Difference (t2 − t1)")
    for view in range(3):
        crop = brain_bbox(take_slice(head, view, center))
        aspect = view_aspect(view, zooms)
        b, f = take_slice(t1, view, center)[crop], take_slice(t2, view, center)[crop]
        d, m = take_slice(diff, view, center)[crop], take_slice(gt, view, center)[crop]
        for col, ax in enumerate(axes[view]):
            if col < 3:
                ax.imshow(b if col == 0 else f, cmap="gray", vmin=0, vmax=1, aspect=aspect)
            else:
                ax.imshow(d, cmap=DIFF_CMAP, norm=DIFF_NORM, aspect=aspect)
            if full and col >= 2 and m.any():
                color, width = (LESION_COLOR, 1.2) if col == 2 else ("white", 0.6)
                ax.contour(m, levels=[0.5], colors=color, linewidths=width)
            if args.layout == "arrows" and col == 1:
                add_arrows(ax, m, aspect)
            if args.layout == "overlay" and col == 1 and m.any():
                ax.imshow(np.ma.masked_where(~m, m), cmap=GT_FILL, alpha=0.85, aspect=aspect)
            ax.set_facecolor("black")
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            top, left = (VIEWS[view], titles[col]) if horizontal else (titles[col], VIEWS[view])
            if (col if horizontal else view) == 0:
                ax.set_title(top, color="white", fontsize=11)
            if (view if horizontal else col) == 0:
                ax.set_ylabel(left, color="white", fontsize=11)

    if full:
        sm = plt.cm.ScalarMappable(norm=DIFF_NORM, cmap=DIFF_CMAP)
        cbar = fig.colorbar(
            sm,
            ax=axes[:, 3],
            location="bottom" if horizontal else "right",
            fraction=0.046,
            pad=0.02,
            shrink=0.6,
        )
        cbar.set_label("Normalised intensity change", color="white")
        cbar.ax.tick_params(colors="white")
        cbar.outline.set_visible(False)
    fig.savefig(out, dpi=300, facecolor="black", bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), facecolor="black", bbox_inches="tight")
    print(f"Saved to {out} (+ .pdf)")


if __name__ == "__main__":
    main()
