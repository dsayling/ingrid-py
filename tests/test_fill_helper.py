"""Tests for the high-level fill() convenience function."""


from ingrid_py import fill

from conftest import GRID_3X3


class TestFillHelper:
    def test_fill_returns_string(self, words_3):
        result = fill(GRID_3X3, words_3, timeout_secs=30.0)
        assert isinstance(result, str)
        assert len(result.strip().splitlines()) == 3

    def test_fill_with_min_score(self, words_3):
        result = fill(GRID_3X3, words_3, min_score=50, timeout_secs=30.0)
        assert isinstance(result, str)

    def test_fill_with_max_shared_substring(self, words_3):
        result = fill(GRID_3X3, words_3, max_shared_substring=2, timeout_secs=30.0)
        assert isinstance(result, str)
