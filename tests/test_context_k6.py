"""test_context_k6.py — K6 bağlam-tabanlı acc-nesne homografı runner.

SPEC docs/superpowers/specs/2026-07-20-context-acc-object-homograph-design.md.
"""
from turkgram import lexicon, context
from turkgram.analysis import analyze
from turkgram.sentence import analyze_sentence

_ROOTS = lexicon.load()
_PM = lexicon.pos_map()
_FREQ = lexicon.load_freq()


def _ctx_top(tokens, idx):
    per = [analyze(t, roots=_ROOTS) for t in tokens]
    ranked = context.rank_in_context(tokens, per, pos=_PM)  # freqless base → K6 belirleyici
    a = ranked[idx][0]
    return (a.kind, a.lemma, a.kwargs.get("case"))


def test_k6_object_context_acc():
    """Çocuk topu ... V → topu = top:acc (nesne bağlamı: önceki nominal + fiil)."""
    assert _ctx_top(["Çocuk", "topu", "bahçede", "oynadı"], 1) == ("decline", "top", "acc")


def test_k6_no_prev_nominal_bare():
    """Topu geldi → K6 ateşlemez (önceki nominal yok) → freqless bare korunur."""
    assert _ctx_top(["Topu", "geldi"], 0) == ("decline", "topu", None)


def test_k6_not_in_set_untouched():
    """birileri geldi → K6 sette değil → bare pron korunur (bağlam-bağımlı, bilinçli dışlandı)."""
    assert _ctx_top(["birileri", "geldi"], 0)[:2] == ("decline", "birileri")


def test_k6_needs_verb():
    """Çocuk topu (fiilsiz) → K6 ateşlemez (finit fiil yok) → bare."""
    # yalnız iki nominal, fiil yok → nesne bağlamı tamamlanmaz
    assert _ctx_top(["Çocuk", "topu"], 1) == ("decline", "topu", None)


def test_sentence_cocuk_topu_belirtili():
    """Uçtan uca: Çocuk topu bahçede oynadı → topu belirtili nesne (golden skip kalktı)."""
    sa = analyze_sentence("Çocuk topu bahçede oynadı", roots=_ROOTS)
    labels = [(e.label, e.tokens) for e in sa.elements]
    assert ("belirtili nesne", ("topu",)) in labels
    assert ("özne", ("Çocuk",)) in labels


def test_sentence_ali_topu():
    sa = analyze_sentence("Ali topu attı", roots=_ROOTS)
    assert ("belirtili nesne", ("topu",)) in [(e.label, e.tokens) for e in sa.elements]


def test_k6_curated_set_drift_lock():
    """`_ACC_OBJECT_PRON` içeriği kilidi (hakem LOW): mekanizma genel, yanlış eleman sessizce
    over-generalize eder. Set genişlerse bu test bilinçli güncellenir (birileri/hepsi GİRMEZ)."""
    assert context._ACC_OBJECT_PRON == frozenset({"topu"})
    # bare-baskın/rakipsiz homograflar KESİNLİKLE sette OLMAMALI
    for w in ("birileri", "hepsi", "çoğu", "kimi", "diğeri", "yarı", "arı"):
        assert w not in context._ACC_OBJECT_PRON


def test_k6_recall_safe_no_prune():
    """K6 aday BUDAMAZ — topu'nun tüm okumaları korunur (yalnız sıra değişir)."""
    per = [analyze(t, roots=_ROOTS) for t in ["Çocuk", "topu", "geldi"]]
    ranked = context.rank_in_context(["Çocuk", "topu", "geldi"], per, pos=_PM)
    isolated = analyze("topu", roots=_ROOTS)
    assert len(ranked[1]) == len([a for a in isolated if not a.hypothetical])
