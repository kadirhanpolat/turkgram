"""Alıntı leksikon kapsam: disharmonik alıntılar (FRONT_HARMONY) + BACK kontrol grubu.

l-final (kontrolü/normali/hayali) + -aat yumuşamayan (cemaati/sadakati). Elle-doğrulanmış
(TDK). BACK kontrol grubu (doktor/vapur) false-positive yakalar. SPEC: alıntı leksikon
kapsam (ünlü-düşme emsali; her ekleme set-üyeliği → yalnız kendini etkiler).
"""
import pytest
from turkgram.morphology_noun import decline

# Disharmonik alıntılar → ön-ünlü ek (acc)
FRONT_LOAN = {
    "kontrol": "kontrolü", "sembol": "sembolü", "santral": "santrali",
    "festival": "festivali", "normal": "normali", "hayal": "hayali",
    "emsal": "emsali", "misal": "misali", "iptal": "iptali", "mahsul": "mahsulü",
    "cemaat": "cemaati", "sadakat": "sadakati", "ziraat": "ziraati",
}

# BACK kontrol grubu → arka-ünlü ek (DEĞİŞMEMELİ; false-positive yakalar).
# Kesin-arka alıntılar (FRONT_HARMONY'de DEĞİL, doğal arka harmoni).
BACK_CONTROL = {
    "doktor": "doktoru", "vapur": "vapuru", "memur": "memuru",
    "motor": "motoru", "kanun": "kanunu", "salon": "salonu",
}


@pytest.mark.parametrize("lemma,exp", sorted(FRONT_LOAN.items()))
def test_front_loan_acc(lemma, exp):
    assert decline(lemma, case="acc") == exp


@pytest.mark.parametrize("lemma,exp", sorted(BACK_CONTROL.items()))
def test_back_control_acc(lemma, exp):
    """BACK kontrol: front eklemeler bu sözcükleri bozmamalı (set-üyeliği lemma-özel)."""
    assert decline(lemma, case="acc") == exp


@pytest.mark.parametrize("lemma", ["cemaat", "sadakat", "ziraat"])
def test_aat_no_soften(lemma):
    """-aat alıntıları yumuşamaz (cemaat→cemaati, cemaadi DEĞİL)."""
    got = decline(lemma, case="acc")
    assert "d" not in got[-2:], f"{got}: t→d yumuşaması olmamalı"


# --- lütuf ters-disharmonik (BACK_HARMONY): kalan ünlü ön ü ama ek arka ---
@pytest.mark.parametrize("kw,exp", [
    ({"case": "acc"}, "lütfu"), ({"case": "dat"}, "lütfa"),
    ({"case": "gen"}, "lütfun"),
    ({"case": "loc"}, "lütufta"), ({"case": "abl"}, "lütuftan"),  # düşmez (ünsüz-başlı)
    ({"possessive": "3sg", "case": "acc"}, "lütfunu"),
    ({"number": "pl"}, "lütuflar"),
])
def test_lutuf_back_harmony(kw, exp):
    assert decline("lütuf", **kw) == exp


def test_lutuf_analiz():
    from turkgram.analysis import analyze
    res = analyze("lütfu", roots={"lütuf"})
    assert any(a.lemma == "lütuf" and a.kind == "decline" and not a.hypothetical
               for a in res)
