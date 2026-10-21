"""Experiment configuration loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML experiment config. Requires ``name`` and ``seed`` keys."""
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    missing = {"name", "seed"} - cfg.keys()
    if missing:
        raise KeyError(f"Config {path} is missing required keys: {sorted(missing)}")
    return cfg
