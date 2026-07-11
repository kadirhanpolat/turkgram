"""turkgram — Türkiye Türkçesi grameri, kod olarak.

Betimleyici gramerlerden (Korkmaz, Ergin, Deny, Vural) elle küratörlenmiş
dilbilgisel değişmezleri ÇALIŞTIRILABİLİR kurallara döken bağımsız kütüphane.

Faz 0 (v0.1): çekim morfolojisi ÜRETİMİ (encode) — fiil çekimi (9 kip + birleşik
zaman + soru), isim çekimi (durum×iyelik×çokluk + ek katmanlar), yapım eki
(türetme) mekanik üreticisi. Motor biçimleri SAKLAMAZ, RUNTIME üretir.

Sonraki fazlar: çözümleme (analiz/parse), türetme genişletme, sözdizimi.

Genel API:
    conjugate, paradigm, parse_verb, inflect_last_token   — fiil (morphology)
    decline, paradigm_noun, parse_noun,
        predicative, with_ki, equative                     — isim (morphology_noun)
    derivations                                            — yapım eki (derivation)

Alt modüllere de doğrudan erişilebilir:
    from turkgram import morphology, morphology_noun, derivation
"""
from __future__ import annotations

from . import morphology, morphology_noun, derivation, tr

# ── Fiil çekimi ──────────────────────────────────────────────────────────
from .morphology import (
    conjugate,
    paradigm,
    parse_verb,
    inflect_last_token,
    VerbStem,
    # morfofonolojik primitifler (paylaşımlı)
    last_vowel,
    low_vowel,
    high_vowel,
    ends_in_vowel,
    hardens,
)

# ── İsim çekimi ──────────────────────────────────────────────────────────
from .morphology_noun import (
    decline,
    paradigm_noun,
    parse_noun,
    predicative,
    copula,
    with_ki,
    equative,
    NounStem,
)

# ── Yapım eki (türetme) ──────────────────────────────────────────────────
from .derivation import derivations

__version__ = "0.1.0"

__all__ = [
    # fiil
    "conjugate", "paradigm", "parse_verb", "inflect_last_token", "VerbStem",
    "last_vowel", "low_vowel", "high_vowel", "ends_in_vowel", "hardens",
    # isim
    "decline", "paradigm_noun", "parse_noun", "predicative", "copula",
    "with_ki", "equative", "NounStem",
    # türetme
    "derivations",
    # alt modüller
    "morphology", "morphology_noun", "derivation", "tr",
    "__version__",
]
