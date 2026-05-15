"""Type stubs for the ingrid_py native Rust extension."""

from typing import Optional

class WordList:
    """A configured word list that can be passed to `GridConfig`.

    Words are stored as ``(word, score)`` pairs. Scores are typically 0–100
    where 50 is average quality.
    """

    def __init__(
        self,
        words: list[tuple[str, int]],
        max_shared_substring: Optional[int] = None,
    ) -> None: ...
    @classmethod
    def from_text(
        cls,
        contents: str,
        max_shared_substring: Optional[int] = None,
    ) -> "WordList":
        """Create a word list from a tab-separated text blob (``WORD\\tSCORE`` per line).

        Lines that cannot be parsed are silently ignored.
        """
        ...

    @property
    def word_count(self) -> int:
        """Number of words in this word list."""
        ...

class Statistics:
    """Statistics about a completed grid fill."""

    states: int
    """Total number of search states explored."""
    backtracks: int
    """Number of backtracks taken."""
    restricted_branchings: int
    """Number of restricted-branching steps."""
    retries: int
    """Number of full retries (randomized restarts)."""
    total_time_ms: float
    """Total fill time in milliseconds."""
    try_time_ms: float
    """Time spent in fill tries (excluding arc consistency) in milliseconds."""
    initial_arc_consistency_time_ms: float
    """Time spent in the initial arc consistency check in milliseconds."""
    choice_arc_consistency_time_ms: float
    """Time spent in arc consistency checks after each choice in milliseconds."""
    elimination_arc_consistency_time_ms: float
    """Time spent in arc consistency checks after each elimination in milliseconds."""

class FillResult:
    """The result of a successful grid fill."""

    filled_grid: str
    """The filled grid as a multi-line string. Blocks are represented as ``#``."""
    statistics: Statistics
    """Statistics about the fill process."""

class GridConfig:
    """A configured crossword grid, ready to be filled.

    Construct with a template string (``.`` = empty cell, ``#`` = block,
    any letter = pre-filled cell) plus a :class:`WordList` and minimum score.
    """

    def __init__(
        self,
        template: str,
        word_list: WordList,
        min_score: int = 50,
    ) -> None: ...
    @property
    def min_score(self) -> int:
        """Minimum word score used for filling. Changing this rebuilds the grid config."""
        ...

    @min_score.setter
    def min_score(self, value: int) -> None: ...
    @property
    def max_shared_substring(self) -> Optional[int]:
        """Maximum shared substring length between any two words in the same grid.

        Changing this rebuilds the grid config.
        """
        ...

    @max_shared_substring.setter
    def max_shared_substring(self, value: Optional[int]) -> None: ...
    def abort(self) -> None:
        """Signal any in-progress :meth:`find_fill` call to stop early."""
        ...

    def find_fill(self, timeout_secs: Optional[float] = None) -> FillResult:
        """Search for a valid fill for this grid.

        Releases the Python GIL during the search so other threads stay responsive.

        Args:
            timeout_secs: Maximum seconds to spend searching. ``None`` means no limit.

        Returns:
            A :class:`FillResult` with the filled grid string and statistics.

        Raises:
            RuntimeError: If the grid is unfillable, times out, is aborted, or
                exceeds the backtrack limit.
        """
        ...

    def slot_options(self) -> list[list[str]]:
        """Return the candidate words for each slot, in fill-quality order.

        Returns a list with one entry per slot (across before down, left-to-right /
        top-to-bottom within each direction). Each entry is a list of word strings
        compatible with the current grid state and minimum score requirement.
        """
        ...

    def render(self, result: FillResult) -> str:
        """Render a previously-computed fill result as a grid string.

        Convenience method; identical to ``result.filled_grid``.
        """
        ...
