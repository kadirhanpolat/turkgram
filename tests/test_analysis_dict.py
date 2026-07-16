"""analysis_to_dict() serileştirme testleri (H-03).

Her kind için: schema_version, lemma, pos, kind, kwargs, hypothetical,
confidence, segments, chain alanları doğrulanır.
"""
import json
import pytest
from turkgram import analyze, analysis_to_dict, ANALYSIS_DICT_SCHEMA_VERSION
from turkgram.disambiguation import disambiguate


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _first(surface, roots=None, **kw):
    results = analyze(surface, roots=roots, **kw)
    assert results, f"analyze({surface!r}) boş döndü"
    return results[0]


def _assert_base(d, kind, lemma, pos):
    """Zorunlu alanları kontrol et."""
    assert d["schema_version"] == ANALYSIS_DICT_SCHEMA_VERSION
    assert d["kind"] == kind
    assert d["lemma"] == lemma
    assert d["pos"] == pos
    assert isinstance(d["hypothetical"], bool)
    assert isinstance(d["kwargs"], dict)
    assert isinstance(d["segments"], list)
    assert isinstance(d["chain"], list)
    for seg in d["segments"]:
        assert "surface" in seg and "label" in seg and "span" in seg
        assert isinstance(seg["span"], list) and len(seg["span"]) == 2


def _assert_json_safe(d):
    """Tüm ağaç JSON-serileştirilebilir olmalı."""
    json.dumps(d)  # hata fırlatırsa test başarısız


# ---------------------------------------------------------------------------
# confidence=None (disambiguation yapılmamış)
# ---------------------------------------------------------------------------

def test_confidence_none_by_default():
    a = _first("okudu", roots={"okumak"})
    d = analysis_to_dict(a)
    assert d["confidence"] is None


def test_confidence_float_from_disambiguate():
    analyses = analyze("okudu", roots={"okumak"})
    ranked = disambiguate(analyses)
    assert ranked
    a, conf = ranked[0]
    d = analysis_to_dict(a, confidence=conf)
    assert isinstance(d["confidence"], float)
    assert 0.0 <= d["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# kind: conjugate
# ---------------------------------------------------------------------------

def test_kind_conjugate():
    a = _first("okudu", roots={"okumak"})
    d = analysis_to_dict(a)
    _assert_base(d, "conjugate", "okumak", "verb")
    assert d["hypothetical"] is False
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: decline
# ---------------------------------------------------------------------------

def test_kind_decline():
    a = _first("evde", roots={"ev"})
    d = analysis_to_dict(a)
    _assert_base(d, "decline", "ev", "noun")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: copula
# ---------------------------------------------------------------------------

def test_kind_copula():
    a = _first("öğrenciydim", roots={"öğrenci"})
    d = analysis_to_dict(a)
    _assert_base(d, "copula", "öğrenci", "noun")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: converb
# ---------------------------------------------------------------------------

def test_kind_converb():
    a = _first("okuyarak", roots={"okumak"})
    d = analysis_to_dict(a)
    _assert_base(d, "converb", "okumak", "verb")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: converb_casina
# ---------------------------------------------------------------------------

def test_kind_converb_casina():
    a = _first("gülercesine", roots={"gülmek"})
    d = analysis_to_dict(a)
    _assert_base(d, "converb_casina", "gülmek", "verb")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: converb_ken
# ---------------------------------------------------------------------------

def test_kind_converb_ken():
    a = _first("gelirken", roots={"gelmek"})
    d = analysis_to_dict(a)
    assert d["kind"] in ("converb_ken", "copula")  # bilerek belirsiz
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: participle
# ---------------------------------------------------------------------------

def test_kind_participle():
    a = _first("okuduğum", roots={"okumak"})
    d = analysis_to_dict(a)
    _assert_base(d, "participle", "okumak", "verb")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: intensify
# ---------------------------------------------------------------------------

def test_kind_intensify():
    a = _first("bembeyaz", roots={"beyaz"})
    d = analysis_to_dict(a)
    _assert_base(d, "intensify", "beyaz", "adj")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: diminutive
# ---------------------------------------------------------------------------

def test_kind_diminutive():
    a = _first("kısacık", roots={"kısa"})
    d = analysis_to_dict(a)
    _assert_base(d, "diminutive", "kısa", "adj")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: ordinal
# ---------------------------------------------------------------------------

def test_kind_ordinal():
    a = _first("birinci", roots={"bir"})
    d = analysis_to_dict(a)
    _assert_base(d, "ordinal", "bir", "num")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: distributive
# ---------------------------------------------------------------------------

def test_kind_distributive():
    a = _first("ikişer", roots={"iki"})
    d = analysis_to_dict(a)
    _assert_base(d, "distributive", "iki", "num")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: conjunction
# ---------------------------------------------------------------------------

def test_kind_conjunction():
    # "da" allomorfu → lemma kanonik "de"
    results = [a for a in analyze("da") if a.kind == "conjunction"]
    assert results
    d = analysis_to_dict(results[0])
    _assert_base(d, "conjunction", "de", "conj")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kind: derivation
# ---------------------------------------------------------------------------

def test_kind_derivation():
    a = _first("gözlük", roots={"göz"})
    d = analysis_to_dict(a)
    _assert_base(d, "derivation", "göz", "noun")
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# chain (zincirli türetme)
# ---------------------------------------------------------------------------

def test_chain_recursive():
    results = analyze("gözlükçülük", roots={"göz"}, max_derivation_depth=5)
    chained = [a for a in results if a.chain]
    assert chained, "zincirli türetme bulunamadı"
    d = analysis_to_dict(chained[0])
    assert len(d["chain"]) > 0
    # chain elemanları da tam schema taşımalı
    for c in d["chain"]:
        assert "schema_version" in c
        assert "lemma" in c
        assert "kind" in c
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# kwargs içinde tuple (voice_chain) → list
# ---------------------------------------------------------------------------

def test_voice_chain_serialized_as_list():
    results = analyze("dövüştürüldü", roots={"dövmek"})
    voice_results = [a for a in results if a.kwargs.get("voice_chain")]
    if not voice_results:
        pytest.skip("voice_chain içeren analiz bulunamadı")
    d = analysis_to_dict(voice_results[0])
    vc = d["kwargs"].get("voice_chain")
    assert isinstance(vc, list), "voice_chain tuple → list çevrilmeli"
    _assert_json_safe(d)


# ---------------------------------------------------------------------------
# hypothetical=True durumu
# ---------------------------------------------------------------------------

def test_hypothetical_true_when_no_roots():
    results = analyze("xyzturkgram")
    assert results
    # roots=None → hepsi hypothetical
    d = analysis_to_dict(results[0])
    assert d["hypothetical"] is True


# ---------------------------------------------------------------------------
# schema_version sabiti
# ---------------------------------------------------------------------------

def test_schema_version_constant():
    assert ANALYSIS_DICT_SCHEMA_VERSION == "1"
    a = _first("okudu", roots={"okumak"})
    d = analysis_to_dict(a)
    assert d["schema_version"] == "1"
