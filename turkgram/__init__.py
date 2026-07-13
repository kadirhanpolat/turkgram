"""turkgram — Türkiye Türkçesi grameri, kod olarak.

Betimleyici gramerlerden (Korkmaz, Ergin, Deny, Vural) elle küratörlenmiş
dilbilgisel değişmezleri ÇALIŞTIRILABİLİR kurallara döken bağımsız kütüphane.

Faz 0 (v0.1): çekim morfolojisi ÜRETİMİ (encode) — fiil çekimi (9 kip + birleşik
zaman + soru), isim çekimi (durum×iyelik×çokluk + ek katmanlar), yapım eki
(türetme) mekanik üreticisi. Motor biçimleri SAKLAMAZ, RUNTIME üretir.

Faz 2a: ÇÖZÜMLEME — `analyze` yüzey biçimden kök+eksen değerleri türetir.
`parse_verb` ↔ `analyze` ayrımı: parse_verb kökü ve morfofonolojik sınıfı
tanımlar (üretim-odaklı); analyze yüzeyi → kök+eksenler çözümler (analiz).

Genel API:
    conjugate, paradigm, parse_verb, inflect_last_token   — fiil (morphology)
    decline, paradigm_noun, parse_noun,
        predicative, with_ki, equative                     — isim (morphology_noun)
    derivations                                            — yapım eki (derivation)
    analyze, Analysis, Segment                             — çözümleme (analysis)

Alt modüllere de doğrudan erişilebilir:
    from turkgram import morphology, morphology_noun, derivation, analysis
"""
from __future__ import annotations

from . import (
    morphology, morphology_noun, derivation, nonfinite, voice, tr, analysis,
    lexicon, disambiguation, compound, context,
)

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

# ── Fiilimsi (zarf-fiil / ulaç + sıfat-fiil/ad-fiil) ─────────────────────
from .nonfinite import converb, participle, converb_casina, converb_ken

# ── Bileşik zaman (birleşik çekim: hikaye/rivayet/şart) ──────────────────
from .compound import compound

# ── Çatı (voice: ettirgen/edilgen/dönüşlü/işteş + yığılma) ───────────────
from .voice import apply_voice

# ── Yapım eki (türetme) ──────────────────────────────────────────────────
from .derivation import derivations

# ── Çözümleme (analysis: yüzey → kök+eksenler, Faz 2a) ──────────────────
from .analysis import analyze, Analysis, Segment

# ── Disambiguation (aday sıralama + güven, Faz 2b) ──────────────────────
from .disambiguation import rank, disambiguate

# ── Cümle-bağlamı disambiguation (kural-tabanlı sözdizimsel katman, Faz 2b) ─
from .context import rank_in_context

__version__ = "0.1.0"

__all__ = [
    # fiil
    "conjugate", "paradigm", "parse_verb", "inflect_last_token", "VerbStem",
    "last_vowel", "low_vowel", "high_vowel", "ends_in_vowel", "hardens",
    # isim
    "decline", "paradigm_noun", "parse_noun", "predicative", "copula",
    "with_ki", "equative", "NounStem",
    # fiilimsi
    "converb", "participle", "converb_casina", "converb_ken",
    # bileşik zaman
    "compound",
    # çatı
    "apply_voice",
    # türetme
    "derivations",
    # çözümleme
    "analyze", "Analysis", "Segment",
    # disambiguation
    "rank", "disambiguate",
    # cümle-bağlamı disambiguation
    "rank_in_context",
    # alt modüller
    "morphology", "morphology_noun", "derivation", "nonfinite", "voice", "tr",
    "analysis", "lexicon", "disambiguation", "compound", "context",
    "__version__",
]
