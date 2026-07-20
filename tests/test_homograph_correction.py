"""test_homograph_correction.py — disambiguation çekimli-üstünlük düzeltmesi.

SPEC docs/superpowers/specs/2026-07-20-homograph-inflected-correction-design.md.
Bare-decline (rare lemma) çok-sık çekimli okumayı morfem-ekonomisiyle YENMESİN.
Beklenenler elle-doğrulanmış (freq: lexicon.load_freq()).
"""
import pytest

from turkgram import lexicon
from turkgram.analysis import parse_text
from turkgram.disambiguation import rank

_ROOTS = lexicon.load()
_FREQ = lexicon.load_freq()
_POS = lexicon.pos_map()


def _real(word):
    return [a for a in parse_text(word, roots=_ROOTS)[0] if not a.hypothetical]


def _top(word, **kw):
    r = rank(_real(word), **kw)
    return r[0] if r else None


def _sig(a):
    return (a.kind, a.lemma, a.kwargs.get("tense") or a.kwargs.get("case"))


# ── Düzeltme TETİKLENİR (bare leksikon-çöpü ad → net-fiil past) ───────────────
@pytest.mark.parametrize("word,expected", [
    ("verdi", ("conjugate", "vermek", "past")),   # 'verdi' noun → vermek past
    ("girdi", ("conjugate", "girmek", "past")),   # 'girdi' noun → girmek past
    ("çıktı", ("conjugate", "çıkmak", "past")),   # 'çıktı' noun → çıkmak past
])
def test_correction_fires(word, expected):
    got = _top(word, freq=_FREQ, pos=_POS, prefer_inflected=True)
    assert _sig(got) == expected


# ── Düzeltme TETİKLENMEZ ──────────────────────────────────────────────────────
# (bare-vs-bare / derivation-rakip / doğru bare / acc-dalı ÇIKARILDI: gerçek -CI adları)
@pytest.mark.parametrize("word,expected", [
    ("yüz", ("conjugate", "yüzmek", "imp")),   # en-iyi zaten conjugate (bare-decline değil)
    ("var", ("conjugate", "varmak", "imp")),   # en-iyi conjugate
    ("dolu", ("decline", "dolu", None)),       # rakip derivation → DAR-dışı
    ("kar", ("conjugate", "karmak", "imp")),   # bare-vs-bare imperatif homograf
    ("kitabı", ("decline", "kitap", "acc")),   # rakip bare-lemma yok
    ("sabah", ("decline", "sabah", None)),     # tek bare, rakip yok
    ("Yarın", ("decline", "yarın", None)),     # rakip imp(yarmak) DAR-dışı → korunur
    ("yazar", ("decline", "yazar", None)),     # rakip aorist(yazmak) DAR-dışı → korunur
    # HAKEM HIGH — acc-dalı çıkarıldı: gerçek -CI adları/sıfatları KORUNUR (kısa-stem+acc DEĞİL)
    ("topu", ("decline", "topu", None)),       # 'topu' gerçek pron → top:acc'e DEVRİLMEZ
    ("yarı", ("decline", "yarı", None)),       # yarı = half (yar:acc değil)
    ("arı", ("decline", "arı", None)),         # arı = bee (ar:acc değil)
    ("salı", ("decline", "salı", None)),       # salı = Tuesday
    ("koyu", ("decline", "koyu", None)),       # koyu = dark (sıfat)
])
def test_correction_no_op(word, expected):
    got = _top(word, freq=_FREQ, pos=_POS, prefer_inflected=True)
    assert _sig(got) == expected


# ── Default davranış DEĞİŞMEZ (prefer_inflected=False == eski) ────────────────
@pytest.mark.parametrize("word", ["topu", "verdi", "yüz", "dolu", "kitabı"])
def test_default_unchanged(word):
    """prefer_inflected default (False) == flag açıkça False (yeni param geriye-uyumlu)."""
    real = _real(word)
    base = rank(real, freq=_FREQ, pos=_POS)                       # default flag=False
    base_no_flag = rank(real, freq=_FREQ, pos=_POS, prefer_inflected=False)
    assert [_sig(a) for a in base] == [_sig(a) for a in base_no_flag]


def test_freqless_base_preserved():
    """prefer_inflected=True base'i FREQ'SİZ tutar → yüz/dolu ham-freq yan etkisinden korunur
    (freqli base sıralaması yüz→noun, dolu→derivation yapardı)."""
    for word, exp in [("yüz", ("conjugate", "yüzmek", "imp")),
                      ("dolu", ("decline", "dolu", None))]:
        got = _top(word, freq=_FREQ, pos=_POS, prefer_inflected=True)
        assert _sig(got) == exp


def test_no_freq_no_op():
    """freq=None → prefer_inflected=True olsa da NO-OP (freq gerektirir)."""
    real = _real("verdi")
    a = rank(real, pos=_POS, prefer_inflected=True)
    b = rank(real, pos=_POS)
    assert [_sig(x) for x in a] == [_sig(x) for x in b]


def test_sentence_verdi_segmentation():
    """Uçtan uca: verdi→vermek düzeltmesi sıralı yargıyı doğru böler + yüklem yapar."""
    from turkgram.sentence import analyze_sentence
    sa = analyze_sentence("Ali kitabı aldı Veli defteri verdi", roots=_ROOTS)
    # verdi verb-flip → yüklem + 2 bağımsız yargı
    assert ("yüklem", ("verdi",)) in [(e.label, e.tokens) for e in sa.elements]
    assert len(sa.clauses) == 2
    assert [c.role for c in sa.clauses] == ["bağımsız", "bağımsız"]
