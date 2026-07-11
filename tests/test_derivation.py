"""derivation.py — yapım eki mekanik üretici testleri.

Mekanik biçimler dilbilgisinden elle doğrulandı (gerçek sözcük olması ŞART DEĞİL —
üretici mekaniktir; varlık sorgusu route'ta). Hiç exception sızmaz.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turkgram.derivation import derivations


def _forms(hw, pos):
    d = derivations(hw, pos)
    return {r["suffix"]: r["form"] for r in d} if d else {}


def test_noun_derivations():
    f = _forms("göz", "noun")
    assert f["-lIk"] == "gözlük"
    assert f["-CI"] == "gözcü"           # c (voiced) + ü
    assert f["-sIz"] == "gözsüz"
    assert f["-lA-"] == "gözlemek"       # isim→fiil → mastar
    assert f["-lAş-"] == "gözleşmek"


def test_noun_hardening():
    f = _forms("kitap", "noun")
    assert f["-CI"] == "kitapçı"         # ç (p sert) + ı
    assert f["-lIk"] == "kitaplık"
    assert f["-DAş"] == "kitaptaş"       # t (p sert)


def test_verb_derivations():
    f = _forms("sevmek", "verb")
    assert f["-mA"] == "sevme"
    assert f["-gI"] == "sevgi"           # g (voiced) + i
    assert f["-Iş"] == "seviş"
    assert f["-DIr- (ettirgen)"] == "sevdirmek"
    assert f["-Il- (edilgen)"] == "sevilmek"
    assert f["-In- (dönüşlü)"] == "sevinmek"
    assert f["-Iş- (işteş)"] == "sevişmek"


def test_causative_t_variant():
    # -t ettirgen: ünlü-final/l-r-final kökte gerçek (okut/oturt/kısalt),
    # ünsüz-final kökte non-word (yaptmak) → sözlükte yok, soluk kalır.
    assert _forms("okumak", "verb")["-t- (ettirgen)"] == "okutmak"
    assert _forms("oturmak", "verb")["-t- (ettirgen)"] == "oturtmak"
    assert _forms("kısalmak", "verb")["-t- (ettirgen)"] == "kısaltmak"
    # iki ettirgen allomorfu birlikte sunulur (biri gerçek, öbürü aday)
    assert _forms("yapmak", "verb")["-DIr- (ettirgen)"] == "yaptırmak"


def test_verb_softening_vowel_initial():
    # ünlü-başlı ek → kök yumuşaması (git→gid); ünsüz-başlıda ham kök (git→gitki).
    f = _forms("gitmek", "verb")
    assert f["-Iş"] == "gidiş"           # yumuşama
    assert f["-gI"] == "gitki"           # ünsüz-başlı → yumuşama YOK, k (t sert)
    assert f["-Il- (edilgen)"] == "gidilmek"


def test_verb_vowel_final_buffer():
    # ünlü-final kök + ünlü-başlı ek → kaynaştırma -y-
    f = _forms("okumak", "verb")
    assert f["-Iş"] == "okuyuş"
    assert f["-mA"] == "okuma"


def test_compound_verb_prefix():
    f = _forms("bahse girmek", "verb")
    assert f["-mA"] == "bahse girme"
    assert f["-Iş"] == "bahse giriş"


def test_non_inflectable_none():
    assert derivations("güzel", "adjective") is None
    assert derivations("book", "noun", lang="en") is None
    assert derivations("", "noun") is None


def test_never_raises():
    for hw, pos in [("", "noun"), ("x", "verb"), ("kâr", "noun"),
                    ("Al", "noun"), ("gitmek", "verb")]:
        r = derivations(hw, pos)
        assert r is None or isinstance(r, list)


def test_added_noun_suffixes():
    # turkedebiyati.org karşılaştırması sonrası eklenenler
    assert _forms("Türk", "noun")["-CA"] == "Türkçe"
    assert _forms("ev", "noun")["-CIl"] == "evcil"


def test_added_verb_to_noun():
    f = _forms("yapmak", "verb")
    assert f["-IcI"] == "yapıcı"
    assert _forms("açmak", "verb")["-Ik"] == "açık"
    assert _forms("sevmek", "verb")["-Inç"] == "sevinç"
    assert _forms("akmak", "verb")["-IntI"] == "akıntı"


def test_added_noun_to_verb():
    assert _forms("az", "noun")["-Al-"] == "azalmak"
    assert _forms("yaş", "noun")["-A-"] == "yaşamak"
    assert _forms("ben", "noun")["-ImsA-"] == "benimsemek"
    assert _forms("su", "noun")["-sA-"] == "susamak"
    assert _forms("mor", "noun")["-Ar-"] == "morarmak"


def test_added_causative_ir_ar():
    # -Ir/-Ar ettirgen allomorfları; -Ar git→gidermek (gerçek ettirgen!)
    assert _forms("pişmek", "verb")["-Ir- (ettirgen)"] == "pişirmek"
    assert _forms("gitmek", "verb")["-Ar- (ettirgen)"] == "gidermek"
    assert _forms("çıkmak", "verb")["-Ar- (ettirgen)"] == "çıkarmak"
    assert _forms("kovmak", "verb")["-AlA- (pekiştirme)"] == "kovalamak"


def test_fiilimsi_category():
    f = _forms("gelmek", "verb")
    # isim-fiil / sıfat-fiil (ortaç) / zarf-fiil (ulaç)
    assert f["-mA"] == "gelme"
    assert f["-An"] == "gelen"
    assert f["-DIk"] == "geldik"
    assert f["-AcAk"] == "gelecek"          # lekstikselleşirse linklenir (isim)
    assert f["-mIş"] == "gelmiş"
    assert f["-ArAk"] == "gelerek"
    assert f["-IncA"] == "gelince"
    assert f["-DIkçA"] == "geldikçe"
    assert _forms("okumak", "verb")["-ArAk"] == "okuyarak"   # kaynaştırma


def test_fiilimsi_categories_present():
    cats = {r["category"] for r in derivations("gelmek", "verb")}
    assert "fiilimsi · isim-fiil" in cats
    assert "fiilimsi · sıfat-fiil (ortaç)" in cats
    assert "fiilimsi · zarf-fiil (ulaç)" in cats


def test_categories_present():
    d = derivations("sevmek", "verb")
    cats = {r["category"] for r in d}
    assert "fiil → isim" in cats
    assert "fiil → fiil (çatı)" in cats
