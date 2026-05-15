mod fill;
mod grid;
mod word_list;

use pyo3::prelude::*;

use fill::{PyFillResult, PyStatistics};
use grid::PyGridConfig;
use word_list::PyWordList;

#[pymodule]
fn ingrid_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyWordList>()?;
    m.add_class::<PyGridConfig>()?;
    m.add_class::<PyFillResult>()?;
    m.add_class::<PyStatistics>()?;
    Ok(())
}
