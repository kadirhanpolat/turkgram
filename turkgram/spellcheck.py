"""turkgram.spellcheck — Türkçe yazım denetimi (Faz 9b).

is_valid() → analyze() + lexicon.load() ile morfolojik geçerlilik.
suggest()  → BK-tree + Türkçe-ağırlıklı Levenshtein (sonraki görevde).
check()    → SpellResult (is_valid + suggestions).

NOT: roots=None burada lexicon.load()'u otomatik yükler (analyze(roots=None)'den farklı).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from .analysis import analyze as _analyze
from . import lexicon as _lexicon

_MAX_WORD_LEN = 200

# Türkçe karakter konfüzyon çiftleri: her çift 0.5 maliyet taşır.
_TR_PAIRS: frozenset[frozenset[str]] = frozenset(
    frozenset(pair) for pair in [("ı", "i"), ("ö", "o"), ("ü", "u"), ("ş", "s"), ("ç", "c"), ("ğ", "g")]
)


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def _roots(roots: frozenset[str] | None) -> frozenset[str]:
    """roots=None → leksikonu otomatik yükle (is_valid/suggest için zorunlu)."""
    return roots if roots is not None else _lexicon.load()


@dataclass(frozen=True)
class SpellResult:
    """Yazım denetimi sonucu.

    suggestions: is_valid=True ise her zaman boş tuple; immutable (frozen uyum).
    word: çağıranın orijinal girdisi (normalize edilmemiş olabilir).
    """
    word: str
    is_valid: bool
    suggestions: tuple[str, ...]


def is_valid(word: str, *, roots: frozenset[str] | None = None) -> bool:
    """Kelimenin morfolojik olarak geçerli Türkçe olup olmadığını döner."""
    word = _tr_lower(word.strip())
    if not word or len(word) > _MAX_WORD_LEN:
        return False
    r = _roots(roots)
    return any(not a.hypothetical for a in _analyze(word, roots=r))


# suggest() ve check() bir sonraki görevde eklenecek — placeholder yok.


def _tr_distance(a: str, b: str) -> float:
    """Türkçe-ağırlıklı Levenshtein.

    Türkçe karakter konfüzyonları (ı/i, ö/o, ü/u, ş/s, ç/c, ğ/g) → maliyet 0.5.
    Diğer ekleme/silme/değiştirme → maliyet 1.0.
    """
    if a == b:
        return 0.0
    la, lb = len(a), len(b)
    prev = [float(j) for j in range(lb + 1)]
    for i in range(1, la + 1):
        curr = [float(i)] + [0.0] * lb
        for j in range(1, lb + 1):
            ca, cb = a[i - 1], b[j - 1]
            if ca == cb:
                cost = 0.0
            elif frozenset((ca, cb)) in _TR_PAIRS:
                cost = 0.5
            else:
                cost = 1.0
            curr[j] = min(
                prev[j] + 1.0,        # silme
                curr[j - 1] + 1.0,    # ekleme
                prev[j - 1] + cost,   # değiştirme
            )
        prev = curr
    return prev[lb]


class _BKTree:
    """BK-tree — edit-distance sorguları için.

    insert O(log n) ort., query O(log n) ort.
    build() O(n log n) ort., O(n²) en kötü.
    Leksikon 26k lemma için tipik build süresi 50–200ms.
    """

    def __init__(self) -> None:
        self._root: tuple[str, dict] | None = None
        self._frozen: bool = False  # build() sonrası True

    def build(self, words: Iterable[str]) -> "_BKTree":
        for w in words:
            self._insert(w)
        self._frozen = True  # artık değiştirilemez
        return self

    def _insert(self, word: str) -> None:
        if self._frozen:
            raise RuntimeError("_BKTree: build() tamamlandıktan sonra insert yapılamaz")
        if self._root is None:
            self._root = (word, {})
            return
        self._insert_at(self._root[0], self._root[1], word)

    def _insert_at(self, node_word: str, children: dict, word: str) -> None:
        # ×2 ölçekleme: 0.5 adımları → tam sayı (1, 2, 3, 4...)
        d = int(round(_tr_distance(node_word, word) * 2))
        if d == 0:
            return
        if d not in children:
            children[d] = (word, {})
        else:
            child_word, child_children = children[d]
            self._insert_at(child_word, child_children, word)

    def query(self, word: str, max_distance: float) -> list[tuple[float, str]]:
        """max_distance içindeki (distance, lemma) çiftleri — SIRASIZ döner."""
        if self._root is None:
            return []
        results: list[tuple[float, str]] = []
        max_d_int = int(round(max_distance * 2))
        self._query_at(self._root[0], self._root[1], word, max_d_int, results)
        return results

    def _query_at(
        self,
        node_word: str,
        children: dict,
        word: str,
        max_d_int: int,
        results: list,
    ) -> None:
        d_float = _tr_distance(node_word, word)
        d_int = int(round(d_float * 2))
        if d_int <= max_d_int:
            results.append((d_float, node_word))
        lo = max(0, d_int - max_d_int)
        hi = d_int + max_d_int
        for key, (child_word, child_children) in children.items():
            if lo <= key <= hi:
                self._query_at(child_word, child_children, word, max_d_int, results)


@lru_cache(maxsize=1)
def _build_tree(roots_key: frozenset) -> _BKTree:
    """Leksikon BK-tree singleton — ilk suggest() çağrısında inşa edilir."""
    return _BKTree().build(roots_key)


def _get_tree(roots: frozenset[str]) -> _BKTree:
    return _build_tree(roots)
