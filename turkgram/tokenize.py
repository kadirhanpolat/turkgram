# turkgram/tokenize.py
"""Türkçe tokenizasyon: boşluk + noktalama + apostrof bölme."""

_PUNCT = set('.,!?:;"()[]{}')
_PUNCT.update("…—–")


def tokenize(text: str) -> list[str]:
    """Metni tokenlara böl: boşluk + noktalama + apostrof."""
    tokens: list[str] = []
    for word in text.split():
        _split_word(word, tokens)
    return tokens


def _split_word(word: str, out: list[str]) -> None:
    # Baştaki noktalamayı soy
    while word and word[0] in _PUNCT:
        out.append(word[0])
        word = word[1:]

    if not word:
        return

    # Sondaki noktalamayı biriktir
    trailing: list[str] = []
    while word and word[-1] in _PUNCT:
        trailing.append(word[-1])
        word = word[:-1]

    if not word:
        out.extend(reversed(trailing))
        return

    # Apostrof bölme: ortadaki düz apostrof (U+0027), pos > 0
    apos = word.find("'")
    if apos > 0:
        left = word[:apos]
        right = word[apos:]  # apostrof sağ parçada kalır
        out.append(left)
        if right != "'":
            out.append(right)
    else:
        out.append(word)

    out.extend(reversed(trailing))
