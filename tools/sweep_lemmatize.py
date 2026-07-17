"""Faz 9c — lemmatizer korpus taraması.

26k leksikon lemması üzerinden:
- 0 çökme hedefi (çökme = gerçek bug)
- lemmatize(lemma) != lemma → belirsizlik logu (hata DEĞİL)
"""
import sys
sys.path.insert(0, ".")

from turkgram.lexicon import load as _load_lexicon
from turkgram.lemmatize import lemmatize


def main() -> None:
    roots = _load_lexicon()
    mismatches: list[tuple[str, str | None]] = []
    errors: list[tuple[str, str]] = []

    total = len(roots)
    for i, lemma in enumerate(sorted(roots), 1):
        try:
            result = lemmatize(lemma, roots=roots)
            if result != lemma:
                mismatches.append((lemma, result))
        except Exception as e:
            errors.append((lemma, str(e)))

        if i % 5000 == 0:
            print(f"  {i}/{total} işlendi...", flush=True)

    print(f"\nToplam: {total} lemma")
    print(f"Çökme (HATA): {len(errors)}")
    print(f"Uyuşmayan (belirsizlik, normal): {len(mismatches)}")

    if errors:
        print("\n--- HATALAR ---")
        for lemma, err in errors[:20]:
            print(f"  {lemma!r}: {err}")
        sys.exit(1)

    if mismatches:
        print(f"\nİlk 20 uyuşmayan (belirsizlik):")
        for lemma, got in mismatches[:20]:
            print(f"  {lemma!r} → {got!r}")

    print("\nSonuç: 0 çökme ✓")


if __name__ == "__main__":
    main()
