"""golden_turetme_cekim.py — türetilmiş gövde + çekim istifi ÇÖZÜMLEMESİ golden.

Motor-körü bağımsız golden. Beklenen çözümlemeler DİLBİLGİSİNDEN elle türetildi
(Korkmaz, Türkiye Türkçesi Grameri — Şekil Bilgisi; yapım ekleri + çekim ekleri
sıralaması); MOTORA BAKILMADI (`analysis.py`/`analysis_candidates.py`/`derivation.py`/
`morphology_noun.py` GÖRÜLMEDİ). SPEC: `docs/superpowers/specs/2026-07-19-turetme-cekim-istif-design.md`.

Konu: Türkçe yapım ekleriyle türetilmiş bir gövde (leksikonda lemma DEĞİL, örn.
"bencillik") çekim eki (durum/iyelik/çoğul) alabilir → tek `kind="derivation"` analizi.

Doğrulama şablonu:
    result = analyze(surface, roots=roots)
    assert any(
        r.lemma == expected["lemma"]
        and r.kind == expected["kind"]
        and getattr(r, "case", None) == expected.get("case")
        and getattr(r, "possessive", None) == expected.get("possessive")
        and getattr(r, "number", None) == expected.get("number")
        for r in result
    )

KİLİT KARARLAR (elle-doğrulanmış):
  * chain YÖNÜ = EN DERİN kök → yüzeye doğru türetilmiş gövde:
    ["ben", "bencil", "bencillik"] (ben=kök, bencil=ben+cil sıfat, bencillik=bencil+lik isim).
  * lemma DAİMA EN DERİN kök (ben/ev/spor/göz) — türetilmiş gövde (bencillik) DEĞİL.
  * roots yalnız EN DERİN kökü içerir ({"ben"}); ara türetilmiş gövde (bencillik) KÖK
    DEĞİL → roots'a KONMAZ.
  * Çekimsiz anahtar (case/possessive/number) → dict'e KONMAZ (§4 nom/None/sg atılır).

KRİTİK MORFOFONOLOJİ (elle doğrulandı):
  1. Yumuşama k→ğ YALNIZ ünlü-başlı ek önünde:
       bencillik + i(acc)          → bencilliği     (bencilliki DEĞİL)
       evsizlik  + i(poss3sg)      → evsizliği...   (k→ğ; sonra +n+i)
       gözlükçülük + ü(acc)        → gözlükçülüğü   (k→ğ)
     Ünsüz-başlı ek önünde tetiklenmez:
       bencillik + ler(pl)         → bencillikler   (k KORUNUR; -ler ünsüz-başlı)
  2. Çekim eki SIRASI: çoğul(-lAr) → iyelik(-(s)I) → durum(-DAn/-(n)In...):
       bencillik + ler + i + n + den = bencilliklerinden
       (pronominal kaynaştırma -n- iyelik ile durum arasında).
  3. İyelik 3.tekil + durum arasında kaynaştırma -n-:
       evsizlik + i(poss3sg) + n + i(acc) = evsizliğini.
  4. Ünlü uyumu:
       bencillik (ince/düz) → +i(acc), +i(poss), +ler(pl), +in→ ...den(abl, e/düz taraf).
       sporcu (kalın/yuvarlak son ünlü u) → +lar(pl), +ın(gen).
       gözlükçülük (ince/yuvarlak) → +ü(acc).
"""

# --- Ana vakalar: türetilmiş gövde + çekim istifi -------------------------
# Her biri elle-doğrulanmış; lemma = en derin kök, chain = [en_derin, ..., türetilmiş_gövde].
TURETME_CEKIM_CASES: list[dict] = [
    # ben + cil + lik + i(acc); bencillik + i → k→ğ → bencilliği
    {
        "surface": "bencilliği",
        "roots": {"ben"},
        "lemma": "ben",
        "kind": "derivation",
        "chain": ["ben", "bencil", "bencillik"],
        "case": "acc",
    },
    # ev + siz + lik + i(poss3sg) + n + i(acc); k→ğ önce iyelik-i önünde → evsizliğini
    {
        "surface": "evsizliğini",
        "roots": {"ev"},
        "lemma": "ev",
        "kind": "derivation",
        "chain": ["ev", "evsiz", "evsizlik"],
        "possessive": "3sg",
        "case": "acc",
    },
    # ben + cil + lik + ler(pl) + i(poss3sg) + n + den(abl)
    # -ler ünsüz-başlı → k KORUNUR (bencillikler); sonra +i+n+den → bencilliklerinden
    {
        "surface": "bencilliklerinden",
        "roots": {"ben"},
        "lemma": "ben",
        "kind": "derivation",
        "chain": ["ben", "bencil", "bencillik"],
        "number": "pl",
        "possessive": "3sg",
        "case": "abl",
    },
    # spor + cu(isim) + lar(pl) + ın(gen); tek türetme katmanı + çekim → sporcuların
    {
        "surface": "sporcuların",
        "roots": {"spor"},
        "lemma": "spor",
        "kind": "derivation",
        "chain": ["spor", "sporcu"],
        "number": "pl",
        "case": "gen",
    },
]

# --- AMBIGUOUS: çok-katmanlı (3 türetme katmanı) + çekim -------------------
# gözlükçülüğü = göz → gözlük → gözlükçü → gözlükçülük + ü(acc); k→ğ → gözlükçülüğü.
# Zincir 3 türetme katmanı içerir (göz+lük, +çü, +lük). SPEC §7 V1 kapsam dışı olabilir
# (`gözlükçülük` saf çok-katmanlı ZATEN çalışıyor der; ama +çekim istifi bu feature).
# Zincir derinliği / motor max_depth belirsizliği nedeniyle AMBIGUOUS listeye alındı:
# test bunu opsiyonel tutabilir (yalnız kind+lemma+case doğrula, chain'e katı bağlanma).
TURETME_CEKIM_AMBIGUOUS: list[dict] = [
    {
        "surface": "gözlükçülüğü",
        "roots": {"göz"},
        "lemma": "göz",
        "kind": "derivation",
        "chain": ["göz", "gözlük", "gözlükçü", "gözlükçülük"],
        "case": "acc",
    },
]

# --- REGRESYON: çekimsiz saf türetme (bu feature'ı TETİKLEMEMELİ) ----------
# Saf çok-katmanlı türetme ZATEN çalışıyor (Faz A). Çekim eki YOK → yalnız saf
# türetme analizi dönmeli; case/possessive/number ANAHTARI YOK (çekimsiz).
# Bu feature (türetme+çekim istifi) burada bir çekim ekseni ÜRETMEMELİ.
TURETME_CEKIM_REGRESSION: list[dict] = [
    # ben + cil + lik = bencillik (çekimsiz saf türetme; case/poss/number YOK)
    {
        "surface": "bencillik",
        "roots": {"ben"},
        "lemma": "ben",
        "kind": "derivation",
        "chain": ["ben", "bencil", "bencillik"],
    },
    # ev + siz + lik = evsizlik (çekimsiz saf türetme; case/poss/number YOK)
    {
        "surface": "evsizlik",
        "roots": {"ev"},
        "lemma": "ev",
        "kind": "derivation",
        "chain": ["ev", "evsiz", "evsizlik"],
    },
]

# --- NEGATİF: saf çekim (türetme YOK → türetme+çekim istifi ÜRETMEZ) -------
# "evler" = ev + ler(pl) yalnızca çekimdir; hiçbir yapım eki yok → derivation+çekim
# istifi analizi DÖNMEMELİ. Saf isim-çekimi (kind="decline") beklenir; bu feature'ın
# kind="derivation" + çekim ekseni sonucu ÜRETMEMESİ doğrulanır.
TURETME_CEKIM_NEGATIVE: list[dict] = [
    {
        "surface": "evler",
        "roots": {"ev"},
        # Bu yüzey için kind="derivation" + case/possessive/number DÖNMEMELİ.
        # (saf çekim; türetme katmanı yok)
        "forbidden_kind": "derivation",
    },
]

# Tüm pozitif (türetme+çekim istifi dönmesi BEKLENEN) — ambiguous dahil.
TURETME_CEKIM_ALL: list[dict] = TURETME_CEKIM_CASES + TURETME_CEKIM_AMBIGUOUS
