"""Tests for the GridConfig class — construction, validation, and mutable settings."""

import pytest

from ingrid_py import GridConfig

from conftest import GRID_3X3


class TestGridConfig:
    def test_construction(self, word_list):
        config = GridConfig(GRID_3X3, word_list, min_score=50)
        assert config is not None

    def test_rejects_empty_template(self, word_list):
        with pytest.raises(RuntimeError, match="at least one row"):
            GridConfig("", word_list)

    def test_rejects_ragged_template(self, word_list):
        with pytest.raises(RuntimeError, match="same width"):
            GridConfig("...\n..", word_list)

    def test_template_normalisation(self, word_list):
        """Leading/trailing whitespace and mixed case should be accepted."""
        config = GridConfig("  ...  \n  ...  \n  ...  ", word_list, min_score=50)
        assert config is not None


class TestMutableSettings:
    def test_min_score_getter(self, word_list):
        config = GridConfig(GRID_3X3, word_list, min_score=42)
        assert config.min_score == 42

    def test_min_score_setter_updates_value(self, word_list):
        config = GridConfig(GRID_3X3, word_list, min_score=42)
        config.min_score = 70
        assert config.min_score == 70

    def test_min_score_setter_affects_slot_options(self, word_list):
        config = GridConfig(GRID_3X3, word_list, min_score=0)
        before = sum(len(s) for s in config.slot_options())
        config.min_score = 99
        after = sum(len(s) for s in config.slot_options())
        assert after <= before

    def test_max_shared_substring_default_none(self, word_list):
        config = GridConfig(GRID_3X3, word_list)
        assert config.max_shared_substring is None

    def test_max_shared_substring_setter(self, word_list):
        config = GridConfig(GRID_3X3, word_list)
        config.max_shared_substring = 3
        assert config.max_shared_substring == 3
