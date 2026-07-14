"""golden_pronoun.py — Zamir çekim golden testleri (SPEC pronoun-spec.md).

Motordan BAĞIMSIZ kuruldu: elle-doğrulanmış dilbilgisel biçimler.
Korkmaz §399–430 referanslı; örnek cümleler KOPYALANMADI (telif).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# §P1-P2 — Suppletif çoğul: ben→biz, sen→siz
# ---------------------------------------------------------------------------
SUPPLETIVE_PLURAL: list[tuple] = [
    # (lemma, number, possessive, case, beklenen)
    ("ben", "pl", None, "nom", "biz"),
    ("ben", "pl", None, "acc", "bizi"),
    ("ben", "pl", None, "dat", "bize"),
    ("ben", "pl", None, "loc", "bizde"),
    ("ben", "pl", None, "abl", "bizden"),
    ("ben", "pl", None, "gen", "bizim"),
    ("ben", "pl", None, "ins", "bizimle"),
    ("sen", "pl", None, "nom", "siz"),
    ("sen", "pl", None, "acc", "sizi"),
    ("sen", "pl", None, "dat", "size"),
    ("sen", "pl", None, "loc", "sizde"),
    ("sen", "pl", None, "abl", "sizden"),
    ("sen", "pl", None, "gen", "sizin"),
    ("sen", "pl", None, "ins", "sizinle"),
]

# ---------------------------------------------------------------------------
# §P3 — N-gövde zamiri: hepsi
# ---------------------------------------------------------------------------
HEPSI: list[tuple] = [
    # (lemma, number, possessive, case, beklenen)
    ("hepsi", "sg", None, "nom",  "hepsi"),
    ("hepsi", "sg", None, "acc",  "hepsini"),
    ("hepsi", "sg", None, "dat",  "hepsine"),
    ("hepsi", "sg", None, "loc",  "hepsinde"),
    ("hepsi", "sg", None, "abl",  "hepsinden"),
    ("hepsi", "sg", None, "gen",  "hepsinin"),
    ("hepsi", "sg", None, "ins",  "hepsiyle"),
]

# ---------------------------------------------------------------------------
# §P4 — N-gövde zamiri: kendi (dönüşlü)
# ---------------------------------------------------------------------------
KENDI: list[tuple] = [
    ("kendi", "sg", None, "nom",  "kendi"),
    ("kendi", "sg", None, "acc",  "kendini"),
    ("kendi", "sg", None, "dat",  "kendine"),
    ("kendi", "sg", None, "loc",  "kendinde"),
    ("kendi", "sg", None, "abl",  "kendinden"),
    ("kendi", "sg", None, "gen",  "kendinin"),
    ("kendi", "sg", None, "ins",  "kendiyle"),
]

# ---------------------------------------------------------------------------
# §P6-P8 — Diğer n-gövde zamirleri
# ---------------------------------------------------------------------------
N_STEM_OTHERS: list[tuple] = [
    # hiçbiri
    ("hiçbiri", "sg", None, "acc",  "hiçbirini"),
    ("hiçbiri", "sg", None, "dat",  "hiçbirine"),
    ("hiçbiri", "sg", None, "loc",  "hiçbirinde"),
    ("hiçbiri", "sg", None, "abl",  "hiçbirinden"),
    ("hiçbiri", "sg", None, "gen",  "hiçbirinin"),
    ("hiçbiri", "sg", None, "ins",  "hiçbiriyle"),
    # birisi
    ("birisi", "sg", None, "acc",  "birisini"),
    ("birisi", "sg", None, "dat",  "birisine"),
    ("birisi", "sg", None, "loc",  "birisinde"),
    ("birisi", "sg", None, "abl",  "birisinden"),
    ("birisi", "sg", None, "gen",  "birisinin"),
    ("birisi", "sg", None, "ins",  "birisiyle"),
    # biri
    ("biri", "sg", None, "acc",  "birini"),
    ("biri", "sg", None, "dat",  "birine"),
    ("biri", "sg", None, "loc",  "birinde"),
    ("biri", "sg", None, "abl",  "birinden"),
    ("biri", "sg", None, "gen",  "birinin"),
    ("biri", "sg", None, "ins",  "biriyle"),
    # öteki
    ("öteki", "sg", None, "acc",  "ötekini"),
    ("öteki", "sg", None, "dat",  "ötekine"),
    ("öteki", "sg", None, "loc",  "ötekinde"),
    ("öteki", "sg", None, "abl",  "ötekinden"),
    ("öteki", "sg", None, "gen",  "ötekinin"),
    ("öteki", "sg", None, "ins",  "ötekiyle"),
    # öbürü
    ("öbürü", "sg", None, "acc",  "öbürünü"),
    ("öbürü", "sg", None, "dat",  "öbürüne"),
    ("öbürü", "sg", None, "loc",  "öbüründe"),
    ("öbürü", "sg", None, "abl",  "öbüründen"),
    ("öbürü", "sg", None, "gen",  "öbürünün"),
    ("öbürü", "sg", None, "ins",  "öbürüyle"),
    # hangisi
    ("hangisi", "sg", None, "acc",  "hangisini"),
    ("hangisi", "sg", None, "dat",  "hangisine"),
    ("hangisi", "sg", None, "loc",  "hangisinde"),
    ("hangisi", "sg", None, "abl",  "hangisinden"),
    ("hangisi", "sg", None, "gen",  "hangisinin"),
    ("hangisi", "sg", None, "ins",  "hangisiyle"),
    # bazısı
    ("bazısı", "sg", None, "acc",  "bazısını"),
    ("bazısı", "sg", None, "dat",  "bazısına"),
    ("bazısı", "sg", None, "loc",  "bazısında"),
    ("bazısı", "sg", None, "abl",  "bazısından"),
    ("bazısı", "sg", None, "gen",  "bazısının"),
    ("bazısı", "sg", None, "ins",  "bazısıyla"),
    # çoğu
    ("çoğu", "sg", None, "acc",  "çoğunu"),
    ("çoğu", "sg", None, "dat",  "çoğuna"),
    ("çoğu", "sg", None, "loc",  "çoğunda"),
    ("çoğu", "sg", None, "abl",  "çoğundan"),
    ("çoğu", "sg", None, "gen",  "çoğunun"),
    ("çoğu", "sg", None, "ins",  "çoğuyla"),
    # azı
    ("azı", "sg", None, "acc",  "azını"),
    ("azı", "sg", None, "dat",  "azına"),
    ("azı", "sg", None, "loc",  "azında"),
    ("azı", "sg", None, "abl",  "azından"),
    ("azı", "sg", None, "gen",  "azının"),
    ("azı", "sg", None, "ins",  "azıyla"),
]

# ---------------------------------------------------------------------------
# §P5 — herkes (düzenli, doğrulama)
# ---------------------------------------------------------------------------
HERKES: list[tuple] = [
    ("herkes", "sg", None, "nom",  "herkes"),
    ("herkes", "sg", None, "acc",  "herkesi"),
    ("herkes", "sg", None, "dat",  "herkese"),
    ("herkes", "sg", None, "loc",  "herkeste"),
    ("herkes", "sg", None, "abl",  "herkesten"),
    ("herkes", "sg", None, "gen",  "herkesin"),
    ("herkes", "sg", None, "ins",  "herkesle"),
]

# ---------------------------------------------------------------------------
# Regresyon — mevcut doğru çalışan zamirler bozulmadı
# ---------------------------------------------------------------------------
REGRESSION: list[tuple] = [
    # Kişi zamirleri tekil (mevcut PRONOUN_FORMS)
    ("ben",  "sg", None, "dat",  "bana"),
    ("ben",  "sg", None, "acc",  "beni"),
    ("ben",  "sg", None, "gen",  "benim"),
    ("sen",  "sg", None, "dat",  "sana"),
    ("sen",  "sg", None, "acc",  "seni"),
    ("o",    "sg", None, "acc",  "onu"),
    ("o",    "sg", None, "dat",  "ona"),
    ("bu",   "sg", None, "acc",  "bunu"),
    ("bu",   "sg", None, "dat",  "buna"),
    ("şu",   "sg", None, "acc",  "şunu"),
    ("biz",  "sg", None, "dat",  "bize"),
    ("biz",  "sg", None, "acc",  "bizi"),
    ("siz",  "sg", None, "dat",  "size"),
    # o/bu/şu çoğul — n-gövde (onlar/bunlar + çekim)
    ("o",    "pl", None, "nom",  "onlar"),
    ("o",    "pl", None, "acc",  "onları"),
    ("o",    "pl", None, "dat",  "onlara"),
    ("bu",   "pl", None, "nom",  "bunlar"),
    ("bu",   "pl", None, "dat",  "bunlara"),
    ("şu",   "pl", None, "nom",  "şunlar"),
    # kim (düzenli)
    ("kim",  "sg", None, "acc",  "kimi"),
    ("kim",  "sg", None, "dat",  "kime"),
    ("kim",  "sg", None, "gen",  "kimin"),
    ("kim",  "sg", None, "loc",  "kimde"),
    ("kim",  "sg", None, "abl",  "kimden"),
    # ne (düzenli)
    ("ne",   "sg", None, "acc",  "neyi"),
    ("ne",   "sg", None, "dat",  "neye"),
]

# ---------------------------------------------------------------------------
# Round-trip golden — analyze çözümlemesi (analysis-by-generation)
# ---------------------------------------------------------------------------
ROUNDTRIP: list[tuple] = [
    # (yüzey, roots, beklenen_kind, beklenen_kwargs_alt_kümesi)
    ("hepsini",   frozenset({"hepsi"}),   "decline", {"case": "acc"}),
    ("hepsine",   frozenset({"hepsi"}),   "decline", {"case": "dat"}),
    ("hepsinde",  frozenset({"hepsi"}),   "decline", {"case": "loc"}),
    ("hepsinden", frozenset({"hepsi"}),   "decline", {"case": "abl"}),
    ("hepsinin",  frozenset({"hepsi"}),   "decline", {"case": "gen"}),
    ("hepsiyle",  frozenset({"hepsi"}),   "decline", {"case": "ins"}),
    ("kendini",   frozenset({"kendi"}),   "decline", {"case": "acc"}),
    ("kendine",   frozenset({"kendi"}),   "decline", {"case": "dat"}),
    ("kendinde",  frozenset({"kendi"}),   "decline", {"case": "loc"}),
    ("kendinden", frozenset({"kendi"}),   "decline", {"case": "abl"}),
    ("kendiyle",  frozenset({"kendi"}),   "decline", {"case": "ins"}),
    ("öbürünü",   frozenset({"öbürü"}),   "decline", {"case": "acc"}),
    ("birini",    frozenset({"biri"}),    "decline", {"case": "acc"}),
    ("birine",    frozenset({"biri"}),    "decline", {"case": "dat"}),
]
