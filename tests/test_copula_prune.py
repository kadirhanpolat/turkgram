"""Copula enumerate person-ending prune — recall-güvenlik regresyon kilidi.

`_enumerate_copula` perf prune'u (person eki SON-karakter ailesi) copula ekinin
DAİMA en sonda olduğu (case/poss/aux son-karakteri değiştirmez) varsayımına dayanır.
Bu test o varsayımı motor çıktısıyla sabitler — copula morfolojisi değişirse yakalar.
40.000-biçim exhaustive diferansiyel 0 recall-miss verdi (2026-07-19).
"""
import pytest
from turkgram.morphology_noun import copula
from turkgram.analysis_candidates import _COPULA_PERSON_LASTCHAR
from turkgram.analysis import analyze

_NOUNS = ["ev", "araba", "kitap", "okul", "göz", "yol", "masa", "defter"]
_AUX = [None, "hikaye", "rivayet", "sart"]
_CASES = [None, "acc", "dat", "loc", "abl", "gen", "ins"]
_POSS = [None, "1sg", "2sg", "3sg", "1pl", "2pl", "3pl"]


@pytest.mark.parametrize("person,family", sorted(_COPULA_PERSON_LASTCHAR.items()))
def test_copula_person_lastchar_family_holds(person, family):
    """Person ekinin SON karakteri, tüm case/poss/aux/number'da ailede kalmalı."""
    for n in _NOUNS:
        for aux in _AUX:
            for c in _CASES:
                for po in _POSS:
                    for num in ("sg", "pl"):
                        try:
                            f = copula(n, aux, person, case=c, possessive=po,
                                       number=num, question=False)
                        except Exception:
                            continue
                        assert f[-1] in family, (
                            f"{f} ({person}) son-karakter {f[-1]!r} ∉ {set(family)} "
                            f"→ prune recall'ı kırar!"
                        )


def test_copula_prune_recall_sample():
    """Örneklem copula biçimleri analyze'da bulunmalı (prune sonrası recall)."""
    for n in ["ev", "kitap"]:
        for aux in _AUX:
            for p in ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl"):
                surf = copula(n, aux, p)
                res = analyze(surf, roots={n})
                assert any(a.kind == "copula" and a.lemma == n
                           and a.kwargs.get("person") == p
                           and a.kwargs.get("aux") == aux for a in res), \
                    f"{surf} (n={n},aux={aux},p={p}) copula analizi kayıp"


# --- conjugate person-ending prune aile-varsayımı kilidi ---
from turkgram.morphology import conjugate as _conjugate
from turkgram.analysis_candidates import (
    _CONJ_PERSON_LASTCHAR, _FINITE_TENSES, _CONJ_AUX, _ASPECTS,
)

_VERBS = ["gelmek", "okumak", "yazmak", "gitmek", "yemek", "bakmak", "almak", "vermek"]


@pytest.mark.parametrize("person,family", sorted(_CONJ_PERSON_LASTCHAR.items()))
def test_conjugate_person_lastchar_family_holds(person, family):
    """Tight-aile person'ların (1sg/1pl/2pl) çekim eki SON-karakteri ailede kalmalı
    (tüm tense×neg×abil×aux×aspect). Prune recall'ının temeli."""
    for v in _VERBS:
        for tense in _FINITE_TENSES:
            for neg in (False, True):
                for abil in (False, True):
                    for aux in _CONJ_AUX:
                        for asp in _ASPECTS:
                            try:
                                f = _conjugate(v, tense, person, negative=neg,
                                               ability=abil, question=False,
                                               aux=aux, aspect=asp)
                            except Exception:
                                continue
                            if not f or " " in f:
                                continue
                            assert f[-1] in family, (
                                f"{f} ({person}) son-karakter {f[-1]!r} ∉ {set(family)} "
                                f"→ conjugate prune recall'ı kırar!"
                            )
