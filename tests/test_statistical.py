"""İstatistiksel disambiguation testleri (Faz 2b, madde A, Artım-1).

SPEC: spec/statistical-disambiguation-spec.md
Golden: tests/golden_statistical.py (motor-körü Artım-1).

Üç aile:
  1. Eşleme golden'ı — parse_oflazer doğruluğu (SPEC §5)
  2. Sayım golden'ı — model_from_counts çıktısı (SPEC §6 sayım golden'ı)
  3. Viterbi golden'ı — viterbi() yolu (SPEC §6 Viterbi golden'ı)
"""
import math
import pytest

from turkgram.statistical import (
    parse_oflazer,
    model_from_counts,
    rank_statistical,
    viterbi,
    StatModel,
    _SENTENCE_START,
    _SENTENCE_END,
    _LOG_UNK,
)
from tests.golden_statistical import (
    MAPPING_CASES,
    MINI_CORPUS,
    EXPECTED_EMISSION_COUNTS,
    EXPECTED_TRANSITION_COUNTS,
    VITERBI_CASES,
)


# ---------------------------------------------------------------------------
# AİLE 1 — Eşleme golden'ı (parse_oflazer, Artım-1)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("oflazer_str,exp_lemma,exp_pos", MAPPING_CASES)
def test_parse_oflazer_mapping(oflazer_str, exp_lemma, exp_pos):
    """parse_oflazer → beklenen (lemma, major_pos)."""
    lemma, pos = parse_oflazer(oflazer_str)
    assert lemma == exp_lemma, (
        f"Etiket={oflazer_str!r}: lemma={lemma!r}, beklenen={exp_lemma!r}"
    )
    assert pos == exp_pos, (
        f"Etiket={oflazer_str!r}: pos={pos!r}, beklenen={exp_pos!r}"
    )


# ---------------------------------------------------------------------------
# AİLE 2 — Sayım golden'ı
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mini_corpus_counts():
    """Mini-korpustan emisyon + geçiş sayımlarını üret (parse_oflazer kullanır)."""
    emission: dict = {}
    transition: dict = {}

    for sentence in MINI_CORPUS:
        prev_pos = _SENTENCE_START
        for surface, oflazer_str in sentence:
            _, pos = parse_oflazer(oflazer_str)
            surf_low = surface.lower()

            # Emisyon
            key = (pos, surf_low)
            emission[key] = emission.get(key, 0) + 1

            # Geçiş
            tkey = (prev_pos, pos)
            transition[tkey] = transition.get(tkey, 0) + 1
            prev_pos = pos

        # Cümle sonu
        tkey = (prev_pos, _SENTENCE_END)
        transition[tkey] = transition.get(tkey, 0) + 1

    return emission, transition


def test_emisyon_sayimlari(mini_corpus_counts):
    """Sayım golden'ı: motorun ürettiği emisyon sayımları beklenenle eşleşmeli."""
    emission, _ = mini_corpus_counts
    for (pos, surf), expected_cnt in EXPECTED_EMISSION_COUNTS.items():
        actual = emission.get((pos, surf.lower()), 0)
        assert actual == expected_cnt, (
            f"Emisyon ({pos!r},{surf!r}): {actual} != {expected_cnt}"
        )


def test_gecis_sayimlari(mini_corpus_counts):
    """Sayım golden'ı: motorun ürettiği geçiş sayımları beklenenle eşleşmeli."""
    _, transition = mini_corpus_counts
    for (prev, nxt), expected_cnt in EXPECTED_TRANSITION_COUNTS.items():
        actual = transition.get((prev, nxt), 0)
        assert actual == expected_cnt, (
            f"Geçiş ({prev!r},{nxt!r}): {actual} != {expected_cnt}"
        )


def test_model_from_counts_log_prob_araliği(mini_corpus_counts):
    """model_from_counts → log-problar ≤ 0 olmalı (log olasılık ≤ 0)."""
    emission, transition = mini_corpus_counts
    model = model_from_counts(emission, transition)
    for lp in model.emission.values():
        assert lp <= 0.0 + 1e-12, f"Emisyon log-prob > 0: {lp}"
    for lp in model.transition.values():
        assert lp <= 0.0 + 1e-12, f"Geçiş log-prob > 0: {lp}"


def test_model_from_counts_bilinmeyen_surface(mini_corpus_counts):
    """Bilinmeyen (pos, surface) → _LOG_UNK (smoothing)."""
    emission, transition = mini_corpus_counts
    model = model_from_counts(emission, transition)
    assert model.emit_lp("Noun", "zzzbilinmeyen") == _LOG_UNK
    assert model.trans_lp("Noun", "ZZZUNKNOWN") == _LOG_UNK


def test_normalize_emisyon(mini_corpus_counts):
    """Belirli bir pos için emisyon dağılımı exp(lp) toplamı ≈ 1 (yalnız bilinen yüzeyler)."""
    emission, transition = mini_corpus_counts
    model = model_from_counts(emission, transition)

    # Punc yalnız "." → exp(lp["."]) ≈ 1.0 (tek yüzey, Laplace küçük)
    lp_punc = model.emit_lp("Punc", ".")
    # Prob Punc → . ≈ (4+ε)/(4+ε) ≈ 1 (tek yüzey, Laplace negligible)
    assert math.exp(lp_punc) > 0.9, f"Punc/. prob çok düşük: {math.exp(lp_punc)}"


# ---------------------------------------------------------------------------
# AİLE 3 — Viterbi golden'ı
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def viterbi_model(mini_corpus_counts):
    """Mini-korpus sayımlarından Viterbi için model."""
    emission, transition = mini_corpus_counts
    return model_from_counts(emission, transition)


class _FakeAnalysis:
    """Viterbi golden'ı için sahte Analysis nesnesi (sadece kind gerekli)."""
    def __init__(self, lemma: str, kind: str):
        self.lemma = lemma
        self.kind = kind
        self.kwargs = {}

    def __repr__(self):
        return f"FA({self.lemma!r},{self.kind!r})"


def _kind_for_pos(pos: str) -> str:
    """major_pos → _analysis_pos'u doğru çalıştıracak kind."""
    _MAP = {
        "Noun": "decline",
        "Prop": "decline",  # Artım-1 Prop → Noun gibi ele alınır (decline)
        "Verb": "conjugate",
        "Adj":  "decline",  # sıfat → Artım-1'de Noun'a düşer; burada nominal eş.
        "Adverb": "decline",
        "Num":  "decline",
        "Det":  "decline",
        "Pron": "decline",
        "Punc": "decline",
        "Conj": "decline",
        "Interj": "decline",
    }
    return _MAP.get(pos, "decline")


@pytest.mark.parametrize("tokens,analyses_input,expected_pos_seq", VITERBI_CASES)
def test_viterbi_pos_dizisi(tokens, analyses_input, expected_pos_seq, viterbi_model):
    """Viterbi yolu — beklenen POS dizisiyle eşleşmeli (Artım-1, SPEC §6)."""
    # analyses_per_token: [[FakeAnalysis, ...], ...]
    aper = []
    for cands in analyses_input:
        aper.append([_FakeAnalysis(lemma, _kind_for_pos(pos)) for lemma, pos in cands])

    result = viterbi(tokens, aper, viterbi_model)

    # Her token'ın ilk adayının kind'ından pos'u al
    assert len(result) == len(tokens)
    for i, (ranked, exp_pos) in enumerate(zip(result, expected_pos_seq)):
        assert ranked, f"Token {i!r} ({tokens[i]!r}): boş sonuç"
        from turkgram.statistical import _analysis_pos
        top_pos = _analysis_pos(ranked[0])
        # Artım-1'de Prop ve Noun ayrımı yapmıyoruz (ikisi de Noun'a düşer)
        # → beklenende Prop/Noun farklıysa bunu normalize et
        _NORM = {"Prop": "Noun", "Adj": "Noun", "Adverb": "Noun", "Num": "Noun",
                 "Det": "Noun", "Pron": "Noun", "Punc": "Noun", "Conj": "Noun",
                 "Interj": "Noun"}
        norm_top = _NORM.get(top_pos, top_pos)
        norm_exp = _NORM.get(exp_pos, exp_pos)
        assert norm_top == norm_exp, (
            f"Token {i} ({tokens[i]!r}): Viterbi POS={top_pos!r} (norm={norm_top!r}) "
            f"!= beklenen={exp_pos!r} (norm={norm_exp!r})"
        )


def test_viterbi_uzunluk_uyumu(viterbi_model):
    """viterbi() çıktı uzunluğu tokens uzunluğuna eşit."""
    tokens = ["üç", "gelin"]
    aper = [
        [_FakeAnalysis("üç", "decline")],
        [_FakeAnalysis("gelin", "decline"), _FakeAnalysis("gel", "conjugate")],
    ]
    result = viterbi(tokens, aper, viterbi_model)
    assert len(result) == len(tokens)


def test_viterbi_bos_giris(viterbi_model):
    """Boş token listesi → boş sonuç."""
    assert viterbi([], [], viterbi_model) == []


def test_viterbi_bos_aday(viterbi_model):
    """Boş aday listesi olan token → çıkışta da boş liste."""
    tokens = ["bilinmeyen", "geldi"]
    aper = [[], [_FakeAnalysis("gel", "conjugate")]]
    result = viterbi(tokens, aper, viterbi_model)
    assert len(result) == 2
    assert result[0] == []
    assert len(result[1]) == 1


def test_recall_guvenli_viterbi(viterbi_model):
    """viterbi() aday sayısını DEĞİŞTİRMEMELİ (recall-güvenli)."""
    tokens = ["üç", "gelin"]
    aper = [
        [_FakeAnalysis("üç", "decline")],
        [_FakeAnalysis("gelin", "decline"), _FakeAnalysis("gel", "conjugate")],
    ]
    result = viterbi(tokens, aper, viterbi_model)
    for i, (orig, out) in enumerate(zip(aper, result)):
        assert len(orig) == len(out), f"Token {i}: aday sayısı değişti"
        assert set(id(a) for a in orig) == set(id(a) for a in out), (
            f"Token {i}: farklı nesneler (ekleme/silme)"
        )


# ---------------------------------------------------------------------------
# Arayüz sözleşmesi
# ---------------------------------------------------------------------------

def test_rank_statistical_bos():
    """rank_statistical([]) → boş liste."""
    model = StatModel()
    assert rank_statistical([], model, surface="test") == []


def test_rank_statistical_tek_aday(mini_corpus_counts):
    """rank_statistical() tek adayla → [aday] (sıra trivial)."""
    emission, transition = mini_corpus_counts
    model = model_from_counts(emission, transition)
    a = _FakeAnalysis("ev", "decline")
    result = rank_statistical([a], model, surface="ev")
    assert result == [a]


def test_model_girdi_mutasyonu_yok(mini_corpus_counts):
    """rank_statistical / viterbi → girdi listesi değişmez."""
    emission, transition = mini_corpus_counts
    model = model_from_counts(emission, transition)
    a1 = _FakeAnalysis("gelin", "decline")
    a2 = _FakeAnalysis("gel", "conjugate")
    orig = [a1, a2]
    snapshot = list(orig)
    rank_statistical(orig, model, surface="gelin")
    assert orig == snapshot
