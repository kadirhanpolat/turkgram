# -*- coding: utf-8 -*-
"""Elle doğrulanmış -ken zarf-fiili biçimleri. MOTORDAN DEĞİL, yalnız dilbilgisinden.
ken-spec.md değişmezi (ken DONMUŞ, ünlü uyumu YOK). Motora bakılmadan bağımsız.

Kritik değişmezler (her hücre elle sağlandı):
  - `ken` DEĞİŞMEZ: hiçbir bağlamda kan/kön/kun OLMAZ. Kalın-ünlülü tabanda bile ken
    (okurken, bakarken, olurken, alırken, dururken, çocukken, okuldayken).
  - Fiil tabanında GLIDE YOK: finit taban daima ünsüzle biter (geliyorken, gelecekken).
  - Nominal glide `y` YALNIZ ünlü-final gövdede: hastayken/evdeyken (y var);
    çocukken/gençken/güzelken (y yok).
  - -AcAk + ken çift-k korunur: gelecekken (k düşmez/yumuşamaz).
  - Aorist 3sg: tek-heceli l/r/n köku → -Ir (gel→gelir, ol→olur, al→alır, dur→durur,
    gül→güler); diğerleri ünlü uyumuyla (oku→okur, bak→bakar, yap→yapar); git→gider (d yumuşama).
"""

# Fiil: (lemma, base, negative) -> biçim
GOLDEN_KEN_VERB = {
    # --- aorist tabanı (base="aorist") — 9 hücre (>=7) ---
    ("gelmek", "aorist", False): "gelirken",
    ("gitmek", "aorist", False): "giderken",
    ("okumak", "aorist", False): "okurken",
    ("bakmak", "aorist", False): "bakarken",
    ("gülmek", "aorist", False): "gülerken",
    ("olmak", "aorist", False): "olurken",
    ("yapmak", "aorist", False): "yaparken",
    ("almak", "aorist", False): "alırken",
    ("durmak", "aorist", False): "dururken",
    # --- diğer tabanlar — 5 hücre ---
    ("gelmek", "pres", False): "geliyorken",
    ("gelmek", "evid", False): "gelmişken",
    ("gelmek", "fut", False): "gelecekken",
    ("okumak", "pres", False): "okuyorken",
    ("gitmek", "fut", False): "gidecekken",
    # --- olumsuz (negative=True) — 3 hücre ---
    ("gelmek", "aorist", True): "gelmezken",
    ("gelmek", "pres", True): "gelmiyorken",
    ("gelmek", "fut", True): "gelmeyecekken",
}

# Nominal: (headword, case_or_None) -> biçim   (case None = yalın)
GOLDEN_KEN_NOMINAL = {
    # --- ünsüz-final → glide YOK ---
    ("çocuk", None): "çocukken",
    ("öğretmen", None): "öğretmenken",
    ("genç", None): "gençken",
    ("güzel", None): "güzelken",
    # --- ünlü-final → glide y ---
    ("hasta", None): "hastayken",
    ("iyi", None): "iyiyken",
    # --- durum-lu (loc, hepsi ünlü-final → y) ---
    ("ev", "loc"): "evdeyken",
    ("okul", "loc"): "okuldayken",
    ("kapı", "loc"): "kapıdayken",
}
