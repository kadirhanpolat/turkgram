"""sweep_sentence.py — cümle çözümleme korpus çökme taraması (hakem kontrolü).

Leksikon sözcüklerinden sentetik cümleler kurar + tek-token/edge girdiler → analyze_sentence
0 çökme doğrular. Üretim değil, sağlamlık taraması.

Kullanım: PYTHONUTF8=1 python tools/sweep_sentence.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from turkgram import lexicon
from turkgram.sentence import analyze_sentence


def main():
    roots = lexicon.load()
    words = sorted(roots)
    nouns = [w for w in words if not w.endswith("mek") and not w.endswith("mak")][:400]
    verbs = [w for w in words if w.endswith("mek") or w.endswith("mak")][:200]

    crashes = 0
    n = 0

    # tek-token + edge
    for w in (words[:2000] + ["", "  ", ".", "mi", "değil", "ve", "ah", "çat"]):
        try:
            analyze_sentence(w, roots=roots); n += 1
        except Exception as e:
            crashes += 1
            print(f"ÇÖKME(tek) {w!r}: {type(e).__name__}: {e}")

    # sentetik çok-token cümleler (özne + tümleç + yüklem kalıpları)
    import itertools
    sample_verbs = ["gitti", "geldi", "okudu", "yaptı", "gördü", "verdi", "aldı"]
    cases = ["", "yı", "ya", "da", "dan"]
    for subj, obj in itertools.islice(itertools.product(nouns[:60], nouns[:60]), 1500):
        for v in sample_verbs[:3]:
            s = f"{subj} {obj} {v}"
            try:
                analyze_sentence(s, roots=roots); n += 1
            except Exception as e:
                crashes += 1
                print(f"ÇÖKME(çok) {s!r}: {type(e).__name__}: {e}")
                if crashes > 20:
                    print("...20+ çökme, durduruluyor"); return

    print(f"\n{n} çağrı, {crashes} çökme")


if __name__ == "__main__":
    main()
