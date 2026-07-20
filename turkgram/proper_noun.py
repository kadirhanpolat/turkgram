"""Kural-tabanlı özel-ad etiketleme (proper-noun tagging).

SPEC: docs/superpowers/specs/2026-07-20-proper-noun-tagging-design.md.

**NER DEĞİL** (ML/öğrenme yok) — kapalı-set gazetteer (kişi/yer/kurum, OLGU verisi) +
Türkçe imla sinyalleri (büyük harf, apostrof-ek). Deterministik, saf-Python, MIT-güvenli.
Motor/analyze DOKUNULMAZ; OPT-IN. `sentence._PERSON_NAMES` bu modülden gelir (tek kaynak).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Collection, Optional

from .tokenize import tokenize as _tokenize
from .analysis import _tr_lower, analyze as _analyze

__all__ = ["ProperNoun", "PERSON_NAMES", "PLACE_NAMES", "ORG_NAMES",
           "proper_type", "tag"]

# ── Gazetteer'ler (OLGU — telifsiz, elle küratörlenmiş) ───────────────────────
# Kişi adları — yaygın Türkçe adlar (küçük harf). Genişletilebilir kapalı-set.
PERSON_NAMES: frozenset[str] = frozenset({
    "ali", "veli", "ayşe", "fatma", "mehmet", "ahmet", "mustafa", "hasan", "hüseyin",
    "ibrahim", "ismail", "osman", "ömer", "yusuf", "murat", "emre", "burak", "can",
    "cem", "kaya", "kemal", "orhan", "oğuz", "serkan", "tolga", "ufuk", "volkan",
    "zafer", "zeynep", "elif", "emine", "hatice", "meryem", "merve", "büşra", "esra",
    "sema", "selin", "deniz", "ece", "eda", "gül", "hande", "irem", "melek", "nur",
    "özge", "pınar", "sevgi", "sibel", "tuğba", "yasemin", "aylin", "aslı", "banu",
    "ceren", "derya", "dilek", "ebru", "figen", "gizem", "hülya", "kübra", "leyla",
    "nazlı", "seda", "şeyma", "tülay", "ümit", "yağmur", "yıldız",
    "kaan", "arda", "efe", "berk", "onur", "taner", "tarık", "levent", "engin",
    "erdem", "ferhat", "gökhan", "haluk", "işıl", "necati", "rıza", "sadık", "vedat",
})

# Yer adları — 81 Türkiye ili + yaygın ülke/kıta/deniz (küçük harf).
_TR_PROVINCES: frozenset[str] = frozenset({
    "adana", "adıyaman", "afyonkarahisar", "ağrı", "amasya", "ankara", "antalya",
    "artvin", "aydın", "balıkesir", "bilecik", "bingöl", "bitlis", "bolu", "burdur",
    "bursa", "çanakkale", "çankırı", "çorum", "denizli", "diyarbakır", "edirne",
    "elazığ", "erzincan", "erzurum", "eskişehir", "gaziantep", "giresun", "gümüşhane",
    "hakkari", "hatay", "ısparta", "mersin", "istanbul", "izmir", "kars", "kastamonu",
    "kayseri", "kırklareli", "kırşehir", "kocaeli", "konya", "kütahya", "malatya",
    "manisa", "kahramanmaraş", "mardin", "muğla", "muş", "nevşehir", "niğde", "ordu",
    "rize", "sakarya", "samsun", "siirt", "sinop", "sivas", "tekirdağ", "tokat",
    "trabzon", "tunceli", "şanlıurfa", "uşak", "van", "yozgat", "zonguldak", "aksaray",
    "bayburt", "karaman", "kırıkkale", "batman", "şırnak", "bartın", "ardahan", "iğdır",
    "yalova", "karabük", "kilis", "osmaniye", "düzce",
})
_COUNTRIES: frozenset[str] = frozenset({
    "türkiye", "almanya", "fransa", "ingiltere", "italya", "ispanya", "yunanistan",
    "rusya", "amerika", "japonya", "çin", "hindistan", "brezilya", "mısır", "iran",
    "irak", "suriye", "azerbaycan", "gürcistan", "bulgaristan", "hollanda", "belçika",
    "avusturya", "isviçre", "kanada", "meksika", "portekiz", "polonya", "ukrayna",
})
_GEO: frozenset[str] = frozenset({
    "asya", "avrupa", "afrika", "amerika", "okyanusya", "akdeniz", "karadeniz",
    "ege", "marmara", "boğaziçi", "kızılırmak", "sakarya", "fırat", "dicle",
})
PLACE_NAMES: frozenset[str] = _TR_PROVINCES | _COUNTRIES | _GEO

# Kurum adları — yaygın kısaltma/ad (küçük kapalı-set; kurum açık-sınıf → caps/apostrof gerisi).
ORG_NAMES: frozenset[str] = frozenset({
    "tbmm", "yök", "tübitak", "tdk", "trt", "thy", "meb", "sgk", "osym", "ösym",
    "milliyet", "hürriyet", "galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor",
    "nato", "bm", "ab", "unicef", "unesco",
})

_ALL_GAZETTEER: frozenset[str] = PERSON_NAMES | PLACE_NAMES | ORG_NAMES

# Kapalı-sınıf işlev sözcükleri — cümle-başı büyük harfle yazılsa da ASLA özel ad DEĞİL
# (demonstratif/zamir/soru/bağlaç/derece). Bazıları leksikon default alt-kümesinde yok
# (bu/o det/pron) → analyze() danışması yetmez, açık liste şart.
_NEVER_PROPER: frozenset[str] = frozenset({
    # demonstratif + kişi zamiri
    "bu", "şu", "o", "bunlar", "şunlar", "onlar", "böyle", "şöyle", "öyle",
    "ben", "sen", "biz", "siz", "kendi",
    # soru + belgisiz zamir/sıfat (analyze() hypothetical → cümle-başı kaçağı; açık liste sağlam)
    "ne", "kim", "hangi", "nasıl", "neden", "niçin", "nerede", "nereye", "kaç", "niye",
    "kimi", "kimse", "herkes", "hiç", "hiçbir", "bütün", "tüm", "bazı", "birçok",
    "birkaç", "her", "birçoğu", "kimisi", "hepsi", "bir",
    # bağlaç + derece + yaygın cümle-başı zarf
    "ve", "ama", "fakat", "ancak", "çünkü", "veya", "yahut", "oysa", "hâlbuki",
    "yani", "lakin", "hem", "hatta", "ayrıca", "belki", "tabii", "evet", "hayır",
    "artık", "çok", "daha", "en", "pek", "biraz", "işte", "eğer", "keşke",
})


@dataclass(frozen=True)
class ProperNoun:
    """Etiketlenmiş özel ad varlığı (kural-tabanlı; çok-token span dahil)."""
    surface: str            # span yüzeyi (çok-token → boşlukla birleşik: "Mustafa Kemal")
    type: str               # 'PER' | 'LOC' | 'ORG' | 'PROPER'
    index: int              # 1-tabanlı BAŞLANGIÇ token id (yüzey sırası)
    tokens: tuple[str, ...] = ()   # span'i oluşturan token'lar (tek-token → 1'li tuple)


def _strip_apostrophe(surface: str) -> tuple[str, bool]:
    """Apostrof-eki sıyır → (taban, apostrof_var). ASCII ' + kıvrık ' ikisi de."""
    for ap in ("'", "’"):
        if ap in surface:
            return surface.split(ap, 1)[0], True
    return surface, False


def proper_type(surface: str, *, sentence_initial: bool = False,
                is_common: bool = False) -> Optional[str]:
    """Tek yüzey → 'PER'|'LOC'|'ORG'|'PROPER'|None (SPEC §2, kural-tabanlı).

    sentence_initial: token cümle başında mı (büyük harf belirsizleşir).
    is_common: taban leksikonda ortak ad mı (cümle-başı ayrımı için).
    """
    base, has_apos = _strip_apostrophe(surface)
    low = _tr_lower(base)
    if not base:
        return None
    # 0. Kapalı-sınıf işlev sözcüğü → ASLA özel ad (her konumda; bu/o/ne/ve…)
    if low in _NEVER_PROPER:
        return None
    # Türkçe imlada özel ad ZORUNLU büyük harf → küçük-harf hiçbir kural tetiklemez
    # (deniz/gül/kaya ortak ad; gazetteer homografı yalnız büyük-harf biçimde LOC/PER).
    if not base[:1].isupper():
        return None
    # 1. Gazetteer (büyük-harf; konumdan bağımsız kesin sinyal)
    if low in PLACE_NAMES:
        return "LOC"
    if low in PERSON_NAMES:
        return "PER"
    if low in ORG_NAMES:
        return "ORG"
    # 2. Apostrof-ek (Türkçe imlada yalnız özel ad → kesin, cümle-başı olsa da)
    if has_apos:
        return "PROPER"
    # 3. Cümle-içi büyük harf (özel ad her konumda büyük) — büyük-harf yukarıda garantili
    if not sentence_initial:
        return "PROPER"
    # 4. Cümle-başı büyük harf: ortak ad değilse (OOV) özel ad
    if not is_common:
        return "PROPER"
    return None


# Kurum/yer head-noun'ları (LOC/ORG span'inin ardıl PROPER'ı bunlardan biriyse EMİLİR:
# `Ankara Üniversitesi`=LOC). Aksi ardıl PROPER (Abajur) EMİLMEZ → over-merge önlenir.
_HEAD_NOUNS: frozenset[str] = frozenset({
    "üniversitesi", "üniversite", "belediyesi", "belediye", "bakanlığı", "bakanlık",
    "okulu", "okul", "lisesi", "lise", "hastanesi", "hastane", "müdürlüğü", "başkanlığı",
    "ili", "ilçesi", "ilçe", "mahallesi", "mahalle", "caddesi", "cadde", "sokağı", "sokak",
    "meydanı", "bulvarı", "köprüsü", "boğazı", "dağı", "nehri", "gölü", "ovası", "vadisi",
    "kalesi", "camii", "sarayı", "müzesi", "havalimanı", "stadyumu", "spor", "kulübü",
})


def _can_join(span_type: str, t2: str, b2: str) -> bool:
    """Ardıl token span'e KATILABİLİR mi (yön+tip-farkındalıklı; over-merge önler).

    PER span: PER (Ali Veli) veya PROPER (soyad Yılmaz/Atatürk) alır. LOC/ORG span:
    YALNIZ head-noun PROPER (Ankara Üniversitesi) alır — keyfi PROPER (Abajur) DEĞİL.
    PROPER span: PER (→kişi adı) veya PROPER alır; typed LOC/ORG almaz (Kadirhan Ankara ayrı).
    """
    if span_type == "PER":
        return t2 in ("PER", "PROPER")
    if span_type in ("LOC", "ORG"):
        return t2 == "PROPER" and _tr_lower(b2) in _HEAD_NOUNS
    if span_type == "PROPER":
        return t2 in ("PER", "PROPER")
    return False


def _merge_spans(per: "list[tuple[str, str, int]]") -> list[ProperNoun]:
    """Bitişik + KATILABİLİR (yön+tip-farkındalıklı, `_can_join`) özel-ad tokenlarını tek
    span'e birleştir (SPEC §10). per: (base, type, idx) artan idx."""
    spans: list[ProperNoun] = []
    i = 0
    while i < len(per):
        base, typ, idx = per[i]
        toks = [base]
        span_type = typ
        j = i + 1
        while j < len(per):
            b2, t2, idx2 = per[j]
            if idx2 != per[j - 1][2] + 1:            # bitişik değil (araya token girdi)
                break
            if not _can_join(span_type, t2, b2):
                break
            toks.append(b2)
            if span_type == "PROPER" and t2 != "PROPER":
                span_type = t2                        # PROPER → PER'e yükselir (kişi adı)
            j += 1
        spans.append(ProperNoun(" ".join(toks), span_type, idx, tuple(toks)))
        i = j
    return spans


def tag(text: str, *, roots: "Collection[str] | None" = None) -> list[ProperNoun]:
    """Metni tokenize et + özel-ad VARLIKLARINI etiketle (SPEC §3, §10). Apostrof-ek + çok-token
    span birleştirilir (`Mustafa Kemal Atatürk` → tek PER; `Ali Ankara'ya` → ayrı PER+LOC).

    roots (lexicon.load()) verilirse cümle-başı ortak-ad danışması yapılır (Kitap=ortak→değil,
    Kadirhan=OOV→PROPER). roots=None → cümle-başı OOV varsayılan PROPER.
    """
    toks = _tokenize(text)
    per: list[tuple[str, str, int]] = []   # (base, type, 1-tabanlı idx) — proper tokenlar
    for i, tok in enumerate(toks):
        # ASCII/kıvrık apostrof-ek tokenı (önceki ada ait) → özel ad değil, atla
        if tok[:1] in ("'", "’"):
            continue
        base, _ = _strip_apostrophe(tok)
        # apostrof sinyali: bu token kıvrık-apostroflu VEYA sonraki token 'ek (ASCII bölünmüş)
        has_apos = ("'" in tok or "’" in tok
                    or (i + 1 < len(toks) and toks[i + 1][:1] in ("'", "’")))
        sentence_initial = (i == 0)
        # cümle-başı büyük-harf belirsizliği (Onu/Kitap vs Kadirhan): çekimli ortak sözcük
        # lemma-kümesinde YOK → analyze() danışması (gerçek çözümleme varsa ortak ad).
        is_common = False
        if (sentence_initial and not has_apos and base[:1].isupper()
                and _tr_lower(base) not in _ALL_GAZETTEER):
            is_common = any(not a.hypothetical for a in _analyze(base, roots=roots))
        surf = base + "'" if has_apos else base
        t = proper_type(surf, sentence_initial=sentence_initial, is_common=is_common)
        if t is not None:
            per.append((base, t, i + 1))
    return _merge_spans(per)
