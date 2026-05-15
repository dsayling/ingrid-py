use ingrid_core::word_list::{WordList, WordListSourceConfig, WordListSourceConfigProvider};
use pyo3::prelude::*;
use pyo3::types::PyType;

/// A configured word list that can be passed to `GridConfig`.
///
/// Words are stored as `(word, score)` pairs. Scores are typically 0–100
/// where 50 is average quality. Words can also be loaded from a
/// tab-separated text blob via `WordList.from_text()`.
#[pyclass(name = "WordList", module = "ingrid_py")]
pub struct PyWordList {
    pub words: Vec<(String, u16)>,
    pub max_shared_substring: Option<usize>,
}

#[pymethods]
impl PyWordList {
    /// Create a word list from a list of (word, score) tuples.
    ///
    /// Args:
    ///     words: List of (word, score) pairs.
    ///     max_shared_substring: If set, words sharing a substring longer than
    ///         this many characters cannot both appear in the same grid.
    #[new]
    #[pyo3(signature = (words, max_shared_substring=None))]
    pub fn new(
        words: Vec<(String, u16)>,
        max_shared_substring: Option<usize>,
    ) -> PyResult<Self> {
        Ok(Self {
            words,
            max_shared_substring,
        })
    }

    /// Create a word list from a tab-separated text blob (`WORD\tSCORE` per line).
    ///
    /// Lines that cannot be parsed are silently ignored.
    #[classmethod]
    #[pyo3(signature = (contents, max_shared_substring=None))]
    pub fn from_text(
        _cls: &Bound<'_, PyType>,
        contents: &str,
        max_shared_substring: Option<usize>,
    ) -> PyResult<Self> {
        let words: Vec<(String, u16)> = contents
            .lines()
            .filter_map(|line| {
                let mut parts = line.splitn(2, '\t');
                let word = parts.next()?.trim().to_string();
                let score: u16 = parts.next()?.trim().parse().ok()?;
                Some((word, score))
            })
            .collect();
        Ok(Self {
            words,
            max_shared_substring,
        })
    }

    /// Number of words in this word list.
    #[getter]
    pub fn word_count(&self) -> usize {
        self.words.len()
    }
}

impl PyWordList {
    /// Build an `ingrid_core::WordList` from this config.
    pub fn build_word_list(&self, max_length: Option<usize>) -> WordList {
        let source = WordListSourceConfig {
            id: "0".into(),
            enabled: true,
            provider: WordListSourceConfigProvider::Memory {
                words: self.words.clone(),
            },
            normalization: None,
        };
        WordList::new(
            vec![source],
            None,
            max_length,
            self.max_shared_substring,
        )
    }
}
