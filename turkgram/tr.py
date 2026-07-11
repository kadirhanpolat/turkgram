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
_FIILIMSI = {
    "dik": "dik", "dık": "dik", "diğ": "dik", "-dik": "dik",
    "acak": "acak", "ecek": "acak", "-acak": "acak", "-ecek": "acak",
    "ma": "ma", "me": "ma", "-ma": "ma", "-me": "ma",
    "mak": "mak", "mek": "mak", "mastar": "mak", "-mak": "mak",
    "is": "is", "iş": "is", "-iş": "is", "uş": "is",
}
_TASVIR = {
    "iver": "iver", "tezlik": "iver", "-iver": "iver",
    "adur": "adur", "sürerlik": "adur", "surerlik": "adur", "-adur": "adur",
    "agel": "agel", "-agel": "agel",
    "akal": "akal", "kalma": "akal", "-akal": "akal",
    "ayaz": "ayaz", "yaklaşma": "ayaz", "yaklasma": "ayaz", "-ayaz": "ayaz",
}
_CATI = {
    "ettirgen": "caus", "ettirgenlik": "caus", "oldurgan": "caus",
    "edilgen": "pass", "edilgenlik": "pass", "pasif": "pass",
    "meçhul": "pass", "mechul": "pass",
    "dönüşlü": "refl", "donuslu": "refl", "dönüşlülük": "refl",
    "işteş": "recip", "istes": "recip", "işteşlik": "recip",
    "karşılıklı": "recip", "karsilikli": "recip",
}


# ── Çekim tablosu anahtarı: çekirdek segment → Türkçe (kanonik) ──────────
# paradigm/paradigm_noun anahtarları nokta-ayrık segment ('neg.pres.1sg',
# 'pl.poss.1pl.abl'). Her segment tek tek çevrilir → tüm kombinasyonlar kapsanır.
_ANAHTAR = {
    # işaretleyiciler
    "neg": "olumsuz", "ability": "yeterlik",
    # kip / zaman
    "pres": "şimdiki", "past": "görülen_geçmiş", "fut": "gelecek",
    "aorist": "geniş", "evid": "öğrenilen_geçmiş", "cond": "şart",
    "necess": "gereklilik", "opt": "istek", "imp": "emir",
    "conv_arak": "ulaç", "part_dik": "ortaç",
    # kişi (fiil çekimi + isim iyelik kişisi)
    "1sg": "1tekil", "2sg": "2tekil", "3sg": "3tekil",
    "1pl": "1çoğul", "2pl": "2çoğul", "3pl": "3çoğul",
    # isim: sayı / iyelik / durum / ek katmanlar
    "pl": "çoğul", "poss": "iyelik",
    "nom": "yalın", "acc": "belirtme", "dat": "yönelme", "loc": "bulunma",
    "abl": "ayrılma", "gen": "tamlayan", "ins": "vasıta",
    "pred": "yüklem", "ki": "ki", "ca": "eşitlik",
}


def _türkçe_anahtar(key: str) -> str:
    """Çekirdek tablo anahtarını Türkçeleştir (segment-segment). Bilinmeyen segment
    aynen korunur (savunmacı — yeni eksen eklenince çökmez)."""
    return ".".join(_ANAHTAR.get(seg, seg) for seg in key.split("."))


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
def _çatı_zincir(çatı):
    """Türkçe çatı adı/adları → çekirdek voice_chain (['caus', ...]). None → None."""
    if çatı is None:
        return None
    değerler = [çatı] if isinstance(çatı, str) else list(çatı)
    return [_map(_CATI, c, "çatı") for c in değerler]


def çekimle(fiil, kip, kişi=None, *, olumsuz=False, yeterlik=False,
            soru=False, birleşik=None, tasvir=None, çatı=None):
    """conjugate — fiil çekimi (bir biçim). tasvir: iver/adur/agel/akal/ayaz.
    çatı: ettirgen/edilgen/dönüşlü/işteş (tekil ya da liste → yığılma,
    ör. çatı=['işteş','ettirgen','edilgen'] → dövüştürüldü)."""
    return _m.conjugate(fiil, _map(_KIP, kip, "kip"), _map(_KISI, kişi, "kişi"),
                        negative=olumsuz, ability=yeterlik, question=soru,
                        aux=_map(_BIRLESIK, birleşik, "birleşik"),
                        aspect=_map(_TASVIR, tasvir, "tasvir"),
                        voice_chain=_çatı_zincir(çatı))


def son_kelimeyi_çek(fiil, kip, kişi=None, *, olumsuz=False, yeterlik=False,
                     soru=False, birleşik=None):
    """inflect_last_token — birleşik/hafif fiilde yalnız son token çekilir."""
    return _m.inflect_last_token(fiil, _map(_KIP, kip, "kip"), _map(_KISI, kişi, "kişi"),
                                 negative=olumsuz, ability=yeterlik, question=soru,
                                 aux=_map(_BIRLESIK, birleşik, "birleşik"))


def çekim_tablosu(fiil):
    """paradigm — tam fiil çekim tablosu (dict; anahtar VE değer Türkçe).
    Anahtar biçimi: 'şimdiki.3tekil', 'olumsuz.görülen_geçmiş.1tekil', 'ulaç'."""
    return {_türkçe_anahtar(k): v for k, v in _m.paradigm(fiil).items()}


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
    """paradigm_noun — tam isim çekim tablosu (dict; anahtar VE değer Türkçe).
    Anahtar biçimi: 'belirtme', 'çoğul.bulunma', 'iyelik.1tekil.yönelme'."""
    return {_türkçe_anahtar(k): v for k, v in _n.paradigm_noun(ad).items()}


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


def fiilimsi(fiil, tür, *, iyelik=None, durum=None):
    """participle — sıfat-fiil (dik/acak) veya ad-fiil (ma/mak/is) + iyelik/durum.
    Adlaşmış yan cümle: okuduğum, gitmesini, geleceğini."""
    return _nf.participle(fiil, _map(_FIILIMSI, tür, "fiilimsi tür"),
                          possessive=_map(_KISI, iyelik, "iyelik"),
                          case=_map(_DURUM, durum, "durum"))


# ── Türetme ─────────────────────────────────────────────────────────────
def türet(kelime, tür):
    """derivations — yapım eki (türetme) mekanik üretici. tür ∈ {isim, fiil, ...}."""
    return _d.derivations(kelime, _map(_TUR, tür, "tür"))


# ── Ters dönüşüm sözlükleri (İngilizce çekirdek → kanonik Türkçe) ─────────
_TERS_KIP = {
    "pres": "şimdiki", "past": "görülen_geçmiş", "fut": "gelecek",
    "aorist": "geniş", "evid": "öğrenilen_geçmiş", "cond": "şart",
    "necess": "gereklilik", "opt": "istek", "imp": "emir",
}
_TERS_KISI = {
    "1sg": "1tekil", "2sg": "2tekil", "3sg": "3tekil",
    "1pl": "1çoğul", "2pl": "2çoğul", "3pl": "3çoğul",
}
_TERS_DURUM = {
    "nom": "yalın", "acc": "belirtme", "dat": "yönelme",
    "loc": "bulunma", "abl": "ayrılma", "gen": "tamlayan", "ins": "vasıta",
}
_TERS_SAYI = {"sg": "tekil", "pl": "çoğul"}
_TERS_BIRLESIK = {"hikaye": "hikaye", "rivayet": "rivayet", "sart": "şart"}
_TERS_TASVIR = {
    "iver": "tezlik", "adur": "sürerlik", "agel": "agel",
    "akal": "kalma", "ayaz": "yaklaşma",
}
_TERS_CATI = {
    "caus": "ettirgen", "pass": "edilgen", "refl": "dönüşlü", "recip": "işteş",
}

# Segment etiket çevirisi (çekirdek kanonik → Türkçe kanonik)
# Not: mA = olumsuz işaretleyici (DIk türünden farklı; ptype segmenti kendi etiketiyle
# görünür: DIk→ortaç, acak/mAk/is passthrough; mA burada olumsuz olarak çevrilir).
_TERS_ETIKET = {
    # tense
    "DI": "görülen_geçmiş", "Iyor": "şimdiki", "AcAk": "gelecek",
    "Ir": "geniş", "mIş": "öğrenilen_geçmiş", "sA": "şart",
    "mAlI": "gereklilik", "A": "istek", "imp": "emir",
    # participle type
    "DIk": "ortaç",
    # modifiers
    "mA": "olumsuz", "Abil": "yeterlik", "AmA": "olumsuz_yeterlik",
    # voice
    "caus": "ettirgen", "pass": "edilgen", "refl": "dönüşlü", "recip": "işteş",
    # aux
    "hikaye": "hikaye", "rivayet": "rivayet", "sart": "şart",
    # decline
    "lAr": "çoğul",
    "acc": "belirtme", "dat": "yönelme", "loc": "bulunma",
    "abl": "ayrılma", "gen": "tamlayan", "ins": "vasıta",
    # person / possessive
    "1sg": "1tekil", "2sg": "2tekil", "3sg": "3tekil",
    "1pl": "1çoğul", "2pl": "2çoğul", "3pl": "3çoğul",
    # root stays
    "KÖK": "KÖK",
    # converb kinds (passthrough — zaten Türkçe)
    "arak": "arak", "ip": "ip", "inca": "inca", "madan": "madan",
    "dikce": "dikce", "meksizin": "meksizin", "eli": "eli", "esiye": "esiye",
}


def _çevir_etiket(label: str) -> str:
    """Segment etiketini Türkçeleştir. Bilinmeyen etiket aynen korunur."""
    return _TERS_ETIKET.get(label, label)


def _çevir_kwargs(kind: str, kwargs) -> dict:
    """Analysis.kwargs (İngilizce çekirdek) → Türkçe parametre adı + değer."""
    out: dict = {}
    if kind == "conjugate":
        if "tense" in kwargs:
            out["kip"] = _TERS_KIP.get(kwargs["tense"], kwargs["tense"])
        if "person" in kwargs:
            out["kişi"] = _TERS_KISI.get(kwargs["person"], kwargs["person"])
        if "negative" in kwargs:
            out["olumsuz"] = kwargs["negative"]
        if "ability" in kwargs:
            out["yeterlik"] = kwargs["ability"]
        if "question" in kwargs:
            out["soru"] = kwargs["question"]
        if "aux" in kwargs:
            out["birleşik"] = _TERS_BIRLESIK.get(kwargs["aux"], kwargs["aux"])
        if "aspect" in kwargs:
            out["tasvir"] = _TERS_TASVIR.get(kwargs["aspect"], kwargs["aspect"])
        if "voice_chain" in kwargs:
            vc = kwargs["voice_chain"]
            if vc:
                out["çatı"] = [_TERS_CATI.get(v, v) for v in vc]
    elif kind == "decline":
        if "number" in kwargs:
            out["sayı"] = _TERS_SAYI.get(kwargs["number"], kwargs["number"])
        if "possessive" in kwargs:
            out["iyelik"] = _TERS_KISI.get(kwargs["possessive"], kwargs["possessive"])
        if "case" in kwargs:
            out["durum"] = _TERS_DURUM.get(kwargs["case"], kwargs["case"])
    elif kind == "copula":
        if "aux" in kwargs:
            out["birleşik"] = _TERS_BIRLESIK.get(kwargs["aux"], kwargs["aux"])
        if "person" in kwargs:
            out["kişi"] = _TERS_KISI.get(kwargs["person"], kwargs["person"])
        if "case" in kwargs:
            out["durum"] = _TERS_DURUM.get(kwargs["case"], kwargs["case"])
        if "possessive" in kwargs:
            out["iyelik"] = _TERS_KISI.get(kwargs["possessive"], kwargs["possessive"])
        if "number" in kwargs:
            out["sayı"] = _TERS_SAYI.get(kwargs["number"], kwargs["number"])
        if "question" in kwargs:
            out["soru"] = kwargs["question"]
    elif kind == "converb":
        if "kind" in kwargs:
            out["tür"] = kwargs["kind"]  # passthrough
    elif kind == "participle":
        if "ptype" in kwargs:
            out["tür"] = kwargs["ptype"]  # passthrough
        if "possessive" in kwargs:
            out["iyelik"] = _TERS_KISI.get(kwargs["possessive"], kwargs["possessive"])
        if "case" in kwargs:
            out["durum"] = _TERS_DURUM.get(kwargs["case"], kwargs["case"])
    return out


def çözümle(yüzey: str, tür: str | None = None, *,
            kökler=None):
    """analyze — yüzey biçim → Analysis listesi (Türkçe kwargs + etiketler).

    Args:
        yüzey: Çözümlenecek biçim (tek ya da çok-token).
        tür:   "fiil" | "isim" | None (ikisi de). Bilinmeyen değer → ValueError.
        kökler: Lemma kümesi. Verilmişse yalnız bu kümeden kök döner.

    Returns:
        list[Analysis] — kwargs ve segment etiketleri Türkçe, sıra korunur.

    Raises:
        ValueError: Boş yüzey, bilinmeyen tür.
    """
    from . import analysis as _ana  # lazy import — döngü tuzağını önler

    pos = _map(_TUR, tür, "tür") if tür is not None else None
    sonuçlar = _ana.analyze(yüzey, pos, roots=kökler)

    çevrilmiş = []
    for a in sonuçlar:
        tr_kwargs = _çevir_kwargs(a.kind, a.kwargs)
        tr_segs = tuple(
            _ana.Segment(surface=s.surface, label=_çevir_etiket(s.label), span=s.span)
            for s in a.segments
        )
        çevrilmiş.append(_ana.Analysis(
            lemma=a.lemma,
            pos=a.pos,
            kind=a.kind,
            kwargs=tr_kwargs,
            segments=tr_segs,
            hypothetical=a.hypothetical,
        ))
    return çevrilmiş
