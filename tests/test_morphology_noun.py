"""TR isim çekim motoru testleri (roadmap 2a faz 2, CLAUDE.md #5).

İki katman:
  1. GOLDEN_NOUNS — elle-doğrulanmış beklenen biçimler (birincil, bağımsız kuruldu).
  2. zeyrek çapraz-kontrol — üretilen biçim analizciyle çözülüp kök isme dönüyor mu
     (üçüncü ağ; zeyrek yoksa skip). zeyrek golden'ın YERİNE GEÇMEZ (SPEC §11).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram import morphology_noun as mn
from tests.golden_nouns import GOLDEN_NOUNS


# ---------------------------------------------------------------------------
# Golden anahtar → decline()/ek-katman çağrısı çevirici (SPEC §10 şeması)
# ---------------------------------------------------------------------------
_CORE_CASES = {"nom", "acc", "dat", "loc", "abl", "gen", "ins"}


def _call_from_key(headword: str, key: str) -> str:
    parts = key.split(".")

    # ek katmanları
    if parts[0] == "pred":
        person = parts[1] if len(parts) > 1 else "3sg"
        return mn.predicative(headword, person=person)
    if parts[0] == "ki":
        case = parts[1] if len(parts) > 1 else "loc"
        return mn.with_ki(headword, case=case)
    if parts[0] == "ca":
        return mn.equative(headword)

    number = "sg"
    if parts and parts[0] == "pl":
        number = "pl"
        parts = parts[1:]

    possessive = None
    if parts and parts[0] == "poss":
        possessive = parts[1]
        parts = parts[2:]

    case = "nom"
    if parts:
        case = parts[0]

    return mn.decline(headword, number=number, possessive=possessive, case=case)


_CASES = [
    (hw, key, expected)
    for hw, cells in GOLDEN_NOUNS.items()
    for key, expected in cells.items()
]


@pytest.mark.parametrize("headword,key,expected", _CASES,
                         ids=[f"{h}:{k}" for h, k, _ in _CASES])
def test_golden_nouns(headword, key, expected):
    got = _call_from_key(headword, key)
    assert got == expected, f"{headword} [{key}]: beklenen {expected!r}, üretilen {got!r}"


# ---------------------------------------------------------------------------
# zeyrek çapraz-kontrol (üçüncü ağ) — opsiyonel (SPEC §11)
# ---------------------------------------------------------------------------
try:
    import zeyrek
    _ANALYZER = zeyrek.MorphAnalyzer()
except Exception:
    _ANALYZER = None


_ZEYREK_SAMPLE = ["ev", "kitap", "göz", "kapı", "araba", "okul", "yol", "kalem"]

# HAKEM-ONAYLI zararsız çakışmalar (isim tarafı) — golden onaylı biçimler,
# zeyrek homograf/türetme yüzünden farklı lemma verir. Yeni çakışmada test kırılır.
_ZEYREK_KNOWN_BENIGN: set[tuple[str, str]] = set()


@pytest.mark.skipif(_ANALYZER is None, reason="zeyrek kurulu değil (pip install zeyrek)")
def test_zeyrek_roundtrip():
    conflicts = []
    blind = 0
    checked = 0
    for headword in _ZEYREK_SAMPLE:
        if headword not in GOLDEN_NOUNS:
            continue
        root = mn.parse_noun(headword).root
        for key in GOLDEN_NOUNS[headword]:
            form = _call_from_key(headword, key)
            checked += 1
            lemmas = {
                p.lemma.lower()
                for group in _ANALYZER.analyze(form) for p in group
                if p.lemma and p.lemma.lower() != "unk"
            }
            if not lemmas:
                blind += 1
                continue
            root_hit = any(lm == root or lm.startswith(root) or root.startswith(lm)
                           for lm in lemmas)
            if not root_hit and (headword, key) not in _ZEYREK_KNOWN_BENIGN:
                conflicts.append((headword, key, form, sorted(lemmas)[:3]))

    if conflicts:
        report = "\n".join(
            f"  {h} [{k}] → {f!r}: zeyrek {lms}" for h, k, f, lms in conflicts
        )
        pytest.fail(f"zeyrek {len(conflicts)} biçimi FARKLI lemmaya çözdü:\n{report}")

    print(f"\nzeyrek: {checked} biçim, {checked-blind} doğrulandı, {blind} 'unk'.")
