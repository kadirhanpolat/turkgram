# Elle doğrulanmış nominal ek-fiil (kopula) biçimleri — motordan DEĞİL, dilbilgisinden.
#
# Kaynak: spec/copula-spec.md (Korkmaz Şekil Bilgisi §579–583 tabanlı dilbilgisel
# değişmez) + elle harmoni/kaynaştırma/sertleşme doğrulaması. Bu tablo motordan
# BAĞIMSIZ kurulmuştur; morphology_noun.py'nin copula uygulamasına BAKILMAMIŞTIR.
#
# Anahtar sözleşmesi (test koşucusu parse eder):
#   pres.<kişi>          -> copula(w, None, kişi)
#   hikaye.<kişi>        -> copula(w, "hikaye", kişi)
#   rivayet.<kişi>       -> copula(w, "rivayet", kişi)
#   sart.<kişi>          -> copula(w, "sart", kişi)
#   loc.hikaye.<kişi>    -> copula(w, "hikaye", kişi, case="loc")
#   loc.rivayet.<kişi>   -> copula(w, "rivayet", kişi, case="loc")
#   soru.pres.<kişi>     -> copula(w, None, kişi, question=True)
#   soru.hikaye.<kişi>   -> copula(w, "hikaye", kişi, question=True)
#   soru.rivayet.<kişi>  -> copula(w, "rivayet", kişi, question=True)
# kişi ∈ {1sg, 2sg, 3sg, 3pl}

GOLDEN_COPULA = {
    # ---- Ünlü-final (kaynaştırma -y-) ----
    "öğrenci": {
        # geniş/bildirme: z-tipi kişi ekleri, 3sg -DIr
        "pres.1sg": "öğrenciyim",       # öğrenci-y-im
        "pres.2sg": "öğrencisin",       # öğrenci-sin
        "pres.3sg": "öğrencidir",       # öğrenci-dir
        # hikâye: k-tipi (-m/-n/-∅/-lAr), ünlü-final -> -y-
        "hikaye.1sg": "öğrenciydim",    # öğrenci-y-di-m
        "hikaye.2sg": "öğrenciydin",
        "hikaye.3sg": "öğrenciydi",
        "hikaye.3pl": "öğrenciydiler",  # 3sg gövde + -lAr (öğrencilerdi DEĞİL)
        # rivayet: z-tipi
        "rivayet.1sg": "öğrenciymişim", # öğrenci-y-miş-im
        "rivayet.3sg": "öğrenciymiş",
        # şart: k-tipi
        "sart.3sg": "öğrenciyse",       # öğrenci-y-se
        # soru: gövde + mI + ekfiil + kişi
        "soru.pres.1sg": "öğrenci miyim",
        "soru.hikaye.1sg": "öğrenci miydim",
        "soru.rivayet.1sg": "öğrenci miymişim",
    },
    "hasta": {
        "pres.1sg": "hastayım",         # hasta-y-ım (a -> ı)
        "pres.3sg": "hastadır",
        "hikaye.1sg": "hastaydım",
        "hikaye.2sg": "hastaydın",
        "hikaye.3sg": "hastaydı",
        "hikaye.3pl": "hastaydılar",
        "rivayet.1sg": "hastaymışım",
        "rivayet.3sg": "hastaymış",
        "sart.3sg": "hastaysa",
        "soru.pres.1sg": "hasta mıyım",
        "soru.hikaye.1sg": "hasta mıydım",
    },
    "kapı": {
        "pres.1sg": "kapıyım",          # kapı-y-ım
        "pres.3sg": "kapıdır",
        "hikaye.1sg": "kapıydım",
        "hikaye.3sg": "kapıydı",
        "hikaye.3pl": "kapıydılar",
        "rivayet.1sg": "kapıymışım",
        "rivayet.3sg": "kapıymış",
        "sart.3sg": "kapıysa",
        "soru.hikaye.1sg": "kapı mıydım",
    },
    "masa": {
        "pres.3sg": "masadır",
        "hikaye.1sg": "masaydım",
        "hikaye.3sg": "masaydı",
        "hikaye.3pl": "masaydılar",
        "rivayet.3sg": "masaymış",
        "sart.3sg": "masaysa",
    },

    # ---- Ünsüz-final, yumuşak (kaynaştırma YOK, sertleşme YOK) ----
    "ev": {
        "pres.1sg": "evim",             # ev-im (ünsüz-final -> -y- YOK)
        "pres.2sg": "evsin",
        "pres.3sg": "evdir",
        "hikaye.1sg": "evdim",          # ev-di-m (evydim DEĞİL)
        "hikaye.2sg": "evdin",
        "hikaye.3sg": "evdi",           # TUZAK: evdi (evydi DEĞİL)
        "hikaye.3pl": "evdiler",
        "rivayet.1sg": "evmişim",
        "rivayet.3sg": "evmiş",
        "sart.3sg": "evse",
        # durum-ekli gövde: evde (loc, ünlü-final) -> -y-
        "loc.hikaye.1sg": "evdeydim",   # evde-y-di-m
        "loc.hikaye.3sg": "evdeydi",    # TUZAK: evde ünlü-final -> -y-
        "loc.rivayet.3sg": "evdeymiş",
        "soru.pres.1sg": "ev miyim",
        "soru.hikaye.1sg": "ev miydim",
    },
    "güzel": {
        "pres.1sg": "güzelim",          # güzel-im
        "pres.3sg": "güzeldir",
        "hikaye.1sg": "güzeldim",       # TUZAK: güzeldi (güzelydi DEĞİL)
        "hikaye.2sg": "güzeldin",
        "hikaye.3sg": "güzeldi",
        "hikaye.3pl": "güzeldiler",
        "rivayet.1sg": "güzelmişim",
        "rivayet.3sg": "güzelmiş",
        "sart.3sg": "güzelse",
        "soru.hikaye.1sg": "güzel miydim",
    },
    "öğretmen": {
        "pres.1sg": "öğretmenim",       # öğretmen-im
        "pres.3sg": "öğretmendir",
        "hikaye.1sg": "öğretmendim",
        "hikaye.2sg": "öğretmendin",
        "hikaye.3sg": "öğretmendi",
        "hikaye.3pl": "öğretmendiler",
        "rivayet.1sg": "öğretmenmişim",
        "rivayet.3sg": "öğretmenmiş",
        "sart.3sg": "öğretmense",
    },
    # okul: loc gövde örneği (okulda -> -y-)
    "okul": {
        "pres.3sg": "okuldur",          # okul-dur
        "loc.hikaye.1sg": "okuldaydım", # okulda-y-dı-m
        "loc.hikaye.3sg": "okuldaydı",  # TUZAK: okulda ünlü-final -> -y-
        "loc.rivayet.3sg": "okuldaymış",
    },

    # ---- Sert-final (f s t k ç ş h p) — -DI d/t sertleşmesi ----
    "genç": {
        # genç ç ile biter; ünlü-başlı ekte ç -> c yumuşar (gencim),
        # -DIr/-DI ünsüz-başlı -> sertleşme (gençtir/gençti).
        "pres.1sg": "gencim",           # genç -> genc + im (ç yumuşar)
        "pres.2sg": "gençsin",          # -sIn ünsüz-başlı, yumuşama YOK
        "pres.3sg": "gençtir",          # TUZAK: sertleşme (gençdir DEĞİL)
        "hikaye.1sg": "gençtim",        # TUZAK: sertleşme (gençdim DEĞİL)
        "hikaye.2sg": "gençtin",
        "hikaye.3sg": "gençti",         # TUZAK: gençti (gençdi DEĞİL)
        "hikaye.3pl": "gençtiler",
        "rivayet.1sg": "gençmişim",     # TUZAK: -mIş sertleşMEZ (gençtmiş DEĞİL)
        "rivayet.3sg": "gençmiş",
        "sart.3sg": "gençse",           # TUZAK: -sA sertleşMEZ (gençtse DEĞİL)
        "soru.pres.1sg": "genç miyim",
        "soru.hikaye.3sg": "genç miydi",  # mi + y-di -> yumuşak (gençti mi DEĞİL)
    },
    "aş": {
        "pres.1sg": "aşım",             # aş-ım (ş yumuşamaz)
        "pres.3sg": "aştır",            # TUZAK: sertleşme (aşdır DEĞİL)
        "hikaye.1sg": "aştım",          # TUZAK: aştı- (aşdı- DEĞİL)
        "hikaye.2sg": "aştın",
        "hikaye.3sg": "aştı",
        "hikaye.3pl": "aştılar",
        "rivayet.1sg": "aşmışım",       # sertleşMEZ
        "rivayet.3sg": "aşmış",
        "sart.3sg": "aşsa",             # aş-sa
    },
    "dost": {
        "pres.1sg": "dostum",           # dost-um (o -> u yuvarlak)
        "pres.2sg": "dostsun",
        "pres.3sg": "dosttur",          # TUZAK: sertleşme (dostdur DEĞİL)
        "hikaye.1sg": "dosttum",        # TUZAK: dosttu- (dostdu- DEĞİL)
        "hikaye.2sg": "dosttun",
        "hikaye.3sg": "dosttu",         # TUZAK: dosttu (dostdu DEĞİL)
        "hikaye.3pl": "dosttular",
        "rivayet.1sg": "dostmuşum",     # dost-muş-um; sertleşMEZ
        "rivayet.3sg": "dostmuş",
        "sart.3sg": "dostsa",
        "soru.hikaye.1sg": "dost muydum",
    },
    "kitap": {
        # kitap p ile biter; ünlü-başlı ekte p -> b yumuşar (kitabım),
        # -DIr/-DI ünsüz-başlı -> sertleşme (kitaptır/kitaptı).
        "pres.1sg": "kitabım",          # kitap -> kitab + ım (p yumuşar)
        "pres.3sg": "kitaptır",         # TUZAK: sertleşme (kitapdır DEĞİL)
        "hikaye.1sg": "kitaptım",       # TUZAK: kitaptı- (kitapdı- DEĞİL)
        "hikaye.2sg": "kitaptın",
        "hikaye.3sg": "kitaptı",
        "hikaye.3pl": "kitaptılar",
        "rivayet.1sg": "kitapmışım",    # sertleşMEZ
        "rivayet.3sg": "kitapmış",
        "sart.3sg": "kitapsa",
        "soru.pres.1sg": "kitap mıyım",
        "soru.hikaye.3sg": "kitap mıydı",
    },
}
