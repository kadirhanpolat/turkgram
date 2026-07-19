"""Turkish onomatopoeia (yansıma sözcükler) — bare imitative roots.

Primary onomatopoeia (asıl yansımalar) imitate sound or motion and, in their bare
form, take no inflection. This module exposes a curated core inventory used by
``analysis.analyze`` for recognition (``pos="yansıma"``, ``kind="onomatopoeia"``).

Onomatopoeia is an open lexical class — completeness is NOT claimed (cf. SPEC
``spec/interjection-onomatopoeia-spec.md`` §3.1). Onomatopoeic derivation
(-TI/-dA-/-kIr-, e.g. şırıltı, şırıldamak, fışkır-) is out of scope in V1.
"""

__all__ = ["ONOMATOPOEIA"]

# Asıl yansımalar (curated core). Lowercase; analyze() applies _tr_lower.
ONOMATOPOEIA: frozenset[str] = frozenset({
    # ses taklidi (sound)
    "şır", "şar", "fır", "vır", "vız", "cız", "fış", "hış", "pır",
    "gür", "hır", "zır", "çat", "pat", "küt", "güm", "tık", "tak",
    "tik", "çıt", "gıcır", "gümbür", "şırıl", "patır",
    # hayvan sesleri (animal)
    "hav", "miyav", "me", "mö", "vak", "cik", "gak",
})
