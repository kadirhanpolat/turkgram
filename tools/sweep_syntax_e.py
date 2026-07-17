"""sweep_syntax_e.py — Faz E hakem: parse_phrase + constituency_to_dep korpus taraması.

Tarama hedefleri:
  1. np_uret / pp_uret / degmod_uret / koordine_np — temsili NP/PP örnekleri
  2. parse_phrase — leksikon fiilleri × basit özne+fiil cümleleri
  3. constituency_to_dep — aynı cümleler üzerinde 0 çökme

Çalıştırma:
    PYTHONUTF8=1 python tools/sweep_syntax_e.py
"""
from __future__ import annotations

import sys
import traceback

from turkgram import tokenize, parse_text
from turkgram.lexicon import load as _load_lexicon
from turkgram.syntax import np_uret, pp_uret, degmod_uret, koordine_np
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep


def _run() -> None:
    errors: list[str] = []
    total = 0

    # ── 1. NP üretimi ────────────────────────────────────────────────────
    np_cases = [
        ("ev",      {},                                "ev"),
        ("kapı",    {"tamlayan": "ev"},                "evin kapısı"),
        ("kitap",   {"miktar": "üç", "durum": "acc"},  "üç kitabı"),
        ("araba",   {"on_sifatlar": ("kırmızı",)},     "kırmızı araba"),
        ("öğrenci", {"iyelik": "1sg"},                 "öğrencim"),
    ]
    for head, kwargs, expected in np_cases:
        total += 1
        try:
            got = np_uret(head, **kwargs)
            if got != expected:
                errors.append(f"np_uret({head!r},{kwargs}) → {got!r} != {expected!r}")
        except Exception as exc:
            errors.append(f"np_uret({head!r},{kwargs}) ÇÖKME: {exc}")

    # ── 2. PP üretimi ─────────────────────────────────────────────────────
    pp_cases = [
        ("ev",  "göre"),
        ("okul","için"),
        ("ben", "göre"),
    ]
    for isim, edat in pp_cases:
        total += 1
        try:
            pp_uret(isim, edat)
        except Exception as exc:
            errors.append(f"pp_uret({isim!r},{edat!r}) ÇÖKME: {exc}")

    # ── 3. DegMod üretimi ─────────────────────────────────────────────────
    for head, derece in [("hızlı", "çok"), ("güzel", None), ("büyük", "en")]:
        total += 1
        try:
            degmod_uret(head, derece=derece)
        except Exception as exc:
            errors.append(f"degmod_uret({head!r},{derece!r}) ÇÖKME: {exc}")

    # ── 4. koordine_np ────────────────────────────────────────────────────
    for items, conj in [(["kitap", "defter"], "ve"), (["ev", "araba"], "veya")]:
        total += 1
        try:
            koordine_np(items, conj)
        except Exception as exc:
            errors.append(f"koordine_np ÇÖKME: {exc}")

    # ── 5. parse_phrase + constituency_to_dep — leksikon fiilleri × cümle ─
    lex = _load_lexicon(pos=("verb",))
    verbs = sorted(lex)[:200]      # ilk 200 fiil yeterli
    subjects = ["öğrenci", "çocuk", "adam"]

    for verb_lemma in verbs:
        for subj in subjects:
            roots = {subj, verb_lemma}
            from turkgram.morphology import conjugate
            try:
                surface = conjugate(verb_lemma, "past", "3sg")
            except Exception:
                continue
            text = f"{subj} {surface}"
            total += 1
            try:
                tokens = tokenize(text)
                analyses = parse_text(text, roots=roots)
                tree = parse_phrase(tokens, analyses)
                dep = constituency_to_dep(tree)
                # temel sağlık kontrolleri
                assert len(dep) == len(tokens), f"uzunluk uyumsuzluğu: {len(dep)} != {len(tokens)}"
                root_count = sum(1 for t in dep if t.deprel == "root")
                assert root_count == 1, f"root sayısı: {root_count}"
            except AssertionError as exc:
                errors.append(f"{text!r}: {exc}")
            except Exception as exc:
                errors.append(f"{text!r}: ÇÖKME — {exc}\n{traceback.format_exc()}")

    # ── Sonuç ────────────────────────────────────────────────────────────
    print(f"Tarama: {total} çağrı, {len(errors)} hata")
    if errors:
        for e in errors[:30]:
            print(" ", e)
        sys.exit(1)
    else:
        print("Tüm kontroller geçti ✓")


if __name__ == "__main__":
    _run()
