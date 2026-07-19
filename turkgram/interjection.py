"""Turkish interjections (ünlem) — closed lexical class.

Primary interjections (asıl ünlemler) are frozen forms that take no inflection
or derivation in V1 (SPEC ``spec/interjection-onomatopoeia-spec.md`` §1.1). This
module exposes the closed inventory used by ``analysis.analyze`` for recognition
(``pos="ünlem"``, ``kind="interjection"``).

Derived / interjection-valued nouns (which inflect) are DELIBERATELY excluded —
they already resolve as nouns.
"""

__all__ = ["INTERJECTIONS"]

# Asıl ünlemler (Korkmaz, Şekil Bilgisi — ünlemler). Lowercase; analyze() applies
# _tr_lower before lookup. Sub-groups: duygu / seslenme / gösterme / buyurma-teşvik
# / onay-övgü.
INTERJECTIONS: frozenset[str] = frozenset({
    # duygu (emotion)
    "ah", "of", "öf", "üf", "oh", "vah", "vay", "ay", "ey", "hay",
    "eyvah", "aman", "eyvallah", "hah", "hıh", "ıh", "oho", "hoppala",
    "pöh", "tüh", "yazık",
    # seslenme / hitap (address)
    "hey", "hişt", "pist", "bre", "be", "yahu",
    # gösterme (deixis)
    "işte", "na",
    # buyurma / teşvik (command / urging)
    "haydi", "hadi", "haydin", "marş", "deh", "hoşt", "kışt", "çüş",
    # onay / övgü / alkış (approval / praise)
    "bravo", "aferin", "yaşa", "maşallah", "inşallah",
})
