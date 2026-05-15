"""Tests for Statistics and FillResult — fields, repr, and timing data."""

from ingrid_py import Statistics


class TestStatistics:
    def test_fill_result_has_statistics(self, grid_3x3):
        result = grid_3x3.find_fill(timeout_secs=30.0)
        stats = result.statistics
        assert isinstance(stats, Statistics)
        assert stats.states >= 0
        assert stats.backtracks >= 0
        assert stats.total_time_ms >= 0.0

    def test_all_timing_fields_present(self, grid_3x3):
        result = grid_3x3.find_fill(timeout_secs=30.0)
        s = result.statistics
        for field in (
            "total_time_ms",
            "try_time_ms",
            "initial_arc_consistency_time_ms",
            "choice_arc_consistency_time_ms",
            "elimination_arc_consistency_time_ms",
        ):
            assert hasattr(s, field), f"Missing field: {field}"
            assert isinstance(getattr(s, field), float)

    def test_total_time_non_negative(self, grid_3x3):
        result = grid_3x3.find_fill(timeout_secs=30.0)
        assert result.statistics.total_time_ms >= 0.0

    def test_repr(self, grid_3x3):
        result = grid_3x3.find_fill(timeout_secs=30.0)
        assert "FillResult" in repr(result)
        assert "Statistics" in repr(result.statistics)
