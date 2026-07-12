#!/usr/bin/env python3
"""Yüzey-frekans listesi → turkgram gömülü LEMMA-frekans tablosu (Faz 2b).

`disambiguation.rank(freq=…)` kancasını besler. Yöntem: her yüzey biçimi turkgram'ın
KENDİ analizör + gömülü leksikonuyla çözümle, yüzeyin sayımını çözülen DISTINCT lemma(lar)a
dağıt (belirsizse eşit böl), lemma bazında topla. Leksikon-dışı/gürültü yüzey → analiz [] →
atlanır. Böylece tablo turkgram'ın tanıdığı lemmalarla sınırlı ve kendinden-tutarlı olur.

Kaynak yüzey-frekansı: hermitdave/FrequencyWords (OpenSubtitles, MIT) — atıf
`THIRD_PARTY_LICENSES.md`. Frekans OLGUsu telif konusu değildir (CLAUDE.md §3); ham liste
KOPYALANMAZ, yalnız türetilmiş lemma-sayımı gömülür.

Kullanım:
    python tools/build_lemma_freq.py <tr_full.txt> -o turkgram/data/lemma_freq_tr.tsv --top 60000
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from turkgram import analysis as an
from turkgram import lexicon as lx


def build(freq_path: Path, top: int, progress: int = 0) -> dict[str, float]:
    roots = lx.load()
    acc: dict[str, float] = defaultdict(float)
    seen = 0
    with freq_path.open(encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            word, count_s = parts
            try:
                count = int(count_s)
            except ValueError:
                continue
            seen += 1
            if seen > top:
                break
            if progress and seen % progress == 0:
                print(f"  … {seen}/{top} yüzey, {len(acc)} lemma", flush=True)
            try:
                cands = an.analyze(word, roots=roots)
            except ValueError:
                continue
            lemmas = {a.lemma for a in cands}
            if not lemmas:
                continue
            share = count / len(lemmas)  # belirsiz yüzey → eşit böl (SPEC prior)
            for lemma in lemmas:
                acc[lemma] += share
    return acc


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("freq", type=Path, help="Yüzey-frekans listesi (kelime<space>sayı)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--top", type=int, default=60000,
                    help="İşlenecek en sık N yüzey (varsayılan 60000)")
    ap.add_argument("--progress", type=int, default=0,
                    help="Her N yüzeyde ilerleme yazdır (0=kapalı)")
    args = ap.parse_args(argv)

    lemma_freq = build(args.freq, args.top, progress=args.progress)
    # tam sayıya yuvarla; sıklık azalan, eşitlikte lemma alfabetik
    rows = sorted(((lemma, round(c)) for lemma, c in lemma_freq.items() if round(c) > 0),
                  key=lambda t: (-t[1], t[0]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(f"{lemma}\t{c}" for lemma, c in rows) + "\n",
                        encoding="utf-8")
    print(f"{len(rows)} lemma → {args.out}")
    print("en sık 10:", rows[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
