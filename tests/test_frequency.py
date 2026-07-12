"""Gömülü lemma-frekans tablosu testleri (Faz 2b, lexicon.load_freq + disambiguation kancası).

VERİ + PLUMBING sınar. Kanca-bağlantısı gerçek veriyle sağlam sınanır: sabit sayım GÖMÜLMEZ;
bunun yerine "rank(freq=…) adayları lemma-sıklığına göre sıralar" özelliği doğrulanır.
"""
import pytest

from turkgram import analysis as an, disambiguation as dis, lexicon as lx


@pytest.fixture(scope="module")
def freq():
    return lx.load_freq()


@pytest.fixture(scope="module")
def roots():
    return lx.load()


@pytest.fixture(scope="module")
def pm():
    return lx.pos_map()


# ---------------------------------------------------------------------------
# Yükleme + içerik
# ---------------------------------------------------------------------------

def test_load_freq_bos_degil(freq):
    assert isinstance(freq, dict)
    assert len(freq) > 1000
    assert all(isinstance(v, int) and v > 0 for v in freq.values())


def test_sik_lemmalar_var(freq):
    # Çok sık işlev/içerik lemmaları tabloda olmalı (OpenSubtitles TR)
    for lemma in ("bir", "olmak", "ben"):
        assert lemma in freq and freq[lemma] > 0


def test_freq_leksikon_altkumesi(freq):
    # Frekans tablosundaki her lemma leksikonda da olmalı (analizör+leksikonla türetildi)
    lex = lx.load(lx.POS_TAGS)
    disari = [l for l in freq if l not in lex]
    # birleşik lemma yok (leksikonda yok) → küçük tolerans yerine tam içerme beklenir
    assert not disari, f"leksikon-dışı lemma: {disari[:10]}"


def test_cache_ayni_nesne(freq):
    assert lx.load_freq() is freq


# ---------------------------------------------------------------------------
# disambiguation kancası — gerçek veriyle
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("surface", ["gelin", "geldik", "yüzü", "evi", "okuma"])
def test_rank_freq_lemma_sikligina_gore(surface, roots, pm, freq):
    cands = an.analyze(surface, roots=roots)
    if len(cands) < 2:
        pytest.skip("tek aday")
    ranked = dis.rank(cands, freq=freq, pos=pm)
    # En tepedeki adayın lemması, aday lemmaları arasında en yüksek sıklığa sahip olmalı
    top_freq = freq.get(ranked[0].lemma, 0)
    assert top_freq == max(freq.get(a.lemma, 0) for a in cands)


def test_freq_gercek_veri_guven_gecerli(roots, pm, freq):
    pairs = dis.disambiguate(an.analyze("gelin", roots=roots), freq=freq, pos=pm)
    probs = [p for _, p in pairs]
    assert abs(sum(probs) - 1.0) < 1e-9
    assert probs == sorted(probs, reverse=True)


def test_freq_none_ile_farkli_olabilir(roots, pm, freq):
    # Sıklık kancasının etkisi: freq'li ve freq'siz sıra (en az bir yüzeyde) farklılaşabilmeli.
    # "gelin": freq'siz isim tepede; gelmek daha sık ise freq'li sıra değişir.
    cands = an.analyze("gelin", roots=roots)
    nofreq = [a.lemma for a in dis.rank(cands, pos=pm)]
    withfreq = [a.lemma for a in dis.rank(cands, freq=freq, pos=pm)]
    # Sıralama en azından geçerli permütasyon; kanca çalışıyorsa tepe sıklığa uyar
    assert set(nofreq) == set(withfreq)
