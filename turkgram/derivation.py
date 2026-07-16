"""derivation.py — yapım eki (türetme) MEKANİK üretici (roadmap ek iş).

ÇEKİM değil TÜRETME. Motor, köke standart yapım eklerini MEKANİK uygular ve
ADAY biçimler üretir. Anlam UYDURMAZ (#8) — yalnız biçim. Üretilen adayın
sözlükte VAR olup olmadığını çağıran (route) sorgular; VAR olan linklenir,
olmayan linksiz gösterilir ("bu kelime sözlükte yok" sinyali, kullanıcı kararı).

Değişmezler:
- Saf Python, morfoloji harmoni yardımcılarını `morphology`/`morphology_noun`'dan
  IMPORT eder (kopyalama yok, #12).
- Türetme DÜZENSİZDİR: mekanik biçim gerçek sözcükle tutmayabilir — bu bilinçli
  sınır ("mekanik" etiketi). Hiç exception sızmaz (üretilemeyen ek atlanır).
- Fiil üreten ekler (isim→fiil, fiil→fiil çatı) mastarla (-mAk) gösterilir;
  varlık sorgusu mastar biçimi üzerinden yapılır (fiil girdileri mastar saklı).
"""
from __future__ import annotations

from . import morphology as _v
from .morphology import (
    ends_in_vowel, hardens, high_vowel, low_vowel,
)

_VERB_POS = frozenset({"verb", "compound_verb"})
_NOUN_POS = frozenset({"noun", "compound_noun"})


# ── Yapım eki tanımı ──────────────────────────────────────────────────────────
# (kategori, etiket, şablon, vowel_initial, produces_verb)
# Şablon arşifonemleri: I=yüksek ünlü(4'lü), A=alçak ünlü(2'li),
#   C=c/ç, D=d/t, G=g/k (kök son ünsüzüne göre sertleşme), diğerleri harfî.
_Suffix = tuple  # (str, str, str, bool, bool)

# İsimden isim (çoğu ünsüz-başlı → kök yumuşaması yok)
_NOUN_TO_NOUN: tuple[_Suffix, ...] = (
    ("isim → isim", "-lIk", "lIk", False, False),
    ("isim → isim", "-CI", "CI", False, False),
    ("isim → isim", "-lI", "lI", False, False),
    ("isim → isim", "-sIz", "sIz", False, False),
    ("isim → isim", "-CIk", "CIk", False, False),
    ("isim → isim", "-DAş", "DAş", False, False),
    ("isim → isim", "-CA", "CA", False, False),      # Türkçe, Çamlıca
    ("isim → isim", "-CIl", "CIl", False, False),    # evcil, bencil, ölümcül
    ("isim → isim", "-sAl", "sAl", False, False),   # toplumsal, ulusal, evrensel
)
# İsimden fiil (fiil üretir → mastar)
_NOUN_TO_VERB: tuple[_Suffix, ...] = (
    ("isim → fiil", "-lA-", "lA", False, True),
    ("isim → fiil", "-lAn-", "lAn", False, True),
    ("isim → fiil", "-lAş-", "lAş", False, True),
    ("isim → fiil", "-Al-", "Al", True, True),       # azal-, daral-, çoğal-
    ("isim → fiil", "-A-", "A", True, True),         # yaşa-, kana-, oyna-
    ("isim → fiil", "-sA-", "sA", False, True),      # susa-, önemse-, garipse-
    ("isim → fiil", "-ImsA-", "ImsA", True, True),   # benimse-, küçümse-, azımsa-
    ("isim → fiil", "-Ar-", "Ar", True, True),       # morar-, sarar-, yaşar-
)
# Fiilden isim (LEKSİK türetme; -mA/-Iş isim-fiil olduğundan fiilimsi'ye taşındı)
_VERB_TO_NOUN: tuple[_Suffix, ...] = (
    ("fiil → isim", "-Im", "Im", True, False),
    ("fiil → isim", "-gI", "GI", False, False),
    ("fiil → isim", "-gIn", "GIn", False, False),
    ("fiil → isim", "-gAn", "GAn", False, False),
    ("fiil → isim", "-Ak", "Ak", True, False),
    ("fiil → isim", "-I", "I", True, False),
    ("fiil → isim", "-mAn", "mAn", False, False),
    ("fiil → isim", "-IcI", "IcI", True, False),     # yapıcı, alıcı, satıcı
    ("fiil → isim", "-Ik", "Ik", True, False),       # açık, kesik, bozuk, düşük
    ("fiil → isim", "-Inç", "Inç", True, False),     # sevinç, korkunç, gülünç
    ("fiil → isim", "-IntI", "IntI", True, False),   # akıntı, esinti, üzüntü
)
# Fiilden fiil (çatı — fiil üretir → mastar)
# İki ettirgen allomorfu: -DIr (ünsüz-final kök: yap→yaptır) ve -t (ünlü-final ya
# da l/r-final kök: oku→okut, otur→oturt). İkisi de MEKANİK aday; gerçek olan
# linklenir (öbürü sözlükte yoksa soluk kalır — birbirini tümler).
_VERB_TO_VERB: tuple[_Suffix, ...] = (
    ("fiil → fiil (çatı)", "-DIr- (ettirgen)", "DIr", False, True),
    ("fiil → fiil (çatı)", "-t- (ettirgen)", "t", False, True),
    ("fiil → fiil (çatı)", "-Ir- (ettirgen)", "Ir", True, True),   # pişir-, içir-, uçur-
    ("fiil → fiil (çatı)", "-Ar- (ettirgen)", "Ar", True, True),   # çıkar-, kopar-, gider-
    ("fiil → fiil (çatı)", "-Il- (edilgen)", "Il", True, True),
    ("fiil → fiil (çatı)", "-In- (dönüşlü)", "In", True, True),
    ("fiil → fiil (çatı)", "-Iş- (işteş)", "Iş", True, True),
    ("fiil → fiil (çatı)", "-AlA- (pekiştirme)", "AlA", True, True),  # kovala-, itele-
)
# Fiilimsi (eylemsi) — fiili isim/sıfat/zarf gibi kullandıran ekler. Çekim ile
# leksik türetme ARASI: çoğu biçim sözlükte YOKtur (linksiz), lekstikselleşenler
# (gelecek=isim, geçmiş, olası, dolmuş) VARdır (linkli) → dürüst sözlükselleşme
# sinyali. Hepsi is_verb=False (biçim OLDUĞU gibi sorgulanır, mastar EKLENMEZ).
_FIILIMSI: tuple[_Suffix, ...] = (
    # İsim-fiil (mastar/eylem adı)
    ("fiilimsi · isim-fiil", "-mA", "mA", False, False),
    ("fiilimsi · isim-fiil", "-Iş", "Iş", True, False),
    # Sıfat-fiil (ortaç)
    ("fiilimsi · sıfat-fiil (ortaç)", "-An", "An", True, False),
    ("fiilimsi · sıfat-fiil (ortaç)", "-mAz", "mAz", False, False),
    ("fiilimsi · sıfat-fiil (ortaç)", "-DIk", "DIk", False, False),
    ("fiilimsi · sıfat-fiil (ortaç)", "-AcAk", "AcAk", True, False),
    ("fiilimsi · sıfat-fiil (ortaç)", "-mIş", "mIş", False, False),
    ("fiilimsi · sıfat-fiil (ortaç)", "-AsI", "AsI", True, False),
    # Zarf-fiil (ulaç)
    ("fiilimsi · zarf-fiil (ulaç)", "-ArAk", "ArAk", True, False),
    ("fiilimsi · zarf-fiil (ulaç)", "-Ip", "Ip", True, False),
    ("fiilimsi · zarf-fiil (ulaç)", "-IncA", "IncA", True, False),
    ("fiilimsi · zarf-fiil (ulaç)", "-mAdAn", "mAdAn", False, False),
    ("fiilimsi · zarf-fiil (ulaç)", "-AlI", "AlI", True, False),
    ("fiilimsi · zarf-fiil (ulaç)", "-DIkçA", "DIkçA", False, False),
)

# ── Analiz için leksik suffix kümesi (fiilimsi + çatı DIŞLANMIŞ) ────────────
# Her eleman: (category, label, src_pos)
# Exclusion (category, label) çiftiyle yapılır — -Ar- çakışmasını doğru çözer:
#   ("isim → fiil", "-Ar-") DAHİL; ("fiil → fiil (çatı)", "-Ar- (ettirgen)") DIŞLI.
_LEXICAL_SUFFIXES: tuple[tuple[str, str, str], ...] = (
    # isim → isim
    ("isim → isim", "-lIk",  "noun"),
    ("isim → isim", "-CI",   "noun"),
    ("isim → isim", "-lI",   "noun"),
    ("isim → isim", "-sIz",  "noun"),
    ("isim → isim", "-CIk",  "noun"),
    ("isim → isim", "-DAş",  "noun"),
    ("isim → isim", "-CA",   "noun"),
    ("isim → isim", "-CIl",  "noun"),
    ("isim → isim", "-sAl",  "noun"),
    # isim → fiil
    ("isim → fiil", "-lA-",   "noun"),
    ("isim → fiil", "-lAn-",  "noun"),
    ("isim → fiil", "-lAş-",  "noun"),
    ("isim → fiil", "-Al-",   "noun"),
    ("isim → fiil", "-A-",    "noun"),
    ("isim → fiil", "-sA-",   "noun"),
    ("isim → fiil", "-ImsA-", "noun"),
    ("isim → fiil", "-Ar-",   "noun"),   # isim→fiil: morar-, sarar- (DIŞLI DEĞİL)
    # fiil → isim (leksik; fiilimsi DIŞLI)
    ("fiil → isim", "-Im",   "verb"),
    ("fiil → isim", "-gI",   "verb"),
    ("fiil → isim", "-gIn",  "verb"),
    ("fiil → isim", "-gAn",  "verb"),
    ("fiil → isim", "-Ak",   "verb"),
    ("fiil → isim", "-I",    "verb"),
    ("fiil → isim", "-mAn",  "verb"),
    ("fiil → isim", "-IcI",  "verb"),
    ("fiil → isim", "-Ik",   "verb"),
    ("fiil → isim", "-Inç",  "verb"),
    ("fiil → isim", "-IntI", "verb"),
)

# Türetilmiş sözcüğün POS'u — suffix etiketine göre
_DERIVED_POS: dict[str, str] = {
    # isim → isim (sıfat üretenler adj)
    "-lI":   "adj",
    "-sIz":  "adj",
    "-CIl":  "adj",
    "-CA":   "adj",
    "-sAl":  "adj",
    "-lIk":  "noun",
    "-CI":   "noun",
    "-CIk":  "noun",
    "-DAş":  "noun",
    # isim → fiil
    "-lA-":   "verb",
    "-lAn-":  "verb",
    "-lAş-":  "verb",
    "-Al-":   "verb",
    "-A-":    "verb",
    "-sA-":   "verb",
    "-ImsA-": "verb",
    "-Ar-":   "verb",
    # fiil → isim / fiil → sıfat
    "-IcI":  "adj",
    "-gAn":  "adj",
    "-Ik":   "adj",
    "-gIn":  "adj",
    "-Im":   "noun",
    "-gI":   "noun",
    "-Ak":   "noun",
    "-I":    "noun",
    "-mAn":  "noun",
    "-Inç":  "noun",
    "-IntI": "noun",
}


def _expand(root: str, template: str, vowel_initial: bool) -> str | None:
    """Kök + şablonu mekanik gerçekle (harmoni/sertleşme). Başarısız → None."""
    if not root:
        return None
    try:
        word = root
        if vowel_initial and ends_in_vowel(root):
            word += "y"                      # ünlü-final kök + ünlü ek → kaynaştırma
        for ch in template:
            if ch == "I":
                word += high_vowel(word)
            elif ch == "A":
                word += low_vowel(word)
            elif ch == "C":
                word += "ç" if hardens(word) else "c"
            elif ch == "D":
                word += "t" if hardens(word) else "d"
            elif ch == "G":
                word += "k" if hardens(word) else "g"
            else:
                word += ch
        return word
    except (ValueError, IndexError):
        return None


def _infinitive(stem: str) -> str | None:
    """Fiil gövdesine mastar -mAk ekle (gözle → gözlemek)."""
    try:
        return stem + "m" + low_vowel(stem) + "k"
    except ValueError:
        return None


def _noun_root(headword: str) -> str:
    """İsim kökü — çekim değil türetme; yumuşama ünsüz-başlı eklerde tetiklenmez,
    ünlü-başlıda kök son ünsüzünü yumuşatmak gerekir ama mekanik sadelik için
    ham kök kullanılır (kitap→kitaplık doğru; ünlü-başlı isim eki setimizde yok)."""
    return headword.strip()


def derivations(headword: str, pos: str, lang: str = "tr") -> list[dict] | None:
    """MEKANİK yapım eki adayları. YALNIZ TR isim/fiil. Aksi → None.

    Dönüş: [{"category","suffix","form","is_verb"}]  (varlık sorgusu route'ta).
    form fiil üreten ekte MASTAR biçimidir. Hiç exception sızmaz.
    """
    if lang != "tr" or not headword:
        return None
    out: list[dict] = []

    if pos in _NOUN_POS:
        root = _noun_root(headword)
        specs = _NOUN_TO_NOUN + _NOUN_TO_VERB
        for cat, label, tmpl, vinit, pv in specs:
            form = _expand(root, tmpl, vinit)
            if form and pv:
                form = _infinitive(form)
            if form:
                out.append({"category": cat, "suffix": label,
                            "form": form, "is_verb": pv})

    elif pos in _VERB_POS:
        try:
            vs = _v.parse_verb(headword)
        except Exception:
            return None
        specs = _VERB_TO_NOUN + _VERB_TO_VERB + _FIILIMSI
        for cat, label, tmpl, vinit, pv in specs:
            # ünlü-başlı ek → yumuşama tetikler (git→gid+iş); ünsüz-başlı → ham kök
            root = _v._stem_before_suffix(vs, vowel_initial=vinit)
            form = _expand(vs.prefix + root, tmpl, vinit)
            if form and pv:
                form = _infinitive(form)
            if form:
                out.append({"category": cat, "suffix": label,
                            "form": form, "is_verb": pv})
    else:
        return None

    return out or None


if __name__ == "__main__":
    import sys
    hw = sys.argv[1] if len(sys.argv) > 1 else "göz"
    pos = sys.argv[2] if len(sys.argv) > 2 else "noun"
    d = derivations(hw, pos)
    if not d:
        print(f"{hw} [{pos}]: türetilemez")
    else:
        for row in d:
            print(f"  {row['category']:20} {row['suffix']:20} {row['form']}")
