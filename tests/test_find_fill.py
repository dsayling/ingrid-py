"""Tests for GridConfig.find_fill() — success, timeout, abort, and failure cases."""

import threading
import time

import pytest
from conftest import GRID_3X3
from ingrid_py import FillResult, GridConfig, WordList


class TestFindFill:
    def test_fill_succeeds(self, grid_3x3):
        result = grid_3x3.find_fill(timeout_secs=30.0)
        assert isinstance(result, FillResult)
        lines = result.filled_grid.strip().splitlines()
        assert len(lines) == 3
        assert all(len(line) == 3 for line in lines)
        assert all(c.isalpha() for line in lines for c in line)

    def test_fill_with_prefilled_cells(self, word_list):
        """A grid with pre-filled letters should respect those constraints."""
        config = GridConfig("c..\n...\n...", word_list, min_score=50)
        result = config.find_fill(timeout_secs=30.0)
        assert result.filled_grid.splitlines()[0][0] == "c"

    def test_fill_with_blocks(self, word_list):
        """Blocks (#) should be preserved in the output."""
        # 7×3 grid with a central column of blocks — all slots are exactly 3 letters.
        config = GridConfig("...#...\n...#...\n...#...", word_list, min_score=50)
        result = config.find_fill(timeout_secs=30.0)
        lines = result.filled_grid.splitlines()
        assert lines[0][3] == "#"
        assert lines[1][3] == "#"
        assert lines[2][3] == "#"

    def test_timeout_raises(self):
        """An extremely short timeout on a large grid should raise RuntimeError."""
        small_words = [("abc", 70), ("def", 70), ("ghi", 70)]
        wl = WordList(small_words)
        config = GridConfig("\n".join(["." * 15] * 15), wl, min_score=0)
        with pytest.raises(RuntimeError):
            config.find_fill(timeout_secs=0.001)

    def test_abort(self):
        """abort() should cause an in-progress fill to stop."""
        limited_words = [(w, 70) for w in ["abc", "bcd", "cde", "def", "efg"]]
        wl = WordList(limited_words)
        config = GridConfig("\n".join(["." * 8] * 8), wl, min_score=0)

        error: list[Exception] = []

        def run_fill():
            try:
                config.find_fill(timeout_secs=60.0)
            except RuntimeError as e:
                error.append(e)

        t = threading.Thread(target=run_fill)
        t.start()
        time.sleep(0.2)
        config.abort()
        t.join(timeout=5.0)
        assert not t.is_alive(), "fill thread did not stop after abort"
        assert error, "expected RuntimeError after abort"
        assert isinstance(error[0], RuntimeError)

    def test_unfillable_grid_raises(self, word_list):
        """A grid that cannot possibly be filled should raise RuntimeError."""
        wl = WordList([("zzz", 80)])
        config = GridConfig(GRID_3X3, wl, min_score=80)
        with pytest.raises(RuntimeError):
            config.find_fill(timeout_secs=5.0)
