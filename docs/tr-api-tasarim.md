# turkgram Türkçe API Katmanı — Tasarım (onaylandı)

**Amaç:** Türkçe-yüzlü paralel API — Türkçe fonksiyon/parametre/değer adları; her Türkçe
fonksiyon içeride orijinal İngilizce çekirdeği çağırır. İngilizce API dokunulmaz; ikisi
bir arada yaşar.

## Kararlar (kullanıcı onayı)

1. **Mekanizma:** Paralel modül `turkgram/tr.py` (`import turkgram.tr as tr`). İnce
   sarmalayıcılar: Türkçe param adı → İngilizce kwarg; Türkçe değer → tek-yönlü sözlükle
   İngilizce anahtar; çekirdek çağrılır; sonuç aynen döner.
2. **Terim geleneği:** KARMA — kanonik akademik (TDK/Korkmaz) değer + tanıdık alias
   (ör. `görülen_geçmiş` ve `dili_geçmiş` ikisi de kabul).
3. **Tanımlayıcı stili:** GERÇEK Türkçe harf (`çekimle`, `kişi`, `işteş`). Python 3 Unicode
   tanımlayıcıyı destekler.
4. **Değer normalizasyonu:** girdi `_tr_lower` (#10: İ→i, I→ı ardından küçült) + `strip`;
   bilinmeyen değer → geçerli seçenekleri sıralayan `ValueError`.
5. **paradigma dönüş sözlüğü:** v1'de `çekim_tablosu`/`ad_çekim_tablosu` çekirdek yapıyı
   AYNEN döndürür (anahtarlar İngilizce, DEĞERLER Türkçe biçim). Türkçe-anahtarlı sözlük
   YAGNI → v2'ye ertelendi (kullanıcı önceliklendirmedi).

## Fonksiyon adları

| İngilizce | Türkçe |
|-----------|--------|
| `conjugate` | `çekimle` |
| `paradigm` | `çekim_tablosu` |
| `parse_verb` | `fiil_çöz` |
| `inflect_last_token` | `son_kelimeyi_çek` |
| `decline` | `ad_çekimle` |
| `paradigm_noun` | `ad_çekim_tablosu` |
| `parse_noun` | `ad_çöz` |
| `predicative` | `yüklem` |
| `copula` | `ekfiil` |
| `with_ki` | `ki_ekle` |
| `equative` | `eşitlik` |
| `derivations` | `türet` |

## Parametre adları

| İngilizce | Türkçe |
|-----------|--------|
| `tense` | `kip` |
| `person` | `kişi` |
| `negative` | `olumsuz` |
| `ability` | `yeterlik` |
| `question` | `soru` |
| `case` | `durum` |
| `possessive` | `iyelik` |
| `number` | `sayı` |
| `aux` | `birleşik` |
| `pos` (türet) | `tür` |

`lemma`/`headword` konumsal (ilk arg) kalır.

## Değer sözlükleri (karma — hepsi kabul → İngilizce anahtar)

**kip:** `şimdiki`→pres · `görülen_geçmiş`/`geçmiş`/`dili_geçmiş`→past · `gelecek`→fut ·
`geniş`→aorist · `öğrenilen_geçmiş`/`mişli_geçmiş`/`duyulan`→evid · `şart`/`dilek_şart`/`koşul`→cond ·
`gereklilik`→necess · `emir`→imp · `istek`→opt · `ulaç`/`zarf_fiil`→conv_arak · `ortaç`/`sıfat_fiil`→part_dik

**kişi / iyelik:** `1tekil`→1sg · `2tekil`→2sg · `3tekil`→3sg · `1çoğul`→1pl · `2çoğul`→2pl ·
`3çoğul`→3pl (ASCII `1cogul`… da kabul)

**sayı:** `tekil`→sg · `çoğul`→pl

**durum:** `yalın`→nom · `belirtme`/`i`→acc · `yönelme`/`e`→dat · `bulunma`/`de`→loc ·
`ayrılma`/`den`→abl · `tamlayan`/`ilgi`→gen · `vasıta`/`araç`/`ile`→ins

**birleşik:** `hikaye`/`hikâye`→hikaye · `rivayet`→rivayet · `şart`→sart

**tür (pos):** `isim`→noun · `fiil`→verb · `birleşik_fiil`→compound_verb · `birleşik_isim`→compound_noun

## Örnek

```python
import turkgram.tr as tr
tr.çekimle("gelmek", "şimdiki", "1tekil")                      # geliyorum
tr.çekimle("gitmek", "görülen_geçmiş", "3tekil", olumsuz=True) # gitmedi
tr.çekimle("okumak", "geniş", "3tekil", yeterlik=True)          # okuyabilir
tr.ad_çekimle("kitap", durum="yönelme")                        # kitaba
tr.ad_çekimle("ev", iyelik="3tekil", durum="bulunma")          # evinde
tr.ekfiil("öğrenci", "hikaye", "1tekil")                       # öğrenciydim
tr.türet("göz", "isim")                                        # -lIk/-CI… türevleri
```

## Test stratejisi (TDD)

`tests/test_tr.py`: her Türkçe çağrının SONUCU, eşdeğer İngilizce çekirdek çağrısının
sonucuyla AYNI olmalı (`tr.çekimle("gelmek","şimdiki","1tekil") == morphology.conjugate(
"gelmek","pres","1sg")`). Böylece çeviri haritaları çekirdeğe karşı doğrulanır; ayrıca
alias'lar (dili_geçmiş==görülen_geçmiş), `_tr_lower` (büyük harf girdi), ve bilinmeyen-değer
`ValueError` sınanır. Çekirdek golden'ları zaten biçim doğruluğunu garanti eder — bu katman
yalnız ÇEVİRİ doğruluğunu sınar.

## Dosyalar

- `turkgram/tr.py` (YENİ) — sarmalayıcılar + `_KIP`/`_KISI`/`_DURUM`/… haritaları + `_tr_lower`.
- `tests/test_tr.py` (YENİ) — çeviri denkliği + alias + hata testleri.
- `turkgram/__init__.py` — `from . import tr` (alt-modül erişimi).
