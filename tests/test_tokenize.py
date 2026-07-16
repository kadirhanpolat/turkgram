import pytest
from turkgram import tokenize
from tests.golden_tokenize import GOLDEN_TOKENIZE


@pytest.mark.parametrize("text,expected", GOLDEN_TOKENIZE)
def test_tokenize_golden(text, expected):
    assert tokenize(text) == expected
