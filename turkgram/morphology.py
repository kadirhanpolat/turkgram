"""TR fiil çekim motoru (roadmap 2a, CLAUDE.md #5).

Saf Python 3, dış bağımlılık YOK. Kurallar: morphology-spec.md.
Türkçe biçimleri SAKLAMAZ, ÜRETİR (kök + morfofonolojik sınıf).

Değişmezler:
- Kurallar saf fonksiyonlarda; mutasyon yok.
- Harmoni/ek-realizasyon yardımcıları ayrı.
"""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# 6. İstisna tablosu (SPEC §6) — küçük kapalı küme
# ---------------------------------------------------------------------------
IRREGULAR: dict[str, str] = {
    # aorist -Ir/-Ur alan 13 tek-heceli
    "almak": "Ir", "bilmek": "Ir", "bulmak": "Ir", "durmak": "Ir",
    "gelmek": "Ir", "görmek": "Ir", "kalmak": "Ir", "olmak": "Ir",
    "ölmek": "Ir", "sanmak": "Ir", "varmak": "Ir", "vermek": "Ir",
    "vurmak": "Ir",
    # kök yumuşaması (t→d, yalnız ünlü önünde)
    "gitmek": "soft", "etmek": "soft", "tatmak": "soft", "gütmek": "soft",
    # ye/de sınıfı (e→i, y + yüksek ünlü önünde)
    "yemek": "ye_de", "demek": "ye_de",
}

# ---------------------------------------------------------------------------
# 2.1 Ünlüler
# ---------------------------------------------------------------------------
VOWELS = "aıoueiöü"
BACK = set("aıou")      # arka
FRONT = set("eiöü")     # ön
ROUND = set("oöuü")     # yuvarlak
HARD_CONS = set("fstkçşhp")  # "fıstıkçı şahap" — sert ünsüzler

TENSES = ("pres", "past", "fut", "aorist", "evid", "cond", "necess",
          "opt", "imp", "conv_arak", "part_dik")
PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


# ---------------------------------------------------------------------------
# Harmoni yardımcıları (saf) — SPEC §2.2
# ---------------------------------------------------------------------------
def last_vowel(word: str) -> str | None:
    for ch in reversed(word):
        if ch in VOWELS:
            return ch
    return None


def low_vowel(stem: str) -> str:
    """A-tipi (2'li): arka→a, ön→e."""
    v = last_vowel(stem)
    if v is None:
        raise ValueError(f"ünlüsüz gövde, harmoni üretilemez: {stem!r}")
    return "a" if v in BACK else "e"


def high_vowel(stem: str) -> str:
    """I-tipi (4'lü): arka+düz→ı, ön+düz→i, arka+yuv→u, ön+yuv→ü."""
    v = last_vowel(stem)
    if v is None:
        raise ValueError(f"ünlüsüz gövde, harmoni üretilemez: {stem!r}")
    back = v in BACK
    rnd = v in ROUND
    if back and rnd:
        return "u"
    if back:
        return "ı"
    if rnd:
        return "ü"
    return "i"


def ends_in_vowel(stem: str) -> bool:
    return bool(stem) and stem[-1] in VOWELS


def hardens(stem: str) -> bool:
    """Gövde sert ünsüzle mi bitiyor (ek-başı sertleşme)? SPEC §2.3."""
    return bool(stem) and stem[-1] in HARD_CONS


# ---------------------------------------------------------------------------
# 1. VerbStem — parse_verb
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class VerbStem:
    lemma: str
    prefix: str          # birleşik fiilde önceki tokenlar ("aday ")
    root: str            # çekilecek çıplak kök ("gel", "oku")
    aorist_ir: bool      # aorist -Ir/-Ur mu (leksik)
    softens: bool        # git→gid gibi t→d yumuşaması
    special: str | None  # 'ye_de' | None
    aorist_forced: str | None = None  # tasvir gövdesinde aoristi yardımcı fiilden zorla ('Ir'/'Ar')

    def to_dict(self) -> dict:
        return {
            "root": self.root, "aorist_ir": self.aorist_ir,
            "softens": self.softens, "special": self.special,
            "harmony_back": last_vowel(self.root) in BACK,
        }


def _strip_infinitive(token: str) -> str:
    """'gelmek'→'gel', 'okumak'→'oku'."""
    if token.endswith("mek") or token.endswith("mak"):
        return token[:-3]
    return token


def parse_verb(lemma: str) -> VerbStem:
    lemma = lemma.strip()
    tokens = lemma.split(" ")
    last = tokens[-1]
    prefix = "".join(t + " " for t in tokens[:-1])

    flag = IRREGULAR.get(last)
    root = _strip_infinitive(last)

    return VerbStem(
        lemma=lemma,
        prefix=prefix,
        root=root,                       # sert kök (ünsüz-başlı ek için)
        aorist_ir=(flag == "Ir"),
        softens=(flag == "soft"),
        special=(flag if flag == "ye_de" else None),
    )


# ---------------------------------------------------------------------------
# Kök varyantı seçimi — yumuşama + ye/de (SPEC §2.7, §2.8)
# ---------------------------------------------------------------------------
def _stem_before_suffix(vs: VerbStem, vowel_initial: bool) -> str:
    """Ünlü-başlı ek önünde uygun kök varyantını döndürür.

    - softens: t→d yalnız ÜNLÜ-başlı ek önünde (git→gid, ama git-ti sert kalır).
    - ye_de: e→i kaynaştırma -y- girdiği her yerde = ünlü-başlı ek önünde
      (yiyecek, yiyerek, yiyebilir). Ünsüz-başlı ekte (-r aorist, -DI) e kalır:
      yer, yedi. (SPEC §2.8 düzeltilmiş kural, 2026-07-11.)
    """
    root = vs.root
    if vs.softens and vowel_initial and root.endswith("t"):
        root = root[:-1] + "d"
    if vs.special == "ye_de" and vowel_initial and root.endswith("e"):
        root = root[:-1] + "i"
    return root


# ---------------------------------------------------------------------------
# Negatif taban (-mA / -AmA) — SPEC §4
# ---------------------------------------------------------------------------
def _negative_stem(vs: VerbStem, ability: bool) -> str:
    """Olumsuz gövde: kök + -mA (ability ise -A(y)AmA). Ünlü-final."""
    root = vs.root  # -mA ünsüz-başlı → yumuşama/ye_de tetiklenmez
    a = low_vowel(root)
    if ability:
        link = "y" if ends_in_vowel(root) else ""
        # gel-e-me, yap-a-ma, oku-y-ama
        return root + link + low_vowel(root) + "m" + a
    return root + "m" + a


# ---------------------------------------------------------------------------
# Ability (-Abil) tabanı — SPEC §5
# ---------------------------------------------------------------------------
def _ability_stem(vs: VerbStem) -> str:
    root = _stem_before_suffix(vs, vowel_initial=True)
    link = "y" if ends_in_vowel(root) else ""
    return root + link + low_vowel(root) + "bil"


# ---------------------------------------------------------------------------
# Kişi ekleri (SPEC §3)
# ---------------------------------------------------------------------------
def _person_group1(stem: str, person: str) -> str:
    """-DI / -sA sonrası (k-tipi). stem ünsüz/ünlü-final olabilir."""
    i = high_vowel(stem)
    endings = {
        "1sg": "m", "2sg": "n", "3sg": "", "1pl": "k",
        "2pl": "n" + i + "z", "3pl": "l" + low_vowel(stem) + "r",
    }
    return stem + endings[person]


def _opt_person(stem: str, person: str) -> str:
    """İstek kipi kişi ekleri (SPEC §10.1). stem = -A işaretleyicili gövde
    (ünlü-final: gele/ala/gideye). 1sg/1pl kaynaştırma -y-."""
    i = high_vowel(stem)
    a = low_vowel(stem)
    endings = {
        "1sg": "y" + i + "m", "2sg": "s" + i + "n", "3sg": "",
        "1pl": "l" + i + "m", "2pl": "s" + i + "n" + i + "z",
        "3pl": "l" + a + "r",
    }
    return stem + endings[person]


def _person_group2(stem: str, person: str) -> str:
    """-Iyor/-AcAk/-Ir/-mIş/-mAlI sonrası (z-tipi).

    stem ünsüz-final varsayılır (yor, cak, r, mış). Ünlü-final (-mAlI) için
    çağıran kaynaştırma y'yi ekler.
    """
    i = high_vowel(stem)
    endings = {
        "1sg": i + "m", "2sg": "s" + i + "n", "3sg": "",
        "1pl": i + "z", "2pl": "s" + i + "n" + i + "z",
        "3pl": "l" + low_vowel(stem) + "r",
    }
    return stem + endings[person]


# ---------------------------------------------------------------------------
# -Iyor (şimdiki zaman) — SPEC §2.5
# ---------------------------------------------------------------------------
def _pres_stem(base: str) -> str:
    """base = pozitif/negatif/ability gövdesi. -Iyor ekler (ünlü-final gövdede
    son ünlü düşer: başla→başlıyor, ye→yiyor)."""
    if ends_in_vowel(base):
        # son ünlü düşer + harmonik yüksek ünlü + yor.
        # trimmed ünlüsüz kalırsa (di→d) harmoniyi base'ten al (diyor).
        trimmed = base[:-1]
        harmony_src = trimmed if last_vowel(trimmed) else base
        return trimmed + high_vowel(harmony_src) + "yor"
    return base + high_vowel(base) + "yor"


# ---------------------------------------------------------------------------
# conjugate — merkez
# ---------------------------------------------------------------------------
AUX = ("hikaye", "rivayet", "sart")  # ek-fiil / birleşik zaman (SPEC §11)


# ---------------------------------------------------------------------------
# Tasvir fiilleri (aktionsart) — SPEC aspect-spec.md. Esas fiil + bağ ünlü +
# yardımcı fiil (ver/dur/gel/kal/yaz); oluşan gövde NORMAL fiil gibi çekilir.
# ---------------------------------------------------------------------------
_ASPECT = {                       # aspect: (yardımcı_kök, bağ_ünlü_tipi, aorist_ir)
    "iver": ("ver", "I", True),   # tezlik
    "adur": ("dur", "A", True),   # sürerlik
    "agel": ("gel", "A", True),
    "akal": ("kal", "A", True),   # kalma
    "ayaz": ("yaz", "A", False),  # yaklaşma (yaz düzenli -Ar)
}
ASPECTS = frozenset(_ASPECT)


def _aspect_stem(vs: VerbStem, aspect: str) -> VerbStem:
    """Esas fiili tasvir gövdesine dönüştür (gövde + bağ ünlü + yardımcı fiil).
    Bağ ünlü ünlü-başlı → yumuşama/ye_de tetiklenir (git→gid, ye→yi); ünlü-final
    kökte kaynaştırma -y-. Yardımcı fiil kendi aorist tipini (ver/dur/gel/kal -Ir,
    yaz -Ar) taşır."""
    aux_root, link, aor = _ASPECT[aspect]
    stem = _stem_before_suffix(vs, vowel_initial=True)
    y = "y" if ends_in_vowel(stem) else ""
    lv = high_vowel(stem) if link == "I" else low_vowel(stem)
    root = stem + y + lv + aux_root
    # aorist: çok-heceli tasvir gövdesinde sezgi (-Ir) yaz'ı bozar → yardımcıdan zorla.
    return VerbStem(lemma=root + "mek", prefix=vs.prefix, root=root,
                    aorist_ir=aor, softens=False, special=None,
                    aorist_forced=("Ir" if aor else "Ar"))


def conjugate(lemma: str, tense: str, person: str | None = None,
              *, negative: bool = False, ability: bool = False,
              question: bool = False, aux: str | None = None,
              aspect: str | None = None) -> str | None:
    """Tek biçim üret. Türkçede olmayan hücrede (emir 1sg/1pl, soru-imp) None
    döner (paradigm bunları atlar); geçersiz tense/person/aux/aspect ValueError.

    aux (birleşik zaman): 'hikaye'|'rivayet'|'sart' → basit gövde + ek-fiil.
    aspect (tasvir): 'iver'|'adur'|'agel'|'akal'|'ayaz' → gövde tasvir fiiline
    dönüşür, sonra tense/olumsuz/soru/aux ona işler (yapıverdi, gidedururyor).
    question ile birleşince mI gövde-ekfiil arasına girer (geliyor muydum)."""
    vs = parse_verb(lemma)
    if tense not in TENSES:
        raise ValueError(f"bilinmeyen tense: {tense}")
    if person is not None and person not in PERSONS:
        raise ValueError(f"bilinmeyen person: {person}")
    if aux is not None and aux not in AUX:
        raise ValueError(f"bilinmeyen aux: {aux}")
    if aspect is not None:
        if aspect not in _ASPECT:
            raise ValueError(f"bilinmeyen aspect: {aspect}")
        vs = _aspect_stem(vs, aspect)

    if aux is not None:
        return _conjugate_aux(vs, tense, person or "3sg", negative=negative,
                              ability=ability, question=question, aux=aux)

    if question:
        return _conjugate_question(vs, tense, person or "3sg",
                                   negative=negative, ability=ability)

    body = _conjugate_core(vs, tense, person, negative=negative, ability=ability)
    if body is None:
        return None
    return vs.prefix + body


# ---------------------------------------------------------------------------
# Soru (interrogative -mI) — SPEC §10.2. tense değil, BOYUT.
# ---------------------------------------------------------------------------
# k-tipi (Grup 1 kişi eki): mI en SONA. z-tipi: mI gövdeden sonra, kişi mI'ye.
_QUESTION_TYPE_B = frozenset({"past", "cond", "opt"})
_QUESTION_NA = frozenset({"imp", "conv_arak", "part_dik"})


def _q_particle(prev_word: str) -> str:
    """mI edatı, önceki sözcüğün son ünlüsüne 4'lü uyumlu (mı/mi/mu/mü)."""
    return "m" + high_vowel(prev_word)


def _q_person_a(mi: str, person: str) -> str:
    """z-tipi zamanlarda kişi eki mI edatına biner (mI ünlü-final)."""
    i = high_vowel(mi)
    endings = {
        "1sg": "y" + i + "m", "2sg": "s" + i + "n", "3sg": "",
        "1pl": "y" + i + "z", "2pl": "s" + i + "n" + i + "z",
    }
    return mi + endings[person]


def _conjugate_question(vs: VerbStem, tense: str, person: str,
                        *, negative: bool, ability: bool) -> str | None:
    if tense in _QUESTION_NA:
        return None                       # emir/ulaç/ortaç soru almaz
    kw = {"negative": negative, "ability": ability}
    # k-tipi VEYA 3pl → tam çekimli biçim + " " + mI (edat sona).
    if tense in _QUESTION_TYPE_B or person == "3pl":
        full = _conjugate_core(vs, tense, person, **kw)
        if full is None:
            return None
        return f"{vs.prefix}{full} {_q_particle(full)}"
    # z-tipi, 3pl değil → bare gövde (3sg biçimi) + " " + mI + kişi(mI'de).
    stem = _conjugate_core(vs, tense, "3sg", **kw)
    if stem is None:
        return None
    return f"{vs.prefix}{stem} {_q_person_a(_q_particle(stem), person)}"


# ---------------------------------------------------------------------------
# Birleşik zaman (ek-fiil i-di/i-miş/i-se) — SPEC §11. aux boyutu.
# ---------------------------------------------------------------------------
_AUX_NA = frozenset({"imp", "conv_arak", "part_dik"})  # ek-fiil almaz


def _ekfiil(stem: str, aux: str, person: str) -> str:
    """`stem`'e ek-fiil (i-di/i-miş/i-se) + kişi ekle. stem ünlü/ünsüz-final
    olabilir (ünlü-finalde kaynaştırma -y-)."""
    vf = ends_in_vowel(stem)
    link = "y" if vf else ""
    if aux == "hikaye":                              # -(y)DI + k-tipi
        d = "t" if (not vf and hardens(stem)) else "d"
        di = stem + link + d + high_vowel(stem)      # geliyordu / gelecekti
        return _person_group1(di, person)
    if aux == "rivayet":                             # -(y)mIş + z-tipi
        mis = stem + link + "m" + high_vowel(stem) + "ş"
        return _person_group2(mis, person)
    # sart: -(y)sA + k-tipi
    sa = stem + link + "s" + low_vowel(stem)         # geliyorsa
    return _person_group1(sa, person)


def _conjugate_aux(vs: VerbStem, tense: str, person: str, *, negative: bool,
                   ability: bool, question: bool, aux: str) -> str | None:
    if tense in _AUX_NA:
        return None                                  # emir/ulaç/ortaç birleşmez
    kw = {"negative": negative, "ability": ability}
    # 3pl: -lAr BASİT gövdede, ek-fiil 3sg (geliyorlardı). Aksi: bare gövde (3sg).
    base_person = "3pl" if person == "3pl" else "3sg"
    base = _conjugate_core(vs, tense, base_person, **kw)
    if base is None:
        return None
    ek_person = "3sg" if person == "3pl" else person
    if question:
        # mI gövde ile ek-fiil ARASINA girer; ek-fiil+kişi mI'ye biner.
        mi = _q_particle(base)
        return f"{vs.prefix}{base} {_ekfiil(mi, aux, ek_person)}"
    return vs.prefix + _ekfiil(base, aux, ek_person)


def _conjugate_core(vs: VerbStem, tense: str, person: str | None,
                    *, negative: bool, ability: bool) -> str | None:
    # --- Aorist olumsuz ÖZEL kalıp (SPEC §2.6) ---
    if tense == "aorist" and negative:
        return _aorist_negative(vs, ability, person)

    # --- Taban seçimi (ability > negative > düz) ---
    if ability and negative:
        base_vowel_final = True
        base = _negative_stem(vs, ability=True)   # -AmA-, ünlü-final
        base_is_negative = True
    elif ability:
        base = _ability_stem(vs)                  # -Abil, ünsüz-final (l)
        base_vowel_final = False
        base_is_negative = False
    elif negative:
        base = _negative_stem(vs, ability=False)  # -mA, ünlü-final
        base_vowel_final = True
        base_is_negative = True
    else:
        base = None
        base_vowel_final = None
        base_is_negative = False

    # --- Şimdiki zaman -Iyor ---
    if tense == "pres":
        stem = base if base is not None else vs.root
        if base is None:
            # düz: ye_de e→i (yüksek), softens t→d (ünlü önünde 'i')
            stem = _stem_before_suffix(vs, vowel_initial=True)
        pres = _pres_stem(stem)
        return _person_group2(pres, person or "3sg")

    # --- Gelecek -AcAk ---
    if tense == "fut":
        stem = base if base is not None else \
            _stem_before_suffix(vs, vowel_initial=True)
        a = low_vowel(stem)
        link = "y" if ends_in_vowel(stem) else ""
        acak = stem + link + a + "c" + a + "k"
        return _fut_person(acak, person or "3sg")

    # --- Görülen geçmiş -DI ---
    if tense == "past":
        stem = base if base is not None else vs.root  # ünsüz-başlı → sert kök
        return _past_stem(stem, person or "3sg", vowel_final=(base_vowel_final if base is not None else ends_in_vowel(stem)))

    # --- Öğrenilen geçmiş -mIş ---
    if tense == "evid":
        stem = base if base is not None else vs.root
        i = high_vowel(stem)
        mis = stem + "m" + i + "ş"
        return _person_group2(mis, person or "3sg")

    # --- Dilek-şart -sA ---
    if tense == "cond":
        stem = base if base is not None else vs.root
        sa = stem + "s" + low_vowel(stem)
        return _person_group1(sa, person or "3sg")

    # --- Gereklilik -mAlI ---
    if tense == "necess":
        stem = base if base is not None else vs.root
        a = low_vowel(stem)
        mali = stem + "m" + a + "l" + high_vowel(stem + a)
        return _necess_person(mali, person or "3sg")

    # --- İstek kipi -A (SPEC §10.1) ---
    if tense == "opt":
        # -A ünlü-BAŞLI ek → yumuşama/ye_de tetikler (gide, yiye).
        stem = base if base is not None else \
            _stem_before_suffix(vs, vowel_initial=True)
        link = "y" if ends_in_vowel(stem) else ""
        opt = stem + link + low_vowel(stem)          # gele, ala, gideye…
        return _opt_person(opt, person or "3sg")

    # --- Aorist olumlu (SPEC §2.6) ---
    if tense == "aorist":
        # ye/de vowel-final: aorist -r ÜNSÜZ-başlı → e→i yok (yer, yir DEĞİL).
        # git consonant-final: aorist -Ar ünlü-başlı → yumuşama (gider).
        stem = base if base is not None else \
            _stem_before_suffix(vs, vowel_initial=not ends_in_vowel(vs.root))
        aor = _aorist_positive_stem(vs, stem, ability, base_is_negative)
        return _person_group2(aor, person or "3sg")

    # --- Emir (SPEC §3.3) ---
    if tense == "imp":
        return _imperative(vs, base, ability, negative, person or "2sg")

    # --- Ulaç -ArAk (kişisiz) ---
    if tense == "conv_arak":
        stem = base if base is not None else \
            _stem_before_suffix(vs, vowel_initial=True)
        a = low_vowel(stem)
        link = "y" if ends_in_vowel(stem) else ""
        return stem + link + a + "r" + a + "k"

    # --- Ortaç -DIğI (kişisiz, 3sg iyelikli varsayılan) ---
    if tense == "part_dik":
        stem = base if base is not None else vs.root
        i = high_vowel(stem)
        d = "t" if hardens(stem) else "d"
        # -DIğI: dık/dik/duk/dük + iyelik ı/i/u/ü
        return stem + d + i + "ğ" + i

    raise ValueError(f"işlenmemiş tense: {tense}")


# ---------------------------------------------------------------------------
# Yardımcı ek-realizasyonları
# ---------------------------------------------------------------------------
def _fut_person(acak: str, person: str) -> str:
    """-AcAk + kişi; 1sg/1pl'de k→ğ (geleceğim, geleceğiz)."""
    i = high_vowel(acak)
    if person in ("1sg", "1pl"):
        soft = acak[:-1] + "ğ"  # k→ğ
        end = i + "m" if person == "1sg" else i + "z"
        return soft + end
    return _person_group2(acak, person)


def _past_stem(stem: str, person: str, vowel_final: bool) -> str:
    """-DI + kişi (Grup 1). Sertleşme + kaynaştırma yok (ünsüz-başlı)."""
    d = "t" if hardens(stem) else "d"
    i = high_vowel(stem)
    di = stem + d + i
    return _person_group1(di, person)


def _necess_person(mali: str, person: str) -> str:
    """-mAlI + kişi; ünlü-final → kaynaştırma y (gelmeliyim)."""
    i = high_vowel(mali)
    endings = {
        "1sg": "y" + i + "m", "2sg": "s" + i + "n", "3sg": "",
        "1pl": "y" + i + "z", "2pl": "s" + i + "n" + i + "z",
        "3pl": "l" + low_vowel(mali) + "r",
    }
    return mali + endings[person]


def _aorist_positive_stem(vs: VerbStem, stem: str, ability: bool,
                          is_negative: bool) -> str:
    """Aorist olumlu gövdesi (kişi eki hariç)."""
    if ends_in_vowel(stem):
        return stem + "r"          # bekle-r, oku-r, -Abil değil (l ünsüz)
    if ability or is_negative:
        # -Abil (ünsüz l) çok-heceli → -Ir; negatif zaten özel kalıpta
        return stem + high_vowel(stem) + "r"
    if vs.aorist_forced == "Ar":                     # tasvir yaz → -Ar (çok-heceli olsa da)
        return stem + low_vowel(stem) + "r"
    if vs.aorist_forced == "Ir":                     # tasvir ver/dur/gel/kal → -Ir
        return stem + high_vowel(stem) + "r"
    # tek-heceli düz ünsüz-final: leksik bayrak
    syllables = sum(1 for ch in vs.root if ch in VOWELS)
    if syllables <= 1:
        if vs.aorist_ir:
            return stem + high_vowel(stem) + "r"    # gel-ir, al-ır, ol-ur
        return stem + low_vowel(stem) + "r"          # yap-ar, yaz-ar
    # çok heceli ünsüz-final → -Ir/-Ur
    return stem + high_vowel(stem) + "r"


def _aorist_negative(vs: VerbStem, ability: bool, person: str | None) -> str:
    """Aorist olumsuz ÖZEL kalıp (SPEC §2.6). ability → -AmA tabanı."""
    person = person or "3sg"
    if ability:
        neg = _negative_stem(vs, ability=True)      # gel-e-me, ünlü-final
    else:
        neg = _negative_stem(vs, ability=False)     # gel-me, ünlü-final
    i = high_vowel(neg)
    a = low_vowel(neg)
    # 1. kişilerde z DÜŞER: -mAm / -mAyIz
    if person == "1sg":
        return neg + "m"                             # gelmem
    if person == "1pl":
        return neg + "y" + i + "z"                   # gelmeyiz
    # diğerlerinde -mAz tabanı
    maz = neg + "z"                                  # gelmez
    endings = {
        "2sg": "s" + i + "n", "3sg": "",
        "2pl": "s" + i + "n" + i + "z",
        "3pl": "l" + a + "r",
    }
    return maz + endings[person]


def _imperative(vs: VerbStem, base: str | None, ability: bool,
                negative: bool, person: str) -> str | None:
    """Emir kipi (SPEC §3.3). base = negatif/ability gövdesi ya da None."""
    if person in ("1sg", "1pl"):
        return None  # emir 1. kişi yok

    if base is not None:
        stem_vowel = base                            # ünlü-final (-mA/-AmA)
        stem_cons = base
    else:
        # 2sg emir = çıplak kök (yumuşama ünlü-başlı ek YOK → sert kök)
        stem_vowel = _stem_before_suffix(vs, vowel_initial=True)
        stem_cons = vs.root

    if person == "2sg":
        # kökün kendisi; softens/ye_de yalnız ünlü-başlı ek önünde → burada YOK
        return base if base is not None else vs.root
    if person == "3sg":
        i = high_vowel(stem_cons)
        return stem_cons + "s" + i + "n"             # gelsin, gelmesin
    if person == "2pl":
        s = stem_vowel
        i = high_vowel(s)
        link = "y" if ends_in_vowel(s) else ""
        return s + link + i + "n"                     # gelin, okuyun, gelmeyin
    if person == "3pl":
        i = high_vowel(stem_cons)
        return stem_cons + "s" + i + "nl" + low_vowel(stem_cons) + "r"
    return None


# ---------------------------------------------------------------------------
# inflect_last_token — birleşik fiil yardımcısı
# ---------------------------------------------------------------------------
def inflect_last_token(lemma: str, tense: str, person: str | None = None,
                       *, negative: bool = False, ability: bool = False,
                       question: bool = False, aux: str | None = None) -> str | None:
    """'aday olmak' → yalnız 'olmak' çekilir, 'aday ' öne eklenir.

    Birleşik-fiil çekimi zaten conjugate/parse_verb (prefix ayırma) tarafından
    yapılır; bu ad SPEC §1'in okunaklı çağrı yüzüdür (aynı davranış, açık niyet)."""
    return conjugate(lemma, tense, person, negative=negative, ability=ability,
                     question=question, aux=aux)


# ---------------------------------------------------------------------------
# paradigm — tüm tense × person, olumlu + olumsuz
# ---------------------------------------------------------------------------
_PERSONAL = ("pres", "past", "fut", "aorist", "evid", "cond", "necess",
             "opt", "imp")
_IMPERSONAL = ("conv_arak", "part_dik")


def paradigm(lemma: str) -> dict:
    out: dict[str, str] = {}
    for tense in _PERSONAL:
        for person in PERSONS:
            for neg in (False, True):
                key = f"{tense}.{person}"
                if neg:
                    key = f"neg.{key}"
                val = conjugate(lemma, tense, person, negative=neg)
                if val is not None:
                    out[key] = val
    for tense in _IMPERSONAL:
        for neg in (False, True):
            key = tense if not neg else f"neg.{tense}"
            val = conjugate(lemma, tense, None, negative=neg)
            if val is not None:
                out[key] = val
    # ability örnekleri (pres 3sg)
    out["ability.pres.3sg"] = conjugate(lemma, "pres", "3sg", ability=True)
    out["ability.aorist.3sg"] = conjugate(lemma, "aorist", "3sg", ability=True)
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        print(conjugate(sys.argv[1], sys.argv[2],
                        sys.argv[3] if len(sys.argv) > 3 else None))
    else:
        for k, v in paradigm("gelmek").items():
            print(f"{k:24} {v}")
