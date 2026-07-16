"""turkgram.lemmatize — Lemmatizer (Faz 9c).

lemmatize()             → str | None
lemmatize_text()        → list[str | None]
lemmatize_detail()      → LemmaResult | None
lemmatize_text_detail() → list[LemmaResult | None]

Fallback zinciri: analyze → spellcheck.suggest → None.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Collection

from .analysis import analyze as _analyze, parse_text as _parse_text
from .disambiguation import disambiguate as _disambiguate
from .context import rank_in_context as _rank_in_context
from .tokenize import tokenize as _tokenize
from .spellcheck import suggest as _suggest
from . import lexicon as _lexicon
from .morphology_noun import PRONOUN_FORMS

_FALLBACK_CONFIDENCE: float = 1.0

# Zamir eğik biçimleri → temel biçim ters tablosu.
# PRONOUN_FORMS: {base: {case: surface}} → ters: {surface: base}
# Tüm eğik biçimleri kapsar (nom hariç, o zaten temel).
_PRONOUN_OBLIQUE: dict[str, str] = {}
for _base, _forms in PRONOUN_FORMS.items():
    for _case, _surface in _forms.items():
        _PRONOUN_OBLIQUE[_surface] = _base

# Noktalama ve sembol tespiti
def _is_punct_only(word: str) -> bool:
    """True if word consists entirely of punctuation/symbol/separator characters."""
    return all(
        unicodedata.category(ch).startswith(("P", "S", "Z"))
        for ch in word
    )


def _resolve_roots(roots: Collection[str] | None) -> frozenset[str]:
    """roots=None → lexicon.load() (spellcheck semantiği ile tutarlı).

    analyze(roots=None) FARKLI davranır (gürültü/hypothetical modu).
    Lemmatizer her zaman leksikon güdümlü çalışır.
    """
    return frozenset(roots) if roots is not None else _lexicon.load()


@dataclass(frozen=True)
class LemmaResult:
    """Zengin lemma sonucu.

    confidence: disambiguation softmax skoru; freq=None → dilbilimsel ağırlıklı.
    corrected: True = spellcheck fallback kullanıldı.
    """
    lemma: str
    pos: str
    confidence: float
    corrected: bool


def _lemmatize_inner(
    word: str,
    resolved_roots: frozenset[str],
    freq: dict[str, int] | None,
    corrected: bool = False,
) -> LemmaResult | None:
    """Ortak implementasyon — tüm public fonksiyonlar buraya delege eder.

    resolved_roots: _resolve_roots() sonucu (her zaman frozenset, boş olabilir).
    """
    # Noktalama/sembol-only → None (spellcheck fallback'e geçmeden kes).
    if _is_punct_only(word):
        return None

    # Zamir eğik biçimleri kapalı küme önceliği:
    # morphology_noun.PRONOUN_FORMS'dan türetilen _PRONOUN_OBLIQUE tablosu
    # doğrudan lemma verir; disambiguation'ın yanlış sıralamasını aşar.
    word_lower = word.lower()
    if word_lower in _PRONOUN_OBLIQUE:
        base = _PRONOUN_OBLIQUE[word_lower]
        return LemmaResult(
            lemma=base,
            pos="noun",
            confidence=_FALLBACK_CONFIDENCE,
            corrected=corrected,
        )

    results = _analyze(word, roots=resolved_roots)

    # Çok-token string (boşluklu) için leksikon filtresini atla: hypothetical=True
    # sonuçlarını da değerlendir (birleşik fiil: 'göz ardı etmek' leksikonda yok).
    is_multi_token_hypothetical = False
    if not results and " " in word:
        results = _analyze(word)  # hypothetical modu
        is_multi_token_hypothetical = bool(results)

    if results:
        ranked = _disambiguate(results, freq=freq)
        # Çok-token hypothetical analizlerde:
        # 1) Segment sayısı fazla olan (daha derin morfolojik ayrışma) öncelikli.
        #    Tek-segment adaylar ("ettimak" gibi) tüm yüzeyi kök sayan hatalı analizdir.
        # 2) Eşit segment sayısında, leksikondaki son kelimeyi içeren lemma tercih edilir
        #    ('etmek' in roots → 'göz ardı etmek' > 'göz ardı etmak').
        if is_multi_token_hypothetical:
            max_segs = max(len(a.segments) for a, _ in ranked)
            ranked = [(a, c) for a, c in ranked if len(a.segments) == max_segs]
            # Son kelime leksikonu filtresi
            if resolved_roots:
                lexicon_pref = [
                    (a, c) for a, c in ranked
                    if a.lemma.split()[-1] in resolved_roots
                ]
                if lexicon_pref:
                    ranked = lexicon_pref
        best, confidence = ranked[0]
        return LemmaResult(
            lemma=best.lemma,
            pos=best.pos,
            confidence=confidence,
            corrected=corrected,
        )
    # Sonsuz özyineleme koruması: spellcheck sonrası gelen çağrıda tekrar deneme
    if corrected:
        return None
    # Fallback: spellcheck (roots=None → lexicon.load() — suggest kendi içinde halleder)
    suggestions = _suggest(word, roots=resolved_roots if resolved_roots else None)
    if suggestions:
        return _lemmatize_inner(suggestions[0], resolved_roots, freq, corrected=True)
    return None


def lemmatize(
    word: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> str | None:
    """Tek kelime veya çok-token string → lemma. Çözümsüz → None.

    Çok-token string (boşluklu) için önce bütünü analyze dener (birleşik fiil desteği);
    başarısız olursa None döner (token-başına lemmatize için lemmatize_text kullan).

    Raises:
        ValueError: Boş string.
    """
    if not isinstance(word, str) or not word.strip():
        raise ValueError(f"geçersiz word: {word!r}")
    resolved = _resolve_roots(roots)
    stripped = word.strip()
    result = _lemmatize_inner(stripped, resolved, freq)
    return result.lemma if result is not None else None


def lemmatize_detail(
    word: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> LemmaResult | None:
    """Tek kelime veya çok-token string → LemmaResult. Çözümsüz → None.

    Raises:
        ValueError: Boş string.
    """
    if not isinstance(word, str) or not word.strip():
        raise ValueError(f"geçersiz word: {word!r}")
    resolved = _resolve_roots(roots)
    return _lemmatize_inner(word.strip(), resolved, freq)


def lemmatize_text(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[str | None]:
    """Metin → token başına lemma listesi. Çözümsüz token → None.

    Raises:
        ValueError: Boş string.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"geçersiz text: {text!r}")
    results = lemmatize_text_detail(text, roots=roots, freq=freq)
    return [r.lemma if r is not None else None for r in results]


def _pick_confidence(
    best: object,
    all_analyses: list,
    freq: dict[str, int] | None,
) -> float:
    """Bağlam sıralaması sonrası güven skorunu belirler.

    TAM aday listesi üzerinden disambiguate ederek best'e ait skoru döner.
    (Tek-elemanlı [best] göndermek softmax=1.0 garantisi verir; anlamsız.)
    all_analyses boşsa _FALLBACK_CONFIDENCE döner.
    """
    if not all_analyses:
        return _FALLBACK_CONFIDENCE
    all_ranked = _disambiguate(all_analyses, freq=freq)
    return next(
        (conf for a, conf in all_ranked if a.lemma == best.lemma and a.kind == best.kind),  # type: ignore[union-attr]
        all_ranked[0][1],
    )


def lemmatize_text_detail(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[LemmaResult | None]:
    """Metin → token başına LemmaResult listesi. Çözümsüz token → None.

    Raises:
        ValueError: Boş string veya boşluk-only string.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"geçersiz text: {text!r}")
    tokens = _tokenize(text)
    resolved = _resolve_roots(roots)

    # roots=None → parse_text kısayolu (_cached_analyze ile önbellekli, gürültü modu)
    # Ancak lemmatizer her zaman leksikon güdümlü → her zaman per-token analyze
    analyses_per_token = [_analyze(t, roots=resolved) for t in tokens]

    ranked_per_token = _rank_in_context(tokens, analyses_per_token, freq=freq)

    output: list[LemmaResult | None] = []
    for i, (ranked, all_analyses) in enumerate(zip(ranked_per_token, analyses_per_token)):
        if ranked:
            best = ranked[0]
            confidence = _pick_confidence(best, all_analyses, freq)
            output.append(LemmaResult(
                lemma=best.lemma,
                pos=best.pos,
                confidence=confidence,
                corrected=False,
            ))
        else:
            # Spellcheck fallback — bağlam dışında işlenir
            output.append(_lemmatize_inner(tokens[i], resolved, freq))
    return output
