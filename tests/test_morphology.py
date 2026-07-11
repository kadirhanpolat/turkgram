"""TR fiil çekim motoru testleri (roadmap 2a, CLAUDE.md #5).

İki katman:
  1. GOLDEN — elle-doğrulanmış beklenen biçimler (birincil referans, bağımsız kuruldu).
  2. zeyrek çapraz-kontrol — üretilen her biçim TR morfoloji analizciyle çözülüp
     lemma köküne geri dönüyor mu (üçüncü ağ; zeyrek yoksa skip).

zeyrek golden'ın YERİNE GEÇMEZ — golden birincildir (SPEC §8).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram import morphology as m
from tests.golden_verbs import GOLDEN


# ---------------------------------------------------------------------------
# Golden anahtar → conjugate() çağrısı çevirici
# ---------------------------------------------------------------------------
def _call_from_key(lemma: str, key: str) -> str:
    """'aorist.neg.3sg' / 'ability.pres.3sg' / 'conv_arak' → conjugate(...)."""
    parts = key.split(".")

    # alias: 'neg.pres.3sg' == 'pres.neg.3sg'
    if parts[0] == "neg":
        parts = [parts[1], "neg", *parts[2:]]

    ability = False
    if parts and parts[0] == "ability":
        ability = True
        parts = parts[1:]

    negative = False
    if "neg" in parts:
        negative = True
        parts = [p for p in parts if p != "neg"]

    tense = parts[0]
    person = parts[1] if len(parts) > 1 else None

    return m.conjugate(lemma, tense, person, negative=negative, ability=ability)


# GOLDEN'i (lemma, key, expected) düzine listeye aç — her hücre ayrı test.
_CASES = [
    (lemma, key, expected)
    for lemma, cells in GOLDEN.items()
    for key, expected in cells.items()
]


@pytest.mark.parametrize("lemma,key,expected", _CASES,
                         ids=[f"{l}:{k}" for l, k, _ in _CASES])
def test_golden(lemma, key, expected):
    got = _call_from_key(lemma, key)
    assert got == expected, f"{lemma} [{key}]: beklenen {expected!r}, üretilen {got!r}"


# ---------------------------------------------------------------------------
# zeyrek çapraz-kontrol (üçüncü ağ) — opsiyonel
# ---------------------------------------------------------------------------
try:
    import zeyrek
    _ANALYZER = zeyrek.MorphAnalyzer()
except Exception:
    _ANALYZER = None


def _root_of(lemma: str) -> str:
    return m.parse_verb(lemma).root


# zeyrek'in üretken/nadir biçimleri kaçırması motor hatası DEĞİL — rapora düşer.
_ZEYREK_SAMPLE = [
    "gelmek", "yapmak", "gitmek", "okumak", "görmek",
    "başlamak", "çalışmak", "vermek", "almak", "konuşmak",
]

# HAKEM-ONAYLI zararsız çakışmalar (2026-07-11): zeyrek bu biçimleri FARKLI lemmaya
# çözer ama biçim DOĞRUdur (golden onaylı) — hepsi zeyrek 0.1.3 kusuru:
#   gider   : git→gid yumuşaması + "gider" (isim) homografı
#   gidin   : yanlış heceleme
#   giderek : sözlükselleşmiş zarf "giderek"i ayrı lemma sanma
#   çalışın : türetme derinliği (çalışmak→çalmak)
# Bu küme testi YENİ çakışmalara duyarlı bırakır; bilineni susturur.
_ZEYREK_KNOWN_BENIGN = {
    ("gitmek", "aorist.3sg"), ("gitmek", "imp.2pl"), ("gitmek", "conv_arak"),
    ("çalışmak", "imp.2pl"),
}


@pytest.mark.skipif(_ANALYZER is None, reason="zeyrek kurulu değil (pip install zeyrek)")
def test_zeyrek_roundtrip():
    """zeyrek çapraz-kontrol (üçüncü ağ, SPEC §8).

    zeyrek 0.1.3 (Zemberek'in kısıtlı Python portu) çok sayıda GEÇERLİ biçimi
    'unk' (çözemedi) döndürür — bu motor hatası DEĞİL, aracın körlüğüdür; golden
    zaten doğruluğu kanıtlıyor. Bu yüzden zeyrek motoru YALNIZCA emin bir şekilde
    FARKLI bir fiil lemmasına çözdüğünde suçlayabilir (gerçek çakışma). 'unk',
    boş çözüm ve kendi-lemması suçlama sayılmaz — bunlar RAPORA düşer.
    """
    conflicts = []   # zeyrek farklı gerçek lemma verdi → motor şüphesi (FAIL)
    blind = 0        # zeyrek unk/boş → araç körlüğü (bilgi)
    checked = 0
    for lemma in _ZEYREK_SAMPLE:
        if lemma not in GOLDEN:
            continue
        root = _root_of(lemma)
        for key in GOLDEN[lemma]:
            form = _call_from_key(lemma, key)
            checked += 1
            lemmas = {
                p.lemma.lower()
                for group in _ANALYZER.analyze(form) for p in group
                if p.lemma and p.lemma.lower() != "unk"
            }
            if not lemmas:
                blind += 1
                continue
            root_hit = any(lm == root or lm.startswith(root) or lm == lemma
                           or root.startswith(lm) for lm in lemmas)
            if not root_hit and (lemma, key) not in _ZEYREK_KNOWN_BENIGN:
                conflicts.append((lemma, key, form, sorted(lemmas)[:3]))

    if conflicts:
        report = "\n".join(
            f"  {lm} [{k}] → {f!r}: zeyrek {lms} (kök beklenirdi: {_root_of(lm)!r})"
            for lm, k, f, lms in conflicts
        )
        pytest.fail(f"zeyrek {len(conflicts)} biçimi FARKLI lemmaya çözdü — motor şüphesi:\n{report}")

    # Çakışma yok: zeyrek çözebildiklerini doğruladı; körlükler yalnız bilgi.
    print(f"\nzeyrek: {checked} biçim, {checked-blind} doğrulandı, "
          f"{blind} 'unk' (araç körlüğü, golden birincil).")
