"""golden_adjective_analysis.py — Sıfat çözümleme golden testleri.

Motordan BAĞIMSIZ kuruldu: analysis-by-generation ile pekiştirme/küçültme
biçimlerinden kök+kind çözümlemesi.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Pekiştirme çözümlemesi — (yüzey, roots, beklenen_kind, beklenen_lemma)
# ---------------------------------------------------------------------------
INTENSIFY_ROUNDTRIP: list[tuple] = [
    # Ünlü-başlı (algoritmik kural)
    ("apaçık",    frozenset({"açık"}),    "intensify", "açık"),
    ("upuzun",    frozenset({"uzun"}),    "intensify", "uzun"),
    ("ipince",    frozenset({"ince"}),    "intensify", "ince"),
    # Ünsüz-başlı (kapalı tablo)
    ("bembeyaz",  frozenset({"beyaz"}),   "intensify", "beyaz"),
    ("kapkara",   frozenset({"kara"}),    "intensify", "kara"),
    ("yepyeni",   frozenset({"yeni"}),    "intensify", "yeni"),
    ("büsbüyük",  frozenset({"büyük"}),   "intensify", "büyük"),
    ("masmavi",   frozenset({"mavi"}),    "intensify", "mavi"),
    ("yemyeşil",  frozenset({"yeşil"}),   "intensify", "yeşil"),
    ("sapsarı",   frozenset({"sarı"}),    "intensify", "sarı"),
    ("dopdolu",   frozenset({"dolu"}),    "intensify", "dolu"),
    ("sımsıcak",  frozenset({"sıcak"}),   "intensify", "sıcak"),
]

# ---------------------------------------------------------------------------
# Küçültme çözümlemesi — (yüzey, roots, beklenen_kind, beklenen_lemma, beklenen_suffix)
# ---------------------------------------------------------------------------
DIMINUTIVE_ROUNDTRIP: list[tuple] = [
    # -CIk
    ("kısacık",   frozenset({"kısa"}),   "diminutive", "kısa",   "-CIk"),
    ("uzuncuk",   frozenset({"uzun"}),   "diminutive", "uzun",   "-CIk"),
    ("ufacık",    frozenset({"ufak"}),   "diminutive", "ufak",   "-CIk"),
    ("küçücük",   frozenset({"küçük"}),  "diminutive", "küçük",  "-CIk"),
    ("tatlıcık",  frozenset({"tatlı"}),  "diminutive", "tatlı",  "-CIk"),
    ("yavaşçık",  frozenset({"yavaş"}),  "diminutive", "yavaş",  "-CIk"),
    # -ImsI
    ("yeşilimsi",  frozenset({"yeşil"}),   "diminutive", "yeşil",   "-ImsI"),
    ("morumsu",    frozenset({"mor"}),     "diminutive", "mor",     "-ImsI"),
    ("karamsı",    frozenset({"kara"}),    "diminutive", "kara",    "-ImsI"),
    ("sarımsı",    frozenset({"sarı"}),    "diminutive", "sarı",    "-ImsI"),
    ("mavimsi",    frozenset({"mavi"}),    "diminutive", "mavi",    "-ImsI"),
    # -ImtIrak
    ("sarımtırak",    frozenset({"sarı"}),   "diminutive", "sarı",   "-ImtIrak"),
    ("yeşilimtirak",  frozenset({"yeşil"}),  "diminutive", "yeşil",  "-ImtIrak"),
    ("karamtırak",    frozenset({"kara"}),   "diminutive", "kara",   "-ImtIrak"),
]

# ---------------------------------------------------------------------------
# Bilinmeyen kök → boş liste (precision garantisi)
# ---------------------------------------------------------------------------
INTENSIFY_NO_RESULT: list[tuple] = [
    # (yüzey, roots) — roots'ta doğru kök YOK → analyze sonucu intensify kind içermemeli
    ("bembeyaz", frozenset({"mavi"})),   # beyaz roots'ta yok
    ("apaçık",   frozenset({"uzun"})),   # açık roots'ta yok
]
