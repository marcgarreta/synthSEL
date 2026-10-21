# data/

Nothing in this folder is committed (see `.gitignore`). IDIBAPS patient data must stay local.

| Folder | Content |
|---|---|
| `raw/` | Original data as received (IDIBAPS, or public sets such as MSSEG-2 / ISBI 2015 while access is pending) |
| `interim/` | Intermediate steps: registration, skull stripping, bias-field correction |
| `processed/` | Model-ready volumes per subject: `sub-XXX/flair.nii.gz`, `wm_mask.nii.gz`, `lesion_mask.nii.gz` |
| `synthetic/` | Generated outputs, one subfolder per experiment name |
