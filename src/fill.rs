use ingrid_core::backtracking_search::Statistics;
use pyo3::prelude::*;

/// Fill statistics returned alongside a completed grid.
#[pyclass(name = "Statistics", get_all, module = "ingrid_py")]
#[derive(Clone)]
pub struct PyStatistics {
    /// Total number of search states explored.
    pub states: usize,
    /// Number of backtracks taken.
    pub backtracks: usize,
    /// Number of restricted-branching steps.
    pub restricted_branchings: usize,
    /// Number of full retries (randomized restarts).
    pub retries: usize,
    /// Total fill time in milliseconds.
    pub total_time_ms: f64,
    /// Time spent in fill tries (excluding arc consistency) in milliseconds.
    pub try_time_ms: f64,
    /// Time spent in initial arc consistency check in milliseconds.
    pub initial_arc_consistency_time_ms: f64,
    /// Time spent in arc consistency checks after each choice in milliseconds.
    pub choice_arc_consistency_time_ms: f64,
    /// Time spent in arc consistency checks after each elimination in milliseconds.
    pub elimination_arc_consistency_time_ms: f64,
}

#[pymethods]
impl PyStatistics {
    fn __repr__(&self) -> String {
        format!(
            "Statistics(states={}, backtracks={}, retries={}, total_time_ms={:.1})",
            self.states, self.backtracks, self.retries, self.total_time_ms
        )
    }
}

impl From<Statistics> for PyStatistics {
    fn from(s: Statistics) -> Self {
        Self {
            states: s.states,
            backtracks: s.backtracks,
            restricted_branchings: s.restricted_branchings,
            retries: s.retries,
            total_time_ms: s.total_time.as_secs_f64() * 1000.0,
            try_time_ms: s.try_time.as_secs_f64() * 1000.0,
            initial_arc_consistency_time_ms: s.initial_arc_consistency_time.as_secs_f64() * 1000.0,
            choice_arc_consistency_time_ms: s.choice_arc_consistency_time.as_secs_f64() * 1000.0,
            elimination_arc_consistency_time_ms: s.elimination_arc_consistency_time.as_secs_f64() * 1000.0,
        }
    }
}

/// The result of a successful grid fill.
#[pyclass(name = "FillResult", get_all, module = "ingrid_py")]
pub struct PyFillResult {
    /// The filled grid as a multi-line string. Blocks are represented as `#`.
    pub filled_grid: String,
    /// Statistics about the fill process.
    pub statistics: Py<PyStatistics>,
}

#[pymethods]
impl PyFillResult {
    fn __repr__(&self, py: Python<'_>) -> String {
        let stats = self.statistics.bind(py).borrow();
        format!(
            "FillResult(states={}, backtracks={}, retries={})",
            stats.states, stats.backtracks, stats.retries
        )
    }
}
