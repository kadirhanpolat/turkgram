"""turkgram.tr — Türkçe-yüzlü API katmanı (docs/tr-api-tasarim.md).

Türkçe adlı sarmalayıcılar; içeride orijinal İngilizce çekirdeği çağırır. Terim
geleneği KARMA: kanonik akademik (TDK/Korkmaz) değer + tanıdık alias (ör.
``görülen_geçmiş`` ve ``dili_geçmiş`` ikisi de kabul). Değerler ``_tr_lower`` (#10) ile
normalize edilir; bilinmeyen değer geçerli seçenekleri sıralayan ``ValueError`` verir.

    >>> import turkgram.tr as tr
    >>> tr.çekimle("gelmek", "şimdiki", "1tekil")
    'geliyorum'
    >>> tr.ad_çekimle("ev", iyelik="3tekil", durum="bulunma")
    'evinde'
    >>> tr.ekfiil("öğrenci", "hikaye", "1tekil")
    'öğrenciydim'
"""
from __future__ import annotations

from . import morphology as _m, morphology_noun as _n, derivation as _d
from . import nonfinite as _nf


# ── Türkçe-duyarlı küçük harf (#10: İ→i, I→ı) ────────────────────────────
def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


# ── Değer sözlükleri (Türkçe → İngilizce çekirdek anahtarı) ──────────────
_KIP = {
    "şimdiki": "pres", "simdiki": "pres",
    "görülen_geçmiş": "past", "gorulen_gecmis": "past",
    "geçmiş": "past", "gecmis": "past", "dili_geçmiş": "past", "dili_gecmis": "past",
    "gelecek": "fut",
    "geniş": "aorist", "genis": "aorist",
    "öğrenilen_geçmiş": "evid", "ogrenilen_gecmis": "evid",
    "mişli_geçmiş": "evid", "misli_gecmis": "evid", "duyulan": "evid",
    "şart": "cond", "sart": "cond", "dilek_şart": "cond", "dilek_sart": "cond",
    "koşul": "cond", "kosul": "cond",
    "gereklilik": "necess",
    "emir": "imp",
    "istek": "opt",
    "ulaç": "conv_arak", "ulac": "conv_arak", "zarf_fiil": "conv_arak",
    "ortaç": "part_dik", "ortac": "part_dik", "sıfat_fiil": "part_dik", "sifat_fiil": "part_dik",
}
_KISI = {
    "1tekil": "1sg", "2tekil": "2sg", "3tekil": "3sg",
    "1çoğul": "1pl", "2çoğul": "2pl", "3çoğul": "3pl",
    "1cogul": "1pl", "2cogul": "2pl", "3cogul": "3pl",
}
_SAYI = {"tekil": "sg", "çoğul": "pl", "cogul": "pl"}
_DURUM = {
    "yalın": "nom", "yalin": "nom",
    "belirtme": "acc", "i": "acc",
    "yönelme": "dat", "yonelme": "dat", "e": "dat",
    "bulunma": "loc", "de": "loc",
    "ayrılma": "abl", "ayrilma": "abl", "den": "abl",
    "tamlayan": "gen", "ilgi": "gen",
    "vasıta": "ins", "vasita": "ins", "araç": "ins", "arac": "ins", "ile": "ins",
}
_BIRLESIK = {
    "hikaye": "hikaye", "hikâye": "hikaye", "hikaye ": "hikaye",
    "rivayet": "rivayet", "şart": "sart", "sart": "sart",
}
_TUR = {
    "isim": "noun", "fiil": "verb",
    "birleşik_fiil": "compound_verb", "birlesik_fiil": "compound_verb",
    "birleşik_isim": "compound_noun", "birlesik_isim": "compound_noun",
}
_ULAC = {
    "arak": "arak", "-arak": "arak",
    "ip": "ip", "-ip": "ip",
    "inca": "inca", "ince": "inca", "-ince": "inca", "ınca": "inca",
    "madan": "madan", "meden": "madan", "-meden": "madan", "-madan": "madan",
    "eli": "eli", "-eli": "eli", "alı": "eli", "-alı": "eli",
    "dikce": "dikce", "dikçe": "dikce", "-dikçe": "dikce", "tıkça": "dikce",
    "meksizin": "meksizin", "maksızın": "meksizin", "-meksizin": "meksizin",
    "esiye": "esiye", "asıya": "esiye", "-esiye": "esiye",
}
_TASVIR = {
    "iver": "iver", "tezlik": "iver", "-iver": "iver",
    "adur": "adur", "sürerlik": "adur", "surerlik": "adur", "-adur": "adur",
    "agel": "agel", "-agel": "agel",
    "akal": "akal", "kalma": "akal", "-akal": "akal",
    "ayaz": "ayaz", "yaklaşma": "ayaz", "yaklasma": "ayaz", "-ayaz": "ayaz",
}


def _map(table: dict, value, param: str):
    """Türkçe değeri çekirdek anahtarına çevir. None → None (kişisiz/varsayılan)."""
    if value is None:
        return None
    key = _tr_lower(str(value).strip())
    try:
        return table[key]
    except KeyError:
        secenekler = sorted({k for k in table})
        raise ValueError(
            f"{param}: bilinmeyen değer {value!r}. Geçerli: {', '.join(secenekler)}"
        ) from None


def _core(sayı, iyelik, durum) -> dict:
    """predicative/with_ki için çekirdek kwarg — YALNIZ varsayılan-dışı olanları koy
    (predicative'in `not core` yumuşama/ön-harmoni dalını yalın adda korumak için)."""
    c: dict = {}
    if sayı not in (None, "tekil"):
        c["number"] = _map(_SAYI, sayı, "sayı")
    if iyelik is not None:
        c["possessive"] = _map(_KISI, iyelik, "iyelik")
    if durum not in (None, "yalın"):
        c["case"] = _map(_DURUM, durum, "durum")
    return c


# ── Fiil ────────────────────────────────────────────────────────────────
def çekimle(fiil, kip, kişi=None, *, olumsuz=False, yeterlik=False,
            soru=False, birleşik=None, tasvir=None):
    """conjugate — fiil çekimi (bir biçim). tasvir: iver/adur/agel/akal/ayaz."""
    return _m.conjugate(fiil, _map(_KIP, kip, "kip"), _map(_KISI, kişi, "kişi"),
                        negative=olumsuz, ability=yeterlik, question=soru,
                        aux=_map(_BIRLESIK, birleşik, "birleşik"),
                        aspect=_map(_TASVIR, tasvir, "tasvir"))


def son_kelimeyi_çek(fiil, kip, kişi=None, *, olumsuz=False, yeterlik=False,
                     soru=False, birleşik=None):
    """inflect_last_token — birleşik/hafif fiilde yalnız son token çekilir."""
    return _m.inflect_last_token(fiil, _map(_KIP, kip, "kip"), _map(_KISI, kişi, "kişi"),
                                 negative=olumsuz, ability=yeterlik, question=soru,
                                 aux=_map(_BIRLESIK, birleşik, "birleşik"))


def çekim_tablosu(fiil):
    """paradigm — tam fiil çekim tablosu (dict; anahtarlar İngilizce, değerler Türkçe)."""
    return _m.paradigm(fiil)


def fiil_çöz(fiil):
    """parse_verb — fiil gövdesi (VerbStem)."""
    return _m.parse_verb(fiil)


# ── İsim ────────────────────────────────────────────────────────────────
def ad_çekimle(ad, *, sayı="tekil", iyelik=None, durum="yalın"):
    """decline — isim çekimi (durum/iyelik/sayı)."""
    return _n.decline(ad, number=_map(_SAYI, sayı, "sayı"),
                      possessive=_map(_KISI, iyelik, "iyelik"),
                      case=_map(_DURUM, durum, "durum"))


def ad_çekim_tablosu(ad):
    """paradigm_noun — tam isim çekim tablosu (dict)."""
    return _n.paradigm_noun(ad)


def ad_çöz(ad):
    """parse_noun — isim gövdesi (NounStem)."""
    return _n.parse_noun(ad)


def yüklem(ad, *, kişi="3tekil", sayı="tekil", iyelik=None, durum="yalın"):
    """predicative — yüklemleme (-DIr + kişi)."""
    return _n.predicative(ad, person=_map(_KISI, kişi, "kişi"),
                          **_core(sayı, iyelik, durum))


def ekfiil(ad, birleşik=None, kişi="3tekil", *, durum=None, iyelik=None,
           sayı="tekil", soru=False):
    """copula — nominal ek-fiil (geniş/hikaye/rivayet/şart + soru)."""
    return _n.copula(ad, _map(_BIRLESIK, birleşik, "birleşik"), _map(_KISI, kişi, "kişi"),
                     case=_map(_DURUM, durum, "durum"),
                     possessive=_map(_KISI, iyelik, "iyelik"),
                     number=_map(_SAYI, sayı, "sayı"), question=soru)


def ki_ekle(ad, *, durum="bulunma", iyelik=None, sayı="tekil"):
    """with_ki — aitlik -ki."""
    extra = {}
    if sayı not in (None, "tekil"):
        extra["number"] = _map(_SAYI, sayı, "sayı")
    if iyelik is not None:
        extra["possessive"] = _map(_KISI, iyelik, "iyelik")
    return _n.with_ki(ad, case=_map(_DURUM, durum, "durum"), **extra)


def eşitlik(ad):
    """equative — eşitlik -CA."""
    return _n.equative(ad)


# ── Fiilimsi (zarf-fiil / ulaç) ──────────────────────────────────────────
def ulaç(fiil, tür):
    """converb — fiilden zarf-fiil (ulaç). tür ∈ {arak, ip, ince, meden, eli,
    dikçe, meksizin, esiye}."""
    return _nf.converb(fiil, _map(_ULAC, tür, "ulaç tür"))


# ── Türetme ─────────────────────────────────────────────────────────────
def türet(kelime, tür):
    """derivations — yapım eki (türetme) mekanik üretici. tür ∈ {isim, fiil, ...}."""
    return _d.derivations(kelime, _map(_TUR, tür, "tür"))
