# synthSEL

[![CI](https://github.com/marcgarreta/synthSEL/actions/workflows/ci.yml/badge.svg)](https://github.com/marcgarreta/synthSEL/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/marcgarreta/synthSEL/branch/main/graph/badge.svg)](https://codecov.io/gh/marcgarreta/synthSEL)

Synthetic generation of **dynamic MS lesions in 3D FLAIR MRI** for detecting **slowly expanding
lesions (SEL)**. This is the code for the TFM *"Generació sintètica de lesions dinàmiques en
ressonància magnètica per a la detecció de lesions d'expansió lenta en esclerosi múltiple"*
(MSc Data Science, UOC). Supervisor: Eloy Martinez-Heras.

## Roadmap

The work follows the three levels from the state of the art. Level 1 is the core goal, and
levels 2–3 are the planned extension.

| Step | Task | Dates | Module | Status |
|---|---|---|---|---|
| 0 | Repo, tests, CI, coverage | Oct | — | ✅ |
| 1 | **Data prep (T2):** IDIBAPS / public FLAIR, skull strip, bias correction, WM mask, intensity normalisation | 12/10 – 01/11 | `synthsel.io`, `synthsel.preprocessing` | 🟡 |
| 2 | **Level 1, static lesions (T3):** heuristic ellipsoids → CarveMix → diffusion inpainting (LeFusion / MSRepaint) | 26/10 – 15/11 | `synthsel.synthesis` | 🟡 |
| 3 | **Level 2, lesion dynamics (T4):** SEL concentric constant growth, new, shrinking and confluent lesions over t0→t1→t2 | 16/11 – 06/12 | `synthsel.dynamics` | 🟡 |
| 4 | **Level 3, atrophy (T4):** deformation field with known Jacobian, combined with level 2 | 16/11 – 06/12 | `synthsel.atrophy` | ⬜ |
| 5 | **Evaluation (T5):** Dice and lesion count (L1); per-lesion volume change and Jacobian (L2–3); LST-AI / SAMSEG | 30/11 – 15/12 | `synthsel.evaluation` | 🟡 |
| 6 | Report, presentation, defence (T6–T9) | → 29/01 | `thesis/` | ⬜ |

✅ done · 🟡 started · ⬜ not started

## Project structure

```
synthSEL/
├── src/synthsel/          # reusable, tested library code
│   ├── io.py              # NIfTI load/save, voxel spacing/volume
│   ├── preprocessing.py   # intensity normalisation
│   ├── config.py          # YAML experiment configs
│   ├── synthesis/         # Level 1: lesion masks + insertion
│   ├── dynamics/          # Level 2: growth / shrinkage / SEL trajectories
│   ├── atrophy/           # Level 3: deformation-based atrophy
│   └── evaluation/        # Dice, lesion count, per-lesion volume change
├── scripts/               # thin CLI entry points, one per experiment
├── configs/               # one YAML per experiment (expNNN_*.yaml)
├── experiments/           # experiment logs: hypothesis, setup, results
├── notebooks/             # exploration and visualisation
├── tests/                 # pytest unit tests (synthetic phantoms, no real data)
├── data/                  # local only, git-ignored (raw/interim/processed/synthetic)
├── docs/                  # notes, references
└── thesis/                # LaTeX report + figures
```

Workflow: explore in `notebooks/` → move reusable code to `src/synthsel/` with tests → run it via
`scripts/` + `configs/` → log it in `experiments/expNNN_*/README.md` → figures in `thesis/figures/`.

## Setup

Uses [uv](https://docs.astral.sh/uv/).

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
- GitHub Actions runs ruff + pytest on Python 3.10 and 3.12 and uploads coverage to Codecov.
  Add a `CODECOV_TOKEN` repository secret (Codecov → repo settings).

## Data

IDIBAPS data is confidential and **never committed**. `data/` and all `*.nii*` files are
git-ignored. See [`data/README.md`](data/README.md).
