# SPEC — Cümle-bağlamı disambiguation (kural-tabanlı sözdizimsel katman), Faz 2b

Ana oturum tarafından elle yazılmış **tasarım değişmezi**. İzole (tek-kelime)
`disambiguation.rank` yalnız kelimenin kendi adaylarına bakar; belirsizlik bağlamdan
çözülür (ör. `gelin` yalın halde fiil~isim; ama `üç gelin` → isim, `içeri gelin` → fiil).
Bu modül (`turkgram/context.py`) bir cümlenin token'larını **komşuluk kanıtıyla** yeniden
sıralar. Kaynak: küratörlenmiş sözdizimsel bitişiklik/uyum/yönetim kuralları (Korkmaz,
*Türkiye Türkçesi Grameri — Şekil Bilgisi*); düzyazı/örnek KOPYALANMAZ (CLAUDE.md §3).

Bu **tam ayrıştırıcı DEĞİLDİR** (sözdizimi Faz 3/4'e defer). Yalnız yerel (±1 token, +
cümle-başı zamir) yüzeysel kanıttan yeniden sıralama yapar.

## 0. Değişmez sözleşme (KRİTİK)

- **OPT-IN, geriye-uyumlu:** `analyze` ve izole `disambiguation.rank`/`disambiguate`
  imza/davranışı DEĞİŞMEZ. Cümle sıralaması isteyen ayrı fonksiyon çağırır:
  `context.rank_in_context(tokens, analyses_per_token, …)`. Motor/analyze/golden'a dokunulmaz.
- **Girdi mutasyonu YOK** (immutability): yeni liste-listesi döndürülür; `Analysis`
  nesneleri ve girdi dizileri değiştirilmez.
- **Recall-güvenli — kural ADAY BUDAMAZ:** her kural yalnız pozitif/negatif KANIT ekler;
  aday listesinden hiçbir şey SİLİNMEZ. Kural hiç ateşlemezse → nötr → sıralama tümüyle
  izole `disambiguation._rank_key`'e düşer (deterministik, bağlam-bağımsız). Bu, analizör
  "ses filtreleri yalnız gereklilik" ilkesinin (analiz SPEC §Adım 2) sıralama karşılığıdır.
- **freq/pos yine PARAMETRE** (veri gömülmez): izole terime aynen geçirilir.

## 1. Arayüz

```
rank_in_context(
    tokens: Sequence[str],                       # yüzey token'ları (çağıran böler — tokenizasyon DIŞ)
    analyses_per_token: Sequence[Sequence[Analysis]],  # her token için analyze(...) çıktısı
    *, freq=None, pos=None,
) -> list[list[Analysis]]                         # her token için best-first yeniden sıralı YENİ liste
```

- `tokens` ve `analyses_per_token` aynı uzunlukta; `analyses_per_token[i]` = `tokens[i]` için
  `analyze(tokens[i], roots=…)` çıktısı. **Tokenizasyon + analyze ÇAĞIRANIN işi** (karar (a),
  sözdizimi defer). Uzunluk uyuşmazsa `ValueError`.
- Dönen `out[i]` = `analyses_per_token[i]` adaylarının yeniden sıralanmış YENİ listesi
  (aynı öğeler, silme/ekleme YOK — recall-güvenli).
- Boş aday listesi → boş liste (aynen geçer). Tek aday → tek öğe (sıralama etkisiz ama
  kanıt yine hesaplanabilir, gösterim için).

## 2. Sıralama anahtarı — bağlam izole'nin ÜSTÜNE biner

Token i'nin adayı `a` için best-first (artan tuple):

```
_context_key(a, i) = (
    -context_evidence(a, i, tokens, analyses_per_token),   # §3 sözdizimsel kanıt (int; yüksek=olası)
    *_rank_key(a, freq, pos),                               # izole tuple AYNEN (disambiguation §1)
)
```

Bağlam kanıtı **en yüksek öncelik**; eşitlikte izole anahtar (sıklık > POS > kind > morfem >
tiebreak) böler. `context_evidence` = 0 → tümüyle izole sıralama (geriye-uyum). Kanıt tam-sayı
tutulur (şeffaf, test-edilebilir; float sıralamaya sızmaz — disambiguation §2 emsali).

## 3. Kanıt kuralları (`context_evidence` = kural katkılarının toplamı)

Her kural token i'nin adayı `a`'ya, komşularına bakarak `+w` (destekler) / `−w` (aleyhte) /
`0` (ilgisiz) katkı verir. Kurallar **kapalı kelime listeleri** kullanır (leksikon-bağımsız,
deterministik). Ağırlıklar küçük tam-sayı; yönetim/uyum > yalın bitişikten güçlü.

**Kind aileleri** (disambiguation §1.2 ile aynı): fiil-kind = {conjugate, converb,
converb_ken, converb_casina, participle}; nominal-kind = {decline, copula}.

### K1 — Niteleyici + ad (nominal head), w=3
tokens[i−1] bir **sayı/belirteç/sıfat niteleyicisi** ise, i'nin nominal-kind adayları `+3`,
fiil-kind adayları `−3`. Niteleyici testi (kapalı küme + POS):
- Sayı: rakam (`\d`) VEYA sayı sözcüğü {bir,iki,üç,dört,beş,altı,yedi,sekiz,dokuz,on,yüz,
  bin,milyon,milyar} VEYA i−1'in analizinde nominal-kind + POS=`num`.
- Belirteç/miktar: {birkaç,çok,az,birçok,her,bazı,tüm,bütün,hiçbir,kimi,birtakım,birçok,
  hangi,nice,onlarca,yüzlerce,binlerce}.
- Sıfat: i−1'in en olası izole analizi nominal + `pos`(lemma)==`adj`.
Korkmaz: sayı/sıfat tamlamasında niteleyici, nitelenen adı ister → i bir ADdır. (Ör.
`üç gelin`, `güzel yaz`, `bu kalem`.)

### K2 — Edat yönetimi (postposition government), w=4
tokens[i+1] bir **çekim edatı** ise, i'nin belirli DURUM'daki adayı `+4`; yanlış durum `−2`.
Kapalı yönetim tablosu (edat → nitelediği adın durumu):
```
nom  (yalın/tamlayan): ile, için, gibi, kadar  (zamirde tamlayan/gen; adda yalın/nom)
dat  (yönelme):        göre, doğru, karşı, rağmen, dair, ilişkin, ait, değin
abl  (çıkma):          önce, sonra, beri, dolayı, ötürü, itibaren, yana
```
i'nin adayı: nominal-kind + durum tabloyla uyumlu → `+4`; nominal-kind + durum uyumsuz →
`−2`; fiil-kind → `0` (edat isim ister ama fiil-önü edat da olur, budama YOK). `göre`
çift yönetim → hem nom hem dat kabul (`+4`). Korkmaz: çekim edatları belirli durum eki
alan adla öbek kurar (ör. `okul-a doğru`, `sen-den önce`, `bun-un için`).

### K3 — Ayrı soru parçacığı (`mI`), w=2
tokens[i+1] ayrı **soru parçacığı** {mı,mi,mu,mü} ise, i'nin adayı: `question=False`
(soru ayrı token'da taşınıyor, eke gömülü DEĞİL) → `+2`; `question=True` → `−2`. Yalnız
conjugate/copula kind'larında `question` ekseni var; diğerlerinde `0`. Korkmaz: soru
eki `mI` ayrı yazılır, vurguladığı öğeyi izler (ör. `geldi mi`, `okulda mı`).

### K4 — Özne–yüklem kişi uyumu, w=3
i'den ÖNCE **soldan en yakın** bir **yalın kişi zamiri** varsa (araya sıfat/niteleyici
girebilir), i'nin fiil-kind adayı o kişiyle uyumlu `person` taşıyorsa `+3`; uyumsuzsa
`−1`. Zamir→kişi (kapalı):
```
ben→1sg  sen→2sg  o→3sg  biz→1pl  siz→2pl  onlar→3pl
```
(`o`/`onlar` zayıf: 3. kişi çoğu biçimde işaretsiz → yalnız 1./2. kişi ve çoğulda güçlü
sinyal; `o` için w=1'e düşür.) Korkmaz: yüklem, öznenin kişisine kişi ekiyle uyar (ör.
`ben geldim`, `siz gelirsiniz`). Yalnız `person` ekseni olan kind (conjugate, copula).

### K5 — Tamlayan–iyelik uyumu (belirtili ad tamlaması), w=3
i'den ÖNCE **soldan en yakın** bir **tamlayan** (nominal-kind + case=gen) VEYA **tamlayan
zamir** {benim,senin,onun,bizim,sizin,onların} varsa (araya sıfat girebilir — `benim güzel
evim`), i'nin nominal-kind adayı uyumlu `possessive` taşıyorsa `+3`, nominal ama
iyelik-yok/uyumsuz `−1`, fiil-kind `−1`. Zamir→iyelik-kişi (kabul edilen iyelik kümesi):
```
benim→{1sg}  senin→{2sg}  onun→{3sg}  bizim→{1pl}  sizin→{2pl}  onların→{3sg,3pl}
```
`onların` çift kabul: 3pl tamlayan, tamlananda hem `-i` (3sg: onların evi) hem `-leri`
(3pl: onların evleri) uyumludur (Korkmaz). Sıradan ad + gen → `possessive∈{3sg,3pl}`
(tamlayan tekilse 3sg, çoğulsa da 3pl kabul). Korkmaz: belirtili ad
tamlamasında tamlanan, tamlayanın kişisine iyelik ekiyle uyar (ör. `benim ev-im`,
`ev-in kapı-sı`).

**Toplam:** `context_evidence(a,i) = Σ Kj(a,i)`. Kurallar bağımsız toplanır; bir aday
birden çok kuraldan kanıt alabilir (ör. `benim güzel evim` → K1+K5).

## 4. Kapsam ve bağımsız golden

- **Golden = SIRA (top-1) testi**, güven değeri DEĞİL. Yalnız bağlamın top-1'i dilbilimsel
  olarak **kesinleştirdiği** cümlelerde beklenir (`üç gelin`→isim; `içeri gelin`→fiil;
  `okula doğru`→dat; `geldi mi`→question=False; `ben geldim`→1sg; `evin kapısı`→3sg iyelik).
  Yakın/nötr çağrılar golden'a KONMAZ (izole tiebreak'e bırakılır).
- **Bağlam-YOK regresyon golden:** kural ateşlemeyen cümlede `rank_in_context` top-1'i ==
  izole `disambiguation.rank` top-1 (geriye-uyum kilidi).
- **Recall-güvenlik golden:** hiçbir kural giriş adaylarını silmez (`set(out[i])==set(in[i])`
  her i için), yalnız sırayı değiştirir.
- Golden motoru/analyze'ı GÖRMEDEN, elle-doğrulanmış cümle→beklenen-token-okuması'ndan
  kurulur (disambiguation SPEC §3 / CLAUDE.md §2 emsali).
- **Türkçe yüz:** ileride `tr.py`'a sarmalayıcı (`cümle_çözümle`) eklenebilir (bu artım
  DIŞI; önce çekirdek + golden).
- **Kapsam-dışı (sonraki):** olasılıksal dizi etiketleme; ikileme/edat öbeği yeniden-kurulum;
  uzun-mesafe bağımlılık (yalnız ±1 + cümle-başı zamir bu artımda).
