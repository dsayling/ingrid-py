"""Comprehensive tests for 15×15 grids using the bundled STWL word list.

Grid templates mirror the ones used in ingrid_core's own Rust test suite
(src/backtracking_search.rs). min_score=40 matches the Rust test helper default.
"""

import pytest
from conftest import STWL_PATH
from ingrid_py import FillResult, GridConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not STWL_PATH.exists(),
    reason="STWL word list not found — expected at resources/spreadthewordlist.dict",
)

TIMEOUT = 120.0  # seconds; generous for CI
MIN_SCORE = 40  # matches generate_config() default in ingrid_core's Rust tests


def _assert_valid_fill(result: FillResult, rows: int, cols: int) -> None:
    """Check that a fill result has the right shape and all cells are filled."""
    lines = result.filled_grid.strip().splitlines()
    assert len(lines) == rows, f"Expected {rows} rows, got {len(lines)}"
    assert all(len(line) == cols for line in lines), "Row width mismatch"
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            assert ch.isalpha() or ch == "#", f"Unexpected char {ch!r} at ({r},{c})"


# ---------------------------------------------------------------------------
# 15×15 themed (rotational symmetry, long theme entries)
# ---------------------------------------------------------------------------

THEMED_15X15 = """\
....#.....#....
....#.....#....
...............
......##.......
###.....#......
............###
.....#.....#...
....#.....#....
...#.....#.....
###............
......#.....###
.......##......
...............
....#.....#....
....#.....#....
"""

# ---------------------------------------------------------------------------
# 15×15 cryptic (dense block pattern, many short words)
# ---------------------------------------------------------------------------

CRYPTIC_15X15 = """\
....#....#....#
.#.#.#.#.#.#.#.
...............
.#.#.#.#.#.#.#.
...............
##.#.#.#.###.#.
...............
.###.#####.###.
...............
.#.###.#.#.#.##
...............
.#.#.#.#.#.#.#.
...............
.#.#.#.#.#.#.#.
#....#....#....
"""

# ---------------------------------------------------------------------------
# 15×15 themeless (open corners, few long blocks)
# ---------------------------------------------------------------------------

THEMELESS_15X15 = """\
..........#....
..........#....
..........#....
...#...#.......
....###........
.........#.....
###.......#....
...#.......#...
....#.......###
.....#.........
........###....
.......#...#...
....#..........
....#..........
....#..........
"""

# ---------------------------------------------------------------------------
# 15×15 partially populated (theme entry "ADMIRERS" pre-filled)
# ---------------------------------------------------------------------------

PARTIAL_15X15 = """\
.......##......
admirers#......
.......t.......
.....#.i...#...
....#..c..#....
...#...k.#.....
###....y......#
##.....f.....##
#......i....###
.....#.n...#...
....#..g..#....
...#...e.#.....
.......r.......
......#s.......
......##.......
"""

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFill15x15Themed:
    def test_fill_succeeds(self, stwl_word_list):
        config = GridConfig(THEMED_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        _assert_valid_fill(result, 15, 15)

    def test_slot_options_non_empty(self, stwl_word_list):
        config = GridConfig(THEMED_15X15, stwl_word_list, min_score=MIN_SCORE)
        options = config.slot_options()
        assert all(len(slot) > 0 for slot in options), "Every slot should have candidates"

    def test_statistics_populated(self, stwl_word_list):
        config = GridConfig(THEMED_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        assert result.statistics.states > 0
        assert result.statistics.total_time_ms > 0.0


class TestFill15x15Cryptic:
    def test_fill_succeeds(self, stwl_word_list):
        config = GridConfig(CRYPTIC_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        _assert_valid_fill(result, 15, 15)

    def test_blocks_preserved(self, stwl_word_list):
        config = GridConfig(CRYPTIC_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        lines = result.filled_grid.splitlines()
        assert lines[0][4] == "#"
        assert lines[14][0] == "#"


class TestFill15x15Themeless:
    def test_fill_succeeds(self, stwl_word_list):
        config = GridConfig(THEMELESS_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        _assert_valid_fill(result, 15, 15)


class TestFill15x15Partial:
    def test_fill_respects_prefilled_word(self, stwl_word_list):
        """'ADMIRERS' in row 1 must be preserved exactly."""
        config = GridConfig(PARTIAL_15X15, stwl_word_list, min_score=MIN_SCORE)
        result = config.find_fill(timeout_secs=TIMEOUT)
        _assert_valid_fill(result, 15, 15)
        lines = result.filled_grid.splitlines()
        assert lines[1][:8] == "admirers", f"Pre-filled word not preserved: {lines[1]}"

    def test_slot_options_reflect_constraints(self, stwl_word_list):
        """Slots crossing the pre-filled word should have fewer options than unconstrained ones."""
        config = GridConfig(PARTIAL_15X15, stwl_word_list, min_score=MIN_SCORE)
        options = config.slot_options()
        # At least one slot should be constrained to a single option (the pre-filled word itself).
        min_options = min(len(slot) for slot in options)
        assert min_options == 1, "Expected at least one fully-constrained slot"
