"""Tests for GridConfig.slot_options()."""


from ingrid_py import GridConfig

from conftest import GRID_3X3


class TestSlotOptions:
    def test_returns_list_of_lists(self, grid_3x3):
        options = grid_3x3.slot_options()
        assert isinstance(options, list)
        assert all(isinstance(slot, list) for slot in options)

    def test_contains_strings(self, grid_3x3):
        options = grid_3x3.slot_options()
        for slot in options:
            assert all(isinstance(w, str) for w in slot)

    def test_slot_count_matches_grid(self, grid_3x3):
        # 3×3 open grid has 3 across + 3 down = 6 slots.
        assert len(grid_3x3.slot_options()) == 6

    def test_higher_min_score_reduces_options(self, word_list):
        config_lo = GridConfig(GRID_3X3, word_list, min_score=0)
        config_hi = GridConfig(GRID_3X3, word_list, min_score=99)
        lo_total = sum(len(s) for s in config_lo.slot_options())
        hi_total = sum(len(s) for s in config_hi.slot_options())
        assert hi_total <= lo_total
