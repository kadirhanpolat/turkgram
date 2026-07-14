"""TR isim çekim motoru — faz 2 (roadmap 2a, CLAUDE.md #5).

Saf Python 3, dış bağımlılık YOK. Kurallar: morphology-noun-spec.md.
Türkçe biçimleri SAKLAMAZ, ÜRETİR (kök + morfofonolojik sınıf).

Harmoni yardımcıları fiil motorundan (morphology.py) IMPORT edilir (DRY);
fiil motoru ve 728 testi bozulmaz.

Değişmezler:
- Kurallar saf fonksiyonlarda; mutasyon yok.
- İstisna tabloları KAPALI ve küçük; kapsam eksiği tabloya eklenir, kural değişmez.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .morphology import (
    VOWELS, BACK, FRONT, ROUND, HARD_CONS,
    last_vowel as _last_vowel_raw,
    low_vowel as _low_vowel_raw,
    high_vowel as _high_vowel_raw,
    hardens,
)

# ---------------------------------------------------------------------------
# Diakritik / büyük-harf normalizasyonu — YALNIZ harmoni algısı için.
# Çıktı ham kökle üretilir (çıktıda â/büyük harf KORUNUR); yalnız ünlü uyumu
# hesabında â→a, î→i, û→u ve Türkçe-duyarlı büyük→küçük eşlemesi yapılır (#10).
# Böylece 'kâr'→kârı, 'Al'→Alı gibi girdiler ünlüsüz-guard'a ÇÖKMEDEN üretilir;
# gerçekten ünlüsüz gövdede (bozuk düşme sonucu 'cht') guard KORUNUR (gizli hata).
# ---------------------------------------------------------------------------
_HARMONY_NORM = {
    "â": "a", "î": "i", "û": "u", "Â": "a", "Î": "i", "Û": "u",
    "A": "a", "E": "e", "I": "ı", "İ": "i", "O": "o", "Ö": "ö",
    "U": "u", "Ü": "ü",
}


def _norm_harmony(s: str) -> str:
    return "".join(_HARMONY_NORM.get(c, c) for c in s)


def last_vowel(word: str) -> str | None:
    return _last_vowel_raw(_norm_harmony(word))


def low_vowel(stem: str) -> str:
    return _low_vowel_raw(_norm_harmony(stem))


def high_vowel(stem: str) -> str:
    return _high_vowel_raw(_norm_harmony(stem))


def ends_in_vowel(word: str) -> bool:
    return bool(word) and _norm_harmony(word[-1]) in VOWELS

# ---------------------------------------------------------------------------
# İstisna tabloları (SPEC §3.2 / §3.3 / §3.4 / §8) — küçük kapalı küme.
# Küratörlü; kapsam eksiği buraya eklenir, kural değişmez.
# ---------------------------------------------------------------------------

# §3.2 — çok-heceli p/ç/t/k biten ama SERT kalan (softens = False):
SOFTEN_NO: set[str] = {
    "sepet", "millet", "devlet", "saat", "dikkat", "sıfat", "sanat",
    "hukuk", "merak", "ahlak", "taahhüt", "kanaat", "hayat", "hâkant",
    "hizmet", "hürriyet", "kuvvet", "gayret", "işaret", "surat", "ziraat",
    "cumhuriyet", "millet", "sürat", "şefkat", "cesaret",
    "faaliyet", "hakikat", "seyahat",
    # drops_vowel ama t SERT kalan (SPEC §3.3: vakit→vakti, vakdi DEĞİL)
    "vakit",
}

# §3.2 — tek-heceli p/ç/t/k biten ama YUMUŞAYAN (softens = True):
SOFTEN_YES: set[str] = {
    "dip", "uç", "kap", "but", "kurt", "yurt", "cilt", "renk", "denk",
    "çelenk", "gök", "kürk", "kayıp", "araç", "amaç", "borç", "burç",
    "güç", "hesap", "kalp", "kürsü", "harç", "ilaç", "kanat", "genç",
}

# §3.3 — ünlü düşmesi (drops_vowel) TAMAMEN leksik. Çoğu 2 heceli, son hece dar.
DROP_VOWEL: set[str] = {
    "ağız", "alın", "boyun", "burun", "göğüs", "karın", "oğul", "gönül",
    "şehir", "fikir", "isim", "resim", "akıl", "nakil", "sabır", "beyin",
    "koyun", "ömür", "vakit", "metin", "zehir", "nehir", "hüküm", "emir",
    "kavim", "cürüm", "keşif", "kısım", "şükür", "asıl", "nesil",
    "seyir", "devir", "kayıp", "meyil", "haciz",
    # ÇIKARILDI (hakem 2026-07-11): sınıf→sınıfı, gurur→gururu DÜŞMEZ;
    # ceht→cehdi (e düşmez, t yumuşar) — ceht dropped'ta "cht" ünlüsüz üretiyordu.
}

# §3.4 — ikizleşme (doubles) TAMAMEN leksik (yaygın Arapça alıntılar).
# ret/cet: DOUBLE + t→d birlikte (ret→redd, cet→cedd; root_variant double dalı).
DOUBLE: set[str] = {
    "hak", "his", "af", "sır", "ret", "had", "hat", "tıp", "zam", "şık",
    "cet", "zan", "hac", "set", "üs", "fen",
}

# §8 — zamir / özel-ad istisnaları. Her durum tam biçim (kapalı tablo).
# Anahtar: başlık; değer: {case: biçim}. nom = başlığın kendisi.
PRONOUN_FORMS: dict[str, dict[str, str]] = {
    "ben": {"acc": "beni", "dat": "bana", "loc": "bende", "abl": "benden",
            "gen": "benim", "ins": "benimle"},
    "sen": {"acc": "seni", "dat": "sana", "loc": "sende", "abl": "senden",
            "gen": "senin", "ins": "seninle"},
    "o": {"acc": "onu", "dat": "ona", "loc": "onda", "abl": "ondan",
          "gen": "onun", "ins": "onunla"},
    "bu": {"acc": "bunu", "dat": "buna", "loc": "bunda", "abl": "bundan",
           "gen": "bunun", "ins": "bununla"},
    "şu": {"acc": "şunu", "dat": "şuna", "loc": "şunda", "abl": "şundan",
           "gen": "şunun", "ins": "şununla"},
    "biz": {"acc": "bizi", "dat": "bize", "loc": "bizde", "abl": "bizden",
            "gen": "bizim", "ins": "bizimle"},
    "siz": {"acc": "sizi", "dat": "size", "loc": "sizde", "abl": "sizden",
            "gen": "sizin", "ins": "sizinle"},
    "ne": {"acc": "neyi", "dat": "neye", "loc": "nede", "abl": "neden",
           "gen": "neyin", "ins": "neyle"},
    "su": {"acc": "suyu", "dat": "suya", "loc": "suda", "abl": "sudan",
           "gen": "suyun", "ins": "suyla"},
}

# §7.3 — -ki uyum gösteren KAPALI küme (yalnız bunlar; başkası değişmez -ki).
Kİ_ROUND: set[str] = {"bugün", "dün", "gün", "öbür"}

# Harmoni-kırıcı alıntılar: arka-ünlülü yazılıp ÖN-ünlülü ek alan kapalı küme
# (saat→saati, saatte; kalp→kalbi; harf→harfi). last_vowel arka verir ama ek
# ön-ünlülü gelir. Bu yalnız HARMONİ yönünü çevirir; yumuşama ayrı bayrak.
# Küratörlü, kapalı; kapsam eksiği buraya eklenir.
FRONT_HARMONY: set[str] = {
    "saat", "harf", "hal", "kalp", "rol", "gol", "hakikat", "kabul",
    "usul", "itibar", "alkol", "menkul", "meşgul", "sual", "ihtimal",
    "istikbal", "ideal", "lokal", "moral", "petrol", "protokol",
    # ünlü-düşmeli alıntı: kalan ünlü arka (vakt) ama ek ön (vakti/vakte)
    "vakit",
}

CASES = ("nom", "acc", "dat", "loc", "abl", "gen", "ins")
NUMBERS = ("sg", "pl")
POSSESSIVES = (None, "1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


# ---------------------------------------------------------------------------
# 2. NounStem — parse_noun (SPEC §2)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class NounStem:
    headword: str
    prefix: str          # birleşik isimde önceki tokenlar ("ana ")
    root: str            # çekilecek çıplak kök ("kitap", "ev")
    softens: bool        # son ünsüz ünlü önünde yumuşar (kitap→kitab)
    drops_vowel: bool    # son hece ünlüsü ünlü önünde düşer (burun→burn)
    doubles: bool        # son ünsüz ünlü önünde ikizleşir (hak→hakk)
    special: str | None  # zamir/istisna anahtarı (su, ben, sen, o, bu, şu, ne)

    def to_dict(self) -> dict:
        return {
            "root": self.root, "softens": self.softens,
            "drops_vowel": self.drops_vowel, "doubles": self.doubles,
            "special": self.special,
            "harmony_back": last_vowel(self.root) in BACK,
        }


def _count_syllables(word: str) -> int:
    return sum(1 for ch in _norm_harmony(word) if ch in VOWELS)


def _guess_softens(root: str) -> bool:
    """§3.2 yumuşama KURALI + istisna. p/ç/t/k (ve nk) biten kökler için."""
    if not root:
        return False
    if root in SOFTEN_NO:
        return False
    if root in SOFTEN_YES:
        return True
    if root.endswith("nk"):
        return True  # k→g (renk→rengi); SOFTEN_YES'te de var, güvenli tekrar
    if root[-1] not in "pçtk":
        return False
    # çok-heceli → yumuşar (varsayılan); tek-heceli → sert (varsayılan)
    return _count_syllables(root) >= 2


def parse_noun(headword: str) -> NounStem:
    """Yalın başlıktan NounStem türet (SPEC §2). Birleşik: yalnız son token."""
    headword = headword.strip()
    tokens = headword.split(" ")
    last = tokens[-1]
    prefix = "".join(t + " " for t in tokens[:-1])

    special = last if last in PRONOUN_FORMS else None
    drops = last in DROP_VOWEL
    doubles = last in DOUBLE
    # Yumuşama: drops/doubles açık ise onlar kök varyantını yönetir; yine de
    # softens bayrağı ayrı hesaplanır (drops+softens birlikte olabilir, §3.3).
    softens = _guess_softens(last)

    return NounStem(
        headword=headword, prefix=prefix, root=last,
        softens=softens, drops_vowel=drops, doubles=doubles, special=special,
    )


# ---------------------------------------------------------------------------
# 3.1 Kök varyantı (SPEC §3.1) — yalnız kök sınırında, ünlü-başlı segment önünde
# ---------------------------------------------------------------------------
def root_variant(vs: NounStem, vowel_next: bool) -> str:
    """Sonraki segment ünlü-başlıysa (vowel_next) ve bayrak açıksa kök değişir.

    Ünsüz-başlı ek (çoğul -lAr, loc -DA…) önünde çıplak kök döner.
    """
    root = vs.root
    if not vowel_next:
        return root

    # ikizleşme: son ünsüz ikizleşir (hak→hakk); ret→redd (t→d + double)
    if vs.doubles:
        last = root[-1]
        if last == "t":              # ret→redd, cet→cedd (softens de tetikler)
            return root[:-1] + "dd"
        return root + last

    # ünlü düşmesi: son hecenin ünlüsü düşer (burun→burn, şehir→şehr)
    if vs.drops_vowel:
        root = _drop_last_vowel(root)
        # vakit gibi drops-ama-softens-DEĞİL: t sert kalır (vakti). softens
        # bayrağı zaten _guess_softens'ten geldi; düşmeden sonra tekrar bakılmaz.
        if vs.softens:
            root = _soften_last(root)
        return root

    # yumuşama: t→d, p→b, ç→c, k→ğ, nk→ng
    if vs.softens:
        return _soften_last(root)

    return root


def _drop_last_vowel(root: str) -> str:
    """Son hecenin (son) ünlüsünü düşür: burun→burn, şehir→şehr, ağız→ağz."""
    idx = None
    for i in range(len(root) - 1, -1, -1):
        if root[i] in VOWELS:
            idx = i
            break
    if idx is None:
        return root
    return root[:idx] + root[idx + 1:]


def _soften_last(root: str) -> str:
    """Son sert ünsüzü yumuşat (ünlü önünde). nk→ng özel."""
    if root.endswith("nk"):
        return root[:-1] + "g"          # renk→reng, denk→deng
    mapping = {"p": "b", "ç": "c", "t": "d", "k": "ğ"}
    last = root[-1]
    if last in mapping:
        return root[:-1] + mapping[last]
    return root


# ---------------------------------------------------------------------------
# Ek gerçekleştiricileri (harmoni ile)
# ---------------------------------------------------------------------------
# FRONT_HARMONY alıntılarında harmoni yönünü çevirmek için, base'in son ünlüsü
# yerine sanal bir ön ünlü kaynağı kullanılır. Kök sınırına EKLENEN İLK ekte
# geçerlidir; sonraki eklerin kendi ünlüsü zaten normal harmoniyi taşır.
def _hsrc(stem: str, front: bool) -> str:
    """Harmoni kaynağı: front ise base'in yuvarlaklığını koruyup ön-ünlüye çevir."""
    if not front:
        return stem
    v = last_vowel(stem)
    if v is None:
        return stem
    # yuvarlaklığı koru, ön yap: a/ı→e/i akışı; o/u→ö/ü; e/i/ö/ü zaten ön
    swap = {"a": "e", "ı": "i", "o": "ö", "u": "ü"}
    return stem + swap.get(v, v)


def _high(stem: str, front: bool = False) -> str:
    return high_vowel(_hsrc(stem, front))


def _low(stem: str, front: bool = False) -> str:
    return low_vowel(_hsrc(stem, front))


def _dt(stem: str) -> str:
    """loc/abl/predicative başı d/t: sert ünsüz sonrası t."""
    return "t" if hardens(stem) else "d"


# ---------------------------------------------------------------------------
# İyelik (SPEC §5)
# ---------------------------------------------------------------------------
def _apply_possessive(base: str, base_vowel_final: bool, person: str,
                      front: bool = False) -> str:
    """base'e iyelik ekle. base_vowel_final: ünlü-final mi (buffer düşer)."""
    i = _high(base, front)
    a = _low(base, front)
    # -lArI (3pl) SON ünlüsü köke değil -lAr'ın ünlüsüne uyar: a→ı, e→i
    # (hep -ları/-leri; kök yuvarlak olsa bile gözlerü DEĞİL gözleri).
    three_pl = "l" + a + "r" + ("ı" if a == "a" else "i")
    if not base_vowel_final:
        endings = {
            "1sg": "" + i + "m", "2sg": "" + i + "n", "3sg": "" + i,
            "1pl": i + "m" + i + "z", "2pl": i + "n" + i + "z",
            "3pl": three_pl,
        }
    else:
        # ünlü-final kök: yüksek-ünlü buffer düşer; 3sg buffer -s-, 3pl -lArI
        endings = {
            "1sg": "m", "2sg": "n", "3sg": "s" + i,
            "1pl": "m" + i + "z", "2pl": "n" + i + "z",
            "3pl": three_pl,
        }
    return base + endings[person]


# ---------------------------------------------------------------------------
# Durum ekleri (SPEC §4, §6)
# ---------------------------------------------------------------------------
def _apply_case(base: str, case: str, *, base_vowel_final: bool,
                has_pron_n: bool, front: bool = False) -> str:
    """base'e durum eki ekle. has_pron_n: 3. kişi iyelik / zamir gövdesi (§6)."""
    if case == "nom":
        return base
    i = _high(base, front)
    a = _low(base, front)

    # §6 pronominal -n-: 3. kişi iyelik ya da zamir gövdesi sonrası tüm durumlar
    if has_pron_n:
        buf = "n"
        if case == "acc":
            return base + buf + i
        if case == "dat":
            return base + buf + a
        if case == "loc":
            return base + buf + "d" + a          # -n- sonrası her zaman d (n sert değil)
        if case == "abl":
            return base + buf + "d" + a + "n"
        if case == "gen":
            return base + buf + i + "n"
        if case == "ins":
            return base + buf + "l" + a          # onunla (base=onun? — §8 tam biçim)
        raise ValueError(f"bilinmeyen case: {case}")

    # buffer ayrımı (§4): ünlü-final base'te acc/dat -y-, gen -n-, ins -y-
    if base_vowel_final:
        if case == "acc":
            return base + "y" + i
        if case == "dat":
            return base + "y" + a
        if case == "gen":
            return base + "n" + i + "n"
        if case == "ins":
            return base + "y" + "l" + a          # araba-y-la
        if case == "loc":
            return base + "d" + a                # masa-da (ünlü sonrası d)
        if case == "abl":
            return base + "d" + a + "n"          # masa-dan
        raise ValueError(f"bilinmeyen case: {case}")

    # ünsüz-final base
    if case == "acc":
        return base + i
    if case == "dat":
        return base + a
    if case == "gen":
        return base + i + "n"
    if case == "ins":
        return base + "l" + a                    # kitap-la (l ünsüz, yumuşama yok)
    if case == "loc":
        return base + _dt(base) + a              # kitap-ta / ev-de
    if case == "abl":
        return base + _dt(base) + a + "n"        # kitap-tan / ev-den
    raise ValueError(f"bilinmeyen case: {case}")


# ---------------------------------------------------------------------------
# 9. decline çekirdeği (SPEC §9)
# ---------------------------------------------------------------------------
def decline(headword: str, *, number: str = "sg",
            possessive: str | None = None, case: str = "nom") -> str:
    """ROOT + (çoğul) + (iyelik) + (durum). Harmoni her adımda güncel son ünlüden."""
    if number not in NUMBERS:
        raise ValueError(f"bilinmeyen number: {number}")
    if possessive not in POSSESSIVES:
        raise ValueError(f"bilinmeyen possessive: {possessive}")
    if case not in CASES:
        raise ValueError(f"bilinmeyen case: {case}")

    vs = parse_noun(headword)

    # §P1-P2 — ben/sen çoğulu suppletif: biz/siz'e yönlendir.
    # biz/siz başlı başına çoğul zamirler; decline('biz', number='sg', ...) doğru
    # eğik biçimleri (bize/bizi/bizde/…) PRONOUN_FORMS'tan üretir.
    if vs.special and number == "pl" and vs.root in _PLURAL_SUPPLETION:
        return decline(_PLURAL_SUPPLETION[vs.root], number="sg",
                       possessive=possessive, case=case)

    # §P3-P8 — n-gövde zamir: iyeliksiz tekil, kök _N_STEM_PRONOUNS'da.
    if vs.root in _N_STEM_PRONOUNS and number == "sg" and possessive is None:
        return vs.prefix + _decline_n_stem_pronoun(vs.root, case)

    if vs.special:
        # §8 zamir istisnası: yalın tekil iyeliksiz → tam-biçim tablosu.
        if number == "sg" and possessive is None:
            return vs.prefix + _decline_pronoun(vs, case)
        # o/bu/şu çoğulu n-gövdelidir (onlar/bunlar/şunlar) — düzenli işlenir.
        if number == "pl" and possessive is None and vs.root in _N_STEM:
            vs2 = replace(vs, root=_N_STEM[vs.root], special=None)
            return vs2.prefix + _decline_core(vs2, number, possessive, case)
        # su iyelikte -y- gövdelidir (suyum/suyu, susu DEĞİL) — §8 düzensizi.
        # 3pl -lArI ünsüz-başlı → -y- YOK: "suları" (normal yola düşer).
        if (vs.root == "su" and possessive is not None
                and possessive != "3pl" and number == "sg"):
            return vs.prefix + _decline_su_possessive(possessive, case)
        # ben/sen çoğulu suppletiftir (biz/siz); diğer zamir+iyelik/çoğul nadir
        # → düz kök işlenir (SPEC §8 kapsam notu).

    body = _decline_core(vs, number, possessive, case)
    return vs.prefix + body


# o/bu/şu durum/çoğul önünde n-gövde alır (pronominal-n çekirdeği).
_N_STEM: dict[str, str] = {"o": "on", "bu": "bun", "şu": "şun"}

# §P1-P2 — ben/sen çoğulu suppletiftir (biz/siz).
_PLURAL_SUPPLETION: dict[str, str] = {"ben": "biz", "sen": "siz"}

# §P3-P8 — n-gövde zamirleri: ünlü-final olmalarına rağmen eğik durumda
# pronominal -n- alırlar (hepsi→hepsini, kendi→kendini). İnstrumental
# istisnası: -yle/-le pron-n'yi tetiklemez (hepsiyle, kendiyle).
_N_STEM_PRONOUNS: frozenset[str] = frozenset({
    "hepsi", "kendi", "hiçbiri", "birisi", "biri",
    "öteki", "öbürü", "hangisi", "bazısı", "çoğu", "azı",
})


def _decline_su_possessive(possessive: str, case: str) -> str:
    """§8: 'su' iyelikte -y- gövdeli (suy-). Ünsüz-final base gibi işlenir.

    Yalnız ünlü-başlı iyelikler (1sg/2sg/3sg/1pl/2pl); 3pl -lArI ünsüz-başlı
    olduğundan çağıran (decline) onu bu yola SOKMAZ → "suları".
    """
    base = _apply_possessive("suy", False, possessive)   # suyum, suyu, suyumuz…
    has_pron_n = possessive in ("3sg", "3pl")
    return _apply_case(base, case, base_vowel_final=ends_in_vowel(base),
                       has_pron_n=has_pron_n)


def _decline_pronoun(vs: NounStem, case: str) -> str:
    """§8 zamir tam-biçim tablosu (yalın tekil, iyeliksiz)."""
    if case == "nom":
        return vs.root
    forms = PRONOUN_FORMS[vs.root]
    return forms[case]


def _decline_n_stem_pronoun(root: str, case: str) -> str:
    """§P3-P8 n-gövde zamir çekimi (hepsi, kendi, hiçbiri, …).

    Kural: ünlü-final kök olmasına rağmen eğik durumda pronominal -n- alır.
    İSTİSNA — instrumental (-yle): pron-n YOK; ünlü-final buffer kullanılır
    (hepsiyle, kendiyle — NOT hepsiniyle).
    Nom: kök kendisi.
    """
    if case == "nom":
        return root
    base = root  # ünlü-final (hepsi, kendi, öbürü, …)
    if case == "ins":
        # İnstrumental: ünlü-final gibi davran → -yle
        return _apply_case(base, case, base_vowel_final=True, has_pron_n=False)
    # Diğer tüm eğik durumlar: pronominal -n-
    return _apply_case(base, case, base_vowel_final=True, has_pron_n=True)


def _decline_core(vs: NounStem, number: str, possessive: str | None,
                  case: str) -> str:
    plural = number == "pl"
    # Harmoni-kırıcı alıntı: kök sınırındaki İLK eke ön-ünlü uygula (saat→saati).
    # Çoğul araya girince -lAr'ın kendi ön ünlüsü (saatler) harmoniyi sürdürür →
    # sonraki eklere override GEREKMEZ.
    front_root = vs.root in FRONT_HARMONY

    # --- base kur: ROOT (+ çoğul) ---
    if plural:
        # çoğul -lAr ünsüz-başlı → kök KORUNUR (§3.1)
        base = vs.root + "l" + _low(vs.root, front_root) + "r"
        base_vowel_final = False  # -lAr r ile biter
        front = False             # -lAr ünlüsü artık harmoniyi taşır
    else:
        # çoğul yoksa: sonraki segment (iyelik ya da durum) ünlü-başlı mı?
        next_vowel = _next_is_vowel_initial(possessive, case, vs)
        base = root_variant(vs, vowel_next=next_vowel)
        base_vowel_final = ends_in_vowel(base)
        front = front_root

    has_pron_n = False

    # --- iyelik ---
    if possessive is not None:
        base = _apply_possessive(base, base_vowel_final, possessive, front)
        base_vowel_final = ends_in_vowel(base)
        front = False             # iyelik ünlüsü artık harmoniyi taşır
        if possessive in ("3sg", "3pl"):
            has_pron_n = True

    # zamir gövdesi (o/bu/şu) iyeliksiz de pronominal-n çekirdeğidir, ama §8
    # tablosu yalın durumları zaten kapsıyor; iyelikli/çoğullu zamir nadir,
    # kök düz işlenir (kapsam notu).

    # --- durum ---
    return _apply_case(base, case, base_vowel_final=base_vowel_final,
                       has_pron_n=has_pron_n, front=front)


def _next_is_vowel_initial(possessive: str | None, case: str,
                           vs: NounStem) -> bool:
    """Kök sınırından sonra gelen İLK segment ünlü-başlı mı?

    İyelik varsa iyeliğe bak; yoksa durum ekine bak.
    """
    if possessive is not None:
        # 3pl -lArI ünsüz-başlı (l); diğerleri ünlü-başlı
        return possessive != "3pl"
    # ünlü-başlı ek → kök yumuşar/düşer: acc(-I), dat(-A), gen(-In).
    # ünsüz-başlı (kök korunur): loc(-DA), abl(-DAn), ins(-lA), nom.
    # ins ünsüz-başlıdır (l) → False DOĞRU: kitap-la (p sert, kitab-la DEĞİL).
    return case in ("acc", "dat", "gen")


# ---------------------------------------------------------------------------
# 7. Ek katmanları (SPEC §7) — çekirdekten sonra
# ---------------------------------------------------------------------------
def predicative(headword: str, *, person: str = "3sg", **core) -> str:
    """§7.2 yüklemleme -DIr + kişi. 4'lü yüksek + d/t; ünsüz-başlı (yumuşama yok)."""
    if person not in PERSONS:
        raise ValueError(f"bilinmeyen person: {person}")
    stem = decline(headword, **core)
    # -DIr doğrudan yalın köke eklenirse (core boş) alıntı ön-harmonisi geçerli
    front = (not core) and parse_noun(headword).root in FRONT_HARMONY
    i = _high(stem, front)
    a = _low(stem, front)
    if person == "3sg":
        return stem + _dt(stem) + i + "r"                  # ev-dir, kitap-tır
    # 1sg/1pl kişi eki (-Im/-Iz) ÜNLÜ-BAŞLI → yalın ünsüz-final gövdede YUMUŞAMA
    # (genç→gencim, kitap→kitabım); 2sg/2pl (-sIn) ünsüz-başlı, yumuşama YOK (gençsin).
    v_stem = stem
    if not core and person in ("1sg", "1pl") and not ends_in_vowel(stem):
        v_stem = root_variant(parse_noun(headword), True)
    vfin = ends_in_vowel(v_stem)
    y = "y" if vfin else ""
    vi = _high(v_stem, front)
    endings = {
        "1sg": v_stem + y + vi + "m",                       # gencim / öğrenciyim
        "2sg": stem + "s" + i + "n",
        "1pl": v_stem + y + vi + "z",
        "2pl": stem + "s" + i + "n" + i + "z",
        "3pl": stem + _dt(stem) + i + "rl" + a + "r",       # -DIrlAr
    }
    return endings[person]


# ---------------------------------------------------------------------------
# Nominal ek-fiil (kopula) — Faz 1 / A4 (spec/copula-spec.md)
# Ad soylu yüklemi çekimler: hikaye -(y)DI, rivayet -(y)mIş, şart -(y)sA + soru.
# Fiil _ekfiil emsali; noun-domain harmoni (diakritik-normalize) kullanır.
# ---------------------------------------------------------------------------
def _copula_suffix(stem: str, aux: str, person: str) -> str:
    """Ek-fiil (i-di/i-miş/i-se) + kişi ekini `stem`'e ekler. Ünlü-final gövdede
    kaynaştırma -y-; -DI sertleşmesi (sert-final → -tI); noun-domain harmoni."""
    vf = ends_in_vowel(stem)
    y = "y" if vf else ""
    i = high_vowel(stem)
    a = low_vowel(stem)
    _k = {"1sg": "m", "2sg": "n", "3sg": "",
          "1pl": "k", "2pl": "n" + i + "z", "3pl": "l" + a + "r"}   # k-tipi
    if aux == "hikaye":                                   # -(y)DI + k-tipi
        d = "t" if (not vf and hardens(stem)) else "d"
        return stem + y + d + i + _k[person]
    if aux == "rivayet":                                  # -(y)mIş + z-tipi
        base = stem + y + "m" + i + "ş"
        _z = {"1sg": i + "m", "2sg": "s" + i + "n", "3sg": "",
              "1pl": i + "z", "2pl": "s" + i + "n" + i + "z", "3pl": "l" + a + "r"}
        return base + _z[person]
    if aux == "sart":                                     # -(y)sA + k-tipi
        # 2pl -nIz araya giren -sA ünlüsüne (düz a/e) uyar → -sanız/-seniz;
        # gövde yuvarlaklığı taşınmaz (geliyorsanız, geliyorsanuz DEĞİL).
        _ks = dict(_k, **{"2pl": "n" + ("ı" if a == "a" else "i") + "z"})
        return stem + y + "s" + a + _ks[person]
    raise ValueError(f"bilinmeyen aux: {aux}")


def _pres_question(stem: str, person: str) -> str:
    """Geniş copula soru: gövde + mI + z-tipi kişi (mI'ye biner). 3pl: çoğul + mI."""
    a = low_vowel(stem)
    if person == "3pl":                                   # öğrenciler mi
        return f"{stem}l{a}r m{high_vowel(stem)}"
    mi = "m" + high_vowel(stem)
    j = high_vowel(mi)
    _z = {"1sg": "y" + j + "m", "2sg": "s" + j + "n", "3sg": "",
          "1pl": "y" + j + "z", "2pl": "s" + j + "n" + j + "z"}
    return f"{stem} {mi}{_z[person]}"


def copula(headword: str, aux: str | None = None, person: str = "3sg", *,
           case: str | None = None, possessive: str | None = None,
           number: str = "sg", question: bool = False) -> str:
    """Nominal ek-fiil (kopula). aux ∈ {None(geniş), 'hikaye', 'rivayet', 'sart', 'ken'};
    gövde `decline(headword, ...)` ile kurulur, ek-fiil son sese göre biner. 'ken'
    (iken) kişisiz DONMUŞ ek: gövde + (y)ken (evdeyken, çocukken)."""
    if person not in PERSONS:
        raise ValueError(f"bilinmeyen person: {person}")
    core: dict = {}
    if case is not None:
        core["case"] = case
    if possessive is not None:
        core["possessive"] = possessive
    if number != "sg":
        core["number"] = number
    if aux is None:                                       # geniş / bildirme
        if question:
            return _pres_question(decline(headword, **core), person)
        return predicative(headword, person=person, **core)
    stem = decline(headword, **core)
    if aux == "ken":                                      # -ken (iken): kişisiz, DONMUŞ ek
        y = "y" if ends_in_vowel(stem) else ""            # glide yalnız ünlü-final gövdede
        return stem + y + "ken"
    if question:                                          # mI gövde ile ek-fiil arasına
        return f"{stem} {_copula_suffix('m' + high_vowel(stem), aux, person)}"
    return _copula_suffix(stem, aux, person)


def with_ki(headword: str, *, case: str = "loc", **core) -> str:
    """§7.3 aitlik -ki. Durum ekinden (loc/gen) sonra; değişmez, Kİ_ROUND uyar."""
    base = decline(headword, case=case, **core)
    root = parse_noun(headword).root
    if root in Kİ_ROUND:
        # bugün-kü, dün-kü — yalın gövdeye yuvarlak -kü (loc/gen atlanır)
        return parse_noun(headword).prefix + root + "k" + _high(root)
    return base + "ki"


def equative(headword: str) -> str:
    """§7.4 eşitlik -CA. 2'li alçak + c/ç sertleşme (sert ünsüz sonrası ç)."""
    vs = parse_noun(headword)
    root = vs.root
    a = _low(root, root in FRONT_HARMONY)
    c = "ç" if hardens(root) else "c"
    return vs.prefix + root + c + a


# ---------------------------------------------------------------------------
# _decline_last_token — birleşik isim yardımcısı (SPEC §1)
# ---------------------------------------------------------------------------
def _decline_last_token(headword: str, **kwargs) -> str:
    """'ana dil' → yalnız 'dil' çekilir, 'ana ' öne eklenir.

    decline zaten prefix ayırmayı (parse_noun) yapar; bu ad SPEC §1'in okunaklı
    çağrı yüzüdür (aynı davranış, açık niyet; fiil inflect_last_token emsali).
    """
    return decline(headword, **kwargs)


# ---------------------------------------------------------------------------
# paradigm_noun — çekirdek hücreler + ek katmanları (SPEC §10 anahtar şeması)
# ---------------------------------------------------------------------------
def paradigm_noun(headword: str) -> dict:
    """Tüm çekirdek hücreler + ek katmanları. Anahtar şeması SPEC §10 ile sabit."""
    out: dict[str, str] = {}
    core_cases = ("acc", "dat", "loc", "abl", "gen", "ins")

    # yalın durumlar
    out["nom"] = decline(headword, case="nom")
    for c in core_cases:
        out[c] = decline(headword, case=c)

    # çoğul + durum
    out["pl.nom"] = decline(headword, number="pl", case="nom")
    for c in core_cases:
        out[f"pl.{c}"] = decline(headword, number="pl", case=c)

    # iyelik (yalın durum)
    for p in PERSONS:
        out[f"poss.{p}"] = decline(headword, possessive=p, case="nom")
    # iyelik + durum (pronominal-n dahil)
    for p in PERSONS:
        for c in core_cases:
            out[f"poss.{p}.{c}"] = decline(headword, possessive=p, case=c)

    # çoğul + iyelik + durum (örnek zincir)
    out["pl.poss.1pl.abl"] = decline(headword, number="pl",
                                     possessive="1pl", case="abl")

    # ek katmanları (ins zaten core_cases döngüsünde üretildi)
    out["pred.3sg"] = predicative(headword)
    out["ki.loc"] = with_ki(headword, case="loc")
    out["ki.gen"] = with_ki(headword, case="gen")
    out["ca"] = equative(headword)
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        # tek biçim: morphology_noun.py <başlık> [case] [number] [poss]
        hw = sys.argv[1]
        case = sys.argv[2] if len(sys.argv) > 2 else "nom"
        number = sys.argv[3] if len(sys.argv) > 3 else "sg"
        poss = sys.argv[4] if len(sys.argv) > 4 else None
        print(decline(hw, number=number, possessive=poss, case=case))
    else:
        for k, v in paradigm_noun("kitap").items():
            print(f"{k:20} {v}")
