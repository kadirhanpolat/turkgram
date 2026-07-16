"""
Corpus crash sweep for derivation analysis.
Tests all lexical derivation forms against analyze() for crashes and misses.
Run: PYTHONUTF8=1 python tools/sweep_derivation_analysis.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram.analysis import analyze
from turkgram.lexicon import load
from turkgram.derivation import _LEXICAL_SUFFIXES, derivations

# Load lexicon roots
roots = load()

# Try dict-db first, fall back to lexicon lemmas
lemmas = None
try:
    import psycopg2
    conn = psycopg2.connect(
        host="127.0.0.1", port=5434, password="dict", dbname="postgres", user="postgres"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT title FROM entries
        WHERE lang = 'tr' AND title != '' AND title IS NOT NULL
        LIMIT 10000
    """)
    lemmas = [row[0] for row in cur.fetchall()]
    conn.close()
    print(f"Source: dict-db ({len(lemmas)} TR lemmas)")
except Exception as e:
    print(f"dict-db unavailable ({e}), falling back to lexicon")

if lemmas is None:
    lemmas = list(roots)[:5000]
    print(f"Source: lexicon ({len(lemmas)} lemmas)")

# Collect the lexical suffix labels
lexical_labels = {label for (_, label, _) in _LEXICAL_SUFFIXES}
print(f"Lexical suffix labels: {sorted(lexical_labels)}")

crashes = []
misses = []
total = 0
tested_lemmas = 0

for lemma in lemmas:
    # Try both noun and verb
    for pos in ("noun", "verb"):
        try:
            derived = derivations(lemma, pos)
        except Exception as e:
            crashes.append(("derivations", lemma, pos, str(e)))
            continue
        if not derived:
            continue

        tested_lemmas += 1
        for row in derived:
            if row["suffix"] not in lexical_labels:
                continue
            surface = row["form"]
            total += 1
            try:
                results = analyze(surface, roots=roots | {lemma})
                derivation_hits = [a for a in results if a.kind == "derivation"]
                if not derivation_hits:
                    misses.append((lemma, pos, row["suffix"], surface))
            except Exception as e:
                crashes.append(("analyze", surface, row["suffix"], str(e)))

print(f"\n--- RESULTS ---")
print(f"Lemmas yielding derivation forms: {tested_lemmas}")
print(f"Total derivation forms tested:    {total}")
print(f"Crashes:                          {len(crashes)}")
print(f"Derivation misses:                {len(misses)}")

if crashes:
    print("\nCRASHES (first 10):")
    for c in crashes[:10]:
        print(f"  {c}")

if misses:
    print(f"\nMISSES (first 20 of {len(misses)}):")
    for m in misses[:20]:
        print(f"  lemma={m[0]!r} pos={m[1]!r} suffix={m[2]!r} surface={m[3]!r}")

    # Group misses by suffix for analysis
    from collections import Counter
    by_suffix = Counter(m[2] for m in misses)
    print(f"\nMisses by suffix:")
    for suffix, count in by_suffix.most_common():
        print(f"  {suffix}: {count}")
else:
    print("\n0 misses — all derivation forms round-trip correctly")
