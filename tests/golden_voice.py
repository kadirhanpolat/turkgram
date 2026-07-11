# Elle doğrulanmış çatı (voice) biçimleri — motordan DEĞİL, dilbilgisinden.
#
# Bağımsızlık: Bu tablo YALNIZCA voice-spec.md kurallarından + Türkçe morfofonolojisinden
# elle türetildi; voice.py/morphology.py'deki uygulama OKUNMADI. Korkmaz §498/§484-499
# ÖRNEKLERİ değil, kuralları kullanıldı (CLAUDE.md #3, #11).
#
# Çatı etiketleri (voice_chain değerleri): caus/pass/refl/recip.
# Türetilmiş çatı gövdesi NORMAL fiil gibi çekilir → çekim hücreleri gövdenin doğru
# threadlendiğini doğrular.
#
# ANAHTAR SÖZLEŞMESİ:  "<chain>.<tense>.<person>"  (chain: '+' ile birleşik)
#   "caus.past.3sg"            → conjugate(v,"past","3sg",voice_chain=["caus"])
#   "recip+caus+pass.past.3sg" → conjugate(v,"past","3sg",voice_chain=["recip","caus","pass"])
#   ".neg." → negative=True   (örn "caus.past.neg.3sg")

GOLDEN_VOICE = {
    # =====================================================================
    # ETTİRGEN (caus) — allomorf dalları
    # =====================================================================
    # -DIr (default ünsüz-final): yap→yaptır
    "yapmak": {
        "caus.pres.3sg":     "yaptırıyor",
        "caus.past.3sg":     "yaptırdı",
        "caus.aorist.3sg":   "yaptırır",
        "caus.past.neg.3sg": "yaptırmadı",
        # edilgen: yap→yapıl
        "pass.pres.3sg":     "yapılıyor",
        "pass.past.3sg":     "yapıldı",
        "pass.aorist.3sg":   "yapılır",
        "pass.past.neg.3sg": "yapılmadı",
        # yığın: ettirgen+edilgen → yaptırıl
        "caus+pass.pres.3sg":     "yaptırılıyor",
        "caus+pass.past.3sg":     "yaptırıldı",
        "caus+pass.aorist.3sg":   "yaptırılır",
        "caus+pass.past.neg.3sg": "yaptırılmadı",
        # çift ettirgen → yaptırt (yaptır -r final → -t)
        "caus+caus.pres.3sg":   "yaptırtıyor",
        "caus+caus.past.3sg":   "yaptırttı",
        "caus+caus.aorist.3sg": "yaptırtır",
        # çift ettirgen + edilgen → yaptırtıl
        "caus+caus+pass.past.3sg": "yaptırtıldı",
        # üçlü ettirgen + edilgen (Korkmaz zinciri yap-tır-t-tır-ıl) → yaptırttırıl
        "caus+caus+caus+pass.past.3sg": "yaptırttırıldı",
    },
    # -t (ünlü-final): oku→okut
    "okumak": {
        "caus.pres.3sg":     "okutuyor",
        "caus.past.3sg":     "okuttu",
        "caus.aorist.3sg":   "okutur",
        "caus.past.neg.3sg": "okutmadı",
        # edilgen ünlü-final → -n: oku→okun
        "pass.pres.3sg":     "okunuyor",
        "pass.past.3sg":     "okundu",
        "pass.aorist.3sg":   "okunur",
        "pass.past.neg.3sg": "okunmadı",
        # ettirgen+edilgen: okut→okutul
        "caus+pass.pres.3sg":   "okutuluyor",
        "caus+pass.past.3sg":   "okutuldu",
        "caus+pass.aorist.3sg": "okutulur",
    },
    # -t (çok-heceli -r final): otur→oturt
    "oturmak": {
        "caus.pres.3sg":     "oturtuyor",
        "caus.past.3sg":     "oturttu",
        "caus.aorist.3sg":   "oturtur",
        "caus.past.neg.3sg": "oturtmadı",
    },
    # -t (çok-heceli -l final) + edilgen: azal→azalt
    "azalmak": {
        "caus.past.3sg":       "azalttı",
        "caus.aorist.3sg":     "azaltır",
        "caus+pass.past.3sg":  "azaltıldı",
    },
    # -t (ünlü-final çok-heceli): başla→başlat + edilgen
    "başlamak": {
        "caus.pres.3sg":       "başlatıyor",
        "caus.past.3sg":       "başlattı",
        "caus.aorist.3sg":     "başlatır",
        "caus+pass.past.3sg":  "başlatıldı",
    },
    # leksik -Ir: piş→pişir
    "pişmek": {
        "caus.pres.3sg":     "pişiriyor",
        "caus.past.3sg":     "pişirdi",
        "caus.aorist.3sg":   "pişirir",
        "caus.past.neg.3sg": "pişirmedi",
        "caus+pass.past.3sg": "pişirildi",
    },
    # leksik -Ir: geç→geçir
    "geçmek": {
        "caus.past.3sg":   "geçirdi",
        "caus.aorist.3sg": "geçirir",
    },
    # leksik -Ir (ön/yuvarlak): düş→düşür
    "düşmek": {
        "caus.past.3sg":   "düşürdü",
        "caus.aorist.3sg": "düşürür",
    },
    # leksik -Ar: çık→çıkar
    "çıkmak": {
        "caus.pres.3sg":     "çıkarıyor",
        "caus.past.3sg":     "çıkardı",
        "caus.aorist.3sg":   "çıkarır",
        "caus.past.neg.3sg": "çıkarmadı",
    },
    # leksik -It: kork→korkut
    "korkmak": {
        "caus.pres.3sg":     "korkutuyor",
        "caus.past.3sg":     "korkuttu",
        "caus.aorist.3sg":   "korkutur",
        "caus.past.neg.3sg": "korkutmadı",
    },
    # leksik -It: ürk→ürküt
    "ürkmek": {
        "caus.past.3sg":   "ürküttü",
        "caus.aorist.3sg": "ürkütür",
    },
    # -DIr (tek-heceli -r → -DIr, TUZAK: -t DEĞİL): gör→gördür + edilgen görül + işteş görüş
    "görmek": {
        "caus.pres.3sg":     "gördürüyor",
        "caus.past.3sg":     "gördürdü",
        "caus.aorist.3sg":   "gördürür",
        "pass.past.3sg":     "görüldü",     # -r final → -Il (l DEĞİL)
        "pass.aorist.3sg":   "görülür",
        "recip.past.3sg":    "görüştü",
        "recip.aorist.3sg":  "görüşür",
    },
    # -DIr (tek-heceli -l → -DIr): gül→güldür + edilgen gülün(-In) + işteş gülüş
    "gülmek": {
        "caus.past.3sg":    "güldürdü",
        "caus.aorist.3sg":  "güldürür",
        "pass.past.3sg":    "gülündü",      # -l final → -In
        "recip.past.3sg":   "gülüştü",
    },

    # =====================================================================
    # EDİLGEN (pass) — -Il / -In / -n dalları
    # =====================================================================
    # -In (l-final): bil→bilin
    "bilmek": {
        "pass.pres.3sg":     "biliniyor",
        "pass.past.3sg":     "bilindi",
        "pass.aorist.3sg":   "bilinir",
        "pass.past.neg.3sg": "bilinmedi",
    },
    # -In (l-final, arka/düz): al→alın
    "almak": {
        "pass.pres.3sg":     "alınıyor",
        "pass.past.3sg":     "alındı",
        "pass.aorist.3sg":   "alınır",
        "pass.past.neg.3sg": "alınmadı",
    },
    # -n (ünlü-final): ara→aran
    "aramak": {
        "pass.past.3sg":   "arandı",
        "pass.aorist.3sg": "aranır",
    },

    # =====================================================================
    # DÖNÜŞLÜ (refl) — -n / -In dalları
    # =====================================================================
    # -n (ünlü-final): yıka→yıkan
    "yıkamak": {
        "refl.pres.3sg":     "yıkanıyor",
        "refl.past.3sg":     "yıkandı",
        "refl.aorist.3sg":   "yıkanır",
        "refl.past.neg.3sg": "yıkanmadı",
    },
    # -In (ünsüz-final): giy→giyin
    "giymek": {
        "refl.pres.3sg":     "giyiniyor",
        "refl.past.3sg":     "giyindi",
        "refl.aorist.3sg":   "giyinir",
        "refl.past.neg.3sg": "giyinmedi",
    },
    # -In (ön/yuvarlak): döv→dövün (dönüşlü) + işteş dövüş + yığın
    "dövmek": {
        "refl.past.3sg":     "dövündü",
        "recip.pres.3sg":    "dövüşüyor",
        "recip.past.3sg":    "dövüştü",
        "recip.aorist.3sg":  "dövüşür",
        "recip.past.neg.3sg": "dövüşmedi",
        # showcase yığın: işteş+ettirgen+edilgen → dövüştürül
        "recip+caus+pass.pres.3sg":   "dövüştürülüyor",
        "recip+caus+pass.past.3sg":   "dövüştürüldü",
        "recip+caus+pass.aorist.3sg": "dövüştürülür",
        "recip+caus+pass.past.neg.3sg": "dövüştürülmedi",
    },
    # dönüşlü -In (sevin) — edilgenle biçim çakışması sevil değil (sevin dönüşlü)
    "sevmek": {
        "refl.past.3sg":   "sevindi",
        "refl.aorist.3sg": "sevinir",
        "pass.past.3sg":   "sevildi",   # edilgen -Il (ünsüz v, l değil)
    },

    # =====================================================================
    # İŞTEŞ (recip) — -Iş / -ş dalları
    # =====================================================================
    # -Iş (arka/düz): bak→bakış
    "bakmak": {
        "recip.pres.3sg":     "bakışıyor",
        "recip.past.3sg":     "bakıştı",
        "recip.aorist.3sg":   "bakışır",
        "recip.past.neg.3sg": "bakışmadı",
    },
    # -ş (ünlü-final): ağla→ağlaş
    "ağlamak": {
        "recip.pres.3sg":   "ağlaşıyor",
        "recip.past.3sg":   "ağlaştı",
        "recip.aorist.3sg": "ağlaşır",
    },
}
