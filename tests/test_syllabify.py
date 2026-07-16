# tests/test_syllabify.py
import pytest
from turkgram.syllabify import syllabify, stress, stress_mark
from tests.golden_syllabify import SYLLABIFY_CASES, STRESS_MARK_CASES


@pytest.mark.parametrize("surface,expected_syllables,expected_stress", SYLLABIFY_CASES)
def test_syllabify_and_stress(surface, expected_syllables, expected_stress):
    assert syllabify(surface) == expected_syllables
    assert stress(surface) == expected_stress


@pytest.mark.parametrize("surface,expected_mark", STRESS_MARK_CASES)
def test_stress_mark(surface, expected_mark):
    assert stress_mark(surface) == expected_mark
