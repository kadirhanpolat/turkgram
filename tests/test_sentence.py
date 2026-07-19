"""test_sentence.py — cümle çözümleme runner (SPEC docs/superpowers/specs/
2026-07-20-cumle-cozumleme-design.md §8).

TÜR (cümle türü) TAM sınanır (7 eksen). ÖGE (öge etiketleme) alias dahil TAM sınanır,
İKİ dokümante sınır DIŞINDA (proper-noun-adj homograf + SOV; SPEC §6). Sınırlı vakalarda
yalnız TÜR sınanır (öge xfail-benzeri, ideal golden'da korunur).
"""
import pytest

from turkgram import lexicon
from turkgram.sentence import analyze_sentence
from tests.golden_sentence import GOLDEN_SENTENCES

# SPEC §6 dokümante sınır: proper-noun-adj homograf (pos_map: ali/çocuk=adj) + SOV
# yalın-nom disambiguation. Öge etiketleme bu 2 cümlede ideali tutturamaz — TÜR yine tam.
# Parser/disambiguation iyileşince bedava düzelir (motor DEĞİŞMEDEN).
_OGE_KNOWN_LIMITS = frozenset({
    "Ali kitabı okudu",         # Ali(adj-homograf) + kitabı(acc) yanlış gruplanır
    "Çocuk topu bahçede oynadı",  # Çocuk(adj) + topu(nom disambig) yanlış gruplanır
})

_ROOTS = lexicon.load()

_IDS = [g["text"] for g in GOLDEN_SENTENCES]


@pytest.mark.parametrize("g", GOLDEN_SENTENCES, ids=_IDS)
def test_sentence_type(g):
    """Cümle türü 7 ekseni TAM (tüm golden)."""
    st = analyze_sentence(g["text"], roots=_ROOTS).sentence_type
    got = (st.yuklem_turu, st.yuklem_yeri, st.olumluluk, st.soru,
           st.kip, st.yapi, st.eksiltili)
    t = g["type"]
    exp = (t["yuklem_turu"], t["yuklem_yeri"], t["olumluluk"], t["soru"],
           t["kip"], t["yapi"], t["eksiltili"])
    assert got == exp


@pytest.mark.parametrize("g", GOLDEN_SENTENCES, ids=_IDS)
def test_sentence_elements(g):
    """Öge etiketleme (alias dahil) TAM — dokümante 2 sınır hariç (SPEC §6)."""
    if g["text"] in _OGE_KNOWN_LIMITS:
        pytest.skip("dokümante sınır: proper-noun-adj homograf + SOV disambiguation")
    sa = analyze_sentence(g["text"], roots=_ROOTS)
    got = [(e.label, e.tokens, e.head_id, e.aliases) for e in sa.elements]
    exp = [(l, t, h, a) for (l, t, h, a) in g["elements"]]
    assert got == exp


def test_known_limits_still_run():
    """Sınırlı vakalar çökmeden çalışır + TÜR yine doğru (regresyon kilidi)."""
    for text in _OGE_KNOWN_LIMITS:
        sa = analyze_sentence(text, roots=_ROOTS)
        assert sa.sentence_type.yuklem_turu == "fiil"
        assert len(sa.elements) >= 2


def test_alias_dolayli_tumlec():
    """dolaylı tümleç → 'yer tamlayıcısı' alias taşır (KARMA gelenek, SPEC §4)."""
    sa = analyze_sentence("Ben eve gidiyorum", roots=_ROOTS)
    dt = [e for e in sa.elements if e.label == "dolaylı tümleç"]
    assert dt and dt[0].aliases == ("yer tamlayıcısı",)


def test_tr_api_equivalence():
    """tr.cümle_çözümle == sentence.analyze_sentence."""
    from turkgram import tr
    a = tr.cümle_çözümle("Hava güzel", kökler=_ROOTS)
    b = analyze_sentence("Hava güzel", roots=_ROOTS)
    assert a == b


def test_empty_and_roots_none():
    """Boş metin + roots=None çökmez (gürültü modu)."""
    assert analyze_sentence("", roots=_ROOTS).sentence_type.eksiltili
    # roots=None: etiketler güvenilmez ama çökmemeli
    analyze_sentence("Ben eve gidiyorum", roots=None)
