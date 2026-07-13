# Artım-2 golden — Oflazer tam eksen eşlemesi (Faz 2b, madde A, Artım-2).
# BAĞIMSIZ: motor-körü olarak yalnız spec/statistical-disambiguation-spec.md +
# Türkçe dilbilgisi + TrMor2018 formatıyla kuruldu (turkgram/statistical.py görülmeden).
# Runner: tests/test_statistical_artim2.py
#
# SPEC §5 Artım-2: Oflazer inflectional özellikler → turkgram eksenleri.
# Eşleme TEK-YÖNLÜ (Oflazer→turkgram).
# Bilinmeyen etiket → "unmapped" işaretlenir (harness'te ayrı sınıf).
#
# Eksen sözlüğü kuralları (beklenen_axes):
#   - person: her zaman dahil (Verb için)
#   - tense:  her zaman dahil (Verb için)
#   - negative: YALNIZ True olduğunda dahil (Pos → atlanır)
#   - case: nom dahil (eksik parse'ı yakalar)
#   - number: YALNIZ "pl" olduğunda dahil (A3sg → atlanır)
#   - possessive: YALNIZ Pnon olmadığında dahil
#   - voice: YALNIZ boş değilse dahil (liste)
#   - ptype: participle/isimleştirme türü (mevcut olduğunda)
#
# Konvansiyonlar (SPEC §5 + turkgram eksenleri):
#   Oflazer → turkgram
#   A1sg/A2sg/A3sg/A1pl/A2pl/A3pl → person: 1sg/2sg/3sg/1pl/2pl/3pl
#   Pnon → possessive yok (atlanır); P1sg..P3pl → possessive: 1sg..3pl
#   Nom/Acc/Dat/Loc/Abl/Gen/Ins → case: nom/acc/dat/loc/abl/gen/ins
#   Pos → atlanır; Neg → negative: True
#   Past→past, Narr→evid, Fut→fut, Aor→aorist, Prog1→pres,
#   Cond→cond, Opt→opt, Imp→imp, Neces→neces
#   Caus→caus, Pass→pass, Reflex→refl, Recip→recip (voice listesinde)
#   PresPart→pres, FutPart→fut, PastPart→past, AorPart→aorist (ptype)
#   Inf1→inf1, Inf2→inf2, Inf3→inf3
#   ^DB → grup sınırı; ses özelliklerini tüm gruplardan topla

# ─── AİLE 1: Tam eksen eşleme golden'ı ─────────────────────────────────────
# (oflazer_str, beklenen_lemma, beklenen_major_pos, beklenen_axes_dict)

AXIS_MAPPING_CASES = [
    # ─── Basit fiiller (^DB yok) ───────────────────────────────────────────

    # Geçmiş, 3sg, olumlu
    ("gel+Verb+Pos+Past+A3sg", "gel", "Verb",
     {"tense": "past", "person": "3sg"}),

    # Geçmiş, 3sg, olumsuz
    ("gel+Verb+Neg+Past+A3sg", "gel", "Verb",
     {"tense": "past", "person": "3sg", "negative": True}),

    # Geçmiş, 1sg
    ("yap+Verb+Pos+Past+A1sg", "yap", "Verb",
     {"tense": "past", "person": "1sg"}),

    # Geçmiş, 1pl
    ("gel+Verb+Pos+Past+A1pl", "gel", "Verb",
     {"tense": "past", "person": "1pl"}),

    # Geçmiş, 3pl
    ("git+Verb+Pos+Past+A3pl", "git", "Verb",
     {"tense": "past", "person": "3pl"}),

    # Geniş zaman (Aor), 3sg
    ("gel+Verb+Pos+Aor+A3sg", "gel", "Verb",
     {"tense": "aorist", "person": "3sg"}),

    # Geniş zaman, olumsuz, 1sg
    ("gel+Verb+Neg+Aor+A1sg", "gel", "Verb",
     {"tense": "aorist", "person": "1sg", "negative": True}),

    # Şimdiki (Prog1 = -Iyor), 3sg
    ("gel+Verb+Pos+Prog1+A3sg", "gel", "Verb",
     {"tense": "pres", "person": "3sg"}),

    # Gelecek (Fut), 3sg
    ("gel+Verb+Pos+Fut+A3sg", "gel", "Verb",
     {"tense": "fut", "person": "3sg"}),

    # Rivayet (Narr = -mIş), 3sg
    ("gel+Verb+Pos+Narr+A3sg", "gel", "Verb",
     {"tense": "evid", "person": "3sg"}),

    # Şart (Cond = -sA), 3sg
    ("gel+Verb+Pos+Cond+A3sg", "gel", "Verb",
     {"tense": "cond", "person": "3sg"}),

    # İstek (Opt = -A), 3sg
    ("gel+Verb+Pos+Opt+A3sg", "gel", "Verb",
     {"tense": "opt", "person": "3sg"}),

    # Emir (Imp), 2sg
    ("git+Verb+Pos+Imp+A2sg", "git", "Verb",
     {"tense": "imp", "person": "2sg"}),

    # Gereklilik (Neces = -mAlI), 3sg
    ("gel+Verb+Pos+Neces+A3sg", "gel", "Verb",
     {"tense": "neces", "person": "3sg"}),

    # Geçmiş, 2pl
    ("yaz+Verb+Pos+Past+A2pl", "yaz", "Verb",
     {"tense": "past", "person": "2pl"}),

    # ─── Basit isimler ──────────────────────────────────────────────────────

    # Yalın (nom), tekil, iyeliksiz
    ("hazine+Noun+A3sg+Pnon+Nom", "hazine", "Noun",
     {"case": "nom"}),

    # Belirtme (acc)
    ("kitap+Noun+A3sg+Pnon+Acc", "kitap", "Noun",
     {"case": "acc"}),

    # Yönelme (dat)
    ("ev+Noun+A3sg+Pnon+Dat", "ev", "Noun",
     {"case": "dat"}),

    # Bulunma (loc)
    ("ev+Noun+A3sg+Pnon+Loc", "ev", "Noun",
     {"case": "loc"}),

    # Çıkma (abl)
    ("okul+Noun+A3sg+Pnon+Abl", "okul", "Noun",
     {"case": "abl"}),

    # Tamlayan (gen)
    ("Hazine+Noun+Prop+A3sg+Pnon+Gen", "Hazine", "Noun",
     {"case": "gen"}),

    # Vasıta (ins)
    ("tren+Noun+A3sg+Pnon+Ins", "tren", "Noun",
     {"case": "ins"}),

    # Çoğul, yalın
    ("kitap+Noun+A3pl+Pnon+Nom", "kitap", "Noun",
     {"case": "nom", "number": "pl"}),

    # Çoğul, bulunma
    ("rezerv+Noun+A3pl+Pnon+Loc", "rezerv", "Noun",
     {"case": "loc", "number": "pl"}),

    # ─── İyelikli isimler ───────────────────────────────────────────────────

    # 1sg iyelik, yalın
    ("ev+Noun+A3sg+P1sg+Nom", "ev", "Noun",
     {"case": "nom", "possessive": "1sg"}),

    # 2sg iyelik, yalın
    ("kız+Noun+A3sg+P2sg+Nom", "kız", "Noun",
     {"case": "nom", "possessive": "2sg"}),

    # 3sg iyelik, yönelme
    ("hesap+Noun+A3sg+P3sg+Dat", "hesap", "Noun",
     {"case": "dat", "possessive": "3sg"}),

    # 1sg iyelik, bulunma
    ("ev+Noun+A3sg+P1sg+Loc", "ev", "Noun",
     {"case": "loc", "possessive": "1sg"}),

    # 3sg iyelik, belirtme
    ("banka+Noun+A3sg+P3sg+Acc", "banka", "Noun",
     {"case": "acc", "possessive": "3sg"}),

    # 3pl iyelik, yalın (Oflazer P3pl)
    ("kaynak+Noun+A3pl+P3sg+Loc", "kaynak", "Noun",
     {"case": "loc", "number": "pl", "possessive": "3sg"}),

    # ─── Çatı zincirleri (^DB) ──────────────────────────────────────────────

    # Ettirgen: rahatla→Caus
    ("rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg", "rahatla", "Verb",
     {"tense": "past", "person": "3sg", "voice": ["caus"]}),

    # Edilgen: gözle→Pass
    ("gözle+Verb^DB+Verb+Pass+Pos+Past+A3sg", "gözle", "Verb",
     {"tense": "past", "person": "3sg", "voice": ["pass"]}),

    # Dönüşlü: Reflex
    ("giy+Verb^DB+Verb+Reflex+Pos+Past+A3sg", "giy", "Verb",
     {"tense": "past", "person": "3sg", "voice": ["refl"]}),

    # İşteş: Recip
    ("dövüş+Verb^DB+Verb+Recip+Pos+Past+A3sg", "dövüş", "Verb",
     {"tense": "past", "person": "3sg", "voice": ["recip"]}),

    # Yığılma: Recip→Caus→Pass (CLAUDE.md §6a örneği)
    ("döv+Verb^DB+Verb+Recip^DB+Verb+Caus^DB+Verb+Pass+Pos+Past+A3sg",
     "döv", "Verb",
     {"tense": "past", "person": "3sg", "voice": ["recip", "caus", "pass"]}),

    # Ettirgen+olumsuz
    ("rahatla+Verb^DB+Verb+Caus+Neg+Past+A3sg", "rahatla", "Verb",
     {"tense": "past", "person": "3sg", "negative": True, "voice": ["caus"]}),

    # ─── Sıfat-fiiller (participle, ^DB Adj) ────────────────────────────────

    # PresPart: -An (yapan = yap+...+Adj+PresPart)
    ("yap+Verb+Pos^DB+Adj+PresPart", "yap", "Adj",
     {"ptype": "pres"}),

    # FutPart: -AcAk, iyelikli (kullanabilecek → FutPart+P3sg)
    ("kullan+Verb+Pos^DB+Verb+Able^DB+Adj+FutPart+P3sg", "kullan", "Adj",
     {"ptype": "fut", "possessive": "3sg"}),

    # PastPart: -DIk (okuduğum = oku+...+Adj+PastPart+P1sg)
    ("oku+Verb+Pos^DB+Adj+PastPart+P1sg", "oku", "Adj",
     {"ptype": "past", "possessive": "1sg"}),

    # AorPart: -Ar (gelir)
    ("gel+Verb+Pos^DB+Adj+AorPart", "gel", "Adj",
     {"ptype": "aorist"}),

    # ─── İsim-fiiller (^DB Noun+Inf*) ───────────────────────────────────────

    # Inf2: -mA (gitmesini → git+...+Noun+Inf2+P3sg+Acc)
    ("git+Verb+Pos^DB+Noun+Inf2+A3sg+P3sg+Acc", "git", "Noun",
     {"ptype": "inf2", "case": "acc", "possessive": "3sg"}),

    # Inf1: -mAk
    ("git+Verb+Pos^DB+Noun+Inf1+A3sg+Pnon+Nom", "git", "Noun",
     {"ptype": "inf1", "case": "nom"}),

    # Inf3: -Iş (gidiş)
    ("git+Verb+Pos^DB+Noun+Inf3+A3sg+Pnon+Nom", "git", "Noun",
     {"ptype": "inf3", "case": "nom"}),

    # ─── Türetme (^DB Adj/Noun, içerik yok) ─────────────────────────────────

    # Adj+With (vadeli ← vade+Nom^DB+Adj+With)
    ("vade+Noun+A3sg+Pnon+Nom^DB+Adj+With", "vade", "Adj",
     {}),  # With derivasyon → Adj, aksiyel özellik yok

    # Adj+JustLike (bankası gibi: banka+...^DB+Adj+JustLike)
    ("banka+Noun+A3sg+P3sg+Nom^DB+Adj+JustLike", "banka", "Adj",
     {}),

    # Noun+Ness (liralkı ← lira+...^DB+Noun+Ness+...)
    ("lira+Noun+A3sg+Pnon+Nom^DB+Noun+Ness+A3sg+Pnon+Nom", "lira", "Noun",
     {"ptype": "ness", "case": "nom"}),

    # ─── Zarf-fiiller (^DB Adverb+While) ────────────────────────────────────

    # While adverb (-ken, Oflazer geleneği)
    ("çık+Verb+Pos+Aor^DB+Adverb+While", "çık", "Adverb",
     {"ptype": "while"}),

    # ─── Bilinmeyen etiket → "unmapped" kaydı ───────────────────────────────
    # Bilinmeyen etiket → axes["_unmapped"] listesine eklenir
    ("test+Verb+Pos+Past+XYZ+A3sg", "test", "Verb",
     {"tense": "past", "person": "3sg"}),
    # XYZ bilinmiyor → atlanır (sessiz; "_unmapped" opsiyonel)
]

# ─── AİLE 2: İnce-taneli durum golden'ı ────────────────────────────────────
# parse_oflazer_full'dan türetilen ince-taneli HMM durumu:
#   Verb → "Verb:{tense}"  (ör. "Verb:past", "Verb:pres")
#   Noun → "Noun:{case}"   (ör. "Noun:dat", "Noun:nom")
#   Diğer → major_pos (ör. "Adj", "Adverb")
#
# (oflazer_str, beklenen_fine_state)
FINE_STATE_CASES = [
    # Fiil ince durumları
    ("gel+Verb+Pos+Past+A3sg",       "Verb:past"),
    ("gel+Verb+Pos+Prog1+A3sg",      "Verb:pres"),
    ("gel+Verb+Pos+Fut+A3sg",        "Verb:fut"),
    ("gel+Verb+Pos+Aor+A3sg",        "Verb:aorist"),
    ("gel+Verb+Pos+Narr+A3sg",       "Verb:evid"),
    ("gel+Verb+Pos+Cond+A3sg",       "Verb:cond"),
    ("gel+Verb+Neg+Past+A3sg",       "Verb:past"),   # neg eksen değil durum değil
    # Ettirgen → son grup Verb, tense korunur
    ("rahatla+Verb^DB+Verb+Caus+Pos+Past+A3sg",  "Verb:past"),

    # İsim ince durumları
    ("hazine+Noun+A3sg+Pnon+Nom",    "Noun:nom"),
    ("kitap+Noun+A3sg+Pnon+Acc",     "Noun:acc"),
    ("ev+Noun+A3sg+Pnon+Dat",        "Noun:dat"),
    ("ev+Noun+A3sg+Pnon+Loc",        "Noun:loc"),
    ("okul+Noun+A3sg+Pnon+Abl",      "Noun:abl"),
    ("Hazine+Noun+Prop+A3sg+Pnon+Gen","Noun:gen"),
    ("tren+Noun+A3sg+Pnon+Ins",      "Noun:ins"),

    # Sıfat → ince durum yok → "Adj"
    ("yap+Verb+Pos^DB+Adj+PresPart",  "Adj"),
    ("geçen+Adj",                     "Adj"),

    # Zarf → "Adverb"
    ("geri+Adverb",                   "Adverb"),

    # İsimleştirilmiş fiil → Noun:{case}
    ("git+Verb+Pos^DB+Noun+Inf2+A3sg+P3sg+Acc", "Noun:acc"),
]

# ─── AİLE 3: Cümle-düzeyi eksen karşılaştırma golden'ı ─────────────────────
# Kural-tabanlı bağlam (context.py) + istatistiksel HMM aynı/farklı seçimleri.
# Format: (tokens, expected_axes_per_token)
# expected_axes_per_token[i] = {axes gold olarak beklenen top-1 çözüm eksenlerinden}
# NOT: Bu golden kural-istatistik KESİŞİMİNİ sınar (ikisi de aynı → gold).
# Yalnız iki sistemin uzlaştığı durumlar dahil edilir.
SENTENCE_AXIS_CASES = [
    # "üç gelin" → gelin = isim (decline, nom kanonik çıkarılır): kural K1 + HMM Num→Noun
    # NOT: turkgram decline() yalın durumda case='nom' kwargs'tan ATAR (CLAUDE.md §4)
    # → lemma ve kind test edilir; axes boş
    (["üç", "gelin"],
     [None,
      {}]),      # gelin → decline, yalın nom (kwargs={})

    # "ben geldim" → geldim = geçmiş 1sg
    (["ben", "geldim"],
     [None,
      {"tense": "past", "person": "1sg"}]),

    # "siz gelirsiniz" → gelirsiniz = aorist 2pl
    (["siz", "gelirsiniz"],
     [None,
      {"tense": "aorist", "person": "2pl"}]),

    # "benim evim" → evim = nom, 1sg iyelik
    # NOT: nom kwargs'tan atılır; yalnız possessive test edilir
    (["benim", "evim"],
     [None,
      {"possessive": "1sg"}]),   # case=nom atılır; possessive şart

    # "okula doğru" → okula = dat
    (["okula", "doğru"],
     [{"case": "dat"},
      None]),
]
