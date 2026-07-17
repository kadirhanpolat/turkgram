import pytest
from turkgram.analysis import analyze
from turkgram.lexicon import load
from tests.golden_postposition_analysis import (
    POSTPOSITION_PRESENT, HOMOGRAPH_NOT_TOP, AMBIGUOUS,
)

_ROOTS = load()


def _kinds(surface):
    return [a.kind for a in analyze(surface, roots=_ROOTS)]


@pytest.mark.parametrize("edat", POSTPOSITION_PRESENT)
def test_postposition_reading_present(edat):
    analyses = analyze(edat, roots=_ROOTS)
    postp = [a for a in analyses if a.kind == "postposition"]
    assert postp, f"{edat}: postposition okuması yok"
    assert postp[0].lemma == edat
    assert postp[0].pos == "postp"


def test_postposition_always_returns_without_roots():
    analyses = analyze("için", roots=None)
    assert any(a.kind == "postposition" for a in analyses)


@pytest.mark.parametrize("surface,_pos", AMBIGUOUS)
def test_ambiguous_returns_both(surface, _pos):
    kinds = _kinds(surface)
    assert "postposition" in kinds
    assert len(set(kinds)) >= 2, f"{surface}: belirsizlik yok, yalnız {kinds}"


@pytest.mark.parametrize("surface,correct_pos", HOMOGRAPH_NOT_TOP)
def test_homograph_postposition_not_top(surface, correct_pos):
    from turkgram.disambiguation import rank
    ranked = rank(analyze(surface, roots=_ROOTS), freq=None)
    assert ranked[0].pos == correct_pos, (
        f"{surface}: tepe {ranked[0].pos}/{ranked[0].kind}, beklenen {correct_pos}"
    )


def test_postposition_stays_out_of_kind_prior():
    """Homograf sıralaması postposition'ın düşük kind-önceliğine (0) bağlı."""
    from turkgram.disambiguation import _KIND_PRIOR
    assert "postposition" not in _KIND_PRIOR, (
        "postposition _KIND_PRIOR'a eklenirse aşkın/başka homografı kırılır"
    )
