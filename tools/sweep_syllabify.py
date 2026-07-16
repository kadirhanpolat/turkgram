# tools/sweep_syllabify.py
"""Syllabify + stress korpus taraması — lexicon.load() tüm lemmalar."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from turkgram.lexicon import load
from turkgram.syllabify import syllabify, stress, stress_mark, _STRESS_EXCEPTIONS

roots = load()
errors: list[tuple[str, str]] = []

for lemma in roots:
    try:
        s = syllabify(lemma)
        st = stress(lemma)
        sm = stress_mark(lemma)
    except Exception as e:
        errors.append((lemma, str(e)))

# İstisna tablosu sweep
for word in _STRESS_EXCEPTIONS:
    try:
        assert stress(word) is not None, f"stress('{word}') returned None"
    except AssertionError as e:
        errors.append((word, str(e)))
    except Exception as e:
        errors.append((word, str(e)))

print(f"Tarandı: {len(roots)} lemma + {len(_STRESS_EXCEPTIONS)} istisna")
print(f"Hata: {len(errors)}")
for word, err in errors[:20]:
    print(f"  {word!r}: {err}")
