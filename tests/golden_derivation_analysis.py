"""Yapım eki analizi — bağımsız golden (motor-körü, elle-doğrulanmış dilbilgisinden).

Her giriş: (yüzey, beklenen_lemma, beklenen_pos, beklenen_suffix, beklenen_src_pos)
- yüzey: küçük harf (analyze() küçültür)
- lemma: kaynak sözcük
  * isim→isim: kaynak ad ("göz", "türk")
  * isim→fiil: kaynak ad ("göz", "mor")
  * fiil→isim: kaynak MASTAR ("seçmek", "sevmek")
- pos: türetilmiş sözcüğün POS'u ("noun"/"verb"/"adj")
- suffix: _LEXICAL_SUFFIXES'ten etiket
- src_pos: "noun" veya "verb"

Morfofonoloji (4'lü I uyumu, 2'li A uyumu, C/D/G sedalılaşma) her girişte
elle doğrulandı. Sedalılaştıran (sertleştiren) küme: {ç,f,h,k,p,s,ş,t}.
"""

GOLDEN_ANALYSIS: list[tuple[str, str, str, str, str]] = [
    # ── isim → isim (src_pos="noun") ─────────────────────────────
    # -lIk (pos=noun)
    ("gözlük",     "göz",     "noun", "-lIk",   "noun"),  # ü uyumu (ö)
    ("kitaplık",   "kitap",   "noun", "-lIk",   "noun"),  # ı uyumu (a)
    # -CI (pos=noun); C sedalı ünsüzden sonra c, sedasızdan sonra ç
    ("gözcü",      "göz",     "noun", "-CI",    "noun"),  # z sedalı→c, ü
    ("kitapçı",    "kitap",   "noun", "-CI",    "noun"),  # p sedasız→ç, ı
    # -lI (pos=adj)
    ("kirli",      "kir",     "adj",  "-lI",    "noun"),  # i uyumu (i)
    ("taşlı",      "taş",     "adj",  "-lI",    "noun"),  # ı uyumu (a)
    # -sIz (pos=adj)
    ("susuz",      "su",      "adj",  "-sIz",   "noun"),  # u uyumu (u)
    ("sessiz",     "ses",     "adj",  "-sIz",   "noun"),  # i uyumu (e)
    # -CIk (pos=noun); isim küçültme
    ("köycük",     "köy",     "noun", "-CIk",   "noun"),  # y sedalı→c, ü
    # -DAş (pos=noun); D: sedasızdan sonra t
    ("meslektaş",  "meslek",  "noun", "-DAş",   "noun"),  # k sedasız→t, a
    # -CA (pos=adj); C sedasızdan sonra ç
    ("türkçe",     "türk",    "adj",  "-CA",    "noun"),  # k sedasız→ç, e
    ("çocukça",    "çocuk",   "adj",  "-CA",    "noun"),  # k sedasız→ç, a
    # -CIl (pos=adj); C sedalıdan sonra c
    ("evcil",      "ev",      "adj",  "-CIl",   "noun"),  # v sedalı→c, i

    # ── isim → fiil (src_pos="noun", pos="verb", yüzey=MASTAR) ───
    # lemma = kaynak AD; yüzey = türetilmiş fiilin mastarı
    ("gözlemek",   "göz",     "verb", "-lA-",   "noun"),  # e uyumu (ö)
    ("sulanmak",   "su",      "verb", "-lAn-",  "noun"),  # a uyumu (u arka)
    ("taşlaşmak",  "taş",     "verb", "-lAş-",  "noun"),  # a uyumu (a)
    ("azalmak",    "az",      "verb", "-Al-",   "noun"),  # a uyumu; z ünsüz
    ("yaşamak",    "yaş",     "verb", "-A-",    "noun"),  # ş ünsüz→glide yok, a
    ("susamak",    "su",      "verb", "-sA-",   "noun"),  # -sA- ünsüz-başlı, a
    ("benimsemek", "ben",     "verb", "-ImsA-", "noun"),  # n ünsüz; I=i,A=e
    ("morarmak",   "mor",     "verb", "-Ar-",   "noun"),  # r ünsüz; A=a arka

    # ── fiil → isim (src_pos="verb", lemma=MASTAR) ──────────────
    ("seçim",      "seçmek",  "noun", "-Im",    "verb"),  # ç; I=i (e), m
    ("sevgi",      "sevmek",  "noun", "-gI",    "verb"),  # G: v sedalı→g, i
    ("bitkin",     "bitmek",  "adj",  "-gIn",   "verb"),  # G: t sedasız→k, i
    ("konuşkan",   "konuşmak","adj",  "-gAn",   "verb"),  # G: ş sedasız→k, a
    ("durak",      "durmak",  "noun", "-Ak",    "verb"),  # A=a arka; k literal
    ("yazı",       "yazmak",  "noun", "-I",     "verb"),  # I=ı arka
    ("okuman",     "okumak",  "noun", "-mAn",   "verb"),  # m literal; A=a arka
    ("yapıcı",     "yapmak",  "adj",  "-IcI",   "verb"),  # şablon literal c; ı
    ("açık",       "açmak",   "adj",  "-Ik",    "verb"),  # I=ı; k literal
    ("sevinç",     "sevmek",  "noun", "-Inç",   "verb"),  # I=i (e); nç
    ("akıntı",     "akmak",   "noun", "-IntI",  "verb"),  # I=ı; D: k→t, I=ı
]
