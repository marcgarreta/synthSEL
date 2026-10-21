# experiments/

One folder per experiment: `expNNN_short_name/`. Each holds a `README.md` log (copy `TEMPLATE.md`)
with the hypothesis, config, results and conclusions. Code lives in `src/synthsel`, the parameters
in `configs/expNNN_*.yaml` and large outputs in `data/synthetic/expNNN_*`. These logs feed
chapters 3–4 of the thesis.

| ID | Level | Description | Status |
|---|---|---|---|
| exp001 | 1 | Heuristic ellipsoid lesions in WM (baseline) | planned |
| exp002 | 1 | CarveMix: copy real lesions between subjects | planned |
| exp003 | 1 | Diffusion-based inpainting (LeFusion / MSRepaint) | planned |
| exp004 | 2 | SEL concentric growth + new/shrinking lesions over t0→t1→t2 | planned |
| exp005 | 3 | Level 2 + atrophy deformation field with known Jacobian | planned |
| exp006 | eval | LST-AI / SAMSEG on synthetic data; per-lesion volume change | planned |
