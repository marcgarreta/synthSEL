from pathlib import Path

import pytest

from synthsel.config import load_config

CONFIGS = Path(__file__).parents[1] / "configs"


def test_repo_configs_are_valid():
    for path in CONFIGS.glob("*.yaml"):
        cfg = load_config(path)
        assert cfg["name"] == path.stem


def test_missing_keys(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("name: x\n")
    with pytest.raises(KeyError, match="seed"):
        load_config(path)
