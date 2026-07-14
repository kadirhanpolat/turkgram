"""golden_syntax.py — Sözdizimi öbek üretimi golden testleri (SPEC syntax.py).

Motordan BAĞIMSIZ kuruldu: elle-doğrulanmış dilbilgisel biçimler.
Korkmaz §200-230 (Tamlama), §265 (Sıfat tamlaması), §295 (Cümle).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# §1 — İsim tamlaması (belirtili)
# tamlayan(gen) + tamlanan(3sg-poss)
# ---------------------------------------------------------------------------
ISIM_TAMLAMASI_BELIRTILI: list[tuple[str, str, str]] = [
    # (tamlayan, tamlanan, beklenen)
    ("ev",       "kapı",    "evin kapısı"),
    ("okul",     "bahçe",   "okulun bahçesi"),
    ("kitap",    "kapak",   "kitabın kapağı"),     # k yumuşama
    ("araba",    "renk",    "arabanın rengi"),
    ("çocuk",    "oyun",    "çocuğun oyunu"),      # k→ğ yumuşama
    ("öğretmen", "masa",    "öğretmenin masası"),
    ("yol",      "kenar",   "yolun kenarı"),
    ("sabah",    "güneş",   "sabahın güneşi"),
    ("deniz",    "kıyı",    "denizin kıyısı"),
    ("şehir",    "merkez",  "şehrin merkezi"),     # şehir → şehrin (r-final)
    ("anne",     "el",      "annenin eli"),
    ("su",       "damla",   "suyun damlası"),      # su → suyun (düzensiz)
    ("kış",      "soğuk",   "kışın soğuğu"),
]

# ---------------------------------------------------------------------------
# §1 — İsim tamlaması (belirtisiz)
# tamlayan(bare) + tamlanan(3sg-poss)
# ---------------------------------------------------------------------------
ISIM_TAMLAMASI_BELIRTISIZ: list[tuple[str, str, str]] = [
    # (tamlayan, tamlanan, beklenen)
    ("taş",   "köprü",  "taş köprüsü"),
    ("demir", "kapı",   "demir kapısı"),
    ("cam",   "bardak", "cam bardağı"),       # k→ğ
    ("çelik", "kasa",   "çelik kasası"),
    ("ahşap", "masa",   "ahşap masası"),
    ("altın", "yüzük",  "altın yüzüğü"),      # k→ğ
    ("plastik","kutu",  "plastik kutusu"),
    ("taş",   "ev",     "taş evi"),
]

# ---------------------------------------------------------------------------
# §2 — Sıfat tamlaması
# sıfat(bare) + isim(bare) — kongruans yok
# ---------------------------------------------------------------------------
SIFAT_TAMLAMASI: list[tuple[str, str, str]] = [
    # (sıfat, isim, beklenen)
    ("kırmızı", "araba",   "kırmızı araba"),
    ("büyük",   "ev",      "büyük ev"),
    ("eski",    "kitap",   "eski kitap"),
    ("uzun",    "yol",     "uzun yol"),
    ("soğuk",   "hava",    "soğuk hava"),
    ("güzel",   "gün",     "güzel gün"),
    ("küçük",   "çocuk",   "küçük çocuk"),
    ("yeni",    "telefon", "yeni telefon"),
    ("siyah",   "kedi",    "siyah kedi"),
    ("taze",    "ekmek",   "taze ekmek"),
]

# ---------------------------------------------------------------------------
# §3 — Zarf türetme (-CA)
# ---------------------------------------------------------------------------
ZARF_YAP: list[tuple[str, str]] = [
    # (sıfat, beklenen)
    ("güzel",   "güzelce"),
    ("hızlı",   "hızlıca"),
    ("sık",     "sıkça"),
    ("iyi",     "iyice"),
    ("kötü",    "kötüce"),
    ("ağır",    "ağırca"),
    ("hafif",   "hafifçe"),
    ("açık",    "açıkça"),
    ("uzak",    "uzakça"),
    ("derin",   "derince"),
    ("çabuk",   "çabukça"),
    ("alçak",   "alçakça"),
    ("net",     "netçe"),     # t sert → ç
    ("sert",    "sertçe"),    # t sert → ç
    ("doğru",   "doğruca"),   # u arka → ca, r yumuşak
]

# ---------------------------------------------------------------------------
# §4 — Cümle üretimi
# ---------------------------------------------------------------------------
CUMLE_URET: list[tuple] = [
    # (ozne, yuklem, kwargs, beklenen)
    ("ben",       "gelmek",   {"kip": "pres"},               "ben geliyorum"),
    ("sen",       "gitmek",   {"kip": "pres"},               "sen gidiyorsun"),
    ("o",         "okumak",   {"kip": "pres"},               "o okuyor"),
    ("biz",       "çalışmak", {"kip": "pres"},               "biz çalışıyoruz"),
    ("siz",       "bilmek",   {"kip": "pres"},               "siz biliyorsunuz"),
    ("onlar",     "gelmek",   {"kip": "pres"},               "onlar geliyorlar"),
    ("öğrenci",   "okumak",   {"kip": "past"},               "öğrenci okudu"),
    ("çocuk",     "oynamak",  {"kip": "fut"},                "çocuk oynayacak"),
    ("ben",       "gitmek",   {"kip": "pres", "olumsuz": True}, "ben gitmiyorum"),
    ("o",         "gelmek",   {"kip": "past", "soru": True}, "o geldi mi"),
]
