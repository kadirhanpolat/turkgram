# Faz E3/E4 — Yan Cümle Desteği: Tasarım Dokümanı

**Tarih:** 2026-07-17  
**Durum:** Onaylandı  
**Kapsam:** E3 (ki-cümleleri: CompP/RelP) + E4 (diye-cümleleri: DiyeP)

---

## 1. Genel Mimari

Mevcut `parse.py` bottom-up pipeline'ına iki yeni kural eklenir. Mevcut dataclass'lar (`LeafNode`, `PhraseNode`), `_leaf_tag`, ve R0–R5 kuralları **değişmez**. `parse.py`'ye yalnız iki fonksiyon + pipeline bağlantısı eklenir.

```
[Mevcut tokenize + analyze + disambiguation katmanı]  (dokunulmaz)
       │
       └── parse_phrase() bottom-up pipeline
           R0   NP[gen+poss]           (değişmez)
           R3   AdjP                   (değişmez)
           R1   NP[modifier* NOUN]     (değişmez)
           R1b  NP[participle NOUN]    (değişmez)
           R2   PP[NP ADP]             (değişmez)
           R6   CompP / RelP  ← YENİ  (ki, R4'ten önce)
           R7   DiyeP         ← YENİ  (diye, R5'ten önce)
           R4   CoordP                 (değişmez)
           R5   S builder              (değişmez)
           wrap_bare_vp               (değişmez)
```

**Temel kararlar:**

- Saf Python, sıfır dış bağımlılık.
- Tüm veri yapıları `frozen=True` dataclass — değişmezlik korunur.
- `analyze()` / `decline()` / `conjugate()` imzaları dokunulmaz.
- `diye` için QuotP/PurpP ayrımı bilinçli olarak yapılmaz — semantik ayrım kural-tabanlı parser kapsamının dışında.

---

## 2. Yeni PhraseNode Etiketleri

| Etiket | Tetikleyici | Örnek |
|--------|------------|-------|
| `CompP` | VERB/VP/S + `ki` + sağ-sequence | `"biliyorum ki geldi"` |
| `RelP` | NP/NOUN + `ki` + sağ-sequence | `"öyle bir şey ki gördüm"` |
| `DiyeP` | sol-sequence + `VERB[diye/demek]` | `"gelir diye bekledi"` |

---

## 3. E3 — R6_ki Kural Detayı

### 3.1 Tanıma

`ki` token `_leaf_tag`'de CCONJ olarak etiketlenmeye devam eder (değişmez). R6 çalışma anında sol komşuya bakarak CompP/RelP/geç üretir.

### 3.2 Örüntüler

```
Sol ∈ {VERB, VP, S}  + CCONJ[ki] + sağ_sequence → CompP(sol, CCONJ[ki], *sağ)
Sol ∈ {NP, NOUN}     + CCONJ[ki] + sağ_sequence → RelP(sol, CCONJ[ki], *sağ)
Aksi halde                                       → değiştirme (R4 görecek)
```

`sağ_sequence`: `ki`'den sonra gelen tüm kalan node'lar (tek geçiş, ilk `ki`'de ateşlenir).

### 3.3 Örnekler

```
"biliyorum ki geldi"
  leaves:  VERB[biliyorum]  CCONJ[ki]  VERB[geldi]
  R6 sol=VERB → CompP(VERB[biliyorum], CCONJ[ki], VERB[geldi])

"öyle bir şey ki gördüm"
  after R1: NP[öyle bir şey]  CCONJ[ki]  VERB[gördüm]
  R6 sol=NP → RelP(NP[öyle bir şey], CCONJ[ki], VERB[gördüm])

"iyi ki geldin"
  leaves:  ADJ[iyi]  CCONJ[ki]  VERB[geldin]
  R6 sol=ADJ → değiştirme → R4/R5'e bırak
```

### 3.4 Edge Cases

- **ki + ki:** İlk `ki` tüm sağ-sequence'i CompP/RelP içine alır; ikinci `ki` CompP'nin çocuğu olarak `surface`'e yansır. İç parsing yok (kapsam dışı).
- **"iyi ki":** Sol ADJ → R6 ateşlemez → R5 sonrasında S düzeyinde serbest kalır.
- **"bana dedi ki":** `dedi` VERB, `ki` CompP oluşturur → R7 ateşlemez. Çatışma yok.

---

## 4. E4 — R7_diye Kural Detayı

### 4.1 Tanıma

`diye` token `_leaf_tag`'de VERB olarak etiketlenir (demek converb, değişmez). R7 çalışma anında şu koşulları kontrol eder:

```python
node.tag == "VERB"
and node.analysis is not None
and node.analysis.kind == "converb"
and node.analysis.lemma == "demek"
```

Koşul sağlanmazsa (OOV, hypothetical, farklı lemma) → R7 atlar, `diye` VERB olarak R5'e bırakılır.

### 4.2 Örüntü

```
sol_sequence + VERB[diye] → DiyeP(sol_sequence..., VERB[diye])
```

`sol_sequence`: `diye`'den önce gelen, mevcut node listesinde birikimiş tüm node'lar.

### 4.3 Örnekler

```
"gelir diye bekledi"
  after R0-R4:  VERB[gelir]  VERB[diye]  VERB[bekledi]
  R7: diye bulundu, sol=[VERB[gelir]]
  → DiyeP(VERB[gelir], VERB[diye])  VERB[bekledi]
  R5: VERB[bekledi] yüklem → S(DiyeP[gelir diye], VP[bekledi])

"okusun diye kitap aldı"
  after R1:  VERB[okusun]  VERB[diye]  NP[kitap]  VERB[aldı]
  R7: diye bulundu, sol=[VERB[okusun]]
  → DiyeP(VERB[okusun], VERB[diye])  NP[kitap]  VERB[aldı]
  R5: VERB[aldı] yüklem, NP[kitap] acc → VP(NP[kitap], VERB[aldı])
  → S(DiyeP[okusun diye], VP[kitap aldı])
```

### 4.4 Edge Cases

- **diye analiz başarısız:** `analysis is None` veya `lemma != "demek"` → R7 atlar.
- **Çok sayıda diye:** İlk `diye`'de sol-sequence tüketilir; ikincisi (nadir) VP içinde VERB olarak kalır.

---

## 5. Dosya Planı

| Dosya | Değişiklik |
|-------|-----------|
| `turkgram/parse.py` | `_apply_r6_ki()` + `_apply_r7_diye()` eklenir; `parse_phrase` pipeline güncellenir |
| `tests/golden_subordinate.py` | Bağımsız golden (Opus, motor-körü) — 8+ giriş |
| `tests/test_subordinate.py` | Runner — mevcut `_node_matches` yardımcısı yeniden kullanılır |
| `tools/sweep_syntax_e.py` | CompP/RelP/DiyeP tag'leri sweep'e dahil edilir |

`turkgram/__init__.py` ve `turkgram/tr.py` değişmez (yeni public API yok).

---

## 6. Test Stratejisi

### 6.1 Golden Kapsamı (minimum 8 giriş)

| # | Giriş | Beklenen kök etiketi | Amaç |
|---|-------|---------------------|------|
| 1 | `"biliyorum ki geldi"` | CompP | E3 temel |
| 2 | `"öyle bir şey ki gördüm"` | RelP | E3 NP-sol |
| 3 | `"iyi ki geldin"` | S | E3 geçiş (ADJ-sol, R6 ateşlemez) |
| 4 | `"gelir diye bekledi"` | S (DiyeP+VP) | E4 alıntı |
| 5 | `"okusun diye kitap aldı"` | S (DiyeP+VP) | E4 amaç |
| 6 | `"okudu diye sevindi"` | S (DiyeP+VP) | E4 varyant |
| 7 | `"kitap ve defter"` | CoordP | Regresyon (ki/diye yok) |
| 8 | `"eve geldiğini biliyorum"` | S | Regresyon (participle NP) |

### 6.2 İş Akışı (CLAUDE.md §2)

1. **SPEC** — bu doküman
2. **Bağımsız golden** (`golden_subordinate.py`) — Opus, motor-körü (parse.py açılmaz)
3. **Motor** — `_apply_r6_ki` + `_apply_r7_diye` implementasyonu
4. **Hakem** — sweep_syntax_e.py güncel + tam paket regresyonsuz

### 6.3 Regresyon Koruması

`tests/test_parse.py` ve `tests/test_dependency.py` mevcut tüm test senaryoları değişmeden geçmeli.

---

## 7. Kapsam Dışı

- `ki`'nin iç yan cümlesinin constituency parse'ı (özyinelemeli parsing)
- `diye` QuotP/PurpP semantik ayrımı (kullanıcı `diye` tokenuna bakarak yorumlar)
- Zincirli yan cümleler (`... ki ... diye ...`)
- İstatistiksel/ML parsing
