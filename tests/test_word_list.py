"""Tests for the WordList class."""

from conftest import WORDS_3
from ingrid_py import WordList


class TestWordList:
    def test_construction_from_tuples(self):
        words = [("cat", 70), ("dog", 60), ("fox", 80)]
        wl = WordList(words)
        assert wl.word_count == 3

    def test_construction_empty(self):
        wl = WordList([])
        assert wl.word_count == 0

    def test_from_text(self):
        blob = "hello\t50\nworld\t60\nearth\t70\n"
        wl = WordList.from_text(blob)
        assert wl.word_count == 3

    def test_from_text_ignores_bad_lines(self):
        blob = "good\t50\nbad_line\ngood2\t60\n"
        wl = WordList.from_text(blob)
        assert wl.word_count == 2

    def test_max_shared_substring_param(self):
        wl = WordList(WORDS_3, max_shared_substring=5)
        assert wl.word_count > 0
