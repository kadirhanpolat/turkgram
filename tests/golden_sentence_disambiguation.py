# Cümle-bağlamı disambiguation golden (Faz 2b — kural-tabanlı sözdizimsel katman).
# BAĞIMSIZ: motor-körü Opus ajanı yalnız spec/sentence-disambiguation-spec.md + Türkçe
# dilbilgisiyle kurdu (turkgram/context.py görülmeden). Runner: tests/test_sentence_disambiguation.py.
# SPEC §4: golden = SIRA (top-1) testi, güven değeri DEĞİL.
#
# Üç aile:
#   1. CONTEXT_TOP1     — hedef token izole belirsiz, bağlam top-1'i KESİNLEŞTİRİR (K1..K5).
#   2. NO_CONTEXT_...   — kural ateşlemez → top-1 == izole disambiguation.rank top-1.
#   3. RECALL_...       — set(out[i]) == set(in[i]) (yalnız yeniden sıralama; silme/ekleme yok).
#
# Reconcile notları (dilbilimsel iddia değişmedi; yalnız kanonik-kwargs ifadesi + 1 açık-takası):
#   - nom/question=False DEFAULT olarak kanonik kwargs'tan ATILIR → beklenen alt-küme {}.
#   - "benim için" (gen yönetimi); "bunun için" dilbilimsel geçerli ama analizör "bunun"u
#     lemma "bun"a çözer (bu'nun düzensiz n-kaynaşmalı tamlayanı — önceden var olan zamir
#     açığı, bu katmana özgü DEĞİL) → temiz örnekle değiştirildi.

# --- AİLE 1: (tokens, hedef_indeks, beklenen_lemma, beklenen_kind, beklenen_kwargs_alt_küme)
CONTEXT_TOP1 = [
    # ---- K1: niteleyici + ad → i nominal (fiil-kind aleyhte) ----
    (["üç", "gelin"], 1, "gelin", "decline", {}),          # sayı → İSİM (gelmek-emir değil)
    (["beş", "yaz"], 1, "yaz", "decline", {}),             # sayı sözcüğü → yaz mevsimi
    (["kırmızı", "gül"], 1, "gül", "decline", {}),         # sıfat → çiçek (gülmek değil)
    (["her", "kız"], 1, "kız", "decline", {}),             # miktar belirteci → kız (kızmak değil)
    (["iki", "yüz"], 1, "yüz", "decline", {}),             # sayı → yüz (isim)

    # ---- K2: edat yönetimi → i belirli DURUM'da nominal ----
    (["okula", "doğru"], 0, "okul", "decline", {"case": "dat"}),   # doğru → dat
    (["senden", "önce"], 0, "sen", "decline", {"case": "abl"}),    # önce → abl (suppletif zamir)
    (["benden", "sonra"], 0, "ben", "decline", {"case": "abl"}),   # sonra → abl
    (["benim", "için"], 0, "ben", "decline", {"case": "gen"}),     # için → gen (zamir)
    (["ev", "kadar"], 0, "ev", "decline", {}),                     # kadar → nom (kanonik {})

    # ---- K3: ayrı soru parçacığı mI → i question=False (kanonik olarak atılır) ----
    (["geldi", "mi"], 0, "gelmek", "conjugate", {}),
    (["gördün", "mü"], 0, "görmek", "conjugate", {"tense": "past", "person": "2sg"}),
    (["yazdın", "mı"], 0, "yazmak", "conjugate", {"tense": "past", "person": "2sg"}),

    # ---- K4: özne–yüklem kişi uyumu → i fiil, person zamirle uyumlu ----
    (["ben", "geldim"], 1, "gelmek", "conjugate", {"person": "1sg"}),
    (["ben", "öğretmenim"], 1, "öğretmen", "copula", {"person": "1sg"}),  # ad yüklemi (copula), K4 copula'ya da uygulanır
    (["siz", "gelirsiniz"], 1, "gelmek", "conjugate", {"person": "2pl"}),
    (["biz", "yazdık"], 1, "yazmak", "conjugate", {"person": "1pl"}),
    (["sen", "gülersin"], 1, "gülmek", "conjugate", {"person": "2sg"}),

    # ---- K5: tamlayan–iyelik uyumu → i nominal, possessive uyumlu ----
    (["benim", "evim"], 1, "ev", "decline", {"possessive": "1sg"}),
    (["senin", "kızın"], 1, "kız", "decline", {"possessive": "2sg"}),
    (["evin", "kapısı"], 1, "kapı", "decline", {"possessive": "3sg"}),   # ad+gen → 3sg
    (["onların", "evi"], 1, "ev", "decline", {"possessive": "3sg"}),     # 3pl tamlayan → 3sg iyelik

    # ---- Çoklu kural (K1+K5): güzel(sıfat)+benim(1sg tamlayan) → ev 1sg ----
    (["benim", "güzel", "evim"], 2, "ev", "decline", {"possessive": "1sg"}),
]

# --- AİLE 2: kural ateşlemeyen cümleler (komşu niteleyici/edat/zamir/parçacık YOK)
NO_CONTEXT_SENTENCES = [
    ["çocuklar", "geldi"],
    ["kitaplar", "masada"],
    ["öğrenci", "yazdı"],
    ["kuşlar", "uçtu"],
]

# --- AİLE 3: recall-güvenlik (Aile 1 belirsiz cümlelerinden)
RECALL_SENTENCES = [
    ["üç", "gelin"],
    ["okula", "doğru"],
    ["ben", "geldim"],
    ["benim", "güzel", "evim"],
    ["geldi", "mi"],
]
