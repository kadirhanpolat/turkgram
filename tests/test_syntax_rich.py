"""E1 zengin öbek üretimi runner."""
import pytest
from tests.golden_syntax_rich import (
    NP_URET_CASES, PP_URET_CASES, DEGMOD_URET_CASES, KOORDINE_NP_CASES,
)
from turkgram.syntax import np_uret, pp_uret, degmod_uret, koordine_np


@pytest.mark.parametrize("head,kwargs,expected", NP_URET_CASES)
def test_np_uret(head, kwargs, expected):
    assert np_uret(head, **kwargs) == expected


@pytest.mark.parametrize("isim,edat,kwargs,expected", PP_URET_CASES)
def test_pp_uret(isim, edat, kwargs, expected):
    assert pp_uret(isim, edat, **kwargs) == expected


@pytest.mark.parametrize("bas,kwargs,expected", DEGMOD_URET_CASES)
def test_degmod_uret(bas, kwargs, expected):
    assert degmod_uret(bas, **kwargs) == expected


@pytest.mark.parametrize("ogeler,baglac,expected", KOORDINE_NP_CASES)
def test_koordine_np(ogeler, baglac, expected):
    assert koordine_np(ogeler, baglac) == expected


def test_tr_isim_obeği_denklik():
    from turkgram.tr import isim_obeği
    assert isim_obeği("kapı", tamlayan="ev") == np_uret("kapı", tamlayan="ev")


def test_tr_derece_obeği_denklik():
    from turkgram.tr import derece_obeği
    assert derece_obeği("hızlı", derece="çok") == degmod_uret("hızlı", derece="çok")
