"""golden_unlu_dusme.py — Ünlü düşmesi (drops_vowel) çekim golden testleri.

MOTOR-KÖRÜ bağımsız golden: elle-doğrulanmış dilbilgisel biçimler.
Motor kaynağına (morphology_noun/morphology/analysis) BAKILMADAN, yalnızca
SPEC (`docs/superpowers/specs/2026-07-19-unlu-dusme-kapsam-design.md`) + Türkçe
ünlü-düşmesi (haplology) grameri (Korkmaz §3.3, TDK) esas alınarak kuruldu.

KİLİT KURALLAR (elle doğrulama):
  1. Ünlü düşmesi YALNIZ ünlü-BAŞLI ek önünde olur:
     - acc  -(y)I  (ünlü-başlı → DÜŞER)      : omuz → omzu
     - poss3sg -(s)I (ünlü-başlı → DÜŞER)     : omuz → omzu
     - dat  -(y)A  (ünlü-başlı → DÜŞER)       : omuz → omza
  2. Ünsüz-BAŞLI ek önünde DÜŞMEZ (tam kök korunur):
     - abl  -DAn   (ünsüz-başlı → DÜŞMEZ)     : omuz → omuzdan
     - loc  -DA    (ünsüz-başlı → DÜŞMEZ)     : omuz → omuzda
     - pl   -lAr   (ünsüz-başlı → DÜŞMEZ)     : omuz → omuzlar
  3. Harmoni: düşme sonrası KALAN gövdenin ön/arka + düz/yuvarlaklığına göre ek.
     AMA disharmonik alıntılarda (haciz/kavim/nakil) arka-ünlü yazımlı gövde
     ÖN-ünlülü ek alır: nakil → nakli (naklı DEĞİL), haciz → haczi, kavim → kavmi.
  4. Düşme + ünsüz yumuşaması birlikte olabilir:
     - kayıt → kaydı (t → d + son-hece ünlüsü düşer).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UNLU_DUSME_CASES — DÜŞEN sözcükler (her biri elle-doğrulanmış).
#   acc / poss3sg / dat  → ünlü-başlı ek → DÜŞER.
#   abl                  → ünsüz-başlı ek → DÜŞMEZ (tam kök; regresyon).
# ---------------------------------------------------------------------------
UNLU_DUSME_CASES: list[dict] = [
    # --- §2.1 harmonik düşme (kalan gövdeye normal ünlü uyumu) ---
    {"lemma": "omuz",  "acc": "omzu",  "poss3sg": "omzu",  "dat": "omza",  "abl": "omuzdan"},
    {"lemma": "zihin", "acc": "zihni", "poss3sg": "zihni", "dat": "zihne", "abl": "zihinden"},
    # lütuf ERTELENDİ (ters-disharmonik: lütfu/lütfunu arka ama kalan ünlü ü ön; motor
    # kalan-ünlüden lütfü üretir — back-harmony override yok). SUPHELI'de değil, kapsam dışı.
    {"lemma": "ilim",  "acc": "ilmi",  "poss3sg": "ilmi",  "dat": "ilme",  "abl": "ilimden"},
    {"lemma": "beniz", "acc": "benzi", "poss3sg": "benzi", "dat": "benze", "abl": "benizden"},
    {"lemma": "hışım", "acc": "hışmı", "poss3sg": "hışmı", "dat": "hışma", "abl": "hışımdan"},
    {"lemma": "kahır", "acc": "kahrı", "poss3sg": "kahrı", "dat": "kahra", "abl": "kahırdan"},
    {"lemma": "kavis", "acc": "kavsi", "poss3sg": "kavsi", "dat": "kavse", "abl": "kavisten"},
    {"lemma": "kibir", "acc": "kibri", "poss3sg": "kibri", "dat": "kibre", "abl": "kibirden"},
    {"lemma": "kutur", "acc": "kutru", "poss3sg": "kutru", "dat": "kutra", "abl": "kuturdan"},
    {"lemma": "nabız", "acc": "nabzı", "poss3sg": "nabzı", "dat": "nabza", "abl": "nabızdan"},
    {"lemma": "remiz", "acc": "remzi", "poss3sg": "remzi", "dat": "remze", "abl": "remizden"},
    {"lemma": "sadır", "acc": "sadrı", "poss3sg": "sadrı", "dat": "sadra", "abl": "sadırdan"},
    {"lemma": "şahıs", "acc": "şahsı", "poss3sg": "şahsı", "dat": "şahsa", "abl": "şahıstan"},
    {"lemma": "vecih", "acc": "vechi", "poss3sg": "vechi", "dat": "veche", "abl": "vecihten"},

    # --- §2.1 düşme + ünsüz yumuşaması (t → d) ---
    #   kayıt: son-hece ünlüsü (ı) düşer + kök-sonu t → d (kayd-).
    #   acc kaydı, dat kayda; abl ünsüz-başlı → düşme YOK, yumuşama YOK (kayıttan).
    {"lemma": "kayıt", "acc": "kaydı", "poss3sg": "kaydı", "dat": "kayda", "abl": "kayıttan"},

    # --- §2.2 disharmonik alıntılar (drops + ÖN-ünlü ek; arka-ünlü gövde) ---
    #   nakil → nakli (naklı DEĞİL); haciz → haczi; kavim → kavmi.
    #   dat de ön-ünlü: nakle/hacze/kavme. abl ünsüz-başlı → DÜŞMEZ (tam kök).
    {"lemma": "haciz", "acc": "haczi", "poss3sg": "haczi", "dat": "hacze", "abl": "hacizden"},
    {"lemma": "kavim", "acc": "kavmi", "poss3sg": "kavmi", "dat": "kavme", "abl": "kavimden"},
    {"lemma": "nakil", "acc": "nakli", "poss3sg": "nakli", "dat": "nakle", "abl": "nakilden"},
]

# ---------------------------------------------------------------------------
# UNLU_DUSME_SUPHELI — motor-körü emin OLAMADIĞIM biçimler.
#   Her giriş: elle-doğrulanabilen alan(lar) + neden şüpheli açıklaması.
#   Bunlar CASES'e KOYULMADI (motor-körülük gereği yalnız emin olduklarım CASES'te).
# ---------------------------------------------------------------------------
UNLU_DUSME_SUPHELI: list[dict] = [
    # kabir: SPEC §2.1 acc=kabri veriyor (arka 'a'ya rağmen ön-ünlü 'i').
    #   acc EMİN (SPEC doğrudan). dat için kabre mi kabra mı? SPEC söylemiyor;
    #   kabir Arapça alıntı, geleneksel çekimde 'kabre' (ön-ünlü) beklenir ama
    #   arka-ünlü gövdeden 'kabra' da mümkün → dat/poss belirsiz bıraktım.
    {"lemma": "kabir", "acc": "kabri", "abl": "kabirden",
     "not": "acc=kabri SPEC-doğrulanmış; disharmonik gibi ön 'i'. dat kabre?/kabra? belirsiz → SUPHELI."},

    # nutuk: son-hece ünlüsü (u) düşer → nutk-. k kök-sonunda AMA önünde ünsüz (t)
    #   → ünlü-başlı ekte k normalde ğ'ye yumuşar; ancak nutk- kümesinde k
    #   ünsüz-sonrası olduğu için ğ'ye GİTMEZ (nutku, nutku değil nutğu DEĞİL).
    #   SPEC §2.1 acc=nutku veriyor → acc EMİN. dat 'nutka' beklenir ama k/ğ
    #   etkileşimi + düşme birleşimi tam emin değilim → SUPHELI.
    {"lemma": "nutuk", "acc": "nutku", "abl": "nutuktan",
     "not": "acc=nutku SPEC-doğrulanmış (k, önünde ünsüz → ğ yok). dat nutka? k/ğ+düşme etkileşimi belirsiz → SUPHELI."},
]

# ---------------------------------------------------------------------------
# UNLU_DUSME_NEGATIVE — DÜŞMEYEN kontrol grubu (regresyon; false-drop yakalar).
#   Bu sözcükler ünlü-başlı ek (acc) alınca DÜŞMEZ (tam kök korunur).
#   SPEC §3: false-drop taraması — eklenen küme dışına düşme sıçraması OLMAMALI.
# ---------------------------------------------------------------------------
UNLU_DUSME_NEGATIVE: list[dict] = [
    {"lemma": "sınıf",  "acc": "sınıfı"},   # sınfı DEĞİL
    {"lemma": "gurur",  "acc": "gururu"},   # grutu/gururu; düşme YOK
    {"lemma": "şiir",   "acc": "şiiri"},    # şiri DEĞİL
    {"lemma": "sinir",  "acc": "siniri"},   # sinri DEĞİL
    {"lemma": "ölüm",   "acc": "ölümü"},    # ölmü DEĞİL
    {"lemma": "gövde",  "acc": "gövdeyi"},  # SPEC §3'te açıkça DIŞLANDI (düşmez)
    {"lemma": "kitap",  "acc": "kitabı"},   # YALNIZ yumuşama (p→b); ünlü düşmesi YOK
    {"lemma": "armut",  "acc": "armudu"},   # YALNIZ yumuşama (t→d); ünlü düşmesi YOK
]
