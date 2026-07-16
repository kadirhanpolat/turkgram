# Architecture Critique — Turkgram Özellik Genişleme Tasarımı
**Tarih:** 2026-07-16  **Tur:** 1  **Toplam bulgu:** 42  **Arbitrasyon:** 4 çatışma + kimlik kararı

## Kimlik Kararı (tüm tasarımı etkiler)

> **Turkgram = bağımsız Türkçe gramer kütüphanesi.**
> spaCy muadili değil; spaCy entegrasyonu (adapter, katman) kapsam dışı — belki sonra opsiyonel.
> UD feature export önceliği düştü (asıl müşterisi spaCy pipeline'ıydı).

Bu karar CLAUDE.md §1'e yansıtılacak.

---

## Onaylı Öncelik Listesi

| # | Özellik | Gerekçe |
|---|---------|---------|
| 1 | `lexicon.load()` lazy singleton fix | Tek satır düzeltme; şu an hot loop'ta her çağrı 26k satır parse |
| 2 | `analysis_to_dict()` + `schema_version` + `confidence` açık | LLM + dictionary projesi için versiyonlu sözleşme |
| 3 | CLI — `python -m turkgram` text+json | Kullanım ve debug kolaylığı |
| 4 | `parse_text()` → `list[list[Analysis]]` | Cümle üzerinde toplu analiz; hypothetical flag zorunlu |
| 5 | Tokenizer — dar (boşluk/noktalama/apostrof) | parse_text'in temeli; klitik karar analyze()'a delege |
| — | UD feature export | Defer (spaCy gitmeyince öncelikli müşteri yok) |
| — | viz.py (morfem görselleştirici) | Defer (CLI text+json önce; viz talep gelince) |
| — | Dependency parsing | Kaldırıldı (C-03: MIT + oracle ikili ihlal) |
| — | NER | Kaldırıldı (C-07: ML/lisans gerektirir, ayrı proje kapsamı) |

---

## Bulgu Kaydı

| ID | Lens | Önem | Saldırılan İddia | Senaryo | Arbitrasyon | Karar |
|----|------|------|------------------|---------|-------------|-------|
| C-01 | Linguistics | Critical | Tokenizer klitik ayrımı kural tabanlı çözülemez | "evde" (bulunma) vs "ev de" (bağlaç) morfolojisiz ayırt edilemez | Tokenizer → dar (boşluk/noktalama/apostrof); klitik karar analyze()'a delege | Fix |
| C-02 | Data Integrity | Critical | parse_text Token.lemma tekil alan | OOV / hypothetical gürültü → downstream tüm katmanlar çöp alır | parse_text → `list[list[Analysis]]` + hypothetical flag zorunlu alan | Fix |
| C-03 | Data Integrity + YAGNI | Critical | ML dep-parsing MIT + oracle ikili ihlal | Treebank CC BY-SA/NC + generator oracle yok → iki bağımsız ihlal | Dep-parsing kapsam dışı; kural-tabanlı chunking ileride ayrı değerlendirilir | Fix |
| C-04 | Linguistics + YAGNI | Critical | "spaCy muadili" kimlik iddiası | ML/data gerektirir, MIT-saf-Python çelişir | Kimlik netleşti: bağımsız morfoloji kütüphanesi; spaCy entegrasyonu kapsam dışı | Fix |
| C-05 | Security | Critical | viz.py unsanitized HTML/SVG | Surface'e `<script>` → stored XSS Jupyter/web | viz.py defer; gelince her surface HTML-escaped olacak (zorunlu) | Defer |
| C-06 | Security | Critical | hermitdave "MIT" OpenSubtitles'ı launder etmiyor | EU sui generis DB rights → ticari dağıtımda hukuki risk | BOUN CC0 alternatifini araştır; şimdilik ticari kullanımda uyarı ekle (THIRD_PARTY) | Fix |
| C-07 | YAGNI + Linguistics | Critical | NER roadmap'te yer alıyor | ML/gazetteer gerektirir; MIT kısıt + ayrı proje kapsamı | NER roadmap'ten kalıcı olarak kaldırıldı | Fix |
| H-01 | Data Integrity | High | Tokenizer + analyze = iki bağımsız segmentasyon otoritesi | tokenize("okudun mu") çıktısı analyze() çok-token dalıyla çelişir | Tek otorite: analyze() çok-token dalı; tokenizer sadece böler, birleştirmez | Fix |
| H-02 | Data Integrity | High | UD export belirsiz analiz seçmeden lossy | `gelirken` = converb_ken \| copula → UD'ye hangisi gidecek? | UD export yalnızca disambiguate() çıktısına; ham analyze() → UD yasak | Fix (UD gelince) |
| H-03 | Data Integrity | High | analysis_to_dict versionsuz schema | Faz-N yeni kind/kwarg → consumer parse patlar | schema_version + kind→field kapalı eşleme + golden serialization testi | Fix |
| H-04 | Data Integrity | High | Embedded TSV data versiyonu yok | turkgram 1.2 train → 1.3 infer → Viterbi farklı çıktı; sessiz skew | `turkgram.DATA_VERSION` sabit + per-TSV hash; minor version'da data değişmez | Fix |
| H-05 | Linguistics | High | Token.lemma tekil alan → belirsiz yüzeyler yanlış seçilir | `analyze("de")` → bağlaç \| demek-imp; hangisi Token.lemma? | parse_text `list[list[Analysis]]` dönsün; Token sınıfı şimdi değil | Fix |
| H-06 | Linguistics | High | UD Turkish eksen haritası tanımsız | converb_casina → UD ne? voice_chain tuple → UD ne? | UD export öncesi SPEC: kind×kwarg → UD feature eşleme tablosu zorunlu | Fix (UD gelince) |
| H-07 | Security | High | CLI kombinatoryal enum → DoS | 1000-karakter token → grid patlaması | Per-token max-length + enum timeout + input cap (CLI + parse_text) | Fix |
| H-08 | Perf | High | analyze() doc-level cache yok | parse_text 10k token → 10k bağımsız grid; dakikalar | parse_text içinde `(surface, roots)` keyed lru_cache | Fix |
| H-09 | Perf | High | lexicon.load() her çağrı 26k TSV parse | hot loop'ta load_freq() → GC baskısı, bellek spike | Module-global lazy singleton; load() ikinci çağrı cached döner | Fix (1. öncelik) |
| H-10 | Perf | High | rank_in_context içte yeniden analyze() yapıyor | Doc katmanı da analyze() → 2-3× redundant enumeration | rank_in_context yalnız pre-computed analyses alacak; internal branch deprecate | Fix |
| H-11 | YAGNI | High | 8 özellik listesi öncelik yanlış | UD/viz/NER önce, CLI+Doc gömülü kalıyor | Yeniden sıralama onaylandı (bkz. Onaylı Öncelik Listesi) | Fix |
| M-01 | YAGNI | Medium | viz.py kullanıcı talebi yok | JSON çıkış yeterken SVG yazmak yük | Defer; CLI text+json önce | Defer |
| M-02 | YAGNI | Medium | UD export gerçek kullanıcı yok şimdi | Dictionary projesi UD istemiyor | Defer; adaptor 1 dosya, talep gelince | Defer |
| M-03 | Perf | Medium | Dep-parse O(n²) bound yok | 40-token cümle → 1600 attachment × feature | Dep-parse kaldırıldı (C-03) → geçersiz | Reject |
| M-04 | YAGNI | Medium | analysis_to_dict zaten %90 var | Analysis dataclass → asdict() trivia | Haklı ama H-03 schema versioning gerektiriyor | Reject |
| L-01 | YAGNI | Low | LLM dict redundant framing | to_dict() 10 satır; "özellik" değil | H-03 schema versioning nedeniyle gerekli, küçük de olsa | Reject |

---

## Çatışma Arbitrasyonu

### Çatışma 1: Tokenizer derinliği (Linguistics ↔ YAGNI)
- Linguistics: Lattice tokenizer üret; klitik karar morfoloji+bağlam gerektirir
- YAGNI: Whitespace + klitik only yeterli
- **Karar:** Tokenizer dar tutulacak (boşluk/noktalama/apostrof). Klitik (-mı, -de, -ki) kararı analyze()'a delege. Birleşik fiil birleştirme tokenizer'dan çıkar — zaten analyze() çok-token dalında var.

### Çatışma 2: Doc/Token nesnesi (Data Integrity ↔ YAGNI)
- Data Integrity: OOV contract + ambiguity sözleşmesi Token sınıfında zorunlu
- YAGNI: `list[Analysis]` zaten var, wrapper class premature
- **Karar:** `parse_text() → list[list[Analysis]]` şimdi. Token sınıfı OOV contract + disambiguation kararı netleşince; wrapper class şimdi değil.

### Çatışma 3: viz.py (Perf ↔ YAGNI)
- Perf: Cache/test et, sonra yap
- YAGNI: Hiç yapma
- **Karar:** Defer. CLI text+JSON önce. viz talep gelince, o zaman sanitasyon zorunlu.

### Çatışma 4: LLM desteği için asıl eksik (Schema ↔ Ambiguity contract)
- Surface: analysis_to_dict() dict şeması yeterli
- Linguistics: Asıl eksik belirsizlik sözleşmesi; dict tek başına güvensiz
- **Karar:** İkisi birlikte. analysis_to_dict() hem schema_version hem confidence hem hypothetical flag taşıyacak. Yalnız dict değil, sözleşmeli dict.

---

## Aksiyonlar (Uygulama için)

### Acil (sıfır geriye uyum kırılması, küçük iş)
- [ ] H-09: `lexicon.load()` / `load_freq()` / `pos_map()` → module-global lazy singleton
- [ ] H-04: `turkgram.DATA_VERSION` sabit ekle

### Sonraki özellik (öncelik sırasıyla)
- [ ] H-03 + H-05: `analysis_to_dict(analysis) → dict` — schema_version, confidence, hypothetical
- [ ] CLI: `python -m turkgram analyze <surface> [--format text|json]`
- [ ] parse_text: `parse_text(text, roots=None) → list[list[Analysis]]` + H-08 cache
- [ ] Tokenizer: dar (boşluk/noktalama/apostrof bölme)

### Defer (talep gelince)
- [ ] C-05/M-01: viz.py (sanitasyon zorunlu gelince)
- [ ] H-02/H-06/M-02: UD feature export (SPEC önce)

### Kaldırıldı
- ~~Dependency parsing~~ (C-03)
- ~~NER~~ (C-07)
- ~~spaCy entegrasyonu~~ (C-04, kimlik kararı)

---

## Açık Soru (Kullanıcı kararı bekliyor)

**C-06 — hermitdave/OpenSubtitles lisans riski:**
BOUN CC0 corpus'undan lemma-frekans rebuild en güvenli yol.
Şu an: THIRD_PARTY_LICENSES.md'e ticari kullanım uyarısı eklenecek mi, yoksa rebuild planlanacak mı?
