# Elle doğrulanmış tasvir fiili (aktionsart) biçimleri — motordan DEĞİL, dilbilgisinden.
#
# Bağımsızlık: Bu tablo YALNIZCA aspect-spec.md dilbilgisel kurallarından ve Türkçe
# morfofonolojisinden elle türetildi; morphology.py'deki aspect uygulaması OKUNMADI.
#
# Aspect ekleri ve yardımcı fiiller (SPEC tablosu):
#   iver : -Iver-  (ver, bağ ünlü -I YÜKSEK 4'lü: yuvarlak duyarlı)
#   adur : -Adur-  (dur, bağ ünlü -A ALÇAK 2'li)
#   agel : -Agel-  (gel, -A)
#   akal : -Akal-  (kal, -A)
#   ayaz : -Ayaz-  (yaz, -A)
#
# Tasvir gövdesi = esas_kök(ünlü-başlı ek varyantı: yumuşama/ye_de/kaynaştırma) + bağ_ünlü + aux_kök.
# Oluşan gövde NORMAL fiil gibi çekilir; yardımcı fiilin LEKSİK aoristi geçerli:
#   ver/dur/gel/kal → -Ir (tek-heceli istisna)   yaz → -Ar (düzenli)
# Yumuşama YOK (aux ünsüz-final). Şimdiki: aux+u/i+yor. olumsuz: gövde + -mA + -DI.
#
# ANAHTAR SÖZLEŞMESİ:
#   <aspect>.pres.3sg      → conjugate(v,"pres","3sg",aspect=<aspect>)
#   <aspect>.past.3sg      → conjugate(v,"past","3sg",aspect=<aspect>)
#   <aspect>.aorist.3sg    → conjugate(v,"aorist","3sg",aspect=<aspect>)
#   <aspect>.past.neg.3sg  → conjugate(v,"past","3sg",aspect=<aspect>,negative=True)

GOLDEN_ASPECT = {
    # --- yapmak: düz ünsüz, arka/düz (bağ -I → ı, aux harmoni normal) ---
    "yapmak": {
        "iver.pres.3sg":     "yapıveriyor",
        "iver.past.3sg":     "yapıverdi",
        "iver.aorist.3sg":   "yapıverir",
        "iver.past.neg.3sg": "yapıvermedi",
        "adur.pres.3sg":     "yapaduruyor",
        "adur.past.3sg":     "yapadurdu",
        "adur.aorist.3sg":   "yapadurur",
        "adur.past.neg.3sg": "yapadurmadı",
        "agel.pres.3sg":     "yapageliyor",
        "agel.past.3sg":     "yapageldi",
        "agel.aorist.3sg":   "yapagelir",
        "agel.past.neg.3sg": "yapagelmedi",
        "akal.pres.3sg":     "yapakalıyor",
        "akal.past.3sg":     "yapakaldı",
        "akal.aorist.3sg":   "yapakalır",
        "akal.past.neg.3sg": "yapakalmadı",
        "ayaz.pres.3sg":     "yapayazıyor",
        "ayaz.past.3sg":     "yapayazdı",
        "ayaz.aorist.3sg":   "yapayazar",   # yaz → -Ar (düzenli aorist)
        "ayaz.past.neg.3sg": "yapayazmadı",
    },

    # --- bakmak: düz ünsüz, arka/düz ---
    "bakmak": {
        "iver.pres.3sg":     "bakıveriyor",
        "iver.past.3sg":     "bakıverdi",
        "iver.aorist.3sg":   "bakıverir",
        "iver.past.neg.3sg": "bakıvermedi",
        "adur.pres.3sg":     "bakaduruyor",
        "adur.past.3sg":     "bakadurdu",
        "adur.aorist.3sg":   "bakadurur",
        "adur.past.neg.3sg": "bakadurmadı",
        "agel.pres.3sg":     "bakageliyor",
        "agel.past.3sg":     "bakageldi",
        "agel.aorist.3sg":   "bakagelir",
        "agel.past.neg.3sg": "bakagelmedi",
        "akal.pres.3sg":     "bakakalıyor",
        "akal.past.3sg":     "bakakaldı",
        "akal.aorist.3sg":   "bakakalır",
        "akal.past.neg.3sg": "bakakalmadı",
        "ayaz.pres.3sg":     "bakayazıyor",
        "ayaz.past.3sg":     "bakayazdı",
        "ayaz.aorist.3sg":   "bakayazar",
        "ayaz.past.neg.3sg": "bakayazmadı",
    },

    # --- gelmek: düz ünsüz, ön/düz (bağ -I → i) ---
    "gelmek": {
        "iver.pres.3sg":     "geliveriyor",
        "iver.past.3sg":     "geliverdi",
        "iver.aorist.3sg":   "geliverir",
        "iver.past.neg.3sg": "gelivermedi",
        "adur.pres.3sg":     "geleduruyor",
        "adur.past.3sg":     "geledurdu",
        "adur.aorist.3sg":   "geledurur",
        "adur.past.neg.3sg": "geledurmadı",
        "agel.pres.3sg":     "gelegeliyor",
        "agel.past.3sg":     "gelegeldi",
        "agel.aorist.3sg":   "gelegelir",
        "agel.past.neg.3sg": "gelegelmedi",
        "akal.pres.3sg":     "gelekalıyor",
        "akal.past.3sg":     "gelekaldı",
        "akal.aorist.3sg":   "gelekalır",
        "akal.past.neg.3sg": "gelekalmadı",
        "ayaz.pres.3sg":     "geleyazıyor",
        "ayaz.past.3sg":     "geleyazdı",
        "ayaz.aorist.3sg":   "geleyazar",
        "ayaz.past.neg.3sg": "geleyazmadı",
    },

    # --- gitmek: YUMUŞAMA git→gid (ünlü-başlı bağ ünlüsü tetikler) ---
    "gitmek": {
        "iver.pres.3sg":     "gidiveriyor",
        "iver.past.3sg":     "gidiverdi",
        "iver.aorist.3sg":   "gidiverir",
        "iver.past.neg.3sg": "gidivermedi",
        "adur.pres.3sg":     "gideduruyor",
        "adur.past.3sg":     "gidedurdu",
        "adur.aorist.3sg":   "gidedurur",
        "adur.past.neg.3sg": "gidedurmadı",
        "agel.pres.3sg":     "gidegeliyor",
        "agel.past.3sg":     "gidegeldi",
        "agel.aorist.3sg":   "gidegelir",
        "agel.past.neg.3sg": "gidegelmedi",
        "akal.pres.3sg":     "gidekalıyor",
        "akal.past.3sg":     "gidekaldı",
        "akal.aorist.3sg":   "gidekalır",
        "akal.past.neg.3sg": "gidekalmadı",
        "ayaz.pres.3sg":     "gideyazıyor",
        "ayaz.past.3sg":     "gideyazdı",
        "ayaz.aorist.3sg":   "gideyazar",
        "ayaz.past.neg.3sg": "gideyazmadı",
    },

    # --- yemek: ye_de (ye→yi) + kaynaştırma -y- (ünlü-final kök) ---
    # ye + I(yüksek,ön/düz→i) + ver → yi + y + i + ver = yiyiver
    # ye + A(ön→e) + dur → yi + y + e + dur = yiyedur
    "yemek": {
        "iver.pres.3sg":     "yiyiveriyor",
        "iver.past.3sg":     "yiyiverdi",
        "iver.aorist.3sg":   "yiyiverir",
        "iver.past.neg.3sg": "yiyivermedi",
        "adur.pres.3sg":     "yiyeduruyor",
        "adur.past.3sg":     "yiyedurdu",
        "adur.aorist.3sg":   "yiyedurur",
        "adur.past.neg.3sg": "yiyedurmadı",
        "agel.pres.3sg":     "yiyegeliyor",
        "agel.past.3sg":     "yiyegeldi",
        "agel.aorist.3sg":   "yiyegelir",
        "agel.past.neg.3sg": "yiyegelmedi",
        "akal.pres.3sg":     "yiyekalıyor",
        "akal.past.3sg":     "yiyekaldı",
        "akal.aorist.3sg":   "yiyekalır",
        "akal.past.neg.3sg": "yiyekalmadı",
        "ayaz.pres.3sg":     "yiyeyazıyor",
        "ayaz.past.3sg":     "yiyeyazdı",
        "ayaz.aorist.3sg":   "yiyeyazar",
        "ayaz.past.neg.3sg": "yiyeyazmadı",
    },

    # --- okumak: ünlü-final + kaynaştırma -y- ; arka/YUVARLAK ---
    # oku + I(yüksek,arka/yuvarlak→u) + ver → oku + y + u + ver = okuyuver
    # oku + A(arka→a) + dur → oku + y + a + dur = okuyadur
    "okumak": {
        "iver.pres.3sg":     "okuyuveriyor",
        "iver.past.3sg":     "okuyuverdi",
        "iver.aorist.3sg":   "okuyuverir",
        "iver.past.neg.3sg": "okuyuvermedi",
        "adur.pres.3sg":     "okuyaduruyor",
        "adur.past.3sg":     "okuyadurdu",
        "adur.aorist.3sg":   "okuyadurur",
        "adur.past.neg.3sg": "okuyadurmadı",
        "agel.pres.3sg":     "okuyageliyor",
        "agel.past.3sg":     "okuyageldi",
        "agel.aorist.3sg":   "okuyagelir",
        "agel.past.neg.3sg": "okuyagelmedi",
        "akal.pres.3sg":     "okuyakalıyor",
        "akal.past.3sg":     "okuyakaldı",
        "akal.aorist.3sg":   "okuyakalır",
        "akal.past.neg.3sg": "okuyakalmadı",
        "ayaz.pres.3sg":     "okuyayazıyor",
        "ayaz.past.3sg":     "okuyayazdı",
        "ayaz.aorist.3sg":   "okuyayazar",
        "ayaz.past.neg.3sg": "okuyayazmadı",
    },

    # --- aramak: ünlü-final + kaynaştırma -y- ; arka/DÜZ ---
    # ara + I(yüksek,arka/düz→ı) + ver → ara + y + ı + ver = arayıver
    # ara + A(arka→a) + dur → ara + y + a + dur = arayadur
    "aramak": {
        "iver.pres.3sg":     "arayıveriyor",
        "iver.past.3sg":     "arayıverdi",
        "iver.aorist.3sg":   "arayıverir",
        "iver.past.neg.3sg": "arayıvermedi",
        "adur.pres.3sg":     "arayaduruyor",
        "adur.past.3sg":     "arayadurdu",
        "adur.aorist.3sg":   "arayadurur",
        "adur.past.neg.3sg": "arayadurmadı",
        "agel.pres.3sg":     "arayageliyor",
        "agel.past.3sg":     "arayageldi",
        "agel.aorist.3sg":   "arayagelir",
        "agel.past.neg.3sg": "arayagelmedi",
        "akal.pres.3sg":     "arayakalıyor",
        "akal.past.3sg":     "arayakaldı",
        "akal.aorist.3sg":   "arayakalır",
        "akal.past.neg.3sg": "arayakalmadı",
        "ayaz.pres.3sg":     "arayayazıyor",
        "ayaz.past.3sg":     "arayayazdı",
        "ayaz.aorist.3sg":   "arayayazar",
        "ayaz.past.neg.3sg": "arayayazmadı",
    },

    # --- görmek: düz ünsüz, ön/YUVARLAK (bağ -I yüksek → ü) ---
    "görmek": {
        "iver.pres.3sg":     "görüveriyor",
        "iver.past.3sg":     "görüverdi",
        "iver.aorist.3sg":   "görüverir",
        "iver.past.neg.3sg": "görüvermedi",
        "adur.pres.3sg":     "göreduruyor",
        "adur.past.3sg":     "göredurdu",
        "adur.aorist.3sg":   "göredurur",
        "adur.past.neg.3sg": "göredurmadı",
        "agel.pres.3sg":     "göregeliyor",
        "agel.past.3sg":     "göregeldi",
        "agel.aorist.3sg":   "göregelir",
        "agel.past.neg.3sg": "göregelmedi",
        "akal.pres.3sg":     "görekalıyor",
        "akal.past.3sg":     "görekaldı",
        "akal.aorist.3sg":   "görekalır",
        "akal.past.neg.3sg": "görekalmadı",
        "ayaz.pres.3sg":     "göreyazıyor",
        "ayaz.past.3sg":     "göreyazdı",
        "ayaz.aorist.3sg":   "göreyazar",
        "ayaz.past.neg.3sg": "göreyazmadı",
    },

    # --- gülmek: düz ünsüz, ön/YUVARLAK ---
    "gülmek": {
        "iver.pres.3sg":     "gülüveriyor",
        "iver.past.3sg":     "gülüverdi",
        "iver.aorist.3sg":   "gülüverir",
        "iver.past.neg.3sg": "gülüvermedi",
        "adur.pres.3sg":     "güleduruyor",
        "adur.past.3sg":     "güledurdu",
        "adur.aorist.3sg":   "güledurur",
        "adur.past.neg.3sg": "güledurmadı",
        "agel.pres.3sg":     "gülegeliyor",
        "agel.past.3sg":     "gülegeldi",
        "agel.aorist.3sg":   "gülegelir",
        "agel.past.neg.3sg": "gülegelmedi",
        "akal.pres.3sg":     "gülekalıyor",
        "akal.past.3sg":     "gülekaldı",
        "akal.aorist.3sg":   "gülekalır",
        "akal.past.neg.3sg": "gülekalmadı",
        "ayaz.pres.3sg":     "güleyazıyor",
        "ayaz.past.3sg":     "güleyazdı",
        "ayaz.aorist.3sg":   "güleyazar",
        "ayaz.past.neg.3sg": "güleyazmadı",
    },
}
