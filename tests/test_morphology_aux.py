"""Birleşik zaman (ek-fiil i-di/i-miş/i-se) golden testleri — morphology.py v1.2.

CLAUDE.md #5: biçimler MOTORDAN DEĞİL, dilbilgisinden elle türetildi ve tek tek
doğrulandı. SPEC §11. Soru × birleşik çaprazı dahil (kullanıcı: tam çapraz).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram import morphology as m

PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


def _check(lemma, tense, aux, expected, **kw):
    for person, exp in zip(PERSONS, expected):
        got = m.conjugate(lemma, tense, person, aux=aux, **kw)
        assert got == exp, f"{lemma} {tense}/{aux} {person}: {got!r} != {exp!r}"


# ── Hikâye (i-di) ─────────────────────────────────────────────────────────────

def test_hikaye_pres():
    _check("gelmek", "pres", "hikaye",
           ["geliyordum", "geliyordun", "geliyordu",
            "geliyorduk", "geliyordunuz", "geliyorlardı"])


def test_hikaye_fut_evid_aorist():
    _check("gelmek", "fut", "hikaye",
           ["gelecektim", "gelecektin", "gelecekti",
            "gelecektik", "gelecektiniz", "geleceklerdi"])
    _check("gelmek", "evid", "hikaye",
           ["gelmiştim", "gelmiştin", "gelmişti",
            "gelmiştik", "gelmiştiniz", "gelmişlerdi"])
    _check("gelmek", "aorist", "hikaye",
           ["gelirdim", "gelirdin", "gelirdi",
            "gelirdik", "gelirdiniz", "gelirlerdi"])


def test_hikaye_dilek():
    # gereklilik / şart / istek hikâyesi (ünlü-final gövde → kaynaştırma -y-)
    assert m.conjugate("gelmek", "necess", "1sg", aux="hikaye") == "gelmeliydim"
    assert m.conjugate("gelmek", "cond", "1sg", aux="hikaye") == "gelseydim"
    assert m.conjugate("gelmek", "opt", "1sg", aux="hikaye") == "geleydim"
    assert m.conjugate("gelmek", "cond", "3sg", aux="hikaye") == "gelseydi"


# ── Rivayet (i-miş) ───────────────────────────────────────────────────────────

def test_rivayet_pres():
    _check("gelmek", "pres", "rivayet",
           ["geliyormuşum", "geliyormuşsun", "geliyormuş",
            "geliyormuşuz", "geliyormuşsunuz", "geliyorlarmış"])


def test_rivayet_aorist():
    _check("gelmek", "aorist", "rivayet",
           ["gelirmişim", "gelirmişsin", "gelirmiş",
            "gelirmişiz", "gelirmişsiniz", "gelirlermiş"])


# ── Şart (i-se) ───────────────────────────────────────────────────────────────

def test_sart_pres():
    _check("gelmek", "pres", "sart",
           ["geliyorsam", "geliyorsan", "geliyorsa",
            "geliyorsak", "geliyorsanız", "geliyorlarsa"])


def test_sart_aorist():
    _check("gelmek", "aorist", "sart",
           ["gelirsem", "gelirsen", "gelirse",
            "gelirsek", "gelirseniz", "gelirlerse"])


# ── Olumsuz / yeterlik BEDAVA (basit gövdeye işler) ──────────────────────────

def test_aux_negative():
    assert m.conjugate("gelmek", "pres", "1sg", aux="hikaye",
                       negative=True) == "gelmiyordum"
    assert m.conjugate("gelmek", "pres", "3sg", aux="sart",
                       negative=True) == "gelmiyorsa"
    # aorist olumsuz hikâye → -mAz gövdesi + di
    assert m.conjugate("gelmek", "aorist", "1sg", aux="hikaye",
                       negative=True) == "gelmezdim"


def test_aux_ability():
    assert m.conjugate("gelmek", "pres", "1sg", aux="hikaye",
                       ability=True) == "gelebiliyordum"
    assert m.conjugate("gelmek", "pres", "3sg", aux="rivayet",
                       ability=True) == "gelebiliyormuş"


# ── Soru × birleşik (tam çapraz) ─────────────────────────────────────────────

def test_soru_hikaye():
    _check("gelmek", "pres", "hikaye",
           ["geliyor muydum", "geliyor muydun", "geliyor muydu",
            "geliyor muyduk", "geliyor muydunuz", "geliyorlar mıydı"],
           question=True)


def test_soru_rivayet():
    _check("gelmek", "aorist", "rivayet",
           ["gelir miymişim", "gelir miymişsin", "gelir miymiş",
            "gelir miymişiz", "gelir miymişsiniz", "gelirler miymiş"],
           question=True)


def test_soru_hikaye_fut():
    assert m.conjugate("gelmek", "fut", "1sg", aux="hikaye",
                       question=True) == "gelecek miydim"
    assert m.conjugate("gelmek", "fut", "3sg", aux="hikaye",
                       question=True) == "gelecek miydi"


def test_soru_hikaye_negative():
    assert m.conjugate("gelmek", "pres", "1sg", aux="hikaye",
                       question=True, negative=True) == "gelmiyor muydum"


# ── Arka-ünlü + birleşik-fiil + geçersiz ─────────────────────────────────────

def test_aux_back_vowel():
    _check("almak", "pres", "hikaye",
           ["alıyordum", "alıyordun", "alıyordu",
            "alıyorduk", "alıyordunuz", "alıyorlardı"])
    assert m.conjugate("almak", "aorist", "1sg", aux="sart") == "alırsam"


def test_aux_compound_verb():
    assert m.conjugate("bahse girmek", "pres", "1sg",
                       aux="hikaye") == "bahse giriyordum"


def test_aux_not_applicable():
    assert m.conjugate("gelmek", "imp", "2sg", aux="hikaye") is None
    assert m.conjugate("gelmek", "conv_arak", None, aux="rivayet") is None


def test_aux_invalid_raises():
    import pytest
    with pytest.raises(ValueError):
        m.conjugate("gelmek", "pres", "1sg", aux="bozuk")
