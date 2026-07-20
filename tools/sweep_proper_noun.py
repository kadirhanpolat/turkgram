"""sweep_proper_noun.py — özel-ad etiketleme yanlış-pozitif taraması.

Ortak adlar (leksikon) özel ad ETİKETLENMEMELİ:
- küçük harf ortak ad → hiç tag YOK;
- cümle-başı büyük-harf ortak ad → analyze() danışmasıyla tag YOK (İstisna: gazetteer homograf).

Kullanım: PYTHONUTF8=1 python tools/sweep_proper_noun.py
"""
from turkgram import lexicon
from turkgram import proper_noun as pn


def main() -> None:
    roots = lexicon.load()
    pm = lexicon.pos_map()
    # ortak isim örneklemi (leksikon noun'ları, gazetteer/never-proper dışı)
    nouns = [w for w, p in pm.items()
             if p == "noun" and w not in pn._ALL_GAZETTEER
             and w not in pn._NEVER_PROPER and w.isalpha()]
    nouns = sorted(nouns)[:3000]

    fp_lower = 0     # küçük harf ortak ad → tag (olmamalı)
    fp_initial = 0   # cümle-başı Büyük ortak ad → tag (olmamalı; homograf hariç)
    crashes = 0
    for w in nouns:
        try:
            # küçük harf tümce-içi
            if pn.tag(f"onu {w} gördüm", roots=roots):
                fp_lower += 1
            # cümle-başı büyük harf
            cap = w[:1].upper() + w[1:]
            tags = pn.tag(f"{cap} geldi", roots=roots)
            if tags:
                fp_initial += 1
        except Exception as e:  # noqa: BLE001
            crashes += 1
            print(f"ÇÖKME: {w!r} → {type(e).__name__}: {e}")

    n = len(nouns)
    print(f"{n} ortak ad tarandı")
    print(f"küçük-harf yanlış-pozitif: {fp_lower} ({100*fp_lower/n:.2f}%)")
    print(f"cümle-başı yanlış-pozitif: {fp_initial} ({100*fp_initial/n:.2f}%)")
    print(f"çökme: {crashes}")
    # Örnek yanlış-pozitifler (cümle-başı)
    shown = 0
    for w in nouns:
        cap = w[:1].upper() + w[1:]
        if pn.tag(f"{cap} geldi", roots=roots) and shown < 15:
            print(f"  FP(cümle-başı): {cap}")
            shown += 1


if __name__ == "__main__":
    main()
