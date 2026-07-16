# tests/test_root_candidates_fix.py
import pytest
from turkgram.analysis_candidates import _root_candidates
from tests.golden_root_candidates_fix import GOLDEN

@pytest.mark.parametrize("surface,expected_root,desc", GOLDEN)
def test_root_candidate_present(surface, expected_root, desc):
    """Fix sonrası beklenen kök aday listesinde bulunmalı."""
    candidates = _root_candidates(surface)  # dict[str, list[str]]
    assert expected_root in candidates, (
        f"{desc}\n  yüzey={surface!r}, aranan={expected_root!r}\n"
        f"  bulunan kökler={sorted(candidates.keys())}"
    )
