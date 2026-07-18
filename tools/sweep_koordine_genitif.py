"""Koordine genitif tamlayan — korpus çökme taraması (hakem).

Özel-isim apostrof-ek merge + koordine genitif tamlama üzerinden çökme taraması.
turkgram bağımsız (korpus YOK) → leksikon isimlerinden sentetik cümle üretir.

Kullanım:
    PYTHONUTF8=1 python tools/sweep_koordine_genitif.py
"""
from __future__ import annotations

from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep, to_conllu
from turkgram.morphology_noun import decline
from turkgram import lexicon


def _run(text: str, roots: set[str]) -> None:
    tokens = tokenize(text)
    analyses = parse_text(text, roots)
    tree = parse_phrase(tokens, analyses)
    dep = constituency_to_dep(tree)
    to_conllu(dep, sent_id="s", text=text)  # CoNLL-U yolu da tetiklensin


def main() -> None:
    nouns = sorted(lexicon.load(pos={"noun"}))
    # Temsili örneklem (tamamı çok yavaş) — çeşitli ses sınıfları
    sample = nouns[::max(1, len(nouns) // 400)][:400]
    crashes = 0
    total = 0

    # 1) Özel-isim apostrof-ek merge: her durum eki × örneklem
    apos_suffixes = ["'nin", "'in", "'de", "'da", "'ye", "'ya", "'den", "'dan",
                     "'yi", "'le", "'nın", "'nun"]
    for w in sample[:120]:
        base = w[:1].upper() + w[1:]
        for suf in apos_suffixes:
            total += 1
            try:
                _run(f"{base}{suf} evi", {"ev", w})
            except Exception as e:  # noqa: BLE001
                crashes += 1
                print(f"ÇÖKME (merge): {base}{suf} evi -> {type(e).__name__}: {e}")

    # 2) Koordine genitif tamlama: ad çiftleri (gen + gen) + head
    for i in range(0, min(len(sample), 300) - 2, 3):
        a, b, head = sample[i], sample[i + 1], sample[i + 2]
        try:
            ga, gb = decline(a, case="gen"), decline(b, case="gen")
        except Exception:  # noqa: BLE001
            continue
        head_poss = None
        try:
            head_poss = decline(head, possessive="3sg")
        except Exception:  # noqa: BLE001
            head_poss = head
        text = f"{ga} ve {gb} {head_poss}"
        total += 1
        try:
            _run(text, {a, b, head})
        except Exception as e:  # noqa: BLE001
            crashes += 1
            print(f"ÇÖKME (koord): {text} -> {type(e).__name__}: {e}")

    print(f"\nToplam {total} çağrı, {crashes} çökme.")


if __name__ == "__main__":
    main()
