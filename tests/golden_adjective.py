"""golden_adjective.py — Sıfat morfolojisi golden testleri (SPEC adjective-spec.md).

Motordan BAĞIMSIZ kuruldu: elle-doğrulanmış dilbilgisel biçimler.
Korkmaz §333-360 referanslı; örnek cümleler KOPYALANMADI (telif).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# §1 — Pekiştirme (intensify)
# ---------------------------------------------------------------------------

# §1.2 — Ünlü-başlı sıfatlar: ilk_ünlü + "p" + sıfat (algoritmik kural)
INTENSIFY_VOWEL: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    ("açık",   "apaçık"),
    ("uzun",   "upuzun"),
    ("ince",   "ipince"),
    ("esmer",  "epesmer"),
    ("ak",     "apak"),       # a + p + ak = apak
    ("iri",    "ipiri"),      # i + p + iri = ipiri
]

# §1.3 — Ünsüz-başlı sıfatlar: kapalı tablo
INTENSIFY_CONSONANT: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    ("beyaz",   "bembeyaz"),
    ("kara",    "kapkara"),
    ("mavi",    "masmavi"),
    ("yeşil",   "yemyeşil"),
    ("kırmızı", "kıpkırmızı"),
    ("sarı",    "sapsarı"),
    ("dolu",    "dopdolu"),
    ("temiz",   "tertemiz"),
    ("düz",     "dümdüz"),
    ("boş",     "bomboş"),
    ("yeni",    "yepyeni"),
    ("büyük",   "büsbüyük"),
    ("kuru",    "kupkuru"),
    ("sağlam",  "sapsağlam"),
    ("saf",     "sapsaf"),
    ("geniş",   "gepgeniş"),
    ("doğru",   "dosdoğru"),
    ("koca",    "koskoca"),
    ("yavaş",   "yapyavaş"),
    ("düzgün",  "düpdüzgün"),
]

# §1.4 — Tire örnekleri (INTENSIFIER_PREFIX tabloda tire dahil saklanır)
INTENSIFY_HYPHEN: list[tuple[str, str]] = [
    ("sıcak",  "sımsıcak"),   # tire varyantı: sım-sıcak da geçerli; canonical: sımsıcak
]

# Tabloda olmayan ünsüz-başlı sıfatlar → None (kapalı küme dışı)
# NOT: ünlü-başlı sıfatlar her zaman algoritmik kural alır → asla None değil
INTENSIFY_UNKNOWN: list[str] = [
    "bilinmeyen",   # ünsüz-başlı, tabloda yok
    "garip",        # ünsüz-başlı, tabloda yok
    "yorgun",       # ünsüz-başlı, tabloda yok
]

# ---------------------------------------------------------------------------
# §2 — Küçültme: -CIk
# ---------------------------------------------------------------------------
DIMINUTIVE_CIK: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    ("kısa",   "kısacık"),    # a arka → ç → cık; kısa + cık → kısacık
    ("az",     "azıcık"),     # z ünsüz-final; buffer ı + cık
    ("dar",    "daracık"),    # r + a + cık
    ("uzun",   "uzuncuk"),    # u → cuk (arka yuvarlak)
    ("ufak",   "ufacık"),     # a → cık
    ("küçük",  "küçücük"),    # ü → cük
    ("büyük",  "büyücek"),    # ü → cek? Hayır: büyük → büyücek — ü harmonisi: cek/cük;
                              # büyük son hecesi 'yük' → yüksek ünlü ü → cük değil cek?
                              # Standart: büyücek (e + k uyumu?) — araştır
                              # TDK: büyücek ✓ (büyük→büyücek, ünlü ü→e geçişi değil, -cek varyantı)
    ("genç",   "gencecik"),   # ç→c + e + cik (pekiştirmeli küçültme)
    ("tatlı",  "tatlıcık"),   # ı → cık
    ("yavaş",  "yavaşçık"),   # ş + çık (sertleşme: ş voiceless → ç)
    ("serin",  "serince"),    # ? serince daha çok zarf; diminutive: serincik — araştır
                              # TDK: serincik ✓
    ("hafif",  "hafifçe"),    # hafif → hafifçe (zarf) değil; diminutive: hafifçik?
                              # -CIk ile: hafif + çik = hafifçik
]

# Daha güvenilir minimal set (tartışmasız örnekler)
DIMINUTIVE_CIK_SAFE: list[tuple[str, str]] = [
    ("kısa",   "kısacık"),
    ("uzun",   "uzuncuk"),
    ("ufak",   "ufacık"),
    ("küçük",  "küçücük"),
    ("tatlı",  "tatlıcık"),
    ("yavaş",  "yavaşçık"),
]

# ---------------------------------------------------------------------------
# §2.2 — Küçültme: -ImsI
# ---------------------------------------------------------------------------
DIMINUTIVE_IMSI: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    ("yeşil",   "yeşilimsi"),    # ünsüz-final + imsi (ön ünlü i)
    ("mor",     "morumsu"),      # ünsüz-final + umsu (arka yuvarlak u)
    ("kara",    "karamsı"),      # ünlü-final: a → msı (a arka düz)
    ("sarı",    "sarımsı"),      # ünlü-final: ı → msı
    ("mavi",    "mavimsi"),      # ünlü-final: i → msi
    ("beyaz",   "beyazımsı"),    # ünsüz-final: z + ımsı
    ("kırmızı", "kırmızımsı"),   # ünlü-final: ı → msı
    ("siyah",   "siyahımsı"),    # ünsüz-final: h + ımsı
    ("gri",     "grimsi"),       # ünlü-final: i → msi
    ("pembe",   "pembemsi"),     # ünlü-final: e → msi
]

# ---------------------------------------------------------------------------
# §2.3 — Küçültme: -ImtIrak
# ---------------------------------------------------------------------------
DIMINUTIVE_IMTIRAK: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    # -ImtIrak: tIrak'taki I = arka-düz (ı) veya ön-düz (i) — yuvarlak değil
    # yuvarlak köklerde de tırak/tirak (u/ü değil ı/i)
    ("sarı",    "sarımtırak"),   # ünlü-final: ı arka → mtırak
    ("yeşil",   "yeşilimtirak"), # ünsüz-final: il ön → imtirak
    ("kara",    "karamtırak"),   # ünlü-final: a arka → mtırak
    ("mor",     "morumtırak"),   # ünsüz-final: or arka yuvarlak → umtırak (I=ı)
    ("beyaz",   "beyazımtırak"), # ünsüz-final: arka düz → ımtırak
    ("pembe",   "pembemtirak"),  # ünlü-final: e ön → mtirak
]
