# tests/test_parse_text.py
from turkgram import tokenize, parse_text
from turkgram.analysis import Analysis, _cached_analyze


def test_parse_text_empty():
    assert parse_text("") == []


def test_parse_text_length_matches_tokens():
    text = "Ali geldi."
    result = parse_text(text)
    assert len(result) == len(tokenize(text))


def test_parse_text_punctuation_empty_list():
    result = parse_text("Ali geldi.")
    tokens = tokenize("Ali geldi.")
    dot_idx = tokens.index(".")
    assert result[dot_idx] == []


def test_parse_text_returns_list_of_list_of_analysis():
    result = parse_text("geldi")
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert all(isinstance(a, Analysis) for a in result[0])


def test_parse_text_apostrophe_strip():
    result = parse_text("Ankara'nın")
    tokens = tokenize("Ankara'nın")
    assert len(result) == len(tokens)  # 2 token → 2 liste
    assert isinstance(result[1], list)  # "'nın" → analyze("nın"), no crash


def test_parse_text_cache_hit():
    import turkgram.analysis as _mod
    _mod._cached_analyze.cache_clear()
    parse_text("geldi geldi geldi")
    info = _mod._cached_analyze.cache_info()
    assert info.hits >= 2  # 3 calls, 1 miss + 2 hits
    assert info.misses == 1


def test_parse_text_roots_none_vs_empty_set():
    """roots=None ve roots=set() farklı cache slotları kullanmalı."""
    import turkgram.analysis as _mod
    _mod._cached_analyze.cache_clear()

    r1 = parse_text("geldi", roots=None)
    r2 = parse_text("geldi", roots=set())
    assert isinstance(r1, list)
    assert isinstance(r2, list)
    info = _mod._cached_analyze.cache_info()
    assert info.currsize >= 2


def test_parse_text_all_punctuation():
    result = parse_text("...")
    assert result == [[], [], []]
