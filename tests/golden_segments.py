# Segmentasyon golden — çözümleyici (Faz 2a Task 3). BAĞIMSIZ: motor-körü Opus ajanı
# SPEC §7 kesim politikasından + dilbilgisinden türetti (turkgram/ görülmeden). Segment
# alanı oracle-doğrulamalı DEĞİL (kritik C-02) → bu golden onun bağımsız denetimidir.
#
# Yapı: yüzey → {"lemma": ..., "segments": [(dilim, etiket), ...]}. Dilimler BİRLEŞİNCE
# yüzeyi verir (bitişik, örtüşmez). Zero-morfem (3sg-∅, nom-∅) YAZILMAZ (yüzey dilimi boş).
# Kaynaştırma ünsüzü (-y-/-s-/-n-) SAĞdaki morfem diliminde; yumuşama yüzey biçimiyle.
# TEST: analyze(surface, roots={lemma}) tek analiz döner → onun segmentleri sınanır.
# Etiket: kök="KÖK"; zaman/durum kanonik (DI/Iyor/loc…); kişi/iyelik "1sg"/"2sg"…; çatı
# caus/pass/refl/recip. Belirsiz yüzeyler (gitmeden, gözlerinde) HARİÇ (tek-çözüm şartı).

GOLDEN_SEGMENTS = {
    # --- fiil çekimi ---
    "okuyor":      {"lemma": "okumak", "segments": [("oku", "KÖK"), ("yor", "Iyor")]},
    "geldi":       {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("di", "DI")]},
    "gelmiş":      {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("miş", "mIş")]},
    "gelse":       {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("se", "sA")]},
    "gelmeli":     {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("meli", "mAlI")]},
    "gelir":       {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("ir", "Ir")]},
    "gidiyor":     {"lemma": "gitmek", "segments": [("gid", "KÖK"), ("iyor", "Iyor")]},
    "okumadı":     {"lemma": "okumak", "segments": [("oku", "KÖK"), ("ma", "mA"), ("dı", "DI")]},
    "okuyamadı":   {"lemma": "okumak", "segments": [("oku", "KÖK"), ("yama", "AmA"), ("dı", "DI")]},
    "gelmedi":     {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("me", "mA"), ("di", "DI")]},
    "gelemedi":    {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("eme", "AmA"), ("di", "DI")]},
    "geliyordu":   {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("iyor", "Iyor"), ("du", "hikaye")]},
    "yapabilir":   {"lemma": "yapmak", "segments": [("yap", "KÖK"), ("abil", "Abil"), ("ir", "Ir")]},
    "gelmemiş":    {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("me", "mA"), ("miş", "mIş")]},

    # --- çatı (voice) ---
    "yaptırdı":    {"lemma": "yapmak", "segments": [("yap", "KÖK"), ("tır", "caus"), ("dı", "DI")]},
    "dövüştürüldü": {"lemma": "dövmek", "segments": [
        ("döv", "KÖK"), ("üş", "recip"), ("tür", "caus"), ("ül", "pass"), ("dü", "DI")]},
    "yazdıramadım": {"lemma": "yazmak", "segments": [
        ("yaz", "KÖK"), ("dır", "caus"), ("ama", "AmA"), ("dı", "DI"), ("m", "1sg")]},

    # --- isim çekimi (decline) ---
    "evlerde":     {"lemma": "ev", "segments": [("ev", "KÖK"), ("ler", "lAr"), ("de", "loc")]},
    "evime":       {"lemma": "ev", "segments": [("ev", "KÖK"), ("im", "1sg"), ("e", "dat")]},
    "evde":        {"lemma": "ev", "segments": [("ev", "KÖK"), ("de", "loc")]},
    "arabası":     {"lemma": "araba", "segments": [("araba", "KÖK"), ("sı", "3sg")]},
    "kitaplarım":  {"lemma": "kitap", "segments": [("kitap", "KÖK"), ("lar", "lAr"), ("ım", "1sg")]},
    "kitabımızdan": {"lemma": "kitap", "segments": [
        ("kitab", "KÖK"), ("ımız", "1pl"), ("dan", "abl")]},   # p→b yumuşama

    # --- copula (ekfiil) — kaynaştırma -y- sağdaki ekfiil diliminde ---
    "öğrenciydim": {"lemma": "öğrenci", "segments": [
        ("öğrenci", "KÖK"), ("ydi", "hikaye"), ("m", "1sg")]},
    "hastaymış":   {"lemma": "hasta", "segments": [("hasta", "KÖK"), ("ymış", "rivayet")]},

    # --- fiilimsi (converb / participle) ---
    "okuyunca":    {"lemma": "okumak", "segments": [("oku", "KÖK"), ("yunca", "inca")]},
    "giderek":     {"lemma": "gitmek", "segments": [("gid", "KÖK"), ("erek", "arak")]},
    "okuduğum":    {"lemma": "okumak", "segments": [("oku", "KÖK"), ("duğ", "DIk"), ("um", "1sg")]},
}
