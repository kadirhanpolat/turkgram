"""Faz 9b hakem: leksikon lemmaları × is_valid + suggest → 0 çökme kontrolü.

Tam tarama (26k is_valid) ~3 saat sürer; varsayılan mod istatistiksel örneklem
(500 verb+noun + 50 suggest) ile birkaç dakika içinde tamamlanır.

Kullanım:
    python tools/sweep_spellcheck.py           # hızlı örneklem (varsayılan)
    python tools/sweep_spellcheck.py --full    # tam tarama (yavaş, ~3 saat)
"""
import sys
import random
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from turkgram import lexicon
from turkgram.spellcheck import is_valid, suggest

parser = argparse.ArgumentParser()
parser.add_argument("--full", action="store_true", help="Tam leksikon taraması (yavaş)")
parser.add_argument("--sample", type=int, default=500, help="Örneklem boyutu (varsayılan: 500)")
parser.add_argument("--seed", type=int, default=42, help="Rastgele tohum")
args = parser.parse_args()

strict_roots = lexicon.load(pos={"verb", "noun"})
all_roots = lexicon.load()
all_lemmalar = list(all_roots)
total_all = len(all_lemmalar)

print(f"Leksikon: {total_all} lemma (verb+noun: {len(strict_roots)})")

if args.full:
    # Tam tarama — tüm lemmalar
    test_lemmalar = all_lemmalar
    print(f"TAM TARAMA: {total_all} lemma (uzun sürer)...")
else:
    # Örneklem — verb+noun'dan rastgele seçim
    random.seed(args.seed)
    n = min(args.sample, len(strict_roots))
    test_lemmalar = random.sample(list(strict_roots), n)
    print(f"ÖRNEKLEM: {n} verb+noun lemma (seed={args.seed})...")

crashes: list = []
is_valid_misses: list = []
total = len(test_lemmalar)

for i, lemma in enumerate(test_lemmalar):
    if i % 100 == 0:
        print(f"  {i}/{total}...", flush=True)
    try:
        v = is_valid(lemma, roots=all_roots)
        if not v:
            is_valid_misses.append(lemma)
    except Exception as e:
        crashes.append(("is_valid_crash", lemma, str(e)))

# suggest: ilk 50 lemma için bozulmuş versiyonu test et
suggest_sample = test_lemmalar[:50]
print(f"suggest testi: {len(suggest_sample)} bozuk kelime...")
for lemma in suggest_sample:
    bozuk = lemma[:-1] + "x" if lemma else "x"
    try:
        suggest(bozuk, roots=all_roots, max_suggestions=3, max_distance=2.0)
    except Exception as e:
        crashes.append(("suggest_crash", bozuk, str(e)))

print(f"\n=== SONUÇ ===")
print(f"Tarama modu: {'TAM' if args.full else 'ÖRNEKLEM'}")
print(f"Test edilen: {total} lemma")
print(f"Çökmeler: {len(crashes)}")
print(f"is_valid miss (verb+noun): {len(is_valid_misses)}")

if crashes:
    print("\nÇÖKME DETAYI (ilk 10):")
    for e in crashes[:10]:
        print(" ", e)
    sys.exit(1)
elif is_valid_misses:
    print("\nIS_VALID MISS DETAYI (ilk 10):")
    for m in is_valid_misses[:10]:
        print(" ", m)
    sys.exit(1)
else:
    print("OK: 0 çökme, verb+noun lemmalar is_valid=True")
