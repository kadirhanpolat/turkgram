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

from .analysis import analyze as _analyze, _call_generator as _regen_surface, _make_frozen
from . import lexicon as _lexicon

# Morfolojik şablon yeniden üretimi desteklenen kind'lar (V2).
# Türetme / ikileme gibi karmaşık kind'lar kapsam dışı.
_REGENERATABLE_KINDS: frozenset[str] = frozenset({
    "conjugate", "decline", "copula",
    "converb", "converb_casina", "converb_ken",
    "participle",
})

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


def _regenerate(lemma: str, analysis: object) -> str | None:
    """analysis'ın morfolojik şablonunu farklı bir köke uygular (V2 yardımcısı).

    analysis.kind ∈ _REGENERATABLE_KINDS → _call_generator ile yüzey üretir.
    Diğer kind'lar veya üretim hatası → None.
    """
    if analysis.kind not in _REGENERATABLE_KINDS:  # type: ignore[union-attr]
        return None
    frozen = _make_frozen(analysis.kwargs)  # type: ignore[union-attr]
    return _regen_surface(analysis.kind, lemma, frozen)


def suggest(
    word: str,
    *,
    roots: frozenset[str] | None = None,
    max_suggestions: int = 5,
    max_distance: float = 2.0,
) -> list[str]:
    """Yanlış yazılmış kelime için öneri listesi — V2.

    V2 algoritması:
    1. Morfolojik şablon yolu: analyze(word, roots=None) → hypothetical analizler →
       her analiz için BK-tree'yi kök üzerinde sorgula → correct_root ile yüzey yeniden üret.
    2. V1 fallback: tüm kelime üzerinde BK-tree (çözümlenemez typo'lar + çıplak isimler).

    Çıplak (nom) typo'lar için V1 ve V2 aynı sonucu verir (lemma = surface).
    Çekimli typo'larda V2, yüzey biçim (kök + doğru ek) önerir.
    """
    if max_suggestions < 1:
        raise ValueError(f"max_suggestions en az 1 olmalı, verildi: {max_suggestions}")
    if max_distance <= 0:
        raise ValueError(f"max_distance 0'dan büyük olmalı, verildi: {max_distance}")

    word = _tr_lower(word.strip())
    if not word or len(word) > _MAX_WORD_LEN:
        return []

    r = _roots(roots)
    tree = _get_tree(r)

    try:
        freq: dict[str, int] = _lexicon.load_freq()
    except Exception:
        freq = {}

    candidates: list[tuple[float, str]] = []
    seen: set[str] = set()

    # V1: BK-tree tüm kelime üzerinde (çıplak isim typo'ları için birincil yol).
    # V1 önce çalışır — doğru distance'ı garantiler (V2 üstüne yazamaz).
    for dist, lemma in tree.query(word, max_distance):
        if lemma not in seen:
            seen.add(lemma)
            candidates.append((dist, lemma))

    # V2: Morfolojik şablon yolu — yalnız V1'de bulunmayan yüzey biçimler eklenir.
    # Çekimli typo'larda V1'in boş döndüğü durumlarda devreye girer.
    hyp_analyses = _analyze(word, roots=None)
    for a in hyp_analyses:
        if a.kind not in _REGENERATABLE_KINDS:
            continue
        for dist, correct_lemma in tree.query(a.lemma, max_distance):
            surface = _regenerate(correct_lemma, a)
            if surface is not None and surface not in seen:
                seen.add(surface)
                candidates.append((dist, surface))

    # Sırala: distance artan, eşitte frekans azalan, sonra alfabetik (deterministik)
    candidates.sort(key=lambda x: (x[0], -freq.get(x[1], 0), x[1]))
    return [s for _, s in candidates[:max_suggestions]]


def check(
    word: str,
    *,
    roots: frozenset[str] | None = None,
    max_suggestions: int = 5,
    max_distance: float = 2.0,
) -> SpellResult:
    """Geçerlilik + öneri — SpellResult döner.

    is_valid=True ise suggestions=() (BK-tree sorgusu yapılmaz, hızlı yol).
    """
    if is_valid(word, roots=roots):
        return SpellResult(word=word, is_valid=True, suggestions=())
    sugs = suggest(word, roots=roots, max_suggestions=max_suggestions, max_distance=max_distance)
    return SpellResult(word=word, is_valid=False, suggestions=tuple(sugs))


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
