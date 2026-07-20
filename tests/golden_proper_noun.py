'''golden_proper_noun.py — kural-tabanlı özel-ad etiketleme bağımsız golden.

Elle doğrulanmış (Türkçe imla + gazetteer kurallarından; SPEC §2).
SPEC: docs/superpowers/specs/2026-07-20-proper-noun-tagging-design.md.

Her eleman: {"text": <cümle>, "tags": [(surface, type, index), ...]}
- type ∈ {PER, LOC, ORG, PROPER}; index = 1-tabanlı token id.
- Beklenen YALNIZ özel adlar (ortak ad/küçük harf listelenmez).
'''

GOLDEN_PROPER = [
    # ── Gazetteer: PER / LOC / ORG (konumdan bağımsız) ─────────────────────
    {"text": "Ali geldi", "tags": [("Ali", "PER", 1)]},
    {"text": "Ayşe ile Fatma geldi", "tags": [("Ayşe", "PER", 1), ("Fatma", "PER", 3)]},
    {"text": "İstanbul güzeldi", "tags": [("İstanbul", "LOC", 1)]},
    {"text": "Ankara başkenttir", "tags": [("Ankara", "LOC", 1)]},
    {"text": "Türkiye Avrupa'da", "tags": [("Türkiye", "LOC", 1), ("Avrupa", "LOC", 2)]},
    {"text": "Fenerbahçe kazandı", "tags": [("Fenerbahçe", "ORG", 1)]},
    {"text": "Mehmet TBMM'de çalışıyor",
     "tags": [("Mehmet", "PER", 1), ("TBMM", "ORG", 2)]},

    # ── Apostrof-ek sinyali (ASCII ' böler → sağ parça atlanır) ────────────
    {"text": "Ali Ankara'ya gitti",
     "tags": [("Ali", "PER", 1), ("Ankara", "LOC", 2)]},
    # cümle-başı apostroflu OOV → PROPER (apostrof kesin sinyal)
    {"text": "Kadirhan'ın kitabı", "tags": [("Kadirhan", "PROPER", 1)]},

    # ── Cümle-içi büyük harf → PROPER (gazetteer dışı OOV) ─────────────────
    {"text": "Onu Kadirhan gördü", "tags": [("Kadirhan", "PROPER", 2)]},

    # ── Cümle-başı: ortak ad (leksikon) vs OOV ─────────────────────────────
    # Kitap = ortak ad (leksikon) → özel ad DEĞİL
    {"text": "Kitap masada", "tags": []},
    # Kadirhan = OOV → PROPER
    {"text": "Kadirhan geldi", "tags": [("Kadirhan", "PROPER", 1)]},

    # ── Negatif: küçük harf / ortak ad → boş ───────────────────────────────
    {"text": "çocuk uyudu", "tags": []},
    {"text": "kırmızı araba", "tags": []},
    {"text": "bugün hava güzel", "tags": []},
    # HAKEM HIGH: küçük-harf gazetteer homografı ortak ad (özel ad ZORUNLU büyük harf)
    {"text": "deniz mavi", "tags": []},        # deniz (ad) — Deniz(PER) değil
    {"text": "bahçede gül var", "tags": []},   # gül (çiçek/gülmek) — Gül(PER) değil
    {"text": "büyük kaya", "tags": []},        # kaya (taş) — Kaya(PER) değil
    # HAKEM MEDIUM: belgisiz/soru cümle-başı → özel ad değil
    {"text": "Kimi zaman gelir", "tags": []},
    {"text": "Herkes geldi", "tags": []},
    {"text": "Bazı çocuklar", "tags": []},

    # ── Homograf gazetteer (bilinçli LOC): Ordu/Van il ─────────────────────
    {"text": "Ordu güzel bir şehir", "tags": [("Ordu", "LOC", 1)]},

    # ── Çok-token varlık span (§10): bitişik + tip-uyumlu → tek span ────────
    {"text": "Mustafa Kemal Atatürk geldi",
     "tags": [("Mustafa Kemal Atatürk", "PER", 1)]},              # 3 PER/PROPER → tek PER
    {"text": "Ahmet Yılmaz aradı", "tags": [("Ahmet Yılmaz", "PER", 1)]},  # PER + PROPER caps
    {"text": "Ankara Üniversitesi büyük",
     "tags": [("Ankara Üniversitesi", "LOC", 1)]},                # LOC + PROPER → LOC (tipli emer)
    {"text": "Kadıköy Belediyesi açıldı",
     "tags": [("Kadıköy Belediyesi", "PROPER", 1)]},              # PROPER + PROPER → PROPER
    {"text": "Mustafa Kemalin evi", "tags": [("Mustafa Kemalin", "PER", 1)]},  # bitişik 2 PER
    # HAKEM HIGH — over-merge önleme (yön+tip-farkındalıklı emme):
    # LOC + keyfi PROPER (head-noun DEĞİL) → AYRI (Abajur emilmez)
    {"text": "Ankara Abajur geldi", "tags": [("Ankara", "LOC", 1), ("Abajur", "PROPER", 2)]},
    # PROPER (kişi OOV) + LOC → AYRI (Kadirhan Ankara farklı varlık)
    {"text": "Kadirhan Ankara geldi",
     "tags": [("Kadirhan", "PROPER", 1), ("Ankara", "LOC", 2)]},
    # NOT: tip-uyumsuz (`Ali Ankara'ya`→PER+LOC ayrı) + araya-token (`Ayşe ile Fatma`→ayrı)
    # vakaları yukarıda (bitişik-değil/farklı-tip birleşmez); merge onları DEĞİŞTİRMEZ.
]
