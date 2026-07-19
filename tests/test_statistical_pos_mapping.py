"""_analysis_pos / _analysis_fine_state — gerçek analizler için POS eşlemesi.

Bulgu (docs/superpowers/specs/2026-07-19-statistical-eval-bulgular.md): eski
eşleme postposition/conjunction/number/adjective kind'larını Noun'a indiriyordu
→ HMM coverage'ı %45'e kilitleniyordu. Bu testler gerçek analiz nesnelerinin
doğru major/fine POS'a eşlendiğini sabitler (fake analizler pos alanı taşımaz;
gerçek analiz pos alanına dayanır).
"""
import pytest
from turkgram import analysis as an, lexicon as lx
from turkgram.statistical import (
    _analysis_pos, _analysis_fine_state, _analysis_pos_lex,
    augment_function_candidates, _MULTI_POS_FUNCTION_WORDS,
)


def _full_roots():
    return lx.load(pos={"noun", "verb", "adj", "adv", "pron", "num",
                        "conj", "postp", "det", "interj"})


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


# --- lexicon-aware refinement (_analysis_pos_lex) ---
@pytest.mark.parametrize("token,expected", [
    ("kırmızı", "Adj"),    # leksikon adj; analizör decline(noun)
    ("hızlı",   "Adj"),
    ("iki",     "Num"),
    ("sen",     "Pron"),
])
def test_analysis_pos_lex_refine(token, expected, roots):
    a = _first(token, roots, pos="noun", kind="decline")
    pm = lx.pos_map()
    assert _analysis_pos_lex(a, pm) == expected
    # pos_map=None → düz _analysis_pos (Noun; geriye uyum)
    assert _analysis_pos_lex(a, None) == "Noun"


def test_analysis_pos_lex_preserves_nonnoun(roots):
    """decline-noun olmayan analiz pos_map'ten etkilenmez (için=Postp kalır)."""
    a = _first("için", roots, pos="postp", kind="postposition")
    assert _analysis_pos_lex(a, lx.pos_map()) == "Postp"


# --- B-cover: full-POS roots fonksiyon sözcüklerine aday üretir ---
@pytest.mark.parametrize("token,expected", [
    ("ve", "Conj"), ("ki", "Conj"), ("bu", "Det"), ("o", "Det"),
])
def test_full_roots_function_words(token, expected):
    """conj/det POS'ları roots'a alınınca fonksiyon sözcükleri decline(noun) üretir;
    _analysis_pos_lex pos_map ile doğru sınıfa refine eder (varsayılan load()'da NO-REAL)."""
    full = lx.load(pos={"noun", "verb", "adj", "adv", "pron", "num",
                        "conj", "postp", "det", "interj"})
    pm = lx.pos_map()
    cands = [a for a in an.analyze(token, roots=full) if not a.hypothetical]
    assert cands, f"{token!r} full-roots'ta aday üretmeli"
    assert expected in {_analysis_pos_lex(a, pm) for a in cands}


# --- çok-POS fonksiyon sözcüğü aday enjeksiyonu (augment_function_candidates) ---
@pytest.mark.parametrize("token,expected_subset", [
    ("çok",  {"Adverb", "Adj"}),
    ("bir",  {"Det", "Num"}),
    ("o",    {"Pron", "Det"}),
    ("her",  {"Det"}),
    ("ne",   {"Pron", "Adj"}),
    ("en",   {"Adverb"}),
])
def test_augment_function_candidates(token, expected_subset):
    """Çok-POS fonksiyon sözcüğü → tüm POS seçenekleri aday olur (HMM ayırır)."""
    full = _full_roots()
    pm = lx.pos_map()
    cand = [a for a in an.analyze(token, roots=full) if not a.hypothetical]
    aug = augment_function_candidates(token, cand, pm)
    poss = {_analysis_pos_lex(a, pm) for a in aug}
    assert expected_subset <= poss, f"{token}: {poss} ⊉ {expected_subset}"


def test_augment_preserves_and_additive():
    """Fonksiyon sözcüğü olmayan token dokunulmaz; augment yalnız EKLER (recall-güvenli)."""
    full = _full_roots()
    pm = lx.pos_map()
    cand = [a for a in an.analyze("kitap", roots=full) if not a.hypothetical]
    aug = augment_function_candidates("kitap", cand, pm)
    assert len(aug) == len(cand)          # kitap funcword değil → değişmez
    assert all(x in aug for x in cand)    # additive


def test_augment_pronoun_oblique():
    """Bağımsız zamir eğik biçimi → Pron adayı eklenir (onu = o+acc)."""
    full = _full_roots()
    pm = lx.pos_map()
    cand = [a for a in an.analyze("onu", roots=full) if not a.hypothetical]
    aug = augment_function_candidates("onu", cand, pm)
    assert "Pron" in {_analysis_pos_lex(a, pm) for a in aug}


def test_multi_pos_table_labels_valid():
    """Tablo yalnız model pos_set'te bulunan geçerli major etiketler içerir."""
    from turkgram.statistical import load_model
    valid = load_model().pos_set | {"Noun", "Verb"}
    for word, opts in _MULTI_POS_FUNCTION_WORDS.items():
        for p in opts:
            assert p in valid, f"{word}: geçersiz POS {p!r}"


@pytest.mark.parametrize("token", ["her", "hep"])
def test_augment_no_spurious_pron(token):
    """her(belirteç)/hep(zarf) zamir DEĞİL → bare biçimde Pron adayı enjekte edilmez
    (hakem HIGH regresyon kilidi)."""
    full = _full_roots()
    pm = lx.pos_map()
    cand = [a for a in an.analyze(token, roots=full) if not a.hypothetical]
    aug = augment_function_candidates(token, cand, pm)
    assert "Pron" not in {_analysis_pos_lex(a, pm) for a in aug}
