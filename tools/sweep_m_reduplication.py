"""m-İkileme nominal parse taraması — çökme yok + m-NP kurulum kontrolü."""
import sys
from turkgram import tokenize, parse_text
from turkgram.parse import parse_phrase
from turkgram.dependency import constituency_to_dep

# Temsili m-ikileme cümleleri (NOUN taban + m-değil + AdvP çakışma-yok)
CASES = [
    ("kitap mitap aldı", {"kitap", "almak"}),
    ("araba maraba aldı", {"araba", "almak"}),   # ünlü-başlı m-form
    ("para mara yok", {"para", "yok"}),
    ("göz möz", {"göz"}),                         # yüklemsiz
    ("kitap mitap", {"kitap"}),                   # yüklemsiz NP kök
    ("kitap kalem", {"kitap", "kalem"}),          # m-DEĞİL → m-NP kurulmaz
    ("yavaş yavaş yürüdü", {"yavaş", "yürümek"}), # AdvP (R8) çakışma-yok
    ("güzel müzel elbise", {"güzel", "elbise"}),  # ADJ-taban → AdjP niteleyici
    ("yeşil meşil", {"yeşil"}),                    # ADJ-taban yüklemsiz
]


def _mred_leaves(node):
    """MRED etiketli yaprak sayısını döndür (m-NP kuruldu mu)."""
    if getattr(node, "tag", None) == "MRED":
        return 1
    return sum(_mred_leaves(c) for c in getattr(node, "children", ()))


def _has_dangling_x(node):
    if getattr(node, "tag", None) == "X":
        return True
    return any(_has_dangling_x(c) for c in getattr(node, "children", ()))


def main():
    crashes = 0
    for text, roots in CASES:
        try:
            tree = parse_phrase(tokenize(text), parse_text(text, roots))
            dep = constituency_to_dep(tree)  # dependency çökme kontrolü
            print(f"{text!r}: MRED={_mred_leaves(tree)}, "
                  f"danglingX={_has_dangling_x(tree)}, {len(dep)} token")
        except Exception as e:
            crashes += 1
            print(f"CRASH {text!r}: {e}")
    print(f"\nTARAMA BİTTİ. Çökme: {crashes}")
    return 1 if crashes else 0


if __name__ == "__main__":
    sys.exit(main())
