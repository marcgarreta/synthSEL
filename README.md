# synthSEL

[![license](https://img.shields.io/badge/license-MIT-c6a925)](LICENSE)
[![python](https://img.shields.io/badge/python-3.14-3776ab?logo=python&logoColor=white)](pyproject.toml)
[![tests](https://img.shields.io/github/actions/workflow/status/marcgarreta/synthSEL/ci.yml?branch=main&label=tests&logo=github)](https://github.com/marcgarreta/synthSEL/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/codecov/c/github/marcgarreta/synthSEL?logo=codecov&label=codecov)](https://codecov.io/gh/marcgarreta/synthSEL)
[![brewing at](https://img.shields.io/badge/brewing%20at-MSc%20Data%20Science%20UOC-2f7fbf)](https://www.uoc.edu)

Synthetic generation of **MS lesions in 3D FLAIR MRI**, with the long-term aim of detecting
**slowly expanding lesions (SEL)**. The current scope is **lesion synthesis only**: lesions are
inserted into real FLAIR scans, and no whole-image generation is planned. This is the code for the TFM *"Generació sintètica de lesions dinàmiques en
ressonància magnètica per a la detecció de lesions d'expansió lenta en esclerosi múltiple"*
(MSc Data Science, UOC). Supervisor: Eloy Martinez-Heras.

## Project structure

```
synthSEL/
├── src/synthsel/          # reusable, tested library code
│   ├── io.py              # NIfTI load/save, voxel spacing/volume
│   ├── preprocessing.py   # intensity normalisation
│   ├── config.py          # YAML experiment configs
│   ├── synthesis/         # lesion masks + insertion
│   ├── dynamics/          # (later) growth / shrinkage / SEL trajectories
│   ├── atrophy/           # (later) deformation-based atrophy
│   └── evaluation/        # Dice, lesion count
├── scripts/               # thin CLI entry points, one per experiment
├── configs/               # one YAML per experiment (expNNN_*.yaml)
├── tests/                 # pytest unit tests (synthetic phantoms, no real data)
├── data/                  # local only, git-ignored (raw/interim/processed/synthetic)
├── docs/                  # notes, references
└── thesis/                # LaTeX report + figures
```

Workflow: write reusable code in `src/synthsel/` with tests → run it via `scripts/` + `configs/`
→ figures in `thesis/figures/`.

## Setup

Uses [uv](https://docs.astral.sh/uv/). Python is pinned to **3.14** (see `.python-version`) for reproducibility, and `uv.lock` pins every
dependency. CI runs the same version.

```bash
uv sync                      # core + dev dependencies
uv sync --extra dl           # + PyTorch / MONAI (diffusion models)
uv sync --extra viz          # + matplotlib / jupyter
```

## Usage

```bash
make test        # unit tests
make cov         # tests + coverage report (htmlcov/index.html)
make lint        # ruff lint + format check
make format      # auto-fix

# Experiment 001: heuristic lesions (edit the input paths in the config first)
uv run python scripts/generate_static_lesions.py configs/exp001_static_spheres.yaml
```

## Testing and coverage

- Tests use small synthetic phantoms, so they run fast in CI without patient data.
- Tests that need real data or a GPU go under `@pytest.mark.slow`, which CI skips.
- GitHub Actions runs ruff + pytest on Python 3.14 and uploads coverage to Codecov.
  Add a `CODECOV_TOKEN` repository secret (Codecov → repo settings).

## Data

IDIBAPS data is confidential and **never committed**. `data/` and all `*.nii*` files are
git-ignored. See [`data/README.md`](data/README.md).

## License

Released under the [MIT License](LICENSE). The license covers the code only, not the IDIBAPS data.
