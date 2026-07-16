import pytest
from turkgram.phonology import to_ipa, ipa_table
from tests.golden_phonology import IPA_CHARS, IPA_WORDS


@pytest.mark.parametrize("ch,expected_sub", IPA_CHARS)
def test_ipa_char(ch, expected_sub):
    result = to_ipa(ch)
    assert expected_sub in result, f"{ch!r} → {result!r}, beklenen substring {expected_sub!r}"


@pytest.mark.parametrize("word,expected", IPA_WORDS)
def test_ipa_word(word, expected):
    assert to_ipa(word) == expected


def test_ipa_table_complete():
    table = ipa_table()
    for ch in "abcçdefghıijklmnoöprsştuüvyz":
        assert ch in table, f"{ch!r} tabloda yok"
