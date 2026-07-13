"""Artım-2 istatistiksel disambiguation testleri (Faz 2b, madde A).

SPEC: spec/statistical-disambiguation-spec.md §5 (Artım-2)
Golden: tests/golden_statistical_artim2.py (motor-körü kuruldu).

Üç aile:
  1. Tam eksen eşleme golden'ı — parse_oflazer_full() doğruluğu
  2. İnce-taneli durum golden'ı — _fine_state_from_oflazer() doğruluğu
  3. Cümle eksen karşılaştırma — analyze() sonuçları turkgram eksenleriyle eşleşir
"""
import pytest

from turkgram.statistical import (
    parse_oflazer_full,
    _fine_state_from_oflazer,
    _analysis_fine_state,
)
from tests.golden_statistical_artim2 import (
    AXIS_MAPPING_CASES,
    FINE_STATE_CASES,
    SENTENCE_AXIS_CASES,
)


# ---------------------------------------------------------------------------
# AİLE 1 — Tam eksen eşleme golden'ı (parse_oflazer_full)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("oflazer_str,exp_lemma,exp_pos,exp_axes", AXIS_MAPPING_CASES)
def test_parse_oflazer_full_axes(oflazer_str, exp_lemma, exp_pos, exp_axes):
    """parse_oflazer_full → (lemma, major_pos, axes_dict) beklenenle eşleşmeli."""
    lemma, pos, axes = parse_oflazer_full(oflazer_str)

    assert lemma == exp_lemma, (
        f"Etiket={oflazer_str!r}: lemma={lemma!r} != {exp_lemma!r}"
    )
    assert pos == exp_pos, (
        f"Etiket={oflazer_str!r}: pos={pos!r} != {exp_pos!r}"
    )

    # Beklenen eksenler → gerçek eksen dict'inin alt-kümesi olmalı
    # (bilinmeyen etiketler sessizce atlanır; beklenenin tümü bulunmalı)
    for key, val in exp_axes.items():
        actual_val = axes.get(key)
        assert actual_val == val, (
            f"Etiket={oflazer_str!r}: axes[{key!r}]={actual_val!r} != {val!r}\n"
            f"  Gerçek axes: {axes}"
        )


def test_parse_oflazer_full_voice_sirasi():
    """Voice zinciri sırası korunmalı (SPEC §5 — eksen tek-yönlü sözlük)."""
    s = "döv+Verb^DB+Verb+Recip^DB+Verb+Caus^DB+Verb+Pass+Pos+Past+A3sg"
    _, _, axes = parse_oflazer_full(s)
    assert axes.get("voice") == ["recip", "caus", "pass"], (
        f"Voice sırası bozuk: {axes.get('voice')!r}"
    )


def test_parse_oflazer_full_pos_negative_atlanir():
    """Pos etiketi → axes'te 'negative' anahtarı YOK olmalı."""
    _, _, axes = parse_oflazer_full("gel+Verb+Pos+Past+A3sg")
    assert "negative" not in axes, f"Pos axes'te negative bıraktı: {axes}"


def test_parse_oflazer_full_pnon_atlanir():
    """Pnon etiketi → axes'te 'possessive' anahtarı YOK olmalı."""
    _, _, axes = parse_oflazer_full("hazine+Noun+A3sg+Pnon+Nom")
    assert "possessive" not in axes, f"Pnon axes'te possessive bıraktı: {axes}"


def test_parse_oflazer_full_a3sg_number_atlanir():
    """A3sg (tekil) → axes'te 'number' anahtarı YOK olmalı."""
    _, _, axes = parse_oflazer_full("kitap+Noun+A3sg+Pnon+Nom")
    assert "number" not in axes, f"A3sg axes'te number bıraktı: {axes}"


def test_parse_oflazer_full_a3pl_number_var():
    """A3pl (çoğul) → axes['number'] == 'pl' olmalı."""
    _, _, axes = parse_oflazer_full("kitap+Noun+A3pl+Pnon+Nom")
    assert axes.get("number") == "pl", f"A3pl number bırakmadı: {axes}"


def test_parse_oflazer_full_bos():
    """Boş dizge → ('', 'unmapped', {})."""
    lemma, pos, axes = parse_oflazer_full("")
    assert lemma == "" and pos == "unmapped" and axes == {}


def test_parse_oflazer_full_bilinmeyen_etiket():
    """Bilinmeyen etiket sessizce atlanır; diğer eksenler bozulmaz."""
    _, _, axes = parse_oflazer_full("test+Verb+Pos+Past+XYZ+A3sg")
    assert axes.get("tense") == "past"
    assert axes.get("person") == "3sg"
    # XYZ bilinmiyor → axes'te yok (sessiz)
    assert "XYZ" not in axes


# ---------------------------------------------------------------------------
# AİLE 2 — İnce-taneli durum golden'ı (_fine_state_from_oflazer)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("oflazer_str,expected_fine_state", FINE_STATE_CASES)
def test_fine_state_from_oflazer(oflazer_str, expected_fine_state):
    """_fine_state_from_oflazer → beklenen ince durum dizgesi."""
    result = _fine_state_from_oflazer(oflazer_str)
    assert result == expected_fine_state, (
        f"Etiket={oflazer_str!r}: fine_state={result!r} != {expected_fine_state!r}"
    )


def test_fine_state_verb_tense_detayi():
    """Verb ince durumları tüm tense değerlerini kapsamalı."""
    cases = [
        ("gel+Verb+Pos+Past+A3sg",  "Verb:past"),
        ("gel+Verb+Pos+Prog1+A3sg", "Verb:pres"),
        ("gel+Verb+Pos+Fut+A3sg",   "Verb:fut"),
        ("gel+Verb+Pos+Aor+A3sg",   "Verb:aorist"),
        ("gel+Verb+Pos+Narr+A3sg",  "Verb:evid"),
        ("gel+Verb+Pos+Cond+A3sg",  "Verb:cond"),
        ("gel+Verb+Pos+Opt+A3sg",   "Verb:opt"),
        ("gel+Verb+Pos+Imp+A2sg",   "Verb:imp"),
        ("gel+Verb+Pos+Neces+A3sg", "Verb:neces"),
    ]
    for oflazer_str, exp in cases:
        result = _fine_state_from_oflazer(oflazer_str)
        assert result == exp, f"{oflazer_str!r}: {result!r} != {exp!r}"


def test_fine_state_noun_case_detayi():
    """Noun ince durumları tüm case değerlerini kapsamalı."""
    cases = [
        ("ev+Noun+A3sg+Pnon+Nom", "Noun:nom"),
        ("ev+Noun+A3sg+Pnon+Acc", "Noun:acc"),
        ("ev+Noun+A3sg+Pnon+Dat", "Noun:dat"),
        ("ev+Noun+A3sg+Pnon+Loc", "Noun:loc"),
        ("ev+Noun+A3sg+Pnon+Abl", "Noun:abl"),
        ("ev+Noun+A3sg+Pnon+Gen", "Noun:gen"),
        ("ev+Noun+A3sg+Pnon+Ins", "Noun:ins"),
    ]
    for oflazer_str, exp in cases:
        result = _fine_state_from_oflazer(oflazer_str)
        assert result == exp, f"{oflazer_str!r}: {result!r} != {exp!r}"


def test_fine_state_ettirgen_tense_korunur():
    """^DB ettirgen zincirinde son tense korunmalı."""
    result = _fine_state_from_oflazer(
        "rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg"
    )
    assert result == "Verb:past"


def test_fine_state_adj():
    """Adj → 'Adj' (ince durum yok)."""
    assert _fine_state_from_oflazer("yap+Verb+Pos^DB+Adj+PresPart") == "Adj"
    assert _fine_state_from_oflazer("geçen+Adj") == "Adj"


def test_fine_state_adverb():
    """Adverb → 'Adverb'."""
    assert _fine_state_from_oflazer("geri+Adverb") == "Adverb"


# ---------------------------------------------------------------------------
# AİLE 3 — Cümle eksen karşılaştırma (analyze + _analysis_fine_state)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def roots():
    from turkgram import lexicon as lx
    return lx.load()


@pytest.fixture(scope="module")
def pm():
    from turkgram import lexicon as lx
    return lx.pos_map()


@pytest.mark.parametrize("tokens,expected_per_token", SENTENCE_AXIS_CASES)
def test_sentence_axis_top1(tokens, expected_per_token, roots, pm):
    """Cümle top-1 analizi — beklenen eksenler alt-küme olarak eşleşmeli."""
    from turkgram import analysis as an, disambiguation as dis, context as ctx

    per_token = [an.analyze(t, roots=roots) for t in tokens]
    ranked    = ctx.rank_in_context(tokens, per_token, pos=pm)

    for i, (ranked_cands, exp_axes) in enumerate(zip(ranked, expected_per_token)):
        if exp_axes is None:
            continue  # bu token test dışı

        assert ranked_cands, (
            f"Token {tokens[i]!r} ({i}): boş aday listesi"
        )
        top = ranked_cands[0]
        actual_kwargs = dict(getattr(top, "kwargs", {}))

        for key, val in exp_axes.items():
            assert actual_kwargs.get(key) == val, (
                f"Token {tokens[i]!r} ({i}): kwargs[{key!r}]={actual_kwargs.get(key)!r} "
                f"!= {val!r} | lemma={top.lemma!r}, kind={top.kind!r}"
            )


# ---------------------------------------------------------------------------
# _analysis_fine_state birim testleri (Analysis nesnelerinden fine state)
# ---------------------------------------------------------------------------

class _FA:
    """Sahte Analysis — fine state testleri için."""
    def __init__(self, kind, kwargs=None):
        self.kind   = kind
        self.kwargs = kwargs or {}
        self.lemma  = "test"


def test_analysis_fine_state_conjugate():
    """conjugate → 'Verb:{tense}'."""
    a = _FA("conjugate", {"tense": "past", "person": "3sg"})
    assert _analysis_fine_state(a) == "Verb:past"


def test_analysis_fine_state_conjugate_pres():
    a = _FA("conjugate", {"tense": "pres", "person": "1sg"})
    assert _analysis_fine_state(a) == "Verb:pres"


def test_analysis_fine_state_converb_base():
    """converb_ken base → 'Verb:{base}'."""
    a = _FA("converb_ken", {"base": "aorist"})
    assert _analysis_fine_state(a) == "Verb:aorist"


def test_analysis_fine_state_decline_case():
    """decline → 'Noun:{case}'."""
    a = _FA("decline", {"case": "dat"})
    assert _analysis_fine_state(a) == "Noun:dat"


def test_analysis_fine_state_decline_no_case():
    """decline (case yok) → 'Noun'."""
    a = _FA("decline", {})
    assert _analysis_fine_state(a) == "Noun"


def test_analysis_fine_state_participle_adj():
    """participle (pres/fut/past) → 'Adj' (sıfat-fiil)."""
    for ptype in ("pres", "fut", "past", "aorist"):
        a = _FA("participle", {"ptype": ptype})
        assert _analysis_fine_state(a) == "Adj", f"ptype={ptype}"


def test_analysis_fine_state_participle_noun():
    """participle (inf1/inf2/inf3/ness) → 'Noun:{case}' veya 'Noun'."""
    a = _FA("participle", {"ptype": "inf2", "case": "acc"})
    assert _analysis_fine_state(a) == "Noun:acc"

    a2 = _FA("participle", {"ptype": "inf1"})
    assert _analysis_fine_state(a2) == "Noun"


def test_analysis_fine_state_copula():
    """copula → 'Noun' (Artım-2 nominal ekfiil)."""
    a = _FA("copula", {"aux": "hikaye", "person": "1sg"})
    assert _analysis_fine_state(a) == "Noun"
