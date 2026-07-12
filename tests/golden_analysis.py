# Precision golden — çözümleyici (Faz 2a Task 2). HİBRİT yöntem:
# ground-truth = üreteci bilinen aday lemma'lar × TAM grid üzerinde brute-force koşarak
# kuruldu (analizöre BAĞIMSIZ: prefix/ünlü-yuvası mantığı kullanmaz, gerçek lemma'larda
# çalışır). Motor-körü Opus ajanı AYRICA bağımsız okuma listesi üretti (recall/tamlık
# denetimi) → uzlaştırıldı: audit'in kesin öngörüleriyle birebir + audit'in kaçırdığı 2
# gerçek üreteç-okuması eklendi (gitmeden ma-abl; gelin çatı-emir).
#
# TEST KULLANIMI: analyze(surface, roots=BATTERY_LEXICON) → TAM-küme eşitliği. roots
# filtresi çıplak-önek gürültüsünü eler (SPEC §8.1). Değer = (lemma,pos,kind,kanonik kwargs).
#
# case='nom'/number='sg'/possessive=None/aux=None/question=False/voice_chain=() daima atılır
# (kanonik, SPEC §6). Korkmaz düzyazısı/örneği YOK (#3); biçimler elle-doğrulanmış üretimden.

GOLDEN_ANALYSIS = {
    'okuyor': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '3sg'}},
    ],
    'geldi': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'yapacak': [
        {'lemma': 'yapmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '3sg'}},
        {'lemma': 'yapmak', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'acak'}},
    ],
    'gelmiş': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'evid', 'person': '3sg'}},
    ],
    'gelse': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'cond', 'person': '3sg'}},
    ],
    'gelmeli': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'necess', 'person': '3sg'}},
    ],
    'gelir': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'aorist', 'person': '3sg'}},
    ],
    'gidiyor': [
        {'lemma': 'gitmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '3sg'}},
    ],
    'yiyecek': [
        {'lemma': 'yemek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '3sg'}},
        {'lemma': 'yemek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'acak'}},
    ],
    'okumadı': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True}},
    ],
    'okuyamadı': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True, 'ability': True}},
    ],
    'gelmedi': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True}},
    ],
    'dövüştürüldü': [
        {'lemma': 'dövmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'voice_chain': ['recip', 'caus', 'pass']}},
    ],
    'yaptırdı': [
        {'lemma': 'yapmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'voice_chain': ['caus']}},
    ],
    'geliyor musun': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '2sg', 'question': True}},
    ],
    'aday oldu': [
        {'lemma': 'aday olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'gelin': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'imp', 'person': '2sg', 'voice_chain': ['pass']}},
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'imp', 'person': '2sg', 'voice_chain': ['refl']}},
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'imp', 'person': '2pl'}},
        {'lemma': 'gelin', 'pos': 'noun', 'kind': 'decline', 'kwargs': {}},
    ],
    'evin': [
        {'lemma': 'ev', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '2sg'}},
        {'lemma': 'ev', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'case': 'gen'}},
    ],
    'okuma': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'imp', 'person': '2sg', 'negative': True}},
        {'lemma': 'okuma', 'pos': 'noun', 'kind': 'decline', 'kwargs': {}},
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'ma'}},
    ],
    'gelmem': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'aorist', 'person': '1sg', 'negative': True}},
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'ma', 'possessive': '1sg'}},
    ],
    'geldik': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '1pl'}},
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'dik'}},
    ],
    'yüzü': [
        {'lemma': 'yüz', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '3sg'}},
        {'lemma': 'yüz', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'case': 'acc'}},
    ],
    'evlerde': [
        {'lemma': 'ev', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'number': 'pl', 'case': 'loc'}},
    ],
    'evime': [
        {'lemma': 'ev', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '1sg', 'case': 'dat'}},
    ],
    'kitabı': [
        {'lemma': 'kitap', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '3sg'}},
        {'lemma': 'kitap', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'case': 'acc'}},
    ],
    'arabası': [
        {'lemma': 'araba', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '3sg'}},
    ],
    'burnu': [
        {'lemma': 'burun', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'possessive': '3sg'}},
        {'lemma': 'burun', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'case': 'acc'}},
    ],
    'öğrenciydim': [
        {'lemma': 'öğrenci', 'pos': 'noun', 'kind': 'copula', 'kwargs': {'person': '1sg', 'aux': 'hikaye'}},
    ],
    'evde': [
        {'lemma': 'ev', 'pos': 'noun', 'kind': 'decline', 'kwargs': {'case': 'loc'}},
    ],
    'hastaymış': [
        {'lemma': 'hasta', 'pos': 'noun', 'kind': 'copula', 'kwargs': {'person': '3sg', 'aux': 'rivayet'}},
    ],
    'okuyunca': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'converb', 'kwargs': {'kind': 'inca'}},
    ],
    'giderek': [
        {'lemma': 'gitmek', 'pos': 'verb', 'kind': 'converb', 'kwargs': {'kind': 'arak'}},
    ],
    'gitmeden': [
        {'lemma': 'gitmek', 'pos': 'verb', 'kind': 'converb', 'kwargs': {'kind': 'madan'}},
        {'lemma': 'gitmek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'ma', 'case': 'abl'}},
    ],
    'okuduğum': [
        {'lemma': 'okumak', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'dik', 'possessive': '1sg'}},
    ],
    'geleceğini': [
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'acak', 'possessive': '2sg', 'case': 'acc'}},
        {'lemma': 'gelmek', 'pos': 'verb', 'kind': 'participle', 'kwargs': {'ptype': 'acak', 'possessive': '3sg', 'case': 'acc'}},
    ],
}
# Küratörlü leksikon: golden'daki tüm gerçek lemma'lar (roots filtresi).
BATTERY_LEXICON = {
    'okumak', 'gelmek', 'yapmak', 'gitmek', 'yemek', 'dövmek', 'aday olmak',
    'gelin', 'ev', 'okuma', 'yüz', 'kitap', 'araba', 'burun', 'öğrenci', 'hasta',
}

# ---------------------------------------------------------------------------
# Birleşik çok-token fiil (yardımcı fiille kurulan) — SPEC §8.2. HİBRİT değil:
# BAĞIMSIZ Opus ajanı motoru GÖRMEDEN, yalnız dilbilgisi + SPEC'ten türetti.
# TEST: analyze(surface, roots=COMPOUND_LEXICON) → TAM-küme eşitliği. Nominal önek
# DEĞİŞMEZ; yalnız SON kelime (yardımcı fiil) çekimli. Soru + ikileme kapsam-dışı (§8.2).
# Kritik morfofonoloji: et- ünlü-başlı ek önünde yumuşar (ediyor/edecek/eder) ama
# ünsüz-başlı önünde YOK (etti/etmiş/etmedi); ol-/kıl- değişmez; kat+tı→kattı.
# ---------------------------------------------------------------------------
GOLDEN_COMPOUND = {
    'göz ardı etti': [
        {'lemma': 'göz ardı etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'kabul ediyor': [
        {'lemma': 'kabul etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '3sg'}},
    ],
    'kabul ettim': [
        {'lemma': 'kabul etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '1sg'}},
    ],
    'yardım edecek': [
        {'lemma': 'yardım etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '3sg'}},
    ],
    'yardım ettiler': [
        {'lemma': 'yardım etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3pl'}},
    ],
    'merak etmiş': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'evid', 'person': '3sg'}},
    ],
    'terk etti': [
        {'lemma': 'terk etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'terk ettin': [
        {'lemma': 'terk etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '2sg'}},
    ],
    'merak etmedi': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True}},
    ],
    'kabul eder': [
        {'lemma': 'kabul etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'aorist', 'person': '3sg'}},
    ],
    'hasta oldu': [
        {'lemma': 'hasta olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'yok oldu': [
        {'lemma': 'yok olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'emin olmadı': [
        {'lemma': 'emin olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True}},
    ],
    'hasta oluyor': [
        {'lemma': 'hasta olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '3sg'}},
    ],
    'emin olacak': [
        {'lemma': 'emin olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '3sg'}},
    ],
    'yok olduk': [
        {'lemma': 'yok olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '1pl'}},
    ],
    'namaz kıldı': [
        {'lemma': 'namaz kılmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'göz önünde bulundurdu': [
        {'lemma': 'göz önünde bulundurmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'hesaba kattı': [
        {'lemma': 'hesaba katmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
    'yoluna koydu': [
        {'lemma': 'yoluna koymak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg'}},
    ],
}

# Küratörlü leksikon: tüm birleşik lemma'lar (roots filtresi, SPEC §8.1/§8.2).
COMPOUND_LEXICON = {
    'göz ardı etmek', 'kabul etmek', 'yardım etmek', 'merak etmek', 'terk etmek',
    'hasta olmak', 'yok olmak', 'emin olmak', 'namaz kılmak',
    'göz önünde bulundurmak', 'hesaba katmak', 'yoluna koymak',
}

# ---------------------------------------------------------------------------
# Birleşik çok-token fiil + SORU (SPEC §8.2). BAĞIMSIZ Opus ajanı motoru GÖRMEDEN
# türetti. Soru eki mI ayrı token, önceki kelimenin son ünlüsüne uyumlu (mı/mi/mu/mü).
# Şahıs yerleşimi: pres/fut/aorist → soru ekiNDEN sonra (ediyor musun); görülen geçmiş
# -DI → şahıs fiile bağlı, soru en sonda (ettim mi). TEST: roots=COMPOUND_Q_LEXICON,
# TAM-küme eşitliği (question=True okuması). Bu grup c99f3bf'te len>2→[] kesimi kalkınca
# yan-etkiyle açıldı; bu golden davranışı KİLİTLER (regresyon koruması).
# ---------------------------------------------------------------------------
GOLDEN_COMPOUND_Q = {
    'göz ardı etti mi': [
        {'lemma': 'göz ardı etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'question': True}},
    ],
    'kabul ediyor musun': [
        {'lemma': 'kabul etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '2sg', 'question': True}},
    ],
    'kabul ediyor muyum': [
        {'lemma': 'kabul etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '1sg', 'question': True}},
    ],
    'yardım edecek mi': [
        {'lemma': 'yardım etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '3sg', 'question': True}},
    ],
    'yardım edecek misin': [
        {'lemma': 'yardım etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'fut', 'person': '2sg', 'question': True}},
    ],
    'merak eder mi': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'aorist', 'person': '3sg', 'question': True}},
    ],
    'merak eder misin': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'aorist', 'person': '2sg', 'question': True}},
    ],
    'merak etmiş mi': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'evid', 'person': '3sg', 'question': True}},
    ],
    'terk ettim mi': [
        {'lemma': 'terk etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '1sg', 'question': True}},
    ],
    'terk ettin mi': [
        {'lemma': 'terk etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '2sg', 'question': True}},
    ],
    'merak etmedi mi': [
        {'lemma': 'merak etmek', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True, 'question': True}},
    ],
    'hasta oldu mu': [
        {'lemma': 'hasta olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'question': True}},
    ],
    'hasta oluyor musun': [
        {'lemma': 'hasta olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'pres', 'person': '2sg', 'question': True}},
    ],
    'yok olduk mu': [
        {'lemma': 'yok olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '1pl', 'question': True}},
    ],
    'emin olmadı mı': [
        {'lemma': 'emin olmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'negative': True, 'question': True}},
    ],
    'namaz kıldı mı': [
        {'lemma': 'namaz kılmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'question': True}},
    ],
    'göz önünde bulundurdu mu': [
        {'lemma': 'göz önünde bulundurmak', 'pos': 'verb', 'kind': 'conjugate', 'kwargs': {'tense': 'past', 'person': '3sg', 'question': True}},
    ],
}

COMPOUND_Q_LEXICON = {
    'göz ardı etmek', 'kabul etmek', 'yardım etmek', 'merak etmek', 'terk etmek',
    'hasta olmak', 'yok olmak', 'emin olmak', 'namaz kılmak', 'göz önünde bulundurmak',
}
