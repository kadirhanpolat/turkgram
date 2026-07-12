# -*- coding: utf-8 -*-
"""Türkçe API çeviri denkliği: gibilik/iken/birleşik_çekim == çekirdek (CLAUDE.md §4).
Biçim doğruluğu çekirdek golden'da; burada yalnız çeviri + alias + hata sınanır."""
import pytest

import turkgram.tr as tr
from turkgram.nonfinite import converb_casina, converb_ken
from turkgram.morphology_noun import copula
from turkgram.compound import compound


def test_gibilik_ceviri():
    assert tr.gibilik("gülmek") == converb_casina("gülmek", base="aorist")
    assert tr.gibilik("gelmek", taban="öğrenilen_geçmiş") == converb_casina("gelmek", base="evid")
    assert tr.gibilik("gelmek", olumsuz=True) == "gelmezcesine"


def test_iken_ceviri():
    assert tr.iken("gelmek") == converb_ken("gelmek", base="aorist")
    assert tr.iken("gelmek", taban="şimdiki") == "geliyorken"
    assert tr.iken("gelmek", taban="gelecek") == "gelecekken"


def test_iken_nominal_ekfiil():
    # Nominal -ken ekfiil(ad, 'ken') üzerinden
    assert tr.ekfiil("çocuk", "ken") == "çocukken"
    assert tr.ekfiil("ev", "ken", durum="bulunma") == "evdeyken"
    assert tr.ekfiil("hasta", "iken") == "hastayken"   # alias


def test_birlesik_cekim_ceviri():
    assert tr.birleşik_çekim("gelmek", "şimdiki", "hikaye", "1tekil") == \
        compound("gelmek", "pres", "hikaye", "1sg")
    assert tr.birleşik_çekim("gelmek", "şimdiki", "hikaye", "3çoğul") == "geliyorlardı"
    assert tr.birleşik_çekim("gelmek", "geniş", "rivayet", "3çoğul") == "gelirlermiş"


def test_hata():
    with pytest.raises(ValueError):
        tr.gibilik("gelmek", taban="gelecek")   # -cAsInA fut tabanı yok
    with pytest.raises(ValueError):
        tr.birleşik_çekim("gelmek", "bilinmez", "hikaye")
