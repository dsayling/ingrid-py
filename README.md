# ingrid-py

Python bindings for the [ingrid](https://github.com/rf-/ingrid_core) crossword-filling library, built with [PyO3](https://pyo3.rs) and [Maturin](https://maturin.rs).

## Installation

```bash
uv add ingrid-py
pip install ingrid-py
poetry add ingrid-py
```

To build from source you need Rust and Maturin:

```bash
git clone <repository-url>
uv run maturin develop --release
```

## Quick start

```python
import ingrid_py

words = [("APPLE", 80), ("PLANE", 75), ("MAPLE", 70), ...]

filled = ingrid_py.fill(
    template="""\
APPLE
.....
.....
.....
.....""",
    words=words,
)
print(filled)
```

The template uses `.` for empty cells, `#` for black squares, and any letter for pre-filled cells.

## API

### `fill(template, words, *, min_score=50, timeout_secs=None, max_shared_substring=None) -> str`

Convenience wrapper that fills a grid and returns the rendered result string. Raises `RuntimeError` if the grid is unfillable or times out.

### `WordList(words, max_shared_substring=None)`

Holds a list of `(word, score)` pairs. Scores are typically 0–100 with 50 being average quality.

```python
wl = ingrid_py.WordList([("APPLE", 80), ("PLANE", 75)])

# Or load from a tab-separated text blob (WORD\tSCORE per line):
wl = ingrid_py.WordList.from_text(open("wordlist.txt").read())
```

### `GridConfig(template, word_list, min_score=50)`

A configured grid ready to be filled. Exposes lower-level control including cancellation and slot inspection.

```python
cfg = ingrid_py.GridConfig(template, wl, min_score=60)

# Fill (releases the GIL so other threads stay responsive)
result = cfg.find_fill(timeout_secs=30.0)
print(result.filled_grid)
print(result.statistics.total_time_ms, "ms")

# Inspect candidates per slot before filling
for i, candidates in enumerate(cfg.slot_options()):
    print(f"Slot {i}: {len(candidates)} options")

# Abort a fill running in another thread
cfg.abort()
```

### `FillResult`

| Attribute | Type | Description |
|---|---|---|
| `filled_grid` | `str` | Filled grid as a multi-line string |
| `statistics` | `Statistics` | Timing and search stats |

### `Statistics`

| Attribute | Type | Description |
|---|---|---|
| `states` | `int` | Search states explored |
| `backtracks` | `int` | Backtracks taken |
| `retries` | `int` | Randomized restarts |
| `total_time_ms` | `float` | Total fill time (ms) |

## Development

```bash
# Build the extension in-place
uv run maturin develop

# Run tests
uv run pytest
```

## License

See [LICENSE](LICENSE).
