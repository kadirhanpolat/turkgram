"""sweep_derivation_chain.py — zincirli türetme corpus taraması.

Leksikon 26k lemma × max_depth=3: 0 çökme kontrolü.
Kullanım: PYTHONUTF8=1 python tools/sweep_derivation_chain.py
"""
import sys
from turkgram import analyze
from turkgram.lexicon import load


def main():
    roots = load()
    lemmas = sorted(roots)
    total = len(lemmas)
    errors = []
    chain_found = 0

    print(f"Taranıyor: {total} lemma x max_depth=3 ...", flush=True)
    for i, lemma in enumerate(lemmas):
        if i % 2000 == 0:
            print(f"  {i}/{total} ({100*i//total}%)", flush=True)
        try:
            results = analyze(lemma, roots=roots, max_derivation_depth=3)
            chain_results = [r for r in results if r.kind == "derivation" and r.chain]
            chain_found += len(chain_results)
        except Exception as e:
            errors.append((lemma, str(e)))

    print(f"\nSonuc: {total} lemma tarandi")
    print(f"  Cokme: {len(errors)}")
    print(f"  Zincirli analiz bulunan: {chain_found}")
    if errors:
        print("\nHATALAR:")
        for lemma, err in errors[:20]:
            print(f"  {lemma}: {err}")
        sys.exit(1)
    else:
        print("OK -- 0 cokme")


if __name__ == "__main__":
    main()
