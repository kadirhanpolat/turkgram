# -*- coding: utf-8 -*-
"""Elle doğrulanmış -cAsInA zarf-fiili biçimleri. MOTORDAN DEĞİL, yalnız dilbilgisinden.
casina-spec.md 'Yapı' değişmezi + Türkçe morfofonoloji. converb_casina uygulamasına
bakılmadan bağımsız kurulmuştur.

Yapı (SPEC §Yapı): taban = conjugate(lemma, base, "3sg", negative) → finit taban
DOKUNULMAZ. Ek = taban + C + A + "s" + Iyi + "n" + A:
  - C = ç (taban sert ünsüzle bitiyorsa: ş → ç), yoksa c (r/z → c).
  - A = alçak ünlü; tabanın SON ünlüsü kalınsa a, inceyse e.
  - Iyi = YÜKSEK-DÜZ (yuvarlaklık taşınmaz): A=="a" → ı, A=="e" → i.

Kritik değişmezler (elle sağlandı):
  - Son ünlü DÜZ: okur→okurcasına (ı, okurcusuna DEĞİL); görür→görürcesine (i);
    okumuş→okumuşçasına (ı); görmüş→görmüşçesine (i). Yuvarlaklık Iyi'ye sızmaz.
  - c/ç YALNIZ son sesten: gelir(r)→c, gelmiş(ş)→ç, gelmez(z)→c.
  - Taban conjugate çıktısında zaten çözülü: yumuşama (gid-), -Ir istisnası
    (alır/görür/olur/verir/durur/sanır), olumsuz (gelmez). Ek bunları değiştirmez.
  - Aorist -Ir istisna: al/bil/bul/dur/gel/gör/kal/ol/öl/san/var/ver/vur (tek-heceli).
"""

# (lemma, base, negative) -> beklenen biçim
GOLDEN_CASINA = {
    # --- aorist tabanı (base="aorist", negative=False) ---
    ("gelmek", "aorist", False): "gelircesine",   # gelir: r→c, son ünlü i(ince)→e, Iyi=i
    ("gülmek", "aorist", False): "gülercesine",   # güler: r→c, son ünlü e(ince), Iyi=i
    ("yapmak", "aorist", False): "yaparcasına",   # yapar: r→c, son ünlü a(kalın), Iyi=ı
    ("okumak", "aorist", False): "okurcasına",    # okur: r→c, son ünlü u(kalın)→a, Iyi=ı DÜZ
    ("gitmek", "aorist", False): "gidercesine",   # gider (yumuşama gid-): r→c, e, Iyi=i
    ("bakmak", "aorist", False): "bakarcasına",   # bakar: r→c, a(kalın), Iyi=ı
    ("almak", "aorist", False): "alırcasına",     # alır (-Ir istisna): r→c, ı(kalın), Iyi=ı
    ("görmek", "aorist", False): "görürcesine",   # görür (-Ir): r→c, son ünlü ü(ince)→e, Iyi=i DÜZ
    ("olmak", "aorist", False): "olurcasına",     # olur (-Ir): r→c, u(kalın), Iyi=ı DÜZ
    ("vermek", "aorist", False): "verircesine",   # verir (-Ir): r→c, i(ince), Iyi=i
    ("durmak", "aorist", False): "dururcasına",   # durur (-Ir): r→c, u(kalın), Iyi=ı DÜZ
    ("sanmak", "aorist", False): "sanırcasına",   # sanır (-Ir): r→c, ı(kalın), Iyi=ı

    # --- -mIş (evid) tabanı (base="evid", negative=False) ---
    ("gelmek", "evid", False): "gelmişçesine",    # gelmiş: ş(sert)→ç, son ünlü i(ince)→e, Iyi=i
    ("yapmak", "evid", False): "yapmışçasına",    # yapmış: ş→ç, son ünlü ı(kalın)→a, Iyi=ı
    ("gitmek", "evid", False): "gitmişçesine",    # gitmiş: ş→ç, i(ince), Iyi=i (yumuşama YOK: ünsüz-başlı)
    ("okumak", "evid", False): "okumuşçasına",    # okumuş: ş→ç, son ünlü u(kalın)→a, Iyi=ı DÜZ
    ("görmek", "evid", False): "görmüşçesine",    # görmüş: ş→ç, son ünlü ü(ince)→e, Iyi=i DÜZ
    ("gülmek", "evid", False): "gülmüşçesine",    # gülmüş: ş→ç, ü(ince)→e, Iyi=i DÜZ
    ("bakmak", "evid", False): "bakmışçasına",    # bakmış: ş→ç, ı(kalın)→a, Iyi=ı
    ("olmak", "evid", False): "olmuşçasına",      # olmuş: ş→ç, u(kalın)→a, Iyi=ı DÜZ

    # --- olumsuz aorist (base="aorist", negative=True) ---
    ("gelmek", "aorist", True): "gelmezcesine",   # gelmez: z(yumuşak)→c, son ünlü e(ince), Iyi=i
    ("yapmak", "aorist", True): "yapmazcasına",   # yapmaz: z→c, son ünlü a(kalın), Iyi=ı
    ("okumak", "aorist", True): "okumazcasına",   # okumaz: z→c, a(kalın), Iyi=ı
    ("almak", "aorist", True): "almazcasına",     # almaz: z→c, a(kalın), Iyi=ı
    ("görmek", "aorist", True): "görmezcesine",   # görmez: z→c, son ünlü e(ince), Iyi=i
}
