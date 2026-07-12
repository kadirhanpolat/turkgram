# -cAsInA çözümleme golden (Faz 2b / motor-dışı biçim 1 — analiz).
# BAĞIMSIZ: motor-körü Opus ajanı yalnız spec/casina-spec.md + Türkçe dilbilgisiyle kurdu
# (turkgram/ görülmeden). Precision = TAM-küme eşitliği (analyze(surface, roots={lemma})).
# Segments = tek-çözümlü sade yüzeyler (olumsuz-aorist füzyon HARİÇ). Delegasyon: KÖK |
# [mA] | base-morfem(Ir/mIş) | cAsInA. Değer: (lemma,pos,kind,kanonik kwargs).

# (surface) -> [ {lemma, pos, kind, kwargs} ]
GOLDEN_CASINA = {
    # ---- aorist tabanı ----
    "gelircesine":  [{"lemma": "gelmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],
    "gülercesine":  [{"lemma": "gülmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],
    "yaparcasına":  [{"lemma": "yapmak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],
    "okurcasına":   [{"lemma": "okumak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # DÜZ ı (yuvarlak DEĞİL)
    "gidercesine":  [{"lemma": "gitmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # yumuşama tabandan
    "bakarcasına":  [{"lemma": "bakmak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],
    "alırcasına":   [{"lemma": "almak",  "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # -Ir istisna
    "görürcesine":  [{"lemma": "görmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # -Ir istisna, DÜZ i
    "bilircesine":  [{"lemma": "bilmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # -Ir istisna
    "dururcasına":  [{"lemma": "durmak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist"}}],  # -Ir istisna, yuvarlak→DÜZ ı
    # ---- evid (-mIş) tabanı ----
    "gelmişçesine": [{"lemma": "gelmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid"}}],
    "yapmışçasına": [{"lemma": "yapmak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid"}}],
    "gitmişçesine": [{"lemma": "gitmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid"}}],  # evid'de yumuşama YOK
    "okumuşçasına": [{"lemma": "okumak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid"}}],  # DÜZ ı
    "görmüşçesine": [{"lemma": "görmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid"}}],  # DÜZ i
    # ---- olumsuz ----
    "gelmezcesine":   [{"lemma": "gelmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist", "negative": True}}],
    "yapmazcasına":   [{"lemma": "yapmak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist", "negative": True}}],
    "okumazcasına":   [{"lemma": "okumak", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "aorist", "negative": True}}],
    "gelmemişçesine": [{"lemma": "gelmek", "pos": "verb", "kind": "converb_casina", "kwargs": {"base": "evid", "negative": True}}],
}

# (surface) -> {"lemma": ..., "segments": [(dilim, etiket), ...]}
GOLDEN_CASINA_SEGMENTS = {
    "gülercesine":  {"lemma": "gülmek", "segments": [("gül", "KÖK"), ("er", "Ir"), ("cesine", "cAsInA")]},
    "yaparcasına":  {"lemma": "yapmak", "segments": [("yap", "KÖK"), ("ar", "Ir"), ("casına", "cAsInA")]},
    "okurcasına":   {"lemma": "okumak", "segments": [("oku", "KÖK"), ("r", "Ir"), ("casına", "cAsInA")]},
    "gelmişçesine": {"lemma": "gelmek", "segments": [("gel", "KÖK"), ("miş", "mIş"), ("çesine", "cAsInA")]},
    "görmüşçesine": {"lemma": "görmek", "segments": [("gör", "KÖK"), ("müş", "mIş"), ("çesine", "cAsInA")]},
    "bakarcasına":  {"lemma": "bakmak", "segments": [("bak", "KÖK"), ("ar", "Ir"), ("casına", "cAsInA")]},
    "yapmışçasına": {"lemma": "yapmak", "segments": [("yap", "KÖK"), ("mış", "mIş"), ("çasına", "cAsInA")]},
    "gidercesine":  {"lemma": "gitmek", "segments": [("gid", "KÖK"), ("er", "Ir"), ("cesine", "cAsInA")]},
}

# Precision testi için lemma kümesi (roots): golden'daki tüm lemma'lar.
CASINA_LEXICON = frozenset(
    g["lemma"] for entries in GOLDEN_CASINA.values() for g in entries
)
