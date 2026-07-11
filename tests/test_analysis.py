"""Çözümleyici — golden koşucusu + sözleşme testleri (Faz 2a).

PYTHONUTF8=1 python -m pytest tests/test_analysis.py -q
"""
import pytest
from turkgram import analysis as an
from tests.golden_analysis import GOLDEN_ANALYSIS, BATTERY_LEXICON
from tests.golden_segments import GOLDEN_SEGMENTS


# ---------------------------------------------------------------------------
# Yardımcı: voice_chain list→tuple normalizer (golden list, Analysis tuple)
# ---------------------------------------------------------------------------

def _norm_kwargs(kw: dict) -> dict:
    """voice_chain list veya tuple → tuple; diğerleri değişmez."""
    return {k: (tuple(v) if k == "voice_chain" and isinstance(v, (list, tuple)) else v)
            for k, v in kw.items()}


def _norm_key(lemma: str, pos: str, kind: str, kwargs: dict) -> tuple:
    """Karşılaştırma anahtarı — voice_chain normalize edilmiş."""
    return (lemma, pos, kind, tuple(sorted(_norm_kwargs(kwargs).items())))


# ---------------------------------------------------------------------------
# Sözleşme testleri (Task 4)
# ---------------------------------------------------------------------------

def test_analysis_frozen_dataclass():
    s = an.Segment(surface="duğ", label="DIk", span=(3, 6))
    a = an.Analysis(lemma="okumak", pos="verb", kind="participle",
                    kwargs={"ptype": "dik", "possessive": "1sg"},
                    segments=(s,), hypothetical=True)
    with pytest.raises(Exception):   # frozen
        a.lemma = "x"  # type: ignore[misc]


def test_gecersiz_girdi():
    for bad in ("", "   ", None, 42):
        with pytest.raises(ValueError):
            an.analyze(bad)  # type: ignore[arg-type]


def test_bilinmeyen_pos():
    with pytest.raises(ValueError, match="pos"):
        an.analyze("okuyor", pos="olmayan")


def test_cozumsuz_bos_liste():
    result = an.analyze("zzzt")
    assert result == []


def test_cok_token_mesru_degil():
    # 3 token → gürültü → boş
    assert an.analyze("git git git") == []


# ---------------------------------------------------------------------------
# İç birim testleri (Task 5)
# ---------------------------------------------------------------------------

def test_kok_adaylari_mutasyon():
    cands = an._root_candidates("gidiyor")
    assert "gitmek" in cands or "git" in cands or "gid" in cands
    # d→t tersi: "gid" önek → "git" mutasyon adayı
    assert any(k in cands for k in ("gitmek", "git"))

    cands2 = an._root_candidates("yiyor")
    # ye_de: i→e tersi, "yi" → "ye"
    assert "yemek" in cands2 or "ye" in cands2


def test_ses_filtresi_pres():
    # 'yor' içermeyen yüzeyde pres hücreleri hiç enumerate edilmez
    hyps = an._enumerate_conjugate("geldi", "gel", "gelmek")
    assert all(h.get("tense") != "pres" for h in hyps)


def test_cati_zinciri_kapali_kume():
    assert len(an._VOICE_CHAINS) == 24


def test_voice_chains_icerigi():
    # Boş zincir (çatısız) dahil
    assert () in an._VOICE_CHAINS
    # caus×3 + pass zinciri
    assert ("caus", "caus", "caus", "pass") in an._VOICE_CHAINS
    # refl + pass
    assert ("refl", "pass") in an._VOICE_CHAINS
    # recip + caus
    assert ("recip", "caus") in an._VOICE_CHAINS


# ---------------------------------------------------------------------------
# Precision golden: TAM küme eşitliği (Task 6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("surface", sorted(GOLDEN_ANALYSIS))
def test_golden_precision_tam_kume(surface):
    got = {_norm_key(a.lemma, a.pos, a.kind, dict(a.kwargs))
           for a in an.analyze(surface, roots=BATTERY_LEXICON)}
    want = {_norm_key(g["lemma"], g["pos"], g["kind"], g["kwargs"])
            for g in GOLDEN_ANALYSIS[surface]}
    missing = want - got
    extra = got - want
    assert got == want, (
        f"surface={surface!r}\n"
        f"  EKSİK (recall): {missing}\n"
        f"  FAZLA (precision): {extra}"
    )


# ---------------------------------------------------------------------------
# Segmentasyon golden (Task 6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("surface", sorted(GOLDEN_SEGMENTS))
def test_golden_segments(surface):
    entry = GOLDEN_SEGMENTS[surface]
    lemma = entry["lemma"]
    expected_segs = entry["segments"]

    results = an.analyze(surface, roots={lemma})
    assert results, f"Çözüm bulunamadı: {surface!r} (lemma={lemma!r})"

    # Tek analiz beklentisi — ancak bazı yüzeyler belirsiz olabilir (SPEC §8)
    if len(results) > 1:
        # Beklenen segmentlerle eşleşen analizi bul
        matching = [r for r in results
                    if [(s.surface, s.label) for s in r.segments] == expected_segs]
        assert matching, (
            f"Belirsiz yüzey, beklenen segmentler bulunamadı: {surface!r}\n"
            f"  beklenen: {expected_segs}\n"
            f"  mevcut analizler:\n"
            + "\n".join(f"    {[(s.surface, s.label) for s in r.segments]}" for r in results)
        )
        a = matching[0]
    else:
        a = results[0]

    got_segs = [(s.surface, s.label) for s in a.segments]
    assert got_segs == expected_segs, (
        f"surface={surface!r}\n  beklenen: {expected_segs}\n  alınan:   {got_segs}"
    )
    # Span garantisi: dilimler birleşince gövde-token
    body_token = surface.split()[-1]
    joined = "".join(s.surface for s in a.segments)
    assert joined == body_token, (
        f"Span bütünlüğü bozuk: {joined!r} != {body_token!r}"
    )


# ---------------------------------------------------------------------------
# Deterministik sıralama
# ---------------------------------------------------------------------------

def test_deterministik_siralama():
    r1 = an.analyze("gelin")
    r2 = an.analyze("gelin")
    assert r1 == r2
    assert len(r1) >= 2


# ---------------------------------------------------------------------------
# Hypothetical bayrağı
# ---------------------------------------------------------------------------

def test_hypothetical_roots_verilen():
    results = an.analyze("evde", roots={"ev"})
    assert all(not a.hypothetical for a in results)


def test_hypothetical_roots_verilmemis():
    results = an.analyze("evde")
    # Roots verilmemiş → hepsi hypothetical=True
    assert all(a.hypothetical for a in results)


# ---------------------------------------------------------------------------
# Call count (bütçe göstergesi)
# ---------------------------------------------------------------------------

def test_call_count_reset():
    an.reset_call_count()
    assert an.call_count() == 0
    an.analyze("okuyor", roots={"okumak"})
    assert an.call_count() > 0
