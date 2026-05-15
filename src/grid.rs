use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use ingrid_core::backtracking_search::{find_fill, FillFailure};
use ingrid_core::grid_config::{generate_grid_config_from_template_string, render_grid, OwnedGridConfig};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use crate::fill::{PyFillResult, PyStatistics};
use crate::word_list::PyWordList;

/// A configured crossword grid, ready to be filled.
///
/// Construct with a template string (`.` = empty cell, `#` = block,
/// any letter = pre-filled cell) plus a `WordList` and minimum score.
#[pyclass(name = "GridConfig", module = "ingrid_py")]
pub struct PyGridConfig {
    config: Arc<Mutex<OwnedGridConfig>>,
    abort: Arc<AtomicBool>,
    // Stored for rebuilding when settings change.
    template: String,
    raw_words: Vec<(String, u16)>,
    _min_score: u16,
    _max_shared_substring: Option<usize>,
}

impl PyGridConfig {
    fn build(
        template: &str,
        raw_words: Vec<(String, u16)>,
        min_score: u16,
        max_shared_substring: Option<usize>,
        abort: Arc<AtomicBool>,
    ) -> PyResult<Arc<Mutex<OwnedGridConfig>>> {
        let height = template.lines().count();
        let widths: std::collections::HashSet<usize> =
            template.lines().map(|l| l.chars().count()).collect();
        let max_side = height.max(*widths.iter().next().unwrap());

        let tmp_wl = PyWordList { words: raw_words, max_shared_substring };
        let word_list = tmp_wl.build_word_list(Some(max_side));

        let mut owned = generate_grid_config_from_template_string(word_list, template, min_score);
        owned.abort = Some(Arc::clone(&abort));

        Ok(Arc::new(Mutex::new(owned)))
    }
}

#[pymethods]
impl PyGridConfig {
    /// Create a grid config from a template string.
    ///
    /// Args:
    ///     template: Multi-line string where `.` is an empty cell, `#` is a
    ///         block, and any letter is a pre-filled cell. All rows must be the
    ///         same width. A trailing newline is optional.
    ///     word_list: The `WordList` to use for filling.
    ///     min_score: Minimum word score allowed (default 50).
    #[new]
    #[pyo3(signature = (template, word_list, min_score=50))]
    pub fn new(template: String, word_list: &PyWordList, min_score: u16) -> PyResult<Self> {
        if template.trim().is_empty() {
            return Err(PyRuntimeError::new_err("Grid template must have at least one row"));
        }

        let template = template
            .lines()
            .map(|l| l.trim().to_lowercase())
            .filter(|l| !l.is_empty())
            .collect::<Vec<_>>()
            .join("\n")
            + "\n";

        let height = template.lines().count();
        if height == 0 {
            return Err(PyRuntimeError::new_err("Grid template must have at least one row"));
        }

        let widths: std::collections::HashSet<usize> =
            template.lines().map(|l| l.chars().count()).collect();
        if widths.len() != 1 {
            return Err(PyRuntimeError::new_err("All rows in the grid template must be the same width"));
        }

        let raw_words = word_list.words.clone();
        let max_shared_substring = word_list.max_shared_substring;
        let abort = Arc::new(AtomicBool::new(false));

        let config = Self::build(&template, raw_words.clone(), min_score, max_shared_substring, Arc::clone(&abort))?;

        Ok(Self {
            config,
            abort,
            template,
            raw_words,
            _min_score: min_score,
            _max_shared_substring: max_shared_substring,
        })
    }

    /// Minimum word score used for filling. Changing this rebuilds the grid config.
    #[getter]
    pub fn min_score(&self) -> u16 {
        self._min_score
    }

    #[setter]
    pub fn set_min_score(&mut self, value: u16) -> PyResult<()> {
        let new_config = Self::build(
            &self.template,
            self.raw_words.clone(),
            value,
            self._max_shared_substring,
            Arc::clone(&self.abort),
        )?;
        self.config = new_config;
        self._min_score = value;
        Ok(())
    }

    /// Maximum shared substring length between any two words in the same grid.
    /// Changing this rebuilds the grid config.
    #[getter]
    pub fn max_shared_substring(&self) -> Option<usize> {
        self._max_shared_substring
    }

    #[setter]
    pub fn set_max_shared_substring(&mut self, value: Option<usize>) -> PyResult<()> {
        let new_config = Self::build(
            &self.template,
            self.raw_words.clone(),
            self._min_score,
            value,
            Arc::clone(&self.abort),
        )?;
        self.config = new_config;
        self._max_shared_substring = value;
        Ok(())
    }

    /// Signal any in-progress `find_fill` call to stop early.
    ///
    /// The fill will return a `RuntimeError("Aborted")` when it notices the
    /// flag. Resets automatically before each new `find_fill` call.
    pub fn abort(&self) {
        self.abort.store(true, Ordering::Relaxed);
    }

    /// Search for a valid fill for this grid.
    ///
    /// Releases the Python GIL during the (potentially long) Rust search so
    /// other Python threads remain responsive.
    ///
    /// Args:
    ///     timeout_secs: Maximum seconds to spend searching. `None` means no
    ///         limit (not recommended for large grids).
    ///
    /// Returns:
    ///     A `FillResult` containing the filled grid string and statistics.
    ///
    /// Raises:
    ///     RuntimeError: If the grid is unfillable, the search times out, is
    ///         aborted via `abort()`, or exceeds the backtrack limit.
    #[pyo3(signature = (timeout_secs=None))]
    pub fn find_fill(&self, py: Python<'_>, timeout_secs: Option<f64>) -> PyResult<PyFillResult> {
        self.abort.store(false, Ordering::Relaxed);

        let timeout = timeout_secs.map(Duration::from_secs_f64);
        let config_arc = Arc::clone(&self.config);

        let result = py.allow_threads(move || {
            let guard = config_arc.lock().unwrap();
            let config_ref = guard.to_config_ref();
            find_fill(&config_ref, timeout, None)
        });

        match result {
            Ok(success) => {
                let guard = self.config.lock().unwrap();
                let config_ref = guard.to_config_ref();
                let rendered = render_grid(&config_ref, &success.choices).replace('.', "#");
                let stats = Py::new(py, PyStatistics::from(success.statistics))?;
                Ok(PyFillResult {
                    filled_grid: rendered,
                    statistics: stats,
                })
            }
            Err(FillFailure::Timeout) => Err(PyRuntimeError::new_err("Fill timed out")),
            Err(FillFailure::Abort) => Err(PyRuntimeError::new_err("Fill was aborted")),
            Err(FillFailure::HardFailure) => {
                Err(PyRuntimeError::new_err("Grid is unfillable with the provided word list"))
            }
            Err(FillFailure::ExceededBacktrackLimit(n)) => Err(PyRuntimeError::new_err(format!(
                "Exceeded backtrack limit ({n} backtracks) — try a longer timeout or simpler grid"
            ))),
        }
    }

    /// Return the candidate words for each slot, in fill-quality order.
    ///
    /// Returns a list with one entry per slot (across slots before down slots,
    /// left-to-right / top-to-bottom within each direction). Each entry is a
    /// list of word strings that are compatible with the current grid state and
    /// meet the minimum score requirement.
    pub fn slot_options(&self) -> Vec<Vec<String>> {
        let guard = self.config.lock().unwrap();
        guard
            .slot_configs
            .iter()
            .zip(guard.slot_options.iter())
            .map(|(slot_cfg, options)| {
                options
                    .iter()
                    .map(|&word_id| {
                        guard.word_list.words[slot_cfg.length][word_id]
                            .normalized_string
                            .clone()
                    })
                    .collect()
            })
            .collect()
    }

    /// Render a previously-computed fill result as a grid string.
    ///
    /// Convenience method; identical to `result.filled_grid`.
    pub fn render(&self, result: &PyFillResult) -> String {
        result.filled_grid.clone()
    }
}

