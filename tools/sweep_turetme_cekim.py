"""Türetme+çekim istifi korpus çökme/perf taraması (hakem)."""
import time
from turkgram.analysis import analyze
from turkgram.morphology_noun import decline
from turkgram.derivation import derivations
from turkgram import lexicon as lx

def main():
    nouns = sorted(lx.load(pos={"noun"}))
    sample = nouns[::max(1, len(nouns)//300)][:300]
    crashes = total = miss = 0
    t0 = time.perf_counter()
    for w in sample:
        # w'den bir türetme üret, sonra çek → round-trip
        try:
            ders = derivations(w, "noun")
        except Exception:
            continue
        for d in (ders or [])[:2]:
            derived = d["form"]
            for kw in ({"case": "acc"}, {"possessive": "3sg", "case": "abl"}):
                try:
                    surf = decline(derived, **kw)
                except Exception:
                    continue
                total += 1
                try:
                    res = analyze(surf, roots={w}, max_derivation_depth=5)
                except Exception as e:
                    crashes += 1
                    print(f"ÇÖKME: {surf} ({w}) -> {type(e).__name__}: {e}")
                    continue
                ok = any(a.kind == "derivation" and a.lemma == w
                         and a.kwargs.get("case") == kw.get("case")
                         and a.kwargs.get("possessive") == kw.get("possessive")
                         and not a.hypothetical for a in res)
                if not ok:
                    miss += 1
                    if miss <= 15:
                        print(f"MISS: {surf} ({w}, {kw})")
    dt = time.perf_counter() - t0
    print(f"\nToplam {total}, çökme {crashes}, miss {miss}, süre {dt:.1f}s ({1000*dt/max(total,1):.1f}ms/çağrı)")

if __name__ == "__main__":
    main()
