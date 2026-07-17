"""Edat analizi korpus taraması — 0 çökme + additive değişmez kontrolü."""
import sys
from turkgram.analysis import analyze
from turkgram.lexicon import load
from turkgram.postposition import _POSTPOSITIONS

def main():
    roots = load()
    crashes = 0
    misses = []
    # 1) Tüm 23 edat → postposition okuması var mı
    for edat in _POSTPOSITIONS:
        try:
            kinds = [a.kind for a in analyze(edat, roots=roots)]
            if "postposition" not in kinds:
                misses.append(edat)
                print(f"MISS: {edat} postposition okuması yok")
        except Exception as e:
            crashes += 1
            print(f"CRASH {edat!r}: {e}")
    # 2) Leksikon geneli çökme taraması (edat dalı her token'da çalışır)
    for i, lemma in enumerate(roots):
        try:
            analyze(lemma, roots=roots)
        except Exception as e:
            crashes += 1
            print(f"CRASH {lemma!r}: {e}")
        if i % 5000 == 0:
            print(f"...{i} lemma tarandı", flush=True)
    print(f"\nTARAMA BİTTİ. Çökme: {crashes}, MISS: {len(misses)}")
    return 1 if (crashes or misses) else 0

if __name__ == "__main__":
    sys.exit(main())
