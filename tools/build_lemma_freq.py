#!/usr/bin/env python3
"""Yüzey-frekans listesi → turkgram gömülü LEMMA-frekans tablosu (Faz 2b).

`disambiguation.rank(freq=…)` kancasını besler. Yöntem: her yüzey biçimi turkgram'ın
KENDİ analizör + gömülü leksikonuyla çözümle, yüzeyin sayımını çözülen DISTINCT lemma(lar)a
dağıt (belirsizse eşit böl), lemma bazında topla. Leksikon-dışı/gürültü yüzey → analiz [] →
atlanır. Böylece tablo turkgram'ın tanıdığı lemmalarla sınırlı ve kendinden-tutarlı olur.

Kaynak yüzey-frekansı: hermitdave/FrequencyWords (OpenSubtitles, MIT) — atıf
`THIRD_PARTY_LICENSES.md`. Frekans OLGUsu telif konusu değildir (CLAUDE.md §3); ham liste
KOPYALANMAZ, yalnız türetilmiş lemma-sayımı gömülür.

Çıktılar:
  -o/--out          Özet: lemma<TAB>toplam (gömülü tablo, mevcut format)
  --out-detail      Detay: lemma<TAB>toplam / <TAB>yüzey<TAB>pay / boş satır

Kullanım:
    python tools/build_lemma_freq.py <tr_full.txt> -o turkgram/data/lemma_freq_tr.tsv --top 60000
    # Detay dosyasıyla:
    python tools/build_lemma_freq.py <tr_full.txt> -o ... --out-detail detail.tsv --top 60000
    # Kontrol noktası ile (kesintide devam):
    python tools/build_lemma_freq.py <tr_full.txt> -o ... --top 60000 --checkpoint ckpt.json --checkpoint-interval 5000
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from turkgram import analysis as an
from turkgram import lexicon as lx


Detail = dict[str, dict[str, float]]  # lemma → {yüzey: pay}


def _save_checkpoint(path: Path, seen: int, acc: dict[str, float], detail: Detail) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({"seen": seen, "acc": dict(acc), "detail": {k: dict(v) for k, v in detail.items()}},
                   ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def _load_checkpoint(path: Path) -> tuple[int, dict[str, float], Detail]:
    data = json.loads(path.read_text(encoding="utf-8"))
    acc = defaultdict(float, {k: float(v) for k, v in data["acc"].items()})
    detail: Detail = {k: {s: float(c) for s, c in v.items()} for k, v in data.get("detail", {}).items()}
    return data["seen"], acc, detail


def build(
    freq_path: Path,
    top: int,
    progress: int = 0,
    checkpoint: Path | None = None,
    checkpoint_interval: int = 5000,
) -> tuple[dict[str, float], Detail]:
    roots = lx.load()

    # Kontrol noktasından devam et
    resume_from = 0
    acc: dict[str, float] = defaultdict(float)
    detail: Detail = {}
    if checkpoint and checkpoint.exists():
        resume_from, acc, detail = _load_checkpoint(checkpoint)
        print(f"  ↺ kontrol noktasından devam: {resume_from} yüzey, {len(acc)} lemma", flush=True)

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
            if seen <= resume_from:
                continue  # zaten işlendi, atla
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
                surfaces = detail.setdefault(lemma, {})
                surfaces[word] = surfaces.get(word, 0.0) + share
            if checkpoint and checkpoint_interval and seen % checkpoint_interval == 0:
                _save_checkpoint(checkpoint, seen, acc, detail)
    return acc, detail


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("freq", type=Path, help="Yüzey-frekans listesi (kelime<space>sayı)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--top", type=int, default=60000,
                    help="İşlenecek en sık N yüzey (varsayılan 60000)")
    ap.add_argument("--progress", type=int, default=0,
                    help="Her N yüzeyde ilerleme yazdır (0=kapalı)")
    ap.add_argument("--checkpoint", type=Path, default=None,
                    help="Kontrol noktası dosyası (JSON); yoksa oluşturulur, varsa devam edilir")
    ap.add_argument("--checkpoint-interval", type=int, default=5000,
                    help="Kaç yüzeyde bir kontrol noktası kaydedilsin (varsayılan 5000)")
    ap.add_argument("--out-detail", type=Path, default=None,
                    help="Detay dosyası: her lemma altında katkıda bulunan yüzeyler")
    ap.add_argument("--keep-checkpoint", action="store_true",
                    help="Bitince kontrol noktası dosyasını silme")
    args = ap.parse_args(argv)

    lemma_freq, detail = build(
        args.freq, args.top,
        progress=args.progress,
        checkpoint=args.checkpoint,
        checkpoint_interval=args.checkpoint_interval,
    )
    # tam sayıya yuvarla; sıklık azalan, eşitlikte lemma alfabetik
    rows = sorted(((lemma, round(c)) for lemma, c in lemma_freq.items() if round(c) > 0),
                  key=lambda t: (-t[1], t[0]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(f"{lemma}\t{c}" for lemma, c in rows) + "\n",
                        encoding="utf-8")
    print(f"{len(rows)} lemma → {args.out}")
    print("en sık 10:", rows[:10])

    if args.out_detail:
        lines: list[str] = []
        for lemma, total in rows:
            lines.append(f"{lemma}\t{total}")
            surfaces = detail.get(lemma, {})
            for surface, share in sorted(surfaces.items(), key=lambda t: -t[1]):
                lines.append(f"\t{surface}\t{round(share)}")
            lines.append("")  # lemmalar arası boş satır
        args.out_detail.parent.mkdir(parents=True, exist_ok=True)
        args.out_detail.write_text("\n".join(lines), encoding="utf-8")
        print(f"detay → {args.out_detail}")

    if args.checkpoint and args.checkpoint.exists() and not args.keep_checkpoint:
        args.checkpoint.unlink()
        print(f"  ✓ kontrol noktası temizlendi: {args.checkpoint}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
