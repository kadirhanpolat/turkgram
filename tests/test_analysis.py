"""Çözümleyici — golden koşucusu + sözleşme testleri (Faz 2a).

PYTHONUTF8=1 python -m pytest tests/test_analysis.py -q
"""
import pytest
from turkgram import analysis as an
from turkgram.morphology_noun import decline, copula
from tests.golden_analysis import (
    GOLDEN_ANALYSIS, BATTERY_LEXICON, GOLDEN_COMPOUND, COMPOUND_LEXICON,
)
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


def test_cok_token_roots_filtreli():
    # SPEC §8.2: çok-token birleşik fiil artık tanınır. roots verilmişse gerçek-olmayan
    # birleşik lemma ("git git gitmek") elenir → boş (precision roots-garantili, §8.1).
    assert an.analyze("git git git", roots={"gitmek"}) == []
    # roots=None → hypothetical gürültü ÜRETİLEBİLİR (leksikonsuz doğa, §8.1); hepsi hyp.
    noisy = an.analyze("git git git")
    assert all(a.hypothetical for a in noisy)


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


def test_kok_adaylari_iyor_unlu_dusme():
    """Ünlü-düşmeli -Iyor yüzeylerinde gerçek kök adayı üretilmeli."""
    # oyna→oynuyor: "oyn" önek, yüksek ünlü "u" düştü → "oyna" kurtarılmalı
    cands = an._root_candidates("oynuyor")
    assert "oynamak" in cands, f"oynamak eksik; adaylar: {list(cands)[:20]}"

    # ara→arıyor: "ar" önek, yüksek ünlü "ı" düştü → "ara" kurtarılmalı
    cands2 = an._root_candidates("arıyor")
    assert "aramak" in cands2, f"aramak eksik; adaylar: {list(cands2)[:20]}"

    # başla→başlıyor: "başl" önek, yüksek ünlü "ı" düştü → "başla" kurtarılmalı
    cands3 = an._root_candidates("başlıyor")
    assert "başlamak" in cands3, f"başlamak eksik; adaylar: {list(cands3)[:20]}"


# ---------------------------------------------------------------------------
# -Iyor ünlü-düşme recall — tam analiz
# ---------------------------------------------------------------------------

def test_iyor_unlu_dusme_recall():
    """Ünlü-final fiillerin -Iyor çekimi geri çözülmeli (sistematik recall açığı fix)."""
    # oyna → oynuyor
    r = an.analyze("oynuyor", roots={"oynamak"})
    assert any(
        a.lemma == "oynamak" and a.kind == "conjugate"
        and dict(a.kwargs).get("tense") == "pres"
        and dict(a.kwargs).get("person") == "3sg"
        for a in r
    ), f"oynuyor çözülemedi: {r}"

    # ara → arıyor
    r2 = an.analyze("arıyor", roots={"aramak"})
    assert any(
        a.lemma == "aramak" and a.kind == "conjugate"
        and dict(a.kwargs).get("tense") == "pres"
        and dict(a.kwargs).get("person") == "3sg"
        for a in r2
    ), f"arıyor çözülemedi: {r2}"

    # başla → başlıyor
    r3 = an.analyze("başlıyor", roots={"başlamak"})
    assert any(
        a.lemma == "başlamak" and a.kind == "conjugate"
        and dict(a.kwargs).get("tense") == "pres"
        and dict(a.kwargs).get("person") == "3sg"
        for a in r3
    ), f"başlıyor çözülemedi: {r3}"

    # demek → diyor (ye_de — zaten çalışıyor, regresyon koruması)
    r4 = an.analyze("diyor", roots={"demek"})
    assert any(
        a.lemma == "demek" and a.kind == "conjugate"
        and dict(a.kwargs).get("tense") == "pres"
        for a in r4
    ), f"diyor çözülemedi: {r4}"

    # yemek → yiyor (ye_de — zaten çalışıyor, regresyon koruması)
    r5 = an.analyze("yiyor", roots={"yemek"})
    assert any(
        a.lemma == "yemek" and a.kind == "conjugate"
        and dict(a.kwargs).get("tense") == "pres"
        for a in r5
    ), f"yiyor çözülemedi: {r5}"


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
# Birleşik çok-token fiil golden (Faz 2b, SPEC §8.2) — TAM-küme eşitliği
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("surface", sorted(GOLDEN_COMPOUND))
def test_golden_compound_tam_kume(surface):
    got = {_norm_key(a.lemma, a.pos, a.kind, dict(a.kwargs))
           for a in an.analyze(surface, roots=COMPOUND_LEXICON)}
    want = {_norm_key(g["lemma"], g["pos"], g["kind"], g["kwargs"])
            for g in GOLDEN_COMPOUND[surface]}
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
# Faz 2b açık kapatma A: suppletif zamir eğik durumları (bana/sana)
#
# Bağımsız round-trip: üreteç (decline) ürettiği HER zamir eğik biçimi geri
# çözülmeli. bana/sana biçimce türetilemez (ben→bana suppletif) → kapalı-küme
# ters tablo gerekir. Düzenli tabanlar (beni/bende/ona…) regresyon koruması.
# ---------------------------------------------------------------------------

_PRONOUNS = ["ben", "sen", "o", "biz", "siz"]
_ALL_CASES = ["nom", "acc", "dat", "loc", "abl", "gen", "ins"]


@pytest.mark.parametrize("pron", _PRONOUNS)
@pytest.mark.parametrize("case", _ALL_CASES)
def test_zamir_egik_roundtrip(pron, case):
    """decline(zamir, case) her eğik biçim analyze ile geri çözülmeli."""
    surface = decline(pron, case=case)
    results = an.analyze(surface, roots={pron})
    assert any(
        a.lemma == pron and a.kind == "decline"
        and dict(a.kwargs).get("case", "nom") == case
        for a in results
    ), f"zamir eğik çözülemedi: {surface!r} (lemma={pron!r}, case={case!r}) → {results}"


def test_zamir_bana_sana_odakli():
    """Suppletif dat biçimleri (kapatma odağı) — açıkça çöz."""
    for surface, lemma in (("bana", "ben"), ("sana", "sen")):
        results = an.analyze(surface, roots={lemma})
        assert any(
            a.lemma == lemma and a.kind == "decline"
            and dict(a.kwargs).get("case") == "dat"
            for a in results
        ), f"{surface!r} → {lemma!r} dat çözülemedi: {results}"


# ---------------------------------------------------------------------------
# Faz 2b açık kapatma B: nominal ekfiil soru grubu (evde miydi / hasta mıymış)
#
# Bağımsız round-trip: üreteç (copula question=True) ürettiği HER çok-token soru
# biçimi geri çözülmeli. Çok-token soru yolu önce yalnız fiil gövdesini deniyordu.
# ---------------------------------------------------------------------------

_COPULA_Q_NOUNS = ["ev", "hasta", "öğrenci"]


@pytest.mark.parametrize("lemma", _COPULA_Q_NOUNS)
@pytest.mark.parametrize("aux", [None, "hikaye", "rivayet"])
@pytest.mark.parametrize("case", [None, "loc"])
@pytest.mark.parametrize("person", ["3sg", "1sg", "2sg"])
def test_ekfiil_soru_roundtrip(lemma, aux, case, person):
    """copula(question=True) her soru biçimi analyze ile geri çözülmeli."""
    surface = copula(lemma, aux, person, case=case, question=True)
    assert " " in surface  # soru biçimi çok-token
    results = an.analyze(surface, roots={lemma})
    want_case = case
    assert any(
        a.lemma == lemma and a.kind == "copula"
        and dict(a.kwargs).get("question") is True
        and dict(a.kwargs).get("aux") == aux
        and dict(a.kwargs).get("case", None) == want_case
        and dict(a.kwargs).get("person", "3sg") == person
        for a in results
    ), f"ekfiil soru çözülemedi: {surface!r} → {results}"


def test_ekfiil_soru_segment_tiling():
    """Soru biçimi segmentleri TAM yüzeyi (boşluk dahil) döşemeli."""
    for lemma in _COPULA_Q_NOUNS:
        for case in (None, "loc"):
            for aux in (None, "hikaye", "rivayet"):
                surface = copula(lemma, aux, "3sg", case=case, question=True)
                results = an.analyze(surface, roots={lemma})
                matching = [a for a in results if a.kind == "copula" and a.lemma == lemma]
                assert matching, f"copula çözümü yok: {surface!r}"
                a = matching[0]
                joined = "".join(s.surface for s in a.segments)
                assert joined == surface, (
                    f"Span bütünlüğü bozuk: {joined!r} != {surface!r}\n"
                    f"  segmentler: {[(s.surface, s.label) for s in a.segments]}"
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
