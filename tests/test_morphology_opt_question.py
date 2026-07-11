"""İstek kipi (opt) + Soru (question) golden testleri — morphology.py v1.1.

CLAUDE.md #5: beklenen biçimler MOTORDAN DEĞİL, dilbilgisinden elle türetildi.
Her biçim tek tek doğrulanmıştır (bağımsızlık şart). SPEC §10.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram import morphology as m

PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


# ── İstek kipi (optative -A) — tam paradigma, elle doğrulanmış ────────────────
OPT_GOLDEN = {
    "gelmek": ["geleyim", "gelesin", "gele", "gelelim", "gelesiniz", "geleler"],
    "almak":  ["alayım", "alasın", "ala", "alalım", "alasınız", "alalar"],
    "okumak": ["okuyayım", "okuyasın", "okuya", "okuyalım", "okuyasınız", "okuyalar"],
    "görmek": ["göreyim", "göresin", "göre", "görelim", "göresiniz", "göreler"],
    "gülmek": ["güleyim", "gülesin", "güle", "gülelim", "gülesiniz", "güleler"],
    "bulmak": ["bulayım", "bulasın", "bula", "bulalım", "bulasınız", "bulalar"],
    "yemek":  ["yiyeyim", "yiyesin", "yiye", "yiyelim", "yiyesiniz", "yiyeler"],
    "demek":  ["diyeyim", "diyesin", "diye", "diyelim", "diyesiniz", "diyeler"],
    "gitmek": ["gideyim", "gidesin", "gide", "gidelim", "gidesiniz", "gideler"],
    "etmek":  ["edeyim", "edesin", "ede", "edelim", "edesiniz", "edeler"],
    "yapmak": ["yapayım", "yapasın", "yapa", "yapalım", "yapasınız", "yapalar"],
}


def test_opt_positive_paradigm():
    for lemma, forms in OPT_GOLDEN.items():
        for person, expected in zip(PERSONS, forms):
            got = m.conjugate(lemma, "opt", person)
            assert got == expected, f"{lemma} opt {person}: {got!r} != {expected!r}"


def test_opt_negative():
    # taban -mA + -y-e; gelmeyeyim…
    assert m.conjugate("gelmek", "opt", "1sg", negative=True) == "gelmeyeyim"
    assert m.conjugate("gelmek", "opt", "3sg", negative=True) == "gelmeye"
    assert m.conjugate("almak", "opt", "1sg", negative=True) == "almayayım"
    assert m.conjugate("almak", "opt", "1pl", negative=True) == "almayalım"


def test_opt_ability():
    # taban -Abil + -A; gelebileyim…
    assert m.conjugate("gelmek", "opt", "1sg", ability=True) == "gelebileyim"
    assert m.conjugate("gelmek", "opt", "3sg", ability=True) == "gelebile"


def test_opt_compound_verb_prefix():
    assert m.conjugate("bahse girmek", "opt", "1sg") == "bahse gireyim"


# ── Soru (interrogative -mI) — her tip, elle doğrulanmış ──────────────────────

# z-tipi (pres/fut/evid/aorist/necess): mI gövdeden sonra, kişi mI'ye biner;
# 3pl istisna (-lAr fiilde, mI sonra).
Q_PRES_GEL = ["geliyor muyum", "geliyor musun", "geliyor mu",
              "geliyor muyuz", "geliyor musunuz", "geliyorlar mı"]
Q_FUT_GEL = ["gelecek miyim", "gelecek misin", "gelecek mi",
             "gelecek miyiz", "gelecek misiniz", "gelecekler mi"]
Q_AORIST_GEL = ["gelir miyim", "gelir misin", "gelir mi",
                "gelir miyiz", "gelir misiniz", "gelirler mi"]
Q_EVID_GEL = ["gelmiş miyim", "gelmiş misin", "gelmiş mi",
              "gelmiş miyiz", "gelmiş misiniz", "gelmişler mi"]
Q_NECESS_GEL = ["gelmeli miyim", "gelmeli misin", "gelmeli mi",
                "gelmeli miyiz", "gelmeli misiniz", "gelmeliler mi"]

# k-tipi (past/cond/opt): kişi fiilde, mI en sona.
Q_PAST_GEL = ["geldim mi", "geldin mi", "geldi mi",
              "geldik mi", "geldiniz mi", "geldiler mi"]
Q_COND_GEL = ["gelsem mi", "gelsen mi", "gelse mi",
              "gelsek mi", "gelseniz mi", "gelseler mi"]
Q_OPT_GEL = ["geleyim mi", "gelesin mi", "gele mi",
             "gelelim mi", "gelesiniz mi", "geleler mi"]


def _check_q(lemma, tense, expected, **kw):
    for person, exp in zip(PERSONS, expected):
        got = m.conjugate(lemma, tense, person, question=True, **kw)
        assert got == exp, f"{lemma} {tense} {person} soru: {got!r} != {exp!r}"


def test_question_z_type():
    _check_q("gelmek", "pres", Q_PRES_GEL)
    _check_q("gelmek", "fut", Q_FUT_GEL)
    _check_q("gelmek", "aorist", Q_AORIST_GEL)
    _check_q("gelmek", "evid", Q_EVID_GEL)
    _check_q("gelmek", "necess", Q_NECESS_GEL)


def test_question_k_type():
    _check_q("gelmek", "past", Q_PAST_GEL)
    _check_q("gelmek", "cond", Q_COND_GEL)
    _check_q("gelmek", "opt", Q_OPT_GEL)


def test_question_back_vowel_harmony():
    # almak: mI arka-ünlü → mı/mu; past mı.
    assert m.conjugate("almak", "pres", "1sg", question=True) == "alıyor muyum"
    assert m.conjugate("almak", "past", "1sg", question=True) == "aldım mı"
    assert m.conjugate("almak", "past", "3pl", question=True) == "aldılar mı"
    assert m.conjugate("almak", "fut", "3sg", question=True) == "alacak mı"


def test_question_negative():
    assert m.conjugate("gelmek", "pres", "1sg", question=True,
                       negative=True) == "gelmiyor muyum"
    # aorist olumsuz soru → -mAz gövdesi + mI
    assert m.conjugate("gelmek", "aorist", "1sg", question=True,
                       negative=True) == "gelmez miyim"
    assert m.conjugate("gelmek", "past", "1sg", question=True,
                       negative=True) == "gelmedim mi"


def test_question_not_applicable():
    # emir/ulaç/ortaç soru almaz → None
    assert m.conjugate("gelmek", "imp", "2sg", question=True) is None
    assert m.conjugate("gelmek", "conv_arak", None, question=True) is None
    assert m.conjugate("gelmek", "part_dik", None, question=True) is None


def test_question_compound_prefix():
    assert m.conjugate("bahse girmek", "pres", "2sg",
                       question=True) == "bahse giriyor musun"


# ── paradigm 9 kipi kapsar ────────────────────────────────────────────────────

def test_paradigm_includes_opt():
    p = m.paradigm("gelmek")
    assert p["opt.1sg"] == "geleyim"
    assert p["opt.3sg"] == "gele"
    assert p["neg.opt.1sg"] == "gelmeyeyim"
