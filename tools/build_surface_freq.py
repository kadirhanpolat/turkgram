#!/usr/bin/env python3
"""Her lemmadan motor aracılığıyla tüm yüzey biçimlerini üret, tr_full.txt'te ara.

Yaklaşım: analyze() YOK. Lemma → motorla enumerate → dict lookup (O(1)).
Sonuç: yalnız corpus'ta geçen biçimler yazılır (yoksa = frekans 0, dosyada yer kaplamaz).

Çıktılar:
  -o / --out         Özet TSV: lemma<TAB>toplam (sıklık azalan)
  --out-detail       Detay TSV: lemma<TAB>toplam / <TAB>yüzey<TAB>sayı / boş satır
  --zero-lemmas      Corpus'ta hiç geçmeyen lemma listesi (txt)

Kullanım:
    python tools/build_surface_freq.py tools/tr_full.txt \\
        -o turkgram/data/lemma_freq_tr.tsv \\
        --out-detail turkgram/data/lemma_freq_detail_tr.tsv \\
        --zero-lemmas turkgram/data/lemma_zero_tr.txt
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

from turkgram import lexicon as lx
from turkgram import morphology as mo
from turkgram import morphology_noun as mn
from turkgram import nonfinite as nf

# ── Parametre kümeleri ──────────────────────────────────────────────────────
_FINITE_TENSES = ("pres", "past", "fut", "aorist", "evid", "cond", "necess", "opt", "imp")
_PERSONS       = mo.PERSONS                          # 1sg 2sg 3sg 1pl 2pl 3pl
_CASES         = mn.CASES                            # nom acc dat loc abl gen ins
_NUMBERS       = mn.NUMBERS                          # sg pl
_POSSESSIVES   = mn.POSSESSIVES                      # None 1sg 2sg 3sg 1pl 2pl 3pl
_COPULA_AUX    = (None, "hikaye", "rivayet", "sart")
_CONVERBS      = sorted(nf.CONVERBS)
_PARTICIPLES   = sorted(nf.PARTICIPLES)


def _safe(fn, *args, **kwargs) -> str | None:
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


def _verb_forms(lemma: str) -> list[str]:
    out: list[str] = []
    # Çekimli fiil: tense × person × neg × question
    for tense, person, neg, quest in itertools.product(
        _FINITE_TENSES, _PERSONS, (False, True), (False, True)
    ):
        f = _safe(mo.conjugate, lemma, tense, person, negative=neg, question=quest)
        if f:
            out.append(f)
    # Ulaç (converb)
    for kind in _CONVERBS:
        f = _safe(nf.converb, lemma, kind)
        if f:
            out.append(f)
    # Fiilimsi (participle) × iyelik × durum
    for kind in _PARTICIPLES:
        for poss, case in itertools.product(_POSSESSIVES, (None, *_CASES)):
            f = _safe(nf.participle, lemma, kind, possessive=poss, case=case)
            if f:
                out.append(f)
    return out


def _nominal_forms(lemma: str) -> list[str]:
    out: list[str] = []
    # Çekim: durum × sayı × iyelik
    for case, number, poss in itertools.product(_CASES, _NUMBERS, _POSSESSIVES):
        f = _safe(mn.decline, lemma, case=case, number=number, possessive=poss)
        if f:
            out.append(f)
    # Ekfiil: aux × kişi × soru (+ case/poss kombolarından gelen gövde)
    for aux, person, quest in itertools.product(_COPULA_AUX, _PERSONS, (False, True)):
        f = _safe(mn.copula, lemma, aux, person, question=quest)
        if f:
            out.append(f)
        # İyelikli gövde + ekfiil
        for poss in _POSSESSIVES:
            if poss is None:
                continue
            f = _safe(mn.copula, lemma, aux, person, possessive=poss, question=quest)
            if f:
                out.append(f)
    return out


def _forms_for(lemma: str, pos: str) -> list[str]:
    """Lemmaya ait tüm yüzey biçimlerini döndür; pos'a göre üretici seçilir."""
    if pos == "verb":
        return _verb_forms(lemma)
    if pos in ("noun", "adj", "adv", "pron", "num"):
        return _nominal_forms(lemma)
    # dup, interj, conj, postp, det, ques — direkt lookup yeterli
    return [lemma]


def _load_freq(path: Path) -> dict[str, int]:
    freq: dict[str, int] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 2:
                try:
                    freq[parts[0]] = int(parts[1])
                except ValueError:
                    pass
    return freq


def build(
    freq_path: Path,
    progress: int = 0,
) -> tuple[
    dict[str, int],              # lemma → toplam
    dict[str, dict[str, int]],   # lemma → {yüzey: sayı}
    list[str],                    # corpus'ta hiç geçmeyen lemmalar
]:
    print(f"  Yükleniyor: {freq_path}", flush=True)
    freq_raw = _load_freq(freq_path)
    print(f"  {len(freq_raw):,} yüzey yüklendi", flush=True)

    used: set[str] = set()
    totals:  dict[str, int]              = {}
    detail:  dict[str, dict[str, int]]   = {}
    zero_lemmas: list[str]               = []

    lemma_pos = list(lx._load_raw())  # [(lemma, pos), ...]
    n = len(lemma_pos)

    for i, (lemma, pos) in enumerate(lemma_pos):
        if progress and (i + 1) % progress == 0:
            print(f"  … {i+1}/{n} lemma, {len(totals)} hit", flush=True)

        forms = _forms_for(lemma, pos)
        surfaces: dict[str, int] = {}
        for form in forms:
            if form in freq_raw and form not in surfaces:
                surfaces[form] = freq_raw[form]
                used.add(form)

        total = sum(surfaces.values())
        if total == 0:
            zero_lemmas.append(lemma)
            continue

        totals[lemma] = total
        detail[lemma] = surfaces

    print(f"  Tamamlandı: {len(totals)} lemma hit, {len(zero_lemmas)} sıfır", flush=True)
    return totals, detail, zero_lemmas


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("freq", type=Path, help="Yüzey-frekans listesi (kelime<space>sayı)")
    ap.add_argument("-o", "--out", type=Path, required=True,
                    help="Özet TSV: lemma<TAB>toplam")
    ap.add_argument("--out-detail", type=Path, default=None,
                    help="Detay TSV: lemma + katkıda bulunan yüzeyler")
    ap.add_argument("--zero-lemmas", type=Path, default=None,
                    help="Corpus'ta hiç geçmeyen lemma listesi")
    ap.add_argument("--progress", type=int, default=2000,
                    help="Her N lemmada ilerleme yazdır (varsayılan 2000)")
    args = ap.parse_args(argv)

    totals, detail, zero_lemmas = build(args.freq, progress=args.progress)

    # Özet dosyası — sıklık azalan, eşitlikte lemma alfabetik
    rows = sorted(totals.items(), key=lambda t: (-t[1], t[0]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "\n".join(f"{lemma}\t{c}" for lemma, c in rows) + "\n",
        encoding="utf-8",
    )
    print(f"{len(rows)} lemma → {args.out}")
    print("en sık 10:", rows[:10])

    # Detay dosyası
    if args.out_detail:
        lines: list[str] = []
        for lemma, total in rows:
            lines.append(f"{lemma}\t{total}")
            for surface, count in sorted(detail[lemma].items(), key=lambda t: -t[1]):
                lines.append(f"\t{surface}\t{count}")
            lines.append("")
        args.out_detail.parent.mkdir(parents=True, exist_ok=True)
        args.out_detail.write_text("\n".join(lines), encoding="utf-8")
        print(f"detay → {args.out_detail}")

    # Sıfır lemmalar
    if args.zero_lemmas:
        args.zero_lemmas.parent.mkdir(parents=True, exist_ok=True)
        args.zero_lemmas.write_text("\n".join(zero_lemmas) + "\n", encoding="utf-8")
        print(f"{len(zero_lemmas)} sıfır lemma → {args.zero_lemmas}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
