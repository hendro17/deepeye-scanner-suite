"""Covers config_service.read_config's FileNotFoundError branch (lines 13-14)."""

from api.services.config_service import read_config


def test_read_config_returns_empty_dict_for_missing_file(tmp_path):
    # explicit path arg -> no monkeypatching needed
    assert read_config(tmp_path / "does-not-exist.yaml") == {}
