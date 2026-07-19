"""golden_ki_analysis.py — `-ki` aitlik eki analiz golden (motor-körü bağımsız golden).

Motordan BAĞIMSIZ kurulmuş, elle-doğrulanmış `-ki` (aitlik/ilgi eki) çözümleme
beklentileri. Beklenen analizler DİLBİLGİSİNDEN türetildi (Korkmaz, Türkiye Türkçesi
Grameri — Şekil Bilgisi, aitlik -ki kuralı); motora BAKILMADI.

Yeni kind: "with_ki" (SPEC `docs/superpowers/specs/2026-07-19-ki-aitlik-analizi-design.md`).

Doğrulama şablonu:
    result = analyze(surface, roots=roots)
    assert any(
        r.lemma == expected["lemma"]
        and r.kind == expected["kind"]
        and r.case == expected["case"]
        and getattr(r, "possessive", None) == expected.get("possessive")
        for r in result
    )

KRİTİK DİLBİLGİSİ DOĞRULAMASI (elle):
  1. `-ki` ÜNLÜ UYUMUNA UYMAZ (değişmez ek). Kalın-sıralı köklerde bile düz "ki"
     kalır: masa+da+ki = masadaki (masadakı DEĞİL), kapı+da+ki = kapıdaki,
     yol+da+ki = yoldaki (yoldakı DEĞİL). Bu, Türkçenin sistematik ünlü uyumu
     istisnalarından biridir → her loc/gen vakasında düz "ki" doğrulandı.
  2. YALNIZ Kİ_ROUND (bugün/dün/gün/öbür) yuvarlak "-kü" alır ve durum ekini ATLAR:
     bugün+kü = bugünkü, dün+kü = dünkü. SPEC §3.3: bu yüzeyler yine kind=with_ki,
     case=loc etiketlenir (base decline'a eşlenmez).
  3. gen -ki: kişi zamirleri düzensiz tamlayan alır → ben→benim, sen→senin, o→onun.
     lemma daima KÖK'tür (ben/sen/o), yüzey biçim (benim/senin/onun) DEĞİL.
  4. loc eki allomorfları: ünlü/sedalı-ünsüz sonrası -de/-da; sert-ünsüz sonrası
     -te/-ta. AMA -ki her zaman düz (bu golden'da tabanlar sedalı/ünlü-final; loc = -de/-da).
"""

# --- loc -ki (bulunma durumu + -ki) ---------------------------------------
# base = decline(kök, case="loc"); yüzey = base + "ki". case=loc, possessive yok.
# -ki değişmez: kalın köklerde bile düz "ki" (masadakı DEĞİL masadaki).
GOLDEN_KI_LOC: list[dict] = [
    {"surface": "evdeki", "roots": {"ev"}, "lemma": "ev",
     "kind": "with_ki", "case": "loc"},            # ev + de + ki
    {"surface": "masadaki", "roots": {"masa"}, "lemma": "masa",
     "kind": "with_ki", "case": "loc"},            # masa + da + ki (ünlü-final → -da; düz ki)
    {"surface": "kapıdaki", "roots": {"kapı"}, "lemma": "kapı",
     "kind": "with_ki", "case": "loc"},            # kapı + da + ki (kalın; düz ki, kapıdakı DEĞİL)
    {"surface": "okuldaki", "roots": {"okul"}, "lemma": "okul",
     "kind": "with_ki", "case": "loc"},            # okul + da + ki (l sedalı → -da; düz ki)
    {"surface": "yoldaki", "roots": {"yol"}, "lemma": "yol",
     "kind": "with_ki", "case": "loc"},            # yol + da + ki (kalın+sedalı; düz ki, yoldakı DEĞİL)
]

# --- gen -ki (tamlayan durumu + -ki) --------------------------------------
# base = decline(kök, case="gen"); yüzey = base + "ki". case=gen.
# Kişi zamirleri düzensiz tamlayan: ben→benim, sen→senin, o→onun.
# lemma KÖK'tür (ben/sen/o), yüzey biçim DEĞİL.
GOLDEN_KI_GEN: list[dict] = [
    {"surface": "benimki", "roots": {"ben"}, "lemma": "ben",
     "kind": "with_ki", "case": "gen"},            # ben → benim + ki
    {"surface": "seninki", "roots": {"sen"}, "lemma": "sen",
     "kind": "with_ki", "case": "gen"},            # sen → senin + ki
    {"surface": "onunki", "roots": {"o"}, "lemma": "o",
     "kind": "with_ki", "case": "gen"},            # o → onun + ki
]

# --- Kİ_ROUND (-kü; durum eki atlanır) ------------------------------------
# bugün/dün gibi zaman sözcükleri: kök + "k" + yüksek-yuvarlak ünlü ("ü") → -kü.
# Durum eki YOK. SPEC §3.3: kind=with_ki, case=loc etiketlenir (base decline'a
# eşlenmez; segmentasyon güvenli geri-düşüş).
GOLDEN_KI_ROUND: list[dict] = [
    {"surface": "bugünkü", "roots": {"bugün"}, "lemma": "bugün",
     "kind": "with_ki", "case": "loc"},            # bugün + kü (yuvarlak; loc atlanır ama case=loc)
    {"surface": "dünkü", "roots": {"dün"}, "lemma": "dün",
     "kind": "with_ki", "case": "loc"},            # dün + kü (dünki DEĞİL — Kİ_ROUND yuvarlak)
]

# --- İyelikli taban + -ki (possessive 3sg) --------------------------------
# iç → iç + i (iyelik 3.tekil) + n (kaynaştırma) + de (bulunma) = içinde;
# içinde + ki = içindeki. case=loc, possessive=3sg.
GOLDEN_KI_POSSESSIVE: list[dict] = [
    {"surface": "içindeki", "roots": {"iç"}, "lemma": "iç",
     "kind": "with_ki", "case": "loc", "possessive": "3sg"},  # iç+i+n+de+ki
]

# --- Belirsizlik / not vakası ---------------------------------------------
# "sonraki" = sonra + ki. Dilbilgisel olarak "sonra" (zarf/edat) ünsüz-final
# DEĞİL, ünlü-final (a). Bu nedenle base'i kesin bir durum ekine oturtmak
# belirsizdir: klasik betimleme "sonra"yı loc/gen'siz doğrudan +ki alan donmuş
# bir öğe sayar (zaman zarfı). Motorun oracle'ı hangi (case) hipoteziyle
# "sonraki" üretiyorsa o çözülür → case'inden EMİN OLMADIĞIMIZDAN çekirdek
# golden'a KOYMUYORUZ (recall-güvenli belirsizlik, SPEC §4 "oracle neyi
# üretiyorsa o çözülür"). Referans amaçlı ayrı liste; test bunu opsiyonel
# tutabilir (case doğrulamadan yalnız with_ki + lemma).
GOLDEN_KI_AMBIGUOUS: list[dict] = [
    # case KASITLI OLARAK belirtilmedi (yukarıdaki nota bkz.); yalnız kind+lemma.
    {"surface": "sonraki", "roots": {"sonra"}, "lemma": "sonra",
     "kind": "with_ki"},
]

# --- Negatif vaka (marker filtresi) ---------------------------------------
# k[ıiuü]$ ile BİTMEYEN yüzey → with_ki enumerate EDİLMEMELİ.
# "kirli" sonu "li" (k[ıiuü]$ değil) → hiçbir with_ki analizi dönmemeli.
GOLDEN_KI_NEGATIVE: list[str] = [
    "kirli",    # -li ile biter, -ki marker'ı yok
    "araba",    # -ba ile biter, k-marker yok
]

# Tüm pozitif vakalar (with_ki dönmesi BEKLENEN).
GOLDEN_KI_ALL: list[dict] = (
    GOLDEN_KI_LOC + GOLDEN_KI_GEN + GOLDEN_KI_ROUND + GOLDEN_KI_POSSESSIVE
)
