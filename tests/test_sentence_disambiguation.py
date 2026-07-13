"""Cümle-bağlamı disambiguation testleri (Faz 2b, turkgram/context.py).

SPEC: `spec/sentence-disambiguation-spec.md`. Golden verisi motor-körü kuruldu
(`tests/golden_sentence_disambiguation.py`). Golden = SIRA (top-1) testi (SPEC §4).
Motor OPT-IN → `analyze`/izole `disambiguation.rank` golden'larına dokunulmaz.
"""
import pytest

from turkgram import analysis as an, context as ctx, disambiguation as dis, lexicon as lx
from tests.golden_sentence_disambiguation import (
    CONTEXT_TOP1, NO_CONTEXT_SENTENCES, RECALL_SENTENCES,
)


@pytest.fixture(scope="module")
def roots():
    return lx.load()


@pytest.fixture(scope="module")
def pm():
    return lx.pos_map()


def _analyze_sentence(tokens, roots):
    """Her token'ı izole analiz et (tokenizasyon + analyze ÇAĞIRANIN işi, SPEC §1)."""
    return [an.analyze(t, roots=roots) for t in tokens]


# ---------------------------------------------------------------------------
# AİLE 1 — Bağlam top-1 (SPEC §4, KESİN çağrılar; K1..K5)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("tokens,idx,lemma,kind,kw", CONTEXT_TOP1)
def test_baglam_top1(tokens, idx, lemma, kind, kw, roots, pm):
    per_token = _analyze_sentence(tokens, roots)
    out = ctx.rank_in_context(tokens, per_token, pos=pm)
    top = out[idx][0]
    assert top.lemma == lemma, f"{tokens!r} @ {idx}: lemma {top.lemma!r} != {lemma!r}"
    assert top.kind == kind, f"{tokens!r} @ {idx}: kind {top.kind!r} != {kind!r}"
    assert kw.items() <= top.kwargs.items(), (
        f"{tokens!r} @ {idx}: kwargs {dict(top.kwargs)!r} beklenen üst-küme {kw!r} değil"
    )


# ---------------------------------------------------------------------------
# AİLE 2 — Bağlam-yok regresyon (SPEC §4): kural ateşlemez → top-1 == izole
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("tokens", NO_CONTEXT_SENTENCES)
def test_baglam_yok_regresyon(tokens, roots, pm):
    per_token = _analyze_sentence(tokens, roots)
    out = ctx.rank_in_context(tokens, per_token, pos=pm)
    for i, cands in enumerate(per_token):
        if not cands:
            assert out[i] == []
            continue
        iso_top = dis.rank(cands, pos=pm)[0]
        assert out[i][0] == iso_top, (
            f"{tokens!r} @ {i}: bağlamlı top-1 {out[i][0]!r} izole {iso_top!r}'den farklı"
        )


# ---------------------------------------------------------------------------
# AİLE 3 — Recall-güvenlik (SPEC §4): hiçbir kural aday SİLMEZ/EKLEMEZ
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("tokens", RECALL_SENTENCES)
def test_recall_guvenli(tokens, roots, pm):
    per_token = _analyze_sentence(tokens, roots)
    out = ctx.rank_in_context(tokens, per_token, pos=pm)
    assert len(out) == len(per_token)
    for i, cands in enumerate(per_token):
        # Analysis frozen ama kwargs=dict → hashable DEĞİL; aynı nesneler yeniden sıralanır
        # → kimlik (id) çokluküme eşitliği silme/ekleme yokluğunu kanıtlar.
        assert sorted(map(id, out[i])) == sorted(map(id, cands)), (
            f"{tokens!r} @ {i}: aday kümesi değişti (silme/ekleme) — recall ihlali"
        )
        assert len(out[i]) == len(cands), f"{tokens!r} @ {i}: uzunluk değişti (duplikasyon?)"


# ---------------------------------------------------------------------------
# Arayüz sözleşmesi (SPEC §1): uzunluk uyumsuzluğu → ValueError; boş aday korunur
# ---------------------------------------------------------------------------
def test_uzunluk_uyusmazligi_hata(roots, pm):
    with pytest.raises(ValueError):
        ctx.rank_in_context(["a", "b"], [an.analyze("ev", roots=roots)], pos=pm)


def test_bos_aday_korunur(roots, pm):
    # analyze'ın çözemediği yüzey → boş liste; rank_in_context onu boş bırakır
    tokens = ["zzzq", "geldi"]
    per_token = _analyze_sentence(tokens, roots)
    out = ctx.rank_in_context(tokens, per_token, pos=pm)
    assert len(out) == 2
    for i, cands in enumerate(per_token):
        assert len(out[i]) == len(cands)
