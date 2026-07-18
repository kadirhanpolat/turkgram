# m-İkileme Nominal-Yeniden-Kurulum Implementation Plan

**Goal:** Parser'ın NOUN-tabanlı m-ikilemeyi (`kitap mitap`) tek bir `NP` öbeği olarak yeniden
kurması (baş = taban isim, reduplikant = `MRED` → `compound:redup`), başıboş `X` bırakmadan.

**Architecture:** Yüzey-tabanlı yeni kural `_apply_r9_mredup` (R8_redup emsali). Bitişik
`NOUN + m-reduplikant` çiftini `m_reduplicate` yüzey testiyle tespit eder → `NP(NOUN, MRED)`.
Pipeline'da R8'den sonra, R0/R1'den önce. NP olduğu için R1/R5 nominal rolü doğrudan işler.
`dependency.py` MRED için `compound:redup` + upos MRED→NOUN eşlemesi alır.

**Kaynak:** `docs/superpowers/specs/2026-07-18-m-ikileme-nominal-design.md`.

**Windows:** `python -m pytest ...`; Türkçe basan ad-hoc python → `PYTHONUTF8=1 python ...`.

---

## Dosya Yapısı

- **Modify** `turkgram/parse.py` — `_apply_r9_mredup` (yeni); pipeline'a ekle (R8'den sonra).
- **Modify** `turkgram/dependency.py` — `_child_deprel` NP dalı `MRED→compound:redup`; DepToken
  `upos = "NOUN" if lf.tag == "MRED" else lf.tag`.
- **Modify** `tests/golden_parse.py` — m-ikileme NP case'leri (motor-körü).
- **Modify** `tests/golden_dependency.py` — m-ikileme compound:redup case (motor-körü).
- **Create** `tools/sweep_m_reduplication.py` — parse korpus tarama (çökme yok).

---

## Task 1: Bağımsız golden (motor-körü, RED)

- Parse case'leri (`golden_parse.py` `PARSE_CASES` sonuna):
  - `kitap mitap aldı` → `S`, çocuk `VP`? HAYIR — `kitap mitap` yalın nom → **özne-NP** (kitap aldı
    emsali): `S(NP[kitap mitap], VP[aldı])`. Beklenen: S kökü, `children`'da `{"tag":"NP","surface":"kitap mitap"}`
    + `{"tag":"VP",...}`.
  - `araba maraba aldı` → `S(NP[araba maraba], VP[aldı])` (ünlü-başlı m-form).
  - `kitap mitap` (yüklemsiz) → `{"tag":"NP","surface":"kitap mitap"}`.
  - REGRESYON: `kitap kalem` (m-değil bitişik NOUN) → mevcut davranış korunur (m-NP KURULMAZ).
- Dependency case (`golden_dependency.py` `DEP_CASES` sonuna):
  - `kitap mitap aldı`: id1 kitap NOUN head=3 nsubj; id2 mitap **upos=NOUN** head=1 `compound:redup`;
    id3 aldı VERB head=0 root.
- **ZORUNLU — upos ampirik:** golden'ı sabitlemeden `kitap`/`aldı` upos'unu ölç (motor olgusu):
  `PYTHONUTF8=1 python -c "from turkgram import tokenize,parse_text; from turkgram.parse import parse_phrase; from turkgram.dependency import constituency_to_dep; t=parse_phrase(tokenize('kitap mitap aldı'), parse_text('kitap mitap aldı',{'kitap','almak'})); print([(d.form,d.lemma,d.upos,d.deprel) for d in constituency_to_dep(t)])"`
  (RED'de yanlış yapı döner; yalnız `kitap`/`aldı` upos/lemma sabit — motor-körü varsayımı doğrula.)
- RED doğrula: `python -m pytest tests/test_parse.py tests/test_dependency.py -q` → yeni case FAIL,
  mevcut + AdvP PASS.
- Commit: `test(parse): m-ikileme nominal bağımsız golden (motor-körü, RED)`.

## Task 2: `_apply_r9_mredup` + pipeline (parse.py, GREEN parse)

```python
def _apply_r9_mredup(nodes: list) -> list:
    """R9: bitişik NOUN + m-reduplikant → NP (m-ikileme nominal-yeniden-kurulum)."""
    from .analysis import _tr_lower
    from .reduplication import m_reduplicate
    out, i = [], 0
    while i < len(nodes):
        a = nodes[i]
        b = nodes[i + 1] if i + 1 < len(nodes) else None
        matched = False
        if (b is not None
                and isinstance(a, LeafNode) and isinstance(b, LeafNode)
                and a.tag == "NOUN"):
            la, lb = _tr_lower(a.token), _tr_lower(b.token)
            try:
                if m_reduplicate(la) == la + " " + lb:
                    mred = LeafNode(tag="MRED", token=b.token, analysis=None)
                    out.append(PhraseNode.make("NP", (a, mred)))
                    i += 2
                    matched = True
            except ValueError:
                pass
        if not matched:
            out.append(a)
            i += 1
    return out
```
- Pipeline: `nodes = _apply_r8_redup(nodes)` sonrası `nodes = _apply_r9_mredup(nodes)`.
- Parse golden GREEN: `python -m pytest tests/test_parse.py -q`.
- Regresyon: `python -m pytest tests/test_parse.py tests/test_parse_text.py tests/test_subordinate.py -q`.
- Commit: `feat(parse): _apply_r9_mredup — m-ikileme nominal NP (MRED reduplikant)`.

## Task 3: dependency.py — compound:redup + upos (GREEN dependency)

- `_child_deprel` NP dalına `if child_tag == "MRED": return "compound:redup"`.
- DepToken kurulumunda (`upos = lf.tag` satırı) → `upos = "NOUN" if lf.tag == "MRED" else lf.tag`.
- lemma/feats: MRED analysis=None → mevcut yol; `_analysis_to_feats(None, "NOUN")` çökmez (doğrula).
- Dependency golden GREEN: `python -m pytest tests/test_dependency.py -q`.
- Commit: `feat(dependency): m-ikileme MRED → compound:redup + upos NOUN`.

## Task 4: Hakem — korpus tarama + tam doğrulama

- `tools/sweep_m_reduplication.py`: temsili NOUN m-ikileme cümleleri (kitap/araba/para/göz + m-değil
  `kitap kalem` + AdvP `yavaş yavaş` çakışma-yok) → parse + `constituency_to_dep`, çökme sayacı,
  m-NP kurulum kontrolü.
- Tam paket: `python -m pytest -q -m "not slow"` sonra `-m slow`.
- Adversarial hakem (code-reviewer): (1) R9 guard NOUN-taban gerçekten m-ikilemeyi mi yakalıyor,
  yanlış-pozitif (`kitap kalem`) var mı? (2) R8/R9/R1/R5 etkileşimi mevcut ağaçları koruyor mu?
  (3) `compound:redup` + upos=NOUN CoNLL-U UD-geçerli mi? (4) MRED öbek dışına sızıyor mu?
- Commit + docs: CLAUDE.md §7 + README + memory güncelle.

---

## Bitiş Kontrol Listesi

- [ ] `kitap mitap aldı` → `S(NP[kitap mitap], VP[aldı])`; mitap MRED (X değil, başıboş değil)
- [ ] `araba maraba aldı` → `S(NP[araba maraba], VP[aldı])`
- [ ] `kitap mitap` → `NP` kök
- [ ] `kitap kalem` (m-değil) → mevcut davranış korunur
- [ ] Dependency: baş `nsubj`, reduplikant `compound:redup` upos=NOUN
- [ ] Mevcut E/AdvP parse + dependency + CoNLL-U testleri değişmez
- [ ] Korpus tarama 0 çökme; tam paket + slow regresyonsuz
- [ ] Docs güncel (CLAUDE.md §7, README, memory)
