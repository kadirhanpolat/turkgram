"""İkileme adverbial parse taraması — çökme yok + AdvP kurulum kontrolü."""
import sys
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep

# Temsili ikileme cümleleri (tam + ulaç + adnominal guard + m-kapsam-dışı)
CASES = [
    ("yavaş yavaş yürüdü", {"yavaş", "yürümek"}),
    ("koşa koşa geldi", {"koşmak", "gelmek"}),
    ("güle güle gitti", {"gülmek", "gitmek"}),
    ("hızlı hızlı koştu", {"hızlı", "koşmak"}),
    ("uzun uzun yollar", {"uzun", "yol"}),      # adnominal → NP, AdvP yok
    ("çok çok güzel", {"güzel"}),
    ("kitap mitap aldı", {"kitap", "almak"}),   # m-ikileme kapsam dışı (AdvP olmamalı)
    # Koordine ikileme/zarf (R4 genelleme)
    ("yavaş yavaş ve hızlı hızlı yürüdü", {"yavaş", "hızlı", "yürümek"}),  # koordine AdvP → CoordP
    ("güzel müzel ve çirkin mirkin", {"güzel", "çirkin"}),                  # koordine AdjP → CoordP
    ("kitap ve kalem aldı", {"kitap", "kalem", "almak"}),                   # regresyon: NP koord
]


def _has_advp(node):
    if getattr(node, "tag", None) == "AdvP":
        return True
    return any(_has_advp(c) for c in getattr(node, "children", ()))


def _has_coordp(node):
    if getattr(node, "tag", None) == "CoordP":
        return True
    return any(_has_coordp(c) for c in getattr(node, "children", ()))


def main():
    crashes = 0
    for text, roots in CASES:
        try:
            tree = parse_phrase(tokenize(text), parse_text(text, roots))
            dep = constituency_to_dep(tree)  # dependency çökme kontrolü
            print(f"{text!r}: AdvP={_has_advp(tree)}, CoordP={_has_coordp(tree)}, {len(dep)} token")
        except Exception as e:
            crashes += 1
            print(f"CRASH {text!r}: {e}")
    print(f"\nTARAMA BİTTİ. Çökme: {crashes}")
    return 1 if crashes else 0


if __name__ == "__main__":
    sys.exit(main())
