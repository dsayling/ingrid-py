"""
ingrid-py — Python bindings for the ingrid_core crossword-filling library.

Quick start::

    from ingrid_py import WordList, GridConfig

    words = WordList([("clue", 60), ("grid", 70), ("fill", 80), ...])
    config = GridConfig("...\\n...\\n...", words, min_score=50)
    result = config.find_fill(timeout_secs=10.0)
    print(result.filled_grid)

Or use the high-level helper::

    from ingrid_py import fill

    print(fill("...\\n...\\n...", [("clue", 60), ...]))
"""

from __future__ import annotations

from typing import Optional

# Re-export the Rust-backed classes from the native extension.
from .ingrid_py import FillResult, GridConfig, Statistics, WordList

__all__ = [
    "WordList",
    "GridConfig",
    "FillResult",
    "Statistics",
    "fill",
]


def fill(
    template: str,
    words: list[tuple[str, int]],
    *,
    min_score: int = 50,
    timeout_secs: Optional[float] = None,
    max_shared_substring: Optional[int] = None,
) -> str:
    """Fill a crossword grid and return the rendered result string.

    This is a convenience wrapper around :class:`WordList` and
    :class:`GridConfig`.  For more control — including cancellation via
    :meth:`GridConfig.abort` — use those classes directly.

    Args:
        template: Multi-line grid template. ``.`` = empty cell, ``#`` = block,
            any letter = pre-filled cell.  All rows must be the same width.
        words: List of ``(word, score)`` pairs.  Scores are typically 0–100
            with 50 being average quality.
        min_score: Minimum word score to allow in the fill (default 50).
        timeout_secs: Maximum seconds to search.  ``None`` means no limit.
        max_shared_substring: If set, words sharing a longer common substring
            cannot both appear in the same grid.

    Returns:
        The filled grid as a multi-line string with ``#`` for blocks.

    Raises:
        RuntimeError: If the grid is unfillable, times out, or is aborted.
    """
    word_list = WordList(words, max_shared_substring)
    config = GridConfig(template, word_list, min_score)
    result = config.find_fill(timeout_secs)
    return result.filled_grid
