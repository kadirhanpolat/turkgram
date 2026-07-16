"""Faz 9b — yazım denetimi runner."""
import pytest
from tests.golden_spellcheck import IS_VALID_CASES, SUGGEST_CASES, CHECK_CASES


@pytest.mark.parametrize("word,expected", IS_VALID_CASES)
def test_is_valid(word, expected):
    from turkgram.spellcheck import is_valid
    assert is_valid(word) == expected


def test_is_valid_empty():
    from turkgram.spellcheck import is_valid
    assert is_valid("") is False


def test_is_valid_too_long():
    from turkgram.spellcheck import is_valid
    assert is_valid("a" * 201) is False


def test_spell_result_is_frozen():
    from turkgram.spellcheck import SpellResult
    r = SpellResult(word="ev", is_valid=True, suggestions=())
    with pytest.raises(Exception):
        r.is_valid = False  # type: ignore


def test_check_valid_word_no_suggestions():
    from turkgram.spellcheck import check
    r = check("ev")
    assert r.is_valid is True
    assert r.suggestions == ()


@pytest.mark.parametrize("a,b,expected", [
    ("ev",    "ev",    0.0),
    ("seker", "şeker", 0.5),
    ("cok",   "çok",   0.5),
    ("kapi",  "kapı",  0.5),
    ("goz",   "göz",   0.5),
    ("dag",   "dağ",   0.5),
    ("abc",   "xyz",   3.0),
    ("ab",    "abc",   1.0),
    ("abc",   "ab",    1.0),
])
def test_tr_distance(a, b, expected):
    from turkgram.spellcheck import _tr_distance
    assert _tr_distance(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("word,must_include,max_dist", SUGGEST_CASES)
def test_suggest_includes(word, must_include, max_dist):
    from turkgram.spellcheck import suggest
    result = suggest(word, max_distance=max_dist)
    assert must_include in result, f"suggest({word!r}) = {result}, beklenen: {must_include!r}"


def test_suggest_max_suggestions():
    from turkgram.spellcheck import suggest
    result = suggest("seker", max_suggestions=2)
    assert len(result) <= 2


def test_suggest_invalid_params():
    from turkgram.spellcheck import suggest
    with pytest.raises(ValueError):
        suggest("test", max_suggestions=0)
    with pytest.raises(ValueError):
        suggest("test", max_distance=0)


@pytest.mark.parametrize("word,exp_valid,exp_sug_superset", CHECK_CASES)
def test_check(word, exp_valid, exp_sug_superset):
    from turkgram.spellcheck import check
    r = check(word)
    assert r.is_valid == exp_valid
    if exp_sug_superset:
        for root in exp_sug_superset:
            assert root in r.suggestions


def test_tr_api():
    from turkgram import tr
    assert tr.yazım_geçerli("ev") is True
    assert isinstance(tr.öneri("seker"), list)
    from turkgram.spellcheck import SpellResult
    assert isinstance(tr.denetle("ev"), SpellResult)


def test_cli_check_invalid(capsys):
    from turkgram.__main__ import cmd_check
    cmd_check(["cok"])  # "seker" sekmek 3sg aorist olduğu için geçerli; "cok" geçersiz
    out = capsys.readouterr().out
    assert "GEÇERSİZ" in out


def test_cli_check_valid(capsys):
    from turkgram.__main__ import cmd_check
    cmd_check(["evde"])
    out = capsys.readouterr().out
    assert "GEÇERLİ" in out


def test_cli_check_too_long():
    from turkgram.__main__ import cmd_check
    with pytest.raises(SystemExit):
        cmd_check(["a" * 201])
