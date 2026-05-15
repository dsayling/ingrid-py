"""ingrid-py — Python bindings for the ingrid_core crossword-filling library."""

from __future__ import annotations

from typing import Optional

from .ingrid_py import FillResult as FillResult
from .ingrid_py import GridConfig as GridConfig
from .ingrid_py import Statistics as Statistics
from .ingrid_py import WordList as WordList

def fill(
    template: str,
    words: list[tuple[str, int]],
    *,
    min_score: int = 50,
    timeout_secs: Optional[float] = None,
    max_shared_substring: Optional[int] = None,
) -> str:
    """Fill a crossword grid and return the rendered result string.

    Args:
        template: Multi-line grid template. ``.`` = empty cell, ``#`` = block,
            any letter = pre-filled cell. All rows must be the same width.
        words: List of ``(word, score)`` pairs. Scores are typically 0–100
            with 50 being average quality.
        min_score: Minimum word score to allow in the fill (default 50).
        timeout_secs: Maximum seconds to search. ``None`` means no limit.
        max_shared_substring: If set, words sharing a longer common substring
            cannot both appear in the same grid.

    Returns:
        The filled grid as a multi-line string with ``#`` for blocks.

    Raises:
        RuntimeError: If the grid is unfillable, times out, or is aborted.
    """
    ...

__all__ = ["WordList", "GridConfig", "FillResult", "Statistics", "fill"]
