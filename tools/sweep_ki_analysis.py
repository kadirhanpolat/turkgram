"""`-ki` aitlik çözümleme korpus çökme taraması (hakem)."""
from turkgram.analysis import analyze
from turkgram.morphology_noun import with_ki
from turkgram import lexicon as lx

def main():
    nouns = sorted(lx.load(pos={"noun"}))
    sample = nouns[::max(1, len(nouns)//500)][:500]
    crashes = miss = total = 0
    for w in sample:
        for case in ("loc", "gen"):
            try:
                surf = with_ki(w, case=case)
            except Exception:
                continue
            total += 1
            try:
                res = analyze(surf, roots={w})
            except Exception as e:
                crashes += 1
                print(f"ÇÖKME: {surf} ({w},{case}) -> {type(e).__name__}: {e}")
                continue
            if not any(a.kind == "with_ki" and a.lemma == w
                       and a.kwargs.get("case") == case for a in res):
                miss += 1
                if miss <= 15:
                    print(f"MISS: {surf} ({w},{case})")
    print(f"\nToplam {total}, çökme {crashes}, recall-miss {miss}")

if __name__ == "__main__":
    main()
