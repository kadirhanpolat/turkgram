"""`-ki` aitlik eki çözümleme runner (with_ki kind)."""
import pytest
from turkgram.analysis import analyze
from tests.golden_ki_analysis import (
    GOLDEN_KI_LOC, GOLDEN_KI_GEN, GOLDEN_KI_ROUND, GOLDEN_KI_POSSESSIVE,
)

_POSITIVE = GOLDEN_KI_LOC + GOLDEN_KI_GEN + GOLDEN_KI_ROUND + GOLDEN_KI_POSSESSIVE


@pytest.mark.parametrize("case", _POSITIVE, ids=[c["surface"] for c in _POSITIVE])
def test_ki_analysis(case):
    result = analyze(case["surface"], roots=case["roots"])
    exp_poss = case.get("possessive")
    hit = [
        r for r in result
        if r.lemma == case["lemma"]
        and r.kind == case["kind"]
        and r.kwargs.get("case") == case["case"]
        and r.kwargs.get("possessive") == exp_poss
    ]
    assert hit, (
        f"{case['surface']}: beklenen (lemma={case['lemma']}, kind={case['kind']}, "
        f"case={case['case']}, poss={exp_poss}) bulunamadı. "
        f"Alınan: {[(r.lemma, r.kind, dict(r.kwargs)) for r in result]}"
    )


def test_ki_marker_negative():
    """k[ıiuü] ile bitmeyen yüzey with_ki üretmez (marker filtresi)."""
    for surface, roots in [("kirli", {"kir"}), ("araba", {"araba"})]:
        result = analyze(surface, roots=roots)
        assert not any(r.kind == "with_ki" for r in result), surface


@pytest.mark.parametrize("surface,root", [("bugünkü", "bugün"), ("dünkü", "dün")])
def test_ki_round_single_analysis(surface, root):
    """Kİ_ROUND tek kanonik with_ki analizi (hakem HIGH: 4x belirsizlik patlaması giderildi)."""
    ki = [a for a in analyze(surface, roots={root}) if a.kind == "with_ki"]
    assert len(ki) == 1, f"{surface}: {len(ki)} analiz (1 beklenir): {[dict(a.kwargs) for a in ki]}"
    assert ki[0].kwargs.get("case") == "loc"
    assert ki[0].kwargs.get("possessive") is None
