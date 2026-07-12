# -*- coding: utf-8 -*-
"""Elle doğrulanmış Türkçe bileşik zaman biçimleri. MOTORDAN DEĞİL, yalnız dilbilgisinden.
compound-tense-spec.md değişmezi (özellikle 3pl=tabanda -lAr). Motora bakılmadan bağımsız.

Bileşik zaman = basit taban (pres/aorist/fut/evid) + ek-fiil (hikaye -DI / rivayet -mIş /
şart -sA) + kişi. 3pl KRİTİK: çoğul -lAr TABANA biner, ek-fiil 3sg olur.

Kişi ekleri:
  k-tipi (hikaye/şart): 1sg -m, 2sg -n, 3sg -Ø, 1pl -k, 2pl -nIz.
  z-tipi (rivayet):     1sg -Im, 2sg -sIn, 3sg -Ø, 1pl -Iz, 2pl -sInIz.
Ek-fiil ünlüsü tabanın son ünlüsünden 4'lü; -DI sertleşmesi tabanın son sesinden.
"""

# (lemma, base, copula, person, negative) -> biçim
GOLDEN_COMPOUND = {
    # 1) şimdiki hikâye — gelmek (pres, hikaye). geliyor: son ünlü o→u, son ses r→d.
    ("gelmek", "pres", "hikaye", "1sg", False): "geliyordum",
    ("gelmek", "pres", "hikaye", "2sg", False): "geliyordun",
    ("gelmek", "pres", "hikaye", "3sg", False): "geliyordu",
    ("gelmek", "pres", "hikaye", "1pl", False): "geliyorduk",
    ("gelmek", "pres", "hikaye", "2pl", False): "geliyordunuz",
    ("gelmek", "pres", "hikaye", "3pl", False): "geliyorlardı",  # 3pl: taban geliyorlar + dı

    # 2) geniş rivayet — gelmek (aorist, rivayet). gelir: son ünlü i→i (miş), z-tipi.
    ("gelmek", "aorist", "rivayet", "1sg", False): "gelirmişim",
    ("gelmek", "aorist", "rivayet", "2sg", False): "gelirmişsin",
    ("gelmek", "aorist", "rivayet", "3sg", False): "gelirmiş",
    ("gelmek", "aorist", "rivayet", "1pl", False): "gelirmişiz",
    ("gelmek", "aorist", "rivayet", "2pl", False): "gelirmişsiniz",
    ("gelmek", "aorist", "rivayet", "3pl", False): "gelirlermiş",  # 3pl: taban gelirler + miş

    # 3) gelecek hikâye — gelmek (fut, hikaye). gelecek: sert-final k→t, son ünlü e→i (ti).
    ("gelmek", "fut", "hikaye", "1sg", False): "gelecektim",
    ("gelmek", "fut", "hikaye", "2sg", False): "gelecektin",
    ("gelmek", "fut", "hikaye", "3sg", False): "gelecekti",
    ("gelmek", "fut", "hikaye", "1pl", False): "gelecektik",
    ("gelmek", "fut", "hikaye", "2pl", False): "gelecektiniz",
    ("gelmek", "fut", "hikaye", "3pl", False): "geleceklerdi",  # 3pl: taban gelecekler + di

    # 4) miş'li geçmişin hikâyesi — gelmek (evid, hikaye). gelmiş: sert-final ş→t, son ünlü i→i.
    ("gelmek", "evid", "hikaye", "1sg", False): "gelmiştim",
    ("gelmek", "evid", "hikaye", "2sg", False): "gelmiştin",
    ("gelmek", "evid", "hikaye", "3sg", False): "gelmişti",
    ("gelmek", "evid", "hikaye", "1pl", False): "gelmiştik",
    ("gelmek", "evid", "hikaye", "2pl", False): "gelmiştiniz",
    ("gelmek", "evid", "hikaye", "3pl", False): "gelmişlerdi",  # 3pl: taban gelmişler + di

    # 5) geniş şart — gelmek (aorist, sart). gelir: son ünlü i→e (se, ön-düz), k-tipi.
    ("gelmek", "aorist", "sart", "1sg", False): "gelirsem",
    ("gelmek", "aorist", "sart", "2sg", False): "gelirsen",
    ("gelmek", "aorist", "sart", "3sg", False): "gelirse",
    ("gelmek", "aorist", "sart", "1pl", False): "gelirsek",
    ("gelmek", "aorist", "sart", "2pl", False): "gelirseniz",
    ("gelmek", "aorist", "sart", "3pl", False): "gelirlerse",  # 3pl: taban gelirler + se

    # 6) ikinci fiil — yapmak, şimdiki hikâye (pres, hikaye). yapıyor: son ünlü o→u, r→d.
    ("yapmak", "pres", "hikaye", "1sg", False): "yapıyordum",
    ("yapmak", "pres", "hikaye", "2sg", False): "yapıyordun",
    ("yapmak", "pres", "hikaye", "3sg", False): "yapıyordu",
    ("yapmak", "pres", "hikaye", "1pl", False): "yapıyorduk",
    ("yapmak", "pres", "hikaye", "2pl", False): "yapıyordunuz",
    ("yapmak", "pres", "hikaye", "3pl", False): "yapıyorlardı",  # 3pl: taban yapıyorlar + dı

    # olumsuz (negative=True), 3sg — olumsuz taban conjugate'ten aynen + hikaye ek-fiili.
    ("gelmek", "pres", "hikaye", "3sg", True): "gelmiyordu",     # gelmiyor + du
    ("gelmek", "aorist", "hikaye", "3sg", True): "gelmezdi",     # gelmez + di (z→d sesli)
    ("gelmek", "fut", "hikaye", "3sg", True): "gelmeyecekti",    # gelmeyecek + ti (k→t)
    ("gelmek", "evid", "hikaye", "3sg", True): "gelmemişti",     # gelmemiş + ti (ş→t)

    # 7) şart-2pl yuvarlak-ünlü kapsamı (regresyon: -sA sonrası 2pl yüksek ünlü DÜZ;
    #    gövde yuvarlaklığı taşınmaz → -sanız/-seniz, -sanuz DEĞİL).
    ("gelmek", "pres", "sart", "2pl", False): "geliyorsanız",    # geliyor + sa + nız (o→u değil, a→ı)
    ("okumak", "pres", "sart", "2pl", False): "okuyorsanız",     # okuyor + sa + nız
    ("okumak", "aorist", "sart", "2pl", False): "okursanız",     # okur + sa + nız
    ("görmek", "pres", "sart", "2pl", False): "görüyorsanız",    # görüyor + sa + nız (ü→ı, düz-arka)
    ("okumak", "evid", "sart", "2pl", False): "okumuşsanız",     # okumuş + sa + nız
}
