"""Gömülü Türkçe kök leksikonu — opt-in yükleyici (Faz 2b).

`analyze(surface, roots=...)` çıplak-önek gürültüsünü (SPEC §8.1) gerçek lemma
kümesiyle eler. Bu modül, pakete gömülü küratörlü lemma listesini sağlar; böylece
çözümleyici, tüketici kendi sözlüğünü geçirmeden de makul çalışır.

TASARIM (değişmez): Bu OPT-IN'dir. `analyze(roots=None)` davranışı DEĞİŞMEZ
(leksikonsuz = hepsi hypothetical gürültü). Leksikonu isteyen çağırır:

    from turkgram import lexicon, analysis
    roots = lexicon.load()                 # tüm lemmalar
    analysis.analyze("evler", roots=roots)

Kaynak: Zemberek `master-dictionary.dict` (Apache-2.0); atıf `THIRD_PARTY_LICENSES.md`.
Fiiller mastar (`gelmek`), isim-soylular çıplak (`ev`). Üretim: `tools/build_lexicon.py`.
"""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Iterable

# Veri dosyasındaki POS kategorileri (build_lexicon.py ile senkron).
POS_TAGS: frozenset[str] = frozenset({
    "verb", "noun", "adj", "adv", "pron", "num",
    "postp", "conj", "det", "interj", "dup", "ques",
})

# Çekilebilir gövde kovaları — `roots` için mantıklı varsayılan alt-küme.
# İsim-soylular nominal çekim (durum/iyelik/ekfiil) alır; fiiller çekimlenir.
_INFLECTABLE: frozenset[str] = frozenset({
    "verb", "noun", "adj", "adv", "pron", "num",
})

_DATA_FILE = "lexicon_tr.tsv"
_FREQ_FILE = "lemma_freq_tr.tsv"


@lru_cache(maxsize=1)
def _load_raw() -> tuple[tuple[str, str], ...]:
    """Ham (lemma, pos) çiftleri — bir kez okunur, cache'lenir."""
    text = files("turkgram").joinpath("data", _DATA_FILE).read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line:
            continue
        lemma, _, pos = line.partition("\t")
        if lemma and pos:
            rows.append((lemma, pos))
    return tuple(rows)


def _normalize_pos(pos: str | Iterable[str] | None) -> frozenset[str]:
    if pos is None:
        return _INFLECTABLE
    if isinstance(pos, str):
        pos = {pos}
    wanted = frozenset(pos)
    unknown = wanted - POS_TAGS
    if unknown:
        raise ValueError(
            f"pos: bilinmeyen kategori {sorted(unknown)}. "
            f"Geçerli: {', '.join(sorted(POS_TAGS))}"
        )
    return wanted


@lru_cache(maxsize=16)
def _load_filtered(wanted: frozenset[str]) -> frozenset[str]:
    """POS filtreli lemma kümesi — normalize edilmiş frozenset üzerinden cache'lenir."""
    return frozenset(lemma for lemma, p in _load_raw() if p in wanted)


def load(pos: str | Iterable[str] | None = None) -> frozenset[str]:
    """Gömülü leksikonu lemma kümesi olarak döndür (`analyze(roots=...)` için).

    Args:
        pos: POS filtresi. None → çekilebilir gövdeler (verb+noun+adj+adv+pron+num;
             interj/dup/conj/postp/det/ques hariç). Tek etiket ("verb") ya da
             etiket kümesi ({"verb","noun"}) verilebilir. "all" için POS_TAGS geç.

    Returns:
        Değişmez lemma kümesi (frozenset).

    Raises:
        ValueError: bilinmeyen POS etiketi.
    """
    return _load_filtered(_normalize_pos(pos))


@lru_cache(maxsize=1)
def pos_map() -> dict[str, str]:
    """{lemma: pos} sözlüğü (POS sorgusu için). Değiştirmeyin — paylaşımlı."""
    return {lemma: pos for lemma, pos in _load_raw()}


def size() -> int:
    """Leksikondaki toplam lemma sayısı (tüm POS)."""
    return len(_load_raw())


@lru_cache(maxsize=1)
def load_freq() -> dict[str, int]:
    """Gömülü lemma-frekans tablosu → {lemma: sayım} (`disambiguation.rank(freq=…)` için).

    hermitdave/FrequencyWords (OpenSubtitles, MIT) yüzey-frekansından turkgram'ın kendi
    analizör + leksikonuyla türetilmiştir (belirsiz yüzey sayımı distinct lemmalara eşit
    bölünür). Tabloda OLMAYAN lemma → sıklık 0 (disambiguation dilbilimsel önceliğe düşer).
    Üretim: `tools/build_lemma_freq.py`; atıf `THIRD_PARTY_LICENSES.md`.

    Returns:
        {lemma: sayım} sözlüğü. DEĞİŞTİRMEYİN — paylaşımlı (cache'li).
    """
    text = files("turkgram").joinpath("data", _FREQ_FILE).read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for line in text.splitlines():
        if not line:
            continue
        lemma, _, count = line.partition("\t")
        if lemma and count:
            out[lemma] = int(count)
    return out
