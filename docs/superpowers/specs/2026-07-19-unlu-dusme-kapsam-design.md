# Ünlü düşmesi (drops_vowel) kapsam genişletme — Tasarım

**Tarih:** 2026-07-19
**Kapsam:** `morphology_noun.py` — `DROP_VOWEL` + `FRONT_HARMONY` kapalı kümeleri
**Statü:** SPEC (ana oturum) → bağımsız golden → motor → hakem
**Köken:** Perf/OOV/round-trip sweep'lerinde tekrar eden `omzuna`/`naklınki`/`zihni` kaçakları;
`_root_candidates` restore ediyor ama motor yanlış üretince oracle eşleşmiyor (analiz de kaçırır).

## 1. Amaç

Ünlü düşmesi (§3.3) TAMAMEN leksik kapalı küme. Mevcut `DROP_VOWEL` (~40 sözcük) EKSİK
ve bazı disharmonik alıntılar `FRONT_HARMONY`'de değil → yanlış üretim + analiz kaçağı.
Motor üretimi kaynak; düzeltilince analiz (oracle + `_root_candidates` restore) BEDAVA düzelir.

Ampirik gap (66-sözcük test, `decline(w, case="acc")`):
- **DROP_VOWEL eksik (düşmüyor):** `omuz→omuzu` (bekl. omzu) vb.
- **DROP_VOWEL'de ama disharmonik (arka ünlü):** `nakil→naklı` (bekl. nakli).

## 2. Değişiklik

### 2.1 `DROP_VOWEL`'e eklenecek (her biri son-hece dar ünlüsü ünlü-başlı ek önünde düşer)

`omuz, zihin, lütuf, ilim, beniz, hışım, kabir, kahır, kavis, kayıt, kibir, kutur,
nabız, nutuk, remiz, sadır, şahıs, vecih`

Beklenen (acc): omzu, zihni, lütfu, ilmi, benzi, hışmı, kabri, kahrı, kavsi, kaydı(t→d),
kibri, kutru, nabzı, nutku, remzi, sadrı, şahsı, vechi.
**NOT — `kayıt`:** düşme + t→d yumuşama birlikte (kaydı). softens bayrağı zaten hesaplanır.

### 2.2 `FRONT_HARMONY`'ye eklenecek (drops + ön-ünlü ek — disharmonik alıntı)

`haciz, kavim, nakil` → haczi/kavmi/nakli (arka-ünlü gövdeye ön-ünlü ek).
Bunlar zaten `DROP_VOWEL`'de; yalnız harmoni yönü düzeltilir (FRONT_HARMONY drops ile birlikte).

## 3. Recall/precision güvenliği (KRİTİK)

- **Her lemma yalnız KENDİNİ etkiler** (set üyeliği kök üzerinde) → yan-etki yok, false-drop
  riski YALNIZ eklenen kelime gerçekten düşmüyorsa. Golden bağımsız doğrular.
- **FALSE-DROP taraması (hakem):** eklenmeyen benzer-desenli sözcükler (sınıf→sınıfı,
  gurur→gururu, şiir→şiiri, sinir→siniri, ölüm→ölümü) DÜŞMEMELİ — regresyon sweep şart.
- **`gövde` DIŞLANDI:** düşmez (gövdeyi doğru); ilk taramada yanlış-pozitifti.

## 4. Test planı

**Bağımsız golden (Opus, motor-körü):** her eklenen sözcük için elle-doğrulanmış çekim
biçimleri (acc + poss3sg + dat, ünlü-başlı ek → düşme). §2.1/§2.2 listesi + düşmeyen
kontrol grubu (sınıf/gurur/şiir/sinir/ölüm → DÜŞMEZ). Analiz round-trip (omzuna→omuz).

**Hakem:** korpus sweep — (a) eklenen sözcükler doğru üretim+analiz; (b) FALSE-DROP yok
(leksikon geneli, eklenen küme dışı düşme sıçraması yok); tam paket regresyonsuz.

## 5. Kapsam dışı

Tam leksikografik ünlü-düşme envanteri (bu artımsal küratör; "kapsam eksiği buraya eklenir"
mevcut yorumu sürüyor). `_root_candidates` disharmonik-mastar sınırı (ayrı, pre-existing).
