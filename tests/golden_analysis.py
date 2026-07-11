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
