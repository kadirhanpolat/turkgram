"""Conjunction utilities for Turkish grammar.

Provides conjoin() for appending a conjunction to a word (with de/da vowel harmony)
and coordinate() for building coordinated lists.
"""

from .morphology import last_vowel as _last_vowel

__all__ = ["conjoin", "coordinate", "CONJUNCTIONS"]

# All Turkish conjunctions recognized by this module
CONJUNCTIONS: frozenset[str] = frozenset({
    "ve", "ama", "fakat", "lakin", "ancak", "çünkü", "oysa", "halbuki",
    "yoksa", "ya da", "veya", "yahut", "üstelik", "hatta", "bile", "dahi",
    "ise", "ki", "de", "da",
    "hem", "ya", "ne", "ister", "gerek",
})

# Valid values for conjoin(conj=) and coordinate(conj=)
_VALID_CONJ: frozenset[str] = frozenset({
    # Coordinatives
    "ve", "ama", "fakat", "lakin", "ancak", "çünkü", "oysa", "halbuki",
    "yoksa", "ya da", "veya", "yahut", "üstelik", "hatta", "bile", "dahi",
    "ise", "ki",
    # Clitics (vowel harmony applied internally)
    "de", "da",
    # Correlatives
    "hem_hem", "ya_ya", "ne_ne", "ister_ister", "gerek_gerek", "hem_hem_de",
})

_CORRELATIVES: frozenset[str] = frozenset({
    "hem_hem", "ya_ya", "ne_ne", "ister_ister", "gerek_gerek", "hem_hem_de",
})

_FRONT_VOWELS: frozenset[str] = frozenset("eiöü")
_BACK_VOWELS: frozenset[str] = frozenset("aıou")


def _de_da(word: str) -> str:
    """Return 'de' or 'da' based on the last vowel of *word* (vowel harmony).

    Returns 'de' when the last vowel is a front vowel (e, i, ö, ü) or when
    no vowel is found. Returns 'da' when the last vowel is a back vowel
    (a, ı, o, u).
    """
    lv = _last_vowel(word)
    if lv is None or lv in _FRONT_VOWELS:
        return "de"
    return "da"


def _format_correlative(a: str, b: str, conj: str) -> str:
    """Format a correlative pair."""
    if conj == "hem_hem":
        return f"hem {a} hem {b}"
    if conj == "ya_ya":
        return f"ya {a} ya {b}"
    if conj == "ne_ne":
        return f"ne {a} ne {b}"
    if conj == "ister_ister":
        return f"ister {a} ister {b}"
    if conj == "gerek_gerek":
        return f"gerek {a} gerek {b}"
    if conj == "hem_hem_de":
        return f"hem {a} hem de {b}"
    raise ValueError(f"Unknown correlative: {conj!r}")


def conjoin(word: str, conj: str) -> str:
    """Append conjunction *conj* to *word*, separated by a space.

    For *conj* ``'de'`` or ``'da'``, vowel harmony is applied automatically —
    pass either form and the correct surface variant is selected based on the
    last vowel of *word*.

    Note: For the locative case suffix *-de/-da*, use ``decline(case='loc')``
    instead of this function.

    Parameters
    ----------
    word:
        The Turkish word or phrase to attach the conjunction to.
    conj:
        A conjunction from the valid set. See ``_VALID_CONJ`` for the full
        list. Correlatives (e.g. ``'hem_hem'``) are not supported here; use
        ``coordinate()`` for those.

    Returns
    -------
    str
        ``word + ' ' + conj`` (with vowel harmony for de/da).

    Raises
    ------
    ValueError
        If *word* is empty or *conj* is not a recognized conjunction.
    """
    if not word:
        raise ValueError("word must not be empty")
    if conj not in _VALID_CONJ:
        valid = sorted(_VALID_CONJ)
        raise ValueError(
            f"Unknown conjunction: {conj!r}. Valid values: {valid}"
        )
    if conj in ("de", "da"):
        return word + " " + _de_da(word)
    return word + " " + conj


def coordinate(items: list[str], conj: str) -> str:
    """Build a coordinated list from *items* using conjunction *conj*.

    Parameters
    ----------
    items:
        A non-empty list of strings to coordinate.
    conj:
        A conjunction from ``_VALID_CONJ``. Coordinatives produce comma-
        separated lists joined by the conjunction; correlatives (e.g.
        ``'hem_hem'``) require exactly two items.

    Returns
    -------
    str
        The coordinated phrase.

    Raises
    ------
    ValueError
        If *items* is empty, *conj* is unknown, or a correlative is used with
        more than two items.
    """
    if not items:
        raise ValueError("items must not be empty")
    if conj not in _VALID_CONJ:
        valid = sorted(_VALID_CONJ)
        raise ValueError(
            f"Unknown conjunction: {conj!r}. Valid values: {valid}"
        )

    # Single item — return unchanged
    if len(items) == 1:
        return items[0]

    # Correlatives require exactly two items
    if conj in _CORRELATIVES:
        if len(items) != 2:
            raise ValueError(
                f"Correlative conjunction {conj!r} requires exactly 2 items, "
                f"got {len(items)}"
            )
        return _format_correlative(items[0], items[1], conj)

    # Coordinatives: two items → "X conj Y"; three+ → "X, Y, ... conj Z"
    actual_conj = _de_da(items[-1]) if conj in ("de", "da") else conj
    if len(items) == 2:
        return f"{items[0]} {actual_conj} {items[1]}"
    head = ", ".join(items[:-1])
    return f"{head} {actual_conj} {items[-1]}"
