# Üçüncü Taraf Lisansları

turkgram MIT lisanslıdır (bkz. `LICENSE`). Aşağıdaki üçüncü taraf verisi pakete
gömülüdür ve kendi lisansı altında dağıtılır.

---

## Zemberek (`turkgram/data/lexicon_tr.tsv`)

Gömülü Türkçe kök leksikonu (`turkgram/data/lexicon_tr.tsv`), **Zemberek-NLP**
projesinin `master-dictionary.dict` sözlüğünden türetilmiş **lemma + sözcük türü
(POS)** olgularını içerir.

- **Kaynak:** https://github.com/ahmetaa/zemberek-nlp
- **Telif:** Copyright 2018 Ahmet A. Akın, Mehmet D. Akın
- **Lisans:** Apache License, Version 2.0 — http://www.apache.org/licenses/LICENSE-2.0

### Yapılan değişiklik beyanı (Apache-2.0 §4-b)

Orijinal `master-dictionary.dict` dosyası, `tools/build_lexicon.py` betiğiyle
işlenerek türetilmiştir. Yapılan dönüşümler:

- Her satırdan yalnızca **lemma** ve **sözcük türü (POS)** çıkarıldı; Zemberek'in
  öznitelik/telaffuz alanları, kod ve düzyazısı KOPYALANMADI.
- Sözcük türü etiketi olmayan girdiler, `-mak`/`-mek` ile bitiyorsa fiil (mastar),
  aksi hâlde isim olarak sınıflandırıldı.
- Noktalama (`Punc`) ve mastar-dışı istisnalar (ör. "değil" fiil etiketi) elendi.
- Lemmalar Türkçe küçük harfe normalize edildi (İ→i, I→ı); yorum satırları atıldı.
- Çıktı `lemma<TAB>pos` biçiminde TSV olarak yeniden dizildi.

Gramer ve sözcük OLGUSU (bir kelimenin var olduğu ve sözcük türü) telif konusu
değildir; bu türetme, olgu-listesi olarak turkgram'ın MIT dağıtımına dâhil edilebilir.
Yine de kaynağa saygı ve Apache-2.0 §4 gereği bu atıf ve lisans bildirimi korunur.

### Apache License 2.0 — bildirim

```
Copyright 2018 Ahmet A. Akın, Mehmet D. Akın

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

Apache License 2.0'ın tam metni: http://www.apache.org/licenses/LICENSE-2.0
