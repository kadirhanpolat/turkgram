# SPEC — Olasılıksal disambiguation (aday sıralama), Faz 2b

Ana oturum tarafından elle yazılmış **tasarım değişmezi**. `analyze` bir yüzey için birden
çok çözümleme döndürebilir (ör. `yüzü` → iyelik/belirtme; `gelin` → fiil/isim). Bu modül
(`turkgram/disambiguation.py`) adayları **olabilirlik sırasına** koyar ve normalize güven
(olasılık) verir. Kaynak: dilbilimsel öncelik + opsiyonel sıklık; Korkmaz düzyazısı YOK (#3).

## 0. Değişmez sözleşme (KRİTİK)

- **OPT-IN, geriye-uyumlu:** `analyze` imzası/sırası DEĞİŞMEZ (SPEC analiz §8; `_sort_key`
  deterministik sırası korunur). Sıralamayı isteyen ayrı fonksiyon çağırır:
  `rank(analyze(...), freq=…, pos=…)`. Motor/golden'a dokunulmaz.
- **Girdi mutasyonu YOK** (immutability): `rank`/`disambiguate` yeni liste döndürür, Analysis
  nesnelerini değiştirmez.
- **freq=None → sıklık terimi ETKİSİZ**; sıralama tümüyle dilbilimsel önceliklere düşer
  (deterministik, veri-bağımsız). Sıklık tablosu sonradan kırılmadan takılır.

## 1. Sıralama anahtarı (best-first = artan tuple sırası)

```
_rank_key(a) = (
    -freq_score(a.lemma),          # sıklık ağırlığı (freq yoksa 0 → etkisiz)
    -pos_consistency(a),           # +1 tutarlı / 0 bilinmiyor / -1 tutarsız
    -kind_prior(a.kind),           # yalın-biçim izole sıklık önceliği
    len(a.segments),               # morfem ekonomisi (az morfem önce; Occam)
    _sort_key(a),                  # mevcut deterministik tiebreak (üretilebilir sıra)
)
```

Lexicographic öncelik: **sıklık > POS-tutarlılık > kind-önceliği > morfem-ekonomisi >
deterministik tiebreak**. Her terim bir öncekini yalnız EŞİTLİKTE böler → şeffaf, test-edilebilir.

### 1.1 `freq_score(lemma)`
`freq` (Mapping[str,float]) verilmişse `freq.get(lemma, 0.0)`; verilmemişse 0.0. Çağıran ham
sayım, log-sayım ya da ters-rütbe geçebilir (yüksek = daha olası). Terim yalnız EŞİT-lemma
değil, FARKLI-lemma adaylarını da ayırır (ör. `gelin`: `gelmek` vs `gelin` sıklığı).

### 1.2 `pos_consistency(a)` — leksikon POS'undan
Fiil-kind'ları = {conjugate, converb, participle}; nominal-kind'ları = {decline, copula}.
`pos` (lemma→POS map/callable) verilmişse:
- lemma POS'u bilinmiyor (map'te yok; ör. birleşik fiil, leksikon-dışı) → **0**.
- POS = `verb` → kind fiil-kind'ıysa **+1**, değilse **−1**.
- POS ∈ nominal {noun,adj,adv,pron,num,…} → kind nominal-kind'ıysa **+1**, değilse **−1**.
`pos=None` → tüm adaylar için 0 (POS sinyali yok). Kolaylık: çağıran `lexicon.pos_map()` geçer.

### 1.3 `kind_prior(kind)` — yalın-biçim izole önceliği
İzole (bağlamsız) bir yüzeyde yalın çekim biçimleri fiilimsilerden daha olası (dilbilimsel
yargı; sıklık gelince bu prior sıklığın gölgesinde kalır):
`decline=2, conjugate=2, copula=1, participle=0, converb=0`. Bilinmeyen kind → 0.

## 2. Güven (olasılık) — `disambiguate`
`disambiguate(analyses, freq, pos) -> [(Analysis, güven), …]` best-first sıralı; güven ∈ [0,1],
toplam ≈ 1 (softmax). Skaler ham puan (yalnız güven için; SIRA §1 tuple'ından gelir):
```
raw(a) = 100·log1p(freq_score) + 10·pos_consistency + 3·kind_prior − 1·len(segments)
güven  = softmax(raw)   # küme üzerinde normalize
```
Güven yalnız gösterim/olasılık yorumu içindir; KESİN SIRA §1 anahtarındandır (float kırılganlığı
sıralamaya sızmaz). Tek aday → güven 1.0. Eşit ham puan → eşit güven.

## 3. Kapsam ve bağımsız golden
- **Golden = SIRA (order) testi**, güven değeri DEĞİL (float). Yalnız dilbilimsel olarak
  **kesin** çağrılabilen belirsiz yüzeylerde top-1 (ve gerekiyorsa tam sıra) beklenir; yakın
  çağrılar (aynı-lemma iyelik/belirtme, sıklıksız berabere) golden'a KONMAZ — deterministik
  tiebreak'e bırakılır (üretilebilir ama dilbilimsel iddia değil).
- **freq-override golden:** enjekte edilen `freq` ile top-1'in sıklık-lehine lemmaya döndüğü
  doğrulanır (kanca çalışıyor). Golden motoru görmeden, dilbilimsel yargıdan kurulur (#2 emsali).
- **Kapsam-dışı (sonraki artım):** gerçek bağlam (cümle) disambiguation; gömülü sıklık tablosu
  (bu artım freq'i PARAMETRE alır, veri gömmez). Motor-dışı biçimler.
