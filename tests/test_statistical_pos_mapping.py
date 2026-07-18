"""_analysis_pos / _analysis_fine_state — gerçek analizler için POS eşlemesi.

Bulgu (docs/superpowers/specs/2026-07-19-statistical-eval-bulgular.md): eski
eşleme postposition/conjunction/number/adjective kind'larını Noun'a indiriyordu
→ HMM coverage'ı %45'e kilitleniyordu. Bu testler gerçek analiz nesnelerinin
doğru major/fine POS'a eşlendiğini sabitler (fake analizler pos alanı taşımaz;
gerçek analiz pos alanına dayanır).
"""
import pytest
from turkgram import analysis as an, lexicon as lx
from turkgram.statistical import _analysis_pos, _analysis_fine_state


@pytest.fixture(scope="module")
def roots():
    return lx.load()


def _first(token, roots, *, pos=None, kind=None):
    """token analizlerinden (pos/kind filtreli) ilk gerçek analizi döndür."""
    for a in an.analyze(token, roots=roots):
        if a.hypothetical:
            continue
        if pos is not None and a.pos != pos:
            continue
        if kind is not None and a.kind != kind:
            continue
        return a
    raise AssertionError(f"{token!r} için pos={pos} kind={kind} analiz yok")


# --- major POS (_analysis_pos) ---
@pytest.mark.parametrize("token,pos,kind,expected", [
    ("için",    "postp", "postposition", "Postp"),
    ("gibi",    "postp", "postposition", "Postp"),
    ("de",      "conj",  "conjunction",  "Conj"),
    ("da",      "conj",  "conjunction",  "Conj"),
    ("birinci", "num",   "ordinal",      "Num"),
    ("ikişer",  "num",   "distributive", "Num"),
    ("bembeyaz","adj",   "intensify",    "Adj"),
    ("kısacık", "adj",   "diminutive",   "Adj"),
    ("ev",      "noun",  "decline",      "Noun"),
    ("geldi",   "verb",  "conjugate",    "Verb"),
])
def test_analysis_pos_major(token, pos, kind, expected, roots):
    a = _first(token, roots, pos=pos, kind=kind)
    assert _analysis_pos(a) == expected


# --- fine state (_analysis_fine_state) ---
@pytest.mark.parametrize("token,pos,kind,expected", [
    ("için",    "postp", "postposition", "Postp"),
    ("de",      "conj",  "conjunction",  "Conj"),
    ("birinci", "num",   "ordinal",      "Num"),
    ("bembeyaz","adj",   "intensify",    "Adj"),
])
def test_analysis_fine_state_wordclass(token, pos, kind, expected, roots):
    a = _first(token, roots, pos=pos, kind=kind)
    assert _analysis_fine_state(a) == expected


def test_fake_analysis_backward_compat():
    """pos alanı olmayan (fake) analiz → Noun (geriye uyum: viterbi golden'ı)."""
    class _Fake:
        kind = "decline"
        kwargs: dict = {}
    assert _analysis_pos(_Fake()) == "Noun"
    assert _analysis_fine_state(_Fake()) == "Noun"
