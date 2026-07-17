"""Bağımsız golden — motor GÖRÜLMEDEN elle-doğrulanmış lemma beklentileri.

Her giriş: (surface, expected_lemma_or_None)
corrected=True beklentisi ayrı: CORRECTED_CASES
"""

# (surface, expected_lemma | None)
LEMMATIZE_CASES: list[tuple[str, str | None]] = [
    # ── Fiil çekim → mastar ──────────────────────────────────────────────────
    # geliyorum: gel- kökü, şimdiki kip 1.tekil → gelmek
    ("geliyorum", "gelmek"),
    # okumuştu: oku- kökü, öğrenilen geçmiş 3.tekil + geçmiş → okumak
    ("okumuştu", "okumak"),
    # gidecekler: git- kökü, gelecek 3.çoğul → gitmek
    ("gidecekler", "gitmek"),
    # yapıyordum: yap- kökü, şimdiki 1.tekil + geçmiş → yapmak
    ("yapıyordum", "yapmak"),
    # söylemiş: söyle- kökü, öğrenilen geçmiş 3.tekil → söylemek
    ("söylemiş", "söylemek"),
    # ── İsim + durum → çıplak kök ────────────────────────────────────────────
    ("evlerde", "ev"),          # ev + çoğul + bulunma
    ("kitabın", "kitap"),       # kitap + iyelik 2.tekil (kitabın) ya da genitif
    ("masaya", "masa"),         # masa + yönelme
    ("kapıdan", "kapı"),        # kapı + ayrılma
    ("arabaları", "araba"),     # araba + çoğul + belirtme
    # ── Zamir ────────────────────────────────────────────────────────────────
    ("bana", "ben"),            # ben + yönelme (suppletif: ban-)
    ("seni", "sen"),            # sen + belirtme
    ("onun", "o"),              # o + genitif
    # ── Sıfat → kök ──────────────────────────────────────────────────────────
    ("güzelce", "güzel"),       # güzel + -ce zarfı
    # ── Bileşik token ─────────────────────────────────────────────────────────
    ("göz ardı etti", "göz ardı etmek"),  # birleşik fiil
    # ── Spellcheck fallback (yanlış yazım → düzeltilmiş lemma) ───────────────
    # NOT: 'seker' KULLANMA (= sekmek geniş → geçerli, spellcheck düşmez)
    ("dag", "dağ"),             # dağ → normalize isim kökü
    ("gozluk", "gözlük"),       # gözlük → normalize isim kökü
    ("kapi", "kapı"),           # kapı → normalize isim kökü
    # ── Çözümsüz → None ──────────────────────────────────────────────────────
    ("xyzabc", None),
    ("qqqqq", None),
    # ── Noktalama → None ─────────────────────────────────────────────────────
    (".", None),
    (",", None),
]

# Spellcheck fallback ile gelen: corrected=True beklentisi
CORRECTED_CASES: list[tuple[str, str]] = [
    ("dag", "dağ"),
    ("gozluk", "gözlük"),
    ("kapi", "kapı"),
]

# lemmatize_text cümle testleri: (text, list[str | None])
TEXT_CASES: list[tuple[str, list[str | None]]] = [
    # "Ali eve geldi" → ["ali", "ev", "gelmek"]
    ("Ali eve geldi", ["ali", "ev", "gelmek"]),
    # "Kitabı okudum" → ["kitap", "okumak"]
    ("Kitabı okudum", ["kitap", "okumak"]),
]
