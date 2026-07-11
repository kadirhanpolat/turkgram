# Elle doğrulanmış fiilimsi + iyelik/durum biçimleri — motordan DEĞİL, dilbilgisinden.
#
# Kaynak: spec/participle-spec.md (Korkmaz §677 sıfat-fiil/ad-fiil) + Türkçe dilbilgisi.
# Bu tablo participle motorundan BAĞIMSIZ kurulmuştur; hiçbir biçim motor çıktısından
# alınmamıştır, her hücre elle çekilmiştir.
#
# ANAHTAR SÖZLEŞMESİ (test koşucusu):
#   kind = ilk parça (dik / acak / ma / mak / is)
#   sonraki parçalar: iyelik {1sg,2sg,3sg,1pl,2pl,3pl} ya da durum {acc,dat,loc,abl,gen,ins}
#   "dik"          -> participle(v, "dik")                                 (bare)
#   "dik.1sg"      -> participle(v, "dik", possessive="1sg")
#   "dik.3sg.loc"  -> participle(v, "dik", possessive="3sg", case="loc")
#   "ma.3sg.acc"   -> participle(v, "ma", possessive="3sg", case="acc")
#   "mak.abl"      -> participle(v, "mak", case="abl")
#
# YUMUŞAMA/ye_de HATIRLATMA (spec "Bare fiilimsi gövdeleri"):
#   - acak/is ünlü-başlı taban -> bare'de yumuşama VAR (gidecek, gidiş, yiyecek, yiyiş)
#   - dik/ma/mak ünsüz-başlı   -> bare'de yumuşama YOK (gittik, gitme, gitmek, yedik, yeme)
#   - k→ğ: dik/acak k-final gövde + ünlü-başlı iyelik (okuduğum, geleceğim, gördüğüm)
#   - pronominal -n-: 3sg iyelik + durum (gitmesini, geldiğinde, geleceğini)
#   - -mAk DEFEKTİF: yalnız {bare, abl, loc}; acc/dat KONMAZ (gitmek/gitmekten/gitmekte)

GOLDEN_PARTICIPLE = {
    # ------------------------------------------------------------------ #
    # okumak — ünlü-final (oku-), art/yuvarlak ünlü uyumu (o→u), -y- buffer
    # ------------------------------------------------------------------ #
    "okumak": {
        # dik: oku + duk (D->d ünlü sonrası; art/yuvarlak -> -duk)
        "dik":         "okuduk",
        "dik.1sg":     "okuduğum",     # k->ğ + ünlü-başlı iyelik (u)
        "dik.2sg":     "okuduğun",     # k->ğ + -un
        "dik.3sg":     "okuduğu",      # k->ğ + -u
        "dik.3sg.loc": "okuduğunda",   # okuduğu + n(pronominal) + da
        "dik.3sg.acc": "okuduğunu",    # okuduğu + n + u
        # acak: oku + y + acak
        "acak":         "okuyacak",
        "acak.1sg":     "okuyacağım",  # k->ğ + -ım
        "acak.2sg":     "okuyacağın",
        "acak.3sg":     "okuyacağı",
        "acak.3sg.acc": "okuyacağını", # okuyacağı + n + ı
        # ma: oku + ma
        "ma":         "okuma",
        "ma.1sg":     "okumam",        # ünlü-final iyelik 1sg -> +m
        "ma.2sg":     "okuman",
        "ma.3sg":     "okuması",       # ünlü-final 3sg -> +sı
        "ma.3sg.acc": "okumasını",     # okuması + n + ı
        "ma.1pl":     "okumamız",
        "ma.1pl.acc": "okumamızı",
        # mak: DEFEKTİF -> yalnız bare/abl/loc
        "mak":     "okumak",
        "mak.abl": "okumaktan",
        "mak.loc": "okumakta",
        # is: oku + y + uş (art/yuvarlak -> -uş)
        "is":     "okuyuş",
        "is.1sg": "okuyuşum",
        "is.2sg": "okuyuşun",
        "is.3sg": "okuyuşu",
    },

    # ------------------------------------------------------------------ #
    # aramak — ünlü-final (ara-), art/düz ünlü uyumu, -y- buffer
    # ------------------------------------------------------------------ #
    "aramak": {
        "dik":         "aradık",       # ara + dık (art/düz -> -dık)
        "dik.1sg":     "aradığım",     # k->ğ + -ım
        "dik.2sg":     "aradığın",
        "dik.3sg":     "aradığı",
        "dik.3sg.loc": "aradığında",   # aradığı + n + da
        "acak":         "arayacak",    # ara + y + acak
        "acak.1sg":     "arayacağım",
        "acak.2sg":     "arayacağın",
        "acak.3sg":     "arayacağı",
        "acak.3sg.acc": "arayacağını",
        "ma":         "arama",
        "ma.1sg":     "aramam",
        "ma.2sg":     "araman",
        "ma.3sg":     "araması",
        "ma.3sg.acc": "aramasını",
        "mak":     "aramak",
        "mak.abl": "aramaktan",
        "mak.loc": "aramakta",
        "is":     "arayış",            # ara + y + ış (art/düz -> -ış)
        "is.1sg": "arayışım",
        "is.3sg": "arayışı",
    },

    # ------------------------------------------------------------------ #
    # gitmek — yumuşama (git->gid ünlü-başlı tabanda), ön/düz ünlü uyumu
    # ------------------------------------------------------------------ #
    "gitmek": {
        # dik: ünsüz-başlı -> yumuşama YOK -> git + ti (t->t sertleşme)
        "dik":         "gittik",
        "dik.1sg":     "gittiğim",     # gittik + ğ(k->ğ) + im  -> gövde k-final yumuşar
        "dik.2sg":     "gittiğin",
        "dik.3sg":     "gittiği",
        "dik.3sg.loc": "gittiğinde",   # gittiği + n + de  (pronominal -n-)
        "dik.3sg.acc": "gittiğini",
        # acak: ünlü-başlı -> yumuşama VAR -> gid + ecek
        "acak":         "gidecek",
        "acak.1sg":     "gideceğim",   # k->ğ + -im
        "acak.2sg":     "gideceğin",
        "acak.3sg":     "gideceği",
        "acak.3sg.acc": "gideceğini",  # gideceği + n + i
        # ma: ünsüz-başlı -> yumuşama YOK -> git + me
        "ma":         "gitme",
        "ma.1sg":     "gitmem",        # ünlü-final 1sg -> +m
        "ma.2sg":     "gitmen",
        "ma.3sg":     "gitmesi",
        "ma.3sg.acc": "gitmesini",     # gitmesi + n + i  (SPEC kritik biçim)
        "ma.1pl":     "gitmemiz",
        "ma.1pl.acc": "gitmemizi",
        # mak: DEFEKTİF -> yalnız bare/abl/loc, ünsüz-başlı yumuşama YOK
        "mak":     "gitmek",
        "mak.abl": "gitmekten",        # SPEC kritik biçim
        "mak.loc": "gitmekte",
        # is: ünlü-başlı -> yumuşama VAR -> gid + iş
        "is":     "gidiş",
        "is.1sg": "gidişim",
        "is.2sg": "gidişin",
        "is.3sg": "gidişi",
    },

    # ------------------------------------------------------------------ #
    # etmek — yumuşama (et->ed ünlü-başlı tabanda), ön/düz ünlü uyumu
    # ------------------------------------------------------------------ #
    "etmek": {
        "dik":         "ettik",        # ünsüz-başlı -> yumuşama YOK, et+ti
        "dik.1sg":     "ettiğim",
        "dik.3sg":     "ettiği",
        "dik.3sg.loc": "ettiğinde",
        "acak":         "edecek",      # ünlü-başlı -> yumuşama VAR, ed+ecek
        "acak.1sg":     "edeceğim",
        "acak.3sg":     "edeceği",
        "acak.3sg.acc": "edeceğini",
        "ma":         "etme",
        "ma.1sg":     "etmem",
        "ma.3sg":     "etmesi",
        "ma.3sg.acc": "etmesini",
        "mak":     "etmek",
        "mak.abl": "etmekten",
        "mak.loc": "etmekte",
        "is":     "ediş",              # ünlü-başlı -> yumuşama VAR, ed+iş
        "is.1sg": "edişim",
        "is.3sg": "edişi",
    },

    # ------------------------------------------------------------------ #
    # yemek — ye_de (ye->yi ünlü-başlı/glide tabanda), ön/düz ünlü uyumu
    # ------------------------------------------------------------------ #
    "yemek": {
        # dik: ünsüz-başlı -> ye_de YOK -> ye + dik
        "dik":         "yedik",
        "dik.1sg":     "yediğim",      # yedik + ğ + im
        "dik.2sg":     "yediğin",
        "dik.3sg":     "yediği",
        "dik.3sg.loc": "yediğinde",
        "dik.3sg.acc": "yediğini",
        # acak: ünlü-başlı/glide -> ye_de VAR -> yi + y + ecek
        "acak":         "yiyecek",     # SPEC kritik biçim
        "acak.1sg":     "yiyeceğim",
        "acak.2sg":     "yiyeceğin",
        "acak.3sg":     "yiyeceği",
        "acak.3sg.acc": "yiyeceğini",
        # ma: ünsüz-başlı -> ye_de YOK -> ye + me
        "ma":         "yeme",
        "ma.1sg":     "yemem",
        "ma.2sg":     "yemen",
        "ma.3sg":     "yemesi",
        "ma.3sg.acc": "yemesini",
        # mak: DEFEKTİF, ünsüz-başlı ye_de YOK
        "mak":     "yemek",
        "mak.abl": "yemekten",
        "mak.loc": "yemekte",
        # is: ünlü-başlı/glide -> ye_de VAR -> yi + y + iş
        "is":     "yiyiş",             # SPEC kritik biçim
        "is.1sg": "yiyişim",
        "is.3sg": "yiyişi",
    },

    # ------------------------------------------------------------------ #
    # gelmek — düz (gel-), ön/düz ünlü uyumu, yumuşama YOK
    # ------------------------------------------------------------------ #
    "gelmek": {
        "dik":         "geldik",
        "dik.1sg":     "geldiğim",     # geldik + ğ + im
        "dik.2sg":     "geldiğin",
        "dik.3sg":     "geldiği",
        "dik.3sg.loc": "geldiğinde",   # SPEC kritik biçim (geldik+i+n+de)
        "dik.3sg.acc": "geldiğini",
        "acak":         "gelecek",
        "acak.1sg":     "geleceğim",   # SPEC kritik biçim (k->ğ)
        "acak.2sg":     "geleceğin",
        "acak.3sg":     "geleceği",
        "acak.3sg.acc": "geleceğini",  # SPEC kritik biçim (pronominal -n-)
        "ma":         "gelme",
        "ma.1sg":     "gelmem",
        "ma.2sg":     "gelmen",
        "ma.3sg":     "gelmesi",
        "ma.3sg.acc": "gelmesini",
        "ma.1pl":     "gelmemiz",
        "ma.1pl.acc": "gelmemizi",     # SPEC kritik biçim
        "mak":     "gelmek",
        "mak.abl": "gelmekten",
        "mak.loc": "gelmekte",
        "is":     "geliş",
        "is.1sg": "gelişim",
        "is.2sg": "gelişin",
        "is.3sg": "gelişi",
    },

    # ------------------------------------------------------------------ #
    # yapmak — düz (yap-), art/düz ünlü uyumu, yumuşama YOK (p sertleşmez ekten önce burada)
    # ------------------------------------------------------------------ #
    "yapmak": {
        "dik":         "yaptık",       # yap + tık (p sonrası t sertleşme)
        "dik.1sg":     "yaptığım",     # yaptık + ğ + ım
        "dik.2sg":     "yaptığın",
        "dik.3sg":     "yaptığı",
        "dik.3sg.loc": "yaptığında",
        "dik.3sg.acc": "yaptığını",
        "acak":         "yapacak",
        "acak.1sg":     "yapacağım",
        "acak.2sg":     "yapacağın",
        "acak.3sg":     "yapacağı",
        "acak.3sg.acc": "yapacağını",
        "ma":         "yapma",
        "ma.1sg":     "yapmam",
        "ma.2sg":     "yapman",
        "ma.3sg":     "yapması",
        "ma.3sg.acc": "yapmasını",
        "mak":     "yapmak",
        "mak.abl": "yapmaktan",
        "mak.loc": "yapmakta",
        "is":     "yapış",             # yap + ış (art/düz)
        "is.1sg": "yapışım",
        "is.3sg": "yapışı",
    },

    # ------------------------------------------------------------------ #
    # görmek — yuvarlak (gör-), ön/yuvarlak ünlü uyumu, yumuşama YOK
    # ------------------------------------------------------------------ #
    "görmek": {
        "dik":         "gördük",       # gör + dük (ön/yuvarlak -> -dük)
        "dik.1sg":     "gördüğüm",     # SPEC kritik biçim (k->ğ, ön/yuvarlak -> -üm)
        "dik.2sg":     "gördüğün",
        "dik.3sg":     "gördüğü",
        "dik.3sg.loc": "gördüğünde",   # gördüğü + n + de
        "dik.3sg.acc": "gördüğünü",    # gördüğü + n + ü
        "acak":         "görecek",     # -AcAk düz A ile: gör + ecek
        "acak.1sg":     "göreceğim",
        "acak.2sg":     "göreceğin",
        "acak.3sg":     "göreceği",
        "acak.3sg.acc": "göreceğini",
        "ma":         "görme",
        "ma.1sg":     "görmem",
        "ma.2sg":     "görmen",
        "ma.3sg":     "görmesi",
        "ma.3sg.acc": "görmesini",
        "mak":     "görmek",
        "mak.abl": "görmekten",
        "mak.loc": "görmekte",
        "is":     "görüş",             # gör + üş (ön/yuvarlak)
        "is.1sg": "görüşüm",
        "is.2sg": "görüşün",
        "is.3sg": "görüşü",
    },

    # ------------------------------------------------------------------ #
    # gülmek — yuvarlak (gül-), ön/yuvarlak ünlü uyumu, yumuşama YOK
    # ------------------------------------------------------------------ #
    "gülmek": {
        "dik":         "güldük",       # gül + dük
        "dik.1sg":     "güldüğüm",     # k->ğ, ön/yuvarlak -> -üm
        "dik.2sg":     "güldüğün",
        "dik.3sg":     "güldüğü",
        "dik.3sg.loc": "güldüğünde",
        "acak":         "gülecek",
        "acak.1sg":     "güleceğim",
        "acak.3sg":     "güleceği",
        "acak.3sg.acc": "güleceğini",
        "ma":         "gülme",
        "ma.1sg":     "gülmem",
        "ma.3sg":     "gülmesi",
        "ma.3sg.acc": "gülmesini",
        "mak":     "gülmek",
        "mak.abl": "gülmekten",
        "mak.loc": "gülmekte",
        "is":     "gülüş",             # gül + üş
        "is.1sg": "gülüşüm",
        "is.3sg": "gülüşü",
    },
}
