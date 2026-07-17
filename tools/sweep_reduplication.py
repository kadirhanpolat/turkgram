"""sweep_reduplication.py — Faz 9d ikileme korpus tarama (0 çökme hedefi).

Kullanım:
    python tools/sweep_reduplication.py
"""
import sys
import itertools

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from turkgram import lexicon, full_reduplicate, converb_reduplicate, m_reduplicate, analyze


def main() -> None:
    roots = lexicon.load()
    verbs = lexicon.load(pos={"verb"})

    errors: list[tuple[str, str, str]] = []

    # 1. full_reduplicate over all roots
    all_lemmalar = list(roots)
    print(f"full_reduplicate: {len(all_lemmalar)} lemma...", flush=True)
    for i, lemma in enumerate(all_lemmalar):
        if i % 2000 == 0 and i > 0:
            print(f"  {i}/{len(all_lemmalar)}...", flush=True)
        try:
            full_reduplicate(lemma)
        except Exception as e:
            errors.append(("full", lemma, str(e)))

    # 2. converb_reduplicate over verbs only
    verb_list = list(verbs)
    print(f"converb_reduplicate: {len(verb_list)} fiil...", flush=True)
    for i, lemma in enumerate(verb_list):
        if i % 1000 == 0 and i > 0:
            print(f"  {i}/{len(verb_list)}...", flush=True)
        try:
            converb_reduplicate(lemma)
        except Exception as e:
            errors.append(("converb", lemma, str(e)))

    # 3. m_reduplicate over all roots (m-başlı ValueError tasarım gereği, atlanır)
    print(f"m_reduplicate: {len(all_lemmalar)} lemma (m-başlı atlanır)...", flush=True)
    for i, lemma in enumerate(all_lemmalar):
        if i % 2000 == 0 and i > 0:
            print(f"  {i}/{len(all_lemmalar)}...", flush=True)
        if lemma.startswith("m"):
            continue
        try:
            m_reduplicate(lemma)
        except Exception as e:
            errors.append(("m", lemma, str(e)))

    # 4. analyze over sample of reduplication surfaces (100 each)
    sample_verbs = list(itertools.islice(verbs, 100))
    sample_roots = list(itertools.islice(roots, 100))

    print(f"analyze converb: {len(sample_verbs)} örnek...", flush=True)
    for lemma in sample_verbs:
        try:
            surface = converb_reduplicate(lemma)
            analyze(surface, roots=roots)
        except Exception as e:
            errors.append(("analyze_converb", lemma, str(e)))

    print(f"analyze full: {len(sample_roots)} örnek...", flush=True)
    for lemma in sample_roots:
        try:
            surface = full_reduplicate(lemma)
            analyze(surface, roots={lemma})
        except Exception as e:
            errors.append(("analyze_full", lemma, str(e)))

    print(f"analyze m: {len(sample_roots)} örnek (m-başlı atlanır)...", flush=True)
    for lemma in sample_roots:
        if lemma.startswith("m"):
            continue
        try:
            surface = m_reduplicate(lemma)
            analyze(surface, roots={lemma})
        except Exception as e:
            errors.append(("analyze_m", lemma, str(e)))

    # Report
    print(f"\n=== SONUÇ ===")
    print(f"Leksikon: {len(all_lemmalar)} lemma, fiil: {len(verb_list)}")
    print(f"Çökmeler: {len(errors)}")

    if errors:
        print(f"\nHATA DETAYI (ilk 20):")
        for kind, lemma, err in errors[:20]:
            print(f"  [{kind}] {lemma!r}: {err}")
        sys.exit(1)
    else:
        print("OK: 0 çökme")


if __name__ == "__main__":
    main()
