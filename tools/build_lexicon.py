#!/usr/bin/env python3
"""Zemberek `master-dictionary.dict` (Apache-2.0) → turkgram gömülü kök leksikonu.

ÜRETİLEBİLİRLİK / PROVENANCE: `turkgram/data/lexicon_tr.tsv` bu betikle üretilir.
Kaynak: https://github.com/ahmetaa/zemberek-nlp (Apache License 2.0). Atıf ve tam
lisans `THIRD_PARTY_LICENSES.md`'de. Gramer/sözcük OLGUSU telifsizdir (CLAUDE.md §3);
Zemberek düzyazısı/kodu KOPYALANMAZ, yalnız lemma+POS olgusu çıkarılır.

Zemberek satır formatı:  `lemma [P:POS; A:Attr1, Attr2; Pr:telaffuz; ...]`
- POS etiketi YOKSA: lemma `-mak/-mek` ile bitiyorsa FİİL (mastar), değilse İSİM.
  (Zemberek fiilleri etiketsiz mastar tutar; `[P:Verb]` yalnız istisnaî "değil" için.)
- Punc atılır; "değil" (mastar-dışı fiil) atılır (çekilebilir gövde değil).

Kullanım:
    python tools/build_lexicon.py <master-dictionary.dict> [ek.dict ...] \
        -o turkgram/data/lexicon_tr.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Zemberek P:POS → turkgram kategori (küçük harf). Punc atılır (None).
_POS_MAP = {
    "Verb": "verb", "Noun": "noun", "Adj": "adj", "Adv": "adv",
    "Pron": "pron", "Num": "num", "Postp": "postp", "Conj": "conj",
    "Det": "det", "Interj": "interj", "Dup": "dup", "Ques": "ques",
    "Punc": None,
}

_P_RE = re.compile(r"P:([A-Za-z]+)")


def _tr_lower(s: str) -> str:
    """Türkçe küçültme (İ→i, I→ı) — analizör yüzey normalizasyonuyla aynı (#10)."""
    return s.replace("I", "ı").replace("İ", "i").lower()


def parse_line(line: str) -> tuple[str, str] | None:
    """Zemberek satırı → (lemma, pos) ya da None (atılacak)."""
    line = line.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"):
        return None  # boş / yorum satırı
    lemma = line.split(" [", 1)[0].strip()
    if not lemma:
        return None
    lemma = _tr_lower(lemma)
    m = _P_RE.search(line)
    if m:
        pos = _POS_MAP.get(m.group(1), "noun")  # bilinmeyen etiket → isim kovası
        if pos is None:  # Punc
            return None
        if m.group(1) == "Verb" and not lemma.endswith(("mak", "mek")):
            return None  # "değil" gibi mastar-dışı — çekilebilir gövde değil
    else:
        pos = "verb" if lemma.endswith(("mak", "mek")) else "noun"
    return lemma, pos


def build(sources: list[Path]) -> dict[str, str]:
    """Kaynak .dict dosyalarını birleştir → {lemma: pos}. İlk POS kazanır."""
    out: dict[str, str] = {}
    for src in sources:
        for line in src.read_text(encoding="utf-8").splitlines():
            parsed = parse_line(line)
            if parsed is None:
                continue
            lemma, pos = parsed
            out.setdefault(lemma, pos)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sources", nargs="+", type=Path, help="Zemberek .dict dosya(lar)ı")
    ap.add_argument("-o", "--out", type=Path, required=True, help="Çıktı TSV yolu")
    args = ap.parse_args(argv)

    lex = build(args.sources)
    lines = [f"{lemma}\t{pos}" for lemma, pos in sorted(lex.items())]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    from collections import Counter
    dist = Counter(lex.values())
    print(f"{len(lex)} lemma → {args.out}")
    print("POS dağılımı:", dict(dist.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
