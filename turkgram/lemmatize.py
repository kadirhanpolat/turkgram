"""turkgram.lemmatize — Lemmatizer (Faz 9c).

lemmatize()             → str | None
lemmatize_text()        → list[str | None]
lemmatize_detail()      → LemmaResult | None
lemmatize_text_detail() → list[LemmaResult | None]

Fallback zinciri: analyze → spellcheck.suggest → None.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Collection

from .analysis import analyze as _analyze, parse_text as _parse_text
from .disambiguation import disambiguate as _disambiguate
from .context import rank_in_context as _rank_in_context
from .tokenize import tokenize as _tokenize
from .spellcheck import suggest as _suggest
from . import lexicon as _lexicon


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
    results = _analyze(word, roots=resolved_roots)
    if results:
        ranked = _disambiguate(results, freq=freq)
        best, confidence = ranked[0]
        return LemmaResult(
            lemma=best.lemma,
            pos=best.pos,
            confidence=confidence,
            corrected=corrected,
        )
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

    Raises:
        ValueError: Boş string.
    """
    if not isinstance(word, str) or not word.strip():
        raise ValueError(f"geçersiz word: {word!r}")
    resolved = _resolve_roots(roots)
    result = _lemmatize_inner(word.strip(), resolved, freq)
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


def lemmatize_text_detail(
    text: str,
    *,
    roots: Collection[str] | None = None,
    freq: dict[str, int] | None = None,
) -> list[LemmaResult | None]:
    """Metin → token başına LemmaResult listesi. Çözümsüz token → None.

    Raises:
        ValueError: Boş string.
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
            # Güven skoru: TAM aday listesi üzerinden disambiguate et
            # (tek-elemanlı [best] göndermek → softmax=1.0 garantili, anlamsız)
            if all_analyses:
                all_ranked = _disambiguate(all_analyses, freq=freq)
                confidence = next(
                    (conf for a, conf in all_ranked if a.lemma == best.lemma and a.kind == best.kind),
                    all_ranked[0][1],
                )
            else:
                confidence = 1.0
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
