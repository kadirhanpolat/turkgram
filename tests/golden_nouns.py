# Elle doğrulanmış Türkçe isim çekimleri — motordan DEĞİL, dilbilgisinden.
#
# ANAHTAR SÖZLEŞMESİ (SPEC §10 — SABİT):
#   Yalın durum:    '<case>'                 ör. 'acc', 'dat', 'loc', 'abl', 'gen', 'ins'
#   Çoğul:          'pl.nom', 'pl.<case>'    ör. 'pl.loc'
#   İyelik:         'poss.<kişi>'            ör. 'poss.1sg', 'poss.3sg'
#   İyelik+durum:   'poss.<kişi>.<case>'     ör. 'poss.3sg.loc' (pronominal -n- testi)
#   Ek katmanlar:   'pred.3sg' (-DIr), 'ki.<case>' (-ki), 'ca' (-CA)
#
# case anahtarları (SPEC §4): acc dat loc abl gen ins  (nom = başlığın kendisi, atlanır)
# kişi: 1sg 2sg 3sg 1pl 2pl 3pl
#
# Beklenen string'ler ELLE üretildi; motora/koda BAKILMADAN, Türkçe dilbilgisiyle.
# Şüpheli/tartışmalı biçim varsa satır sonunda '# ?' yorumu vardır (hakem bakar).

GOLDEN_NOUNS = {

    # === Grup 1: Düz ünsüz-final (yumuşama YOK) ===
    'ev': {
        'acc': 'evi', 'dat': 'eve', 'loc': 'evde', 'abl': 'evden', 'gen': 'evin',
        'ins': 'evle',
        'pl.nom': 'evler', 'pl.loc': 'evlerde', 'pl.abl': 'evlerden',
        'poss.1sg': 'evim', 'poss.2sg': 'evin', 'poss.3sg': 'evi',
        'poss.1pl': 'evimiz', 'poss.2pl': 'eviniz', 'poss.3pl': 'evleri',
        'poss.3sg.loc': 'evinde', 'poss.3sg.acc': 'evini', 'poss.3sg.dat': 'evine',
        'poss.3sg.abl': 'evinden', 'poss.3sg.gen': 'evinin',
        'poss.1sg.loc': 'evimde', 'poss.1sg.acc': 'evimi', 'poss.1sg.gen': 'evimin',
        'poss.3pl.loc': 'evlerinde', 'poss.3pl.abl': 'evlerinden',
        'pred.3sg': 'evdir',
        'ki.loc': 'evdeki',
    },
    'göz': {  # yuvarlak ön harmoni (ö → ü/e/ö)
        'acc': 'gözü', 'dat': 'göze', 'loc': 'gözde', 'abl': 'gözden', 'gen': 'gözün',
        'ins': 'gözle',
        'pl.nom': 'gözler', 'pl.loc': 'gözlerde',
        'poss.1sg': 'gözüm', 'poss.2sg': 'gözün', 'poss.3sg': 'gözü',
        'poss.1pl': 'gözümüz', 'poss.2pl': 'gözünüz', 'poss.3pl': 'gözleri',
        'poss.3sg.loc': 'gözünde', 'poss.3sg.acc': 'gözünü', 'poss.3sg.dat': 'gözüne',
        'poss.3pl.dat': 'gözlerine',
        'pred.3sg': 'gözdür',
        'ki.loc': 'gözdeki',
    },
    'kalem': {  # düz ünsüz-final, ön/düz harmoni (e → i/e)
        'acc': 'kalemi', 'dat': 'kaleme', 'loc': 'kalemde', 'abl': 'kalemden', 'gen': 'kalemin',
        'ins': 'kalemle',
        'pl.nom': 'kalemler', 'pl.loc': 'kalemlerde',
        'poss.1sg': 'kalemim', 'poss.2sg': 'kalemin', 'poss.3sg': 'kalemi',
        'poss.1pl': 'kalemimiz', 'poss.2pl': 'kaleminiz', 'poss.3pl': 'kalemleri',
        'poss.3sg.loc': 'kaleminde', 'poss.3sg.acc': 'kalemini',
        'pred.3sg': 'kalemdir',
        'ki.loc': 'kalemdeki',
    },
    'yol': {  # arka/yuvarlak harmoni (o → u/a/o)
        'acc': 'yolu', 'dat': 'yola', 'loc': 'yolda', 'abl': 'yoldan', 'gen': 'yolun',
        'ins': 'yolla',
        'pl.nom': 'yollar', 'pl.loc': 'yollarda',
        'poss.1sg': 'yolum', 'poss.2sg': 'yolun', 'poss.3sg': 'yolu',
        'poss.1pl': 'yolumuz', 'poss.2pl': 'yolunuz', 'poss.3pl': 'yolları',
        'poss.3sg.loc': 'yolunda', 'poss.3sg.dat': 'yoluna',
        'pred.3sg': 'yoldur',
        'ki.loc': 'yoldaki',
    },
    'okul': {  # arka/yuvarlak (u → u/a/u)
        'acc': 'okulu', 'dat': 'okula', 'loc': 'okulda', 'abl': 'okuldan', 'gen': 'okulun',
        'ins': 'okulla',
        'pl.nom': 'okullar', 'pl.loc': 'okullarda',
        'poss.1sg': 'okulum', 'poss.2sg': 'okulun', 'poss.3sg': 'okulu',
        'poss.1pl': 'okulumuz', 'poss.2pl': 'okulunuz', 'poss.3pl': 'okulları',
        'poss.3sg.loc': 'okulunda',
        'pred.3sg': 'okuldur',
        'ki.loc': 'okuldaki',
    },
    'köy': {  # ön/yuvarlak (ö → ü/e/ö)
        'acc': 'köyü', 'dat': 'köye', 'loc': 'köyde', 'abl': 'köyden', 'gen': 'köyün',
        'ins': 'köyle',
        'pl.nom': 'köyler', 'pl.loc': 'köylerde',
        'poss.1sg': 'köyüm', 'poss.3sg': 'köyü',
        'poss.3sg.loc': 'köyünde',
        'pred.3sg': 'köydür',
    },
    'gül': {  # ön/yuvarlak (ü → ü/e/ü)
        'acc': 'gülü', 'dat': 'güle', 'loc': 'gülde', 'abl': 'gülden', 'gen': 'gülün',
        'ins': 'gülle',
        'pl.nom': 'güller',
        'poss.1sg': 'gülüm', 'poss.3sg': 'gülü',
        'poss.3sg.loc': 'gülünde',
        'pred.3sg': 'güldür',
    },

    # === Grup 2: Ünlü-final (buffer testi: acc/dat -y-, gen -n-, 3sg -sI) ===
    'kapı': {  # arka/düz (ı)
        'acc': 'kapıyı', 'dat': 'kapıya', 'loc': 'kapıda', 'abl': 'kapıdan', 'gen': 'kapının',
        'ins': 'kapıyla',
        'pl.nom': 'kapılar', 'pl.loc': 'kapılarda',
        'poss.1sg': 'kapım', 'poss.2sg': 'kapın', 'poss.3sg': 'kapısı',
        'poss.1pl': 'kapımız', 'poss.2pl': 'kapınız', 'poss.3pl': 'kapıları',
        'poss.3sg.loc': 'kapısında', 'poss.3sg.acc': 'kapısını', 'poss.3sg.dat': 'kapısına',
        'poss.1sg.loc': 'kapımda',
        'pred.3sg': 'kapıdır',
        'ki.loc': 'kapıdaki',
    },
    'masa': {  # arka/düz (a)
        'acc': 'masayı', 'dat': 'masaya', 'loc': 'masada', 'abl': 'masadan', 'gen': 'masanın',
        'ins': 'masayla',
        'pl.nom': 'masalar', 'pl.loc': 'masalarda',
        'poss.1sg': 'masam', 'poss.2sg': 'masan', 'poss.3sg': 'masası',
        'poss.1pl': 'masamız', 'poss.2pl': 'masanız', 'poss.3pl': 'masaları',
        'poss.3sg.loc': 'masasında', 'poss.3sg.acc': 'masasını',
        'pred.3sg': 'masadır',
        'ki.loc': 'masadaki',
    },
    'araba': {  # arka/düz (a)
        'acc': 'arabayı', 'dat': 'arabaya', 'loc': 'arabada', 'abl': 'arabadan', 'gen': 'arabanın',
        'ins': 'arabayla',
        'pl.nom': 'arabalar',
        'poss.1sg': 'arabam', 'poss.2sg': 'araban', 'poss.3sg': 'arabası',
        'poss.1pl': 'arabamız', 'poss.3pl': 'arabaları',
        'poss.3sg.loc': 'arabasında', 'poss.3sg.dat': 'arabasına',
        'pred.3sg': 'arabadır',
    },
    'elma': {  # arka/düz (a)
        'acc': 'elmayı', 'dat': 'elmaya', 'loc': 'elmada', 'abl': 'elmadan', 'gen': 'elmanın',
        'ins': 'elmayla',
        'pl.nom': 'elmalar',
        'poss.1sg': 'elmam', 'poss.3sg': 'elması',
        'poss.3sg.loc': 'elmasında',
        'pred.3sg': 'elmadır',
    },
    'ütü': {  # ön/yuvarlak (ü)
        'acc': 'ütüyü', 'dat': 'ütüye', 'loc': 'ütüde', 'abl': 'ütüden', 'gen': 'ütünün',
        'ins': 'ütüyle',
        'pl.nom': 'ütüler',
        'poss.1sg': 'ütüm', 'poss.3sg': 'ütüsü',
        'poss.3sg.loc': 'ütüsünde',
        'pred.3sg': 'ütüdür',
    },
    'kutu': {  # arka/yuvarlak (u)
        'acc': 'kutuyu', 'dat': 'kutuya', 'loc': 'kutuda', 'abl': 'kutudan', 'gen': 'kutunun',
        'ins': 'kutuyla',
        'pl.nom': 'kutular',
        'poss.1sg': 'kutum', 'poss.3sg': 'kutusu',
        'poss.3sg.loc': 'kutusunda', 'poss.3sg.acc': 'kutusunu',
        'pred.3sg': 'kutudur',
    },
    'arı': {  # arka/düz (ı)
        'acc': 'arıyı', 'dat': 'arıya', 'loc': 'arıda', 'abl': 'arıdan', 'gen': 'arının',
        'ins': 'arıyla',
        'pl.nom': 'arılar',
        'poss.1sg': 'arım', 'poss.3sg': 'arısı',
        'poss.3sg.loc': 'arısında',
        'pred.3sg': 'arıdır',
    },

    # === Grup 3: Yumuşama (softens: son ünsüz ünlü önünde yumuşar) ===
    'kitap': {  # p → b, çok-heceli
        'acc': 'kitabı', 'dat': 'kitaba', 'loc': 'kitapta', 'abl': 'kitaptan', 'gen': 'kitabın',
        'ins': 'kitapla',  # l ünsüz-başlı → p SERT
        'pl.nom': 'kitaplar', 'pl.loc': 'kitaplarda', 'pl.abl': 'kitaplardan',
        'poss.1sg': 'kitabım', 'poss.2sg': 'kitabın', 'poss.3sg': 'kitabı',
        'poss.1pl': 'kitabımız', 'poss.2pl': 'kitabınız', 'poss.3pl': 'kitapları',  # -lArI ünsüz → p SERT
        'poss.3sg.loc': 'kitabında', 'poss.3sg.acc': 'kitabını', 'poss.3sg.dat': 'kitabına',
        'poss.1sg.loc': 'kitabımda',
        'poss.1pl.loc': 'kitabımızda',
        'pred.3sg': 'kitaptır',  # -DIr ünsüz-başlı → p SERT
        'ki.loc': 'kitaptaki',
    },
    'ağaç': {  # ç → c, çok-heceli
        'acc': 'ağacı', 'dat': 'ağaca', 'loc': 'ağaçta', 'abl': 'ağaçtan', 'gen': 'ağacın',
        'ins': 'ağaçla',
        'pl.nom': 'ağaçlar', 'pl.loc': 'ağaçlarda',
        'poss.1sg': 'ağacım', 'poss.3sg': 'ağacı', 'poss.3pl': 'ağaçları',
        'poss.3sg.loc': 'ağacında', 'poss.3sg.dat': 'ağacına',
        'pred.3sg': 'ağaçtır',
        'ki.loc': 'ağaçtaki',
    },
    'kanat': {  # t → d, çok-heceli
        'acc': 'kanadı', 'dat': 'kanada', 'loc': 'kanatta', 'abl': 'kanattan', 'gen': 'kanadın',
        'ins': 'kanatla',
        'pl.nom': 'kanatlar',
        'poss.1sg': 'kanadım', 'poss.3sg': 'kanadı', 'poss.3pl': 'kanatları',
        'poss.3sg.loc': 'kanadında',
        'pred.3sg': 'kanattır',
    },
    'bebek': {  # k → ğ, çok-heceli, ön/düz
        'acc': 'bebeği', 'dat': 'bebeğe', 'loc': 'bebekte', 'abl': 'bebekten', 'gen': 'bebeğin',
        'ins': 'bebekle',
        'pl.nom': 'bebekler',
        'poss.1sg': 'bebeğim', 'poss.3sg': 'bebeği', 'poss.3pl': 'bebekleri',
        'poss.3sg.loc': 'bebeğinde', 'poss.3sg.dat': 'bebeğine',
        'pred.3sg': 'bebektir',
    },
    'renk': {  # nk → ng (k → g, ğ DEĞİL), ön/düz
        'acc': 'rengi', 'dat': 'renge', 'loc': 'renkte', 'abl': 'renkten', 'gen': 'rengin',
        'ins': 'renkle',
        'pl.nom': 'renkler',
        'poss.1sg': 'rengim', 'poss.3sg': 'rengi', 'poss.3pl': 'renkleri',
        'poss.3sg.loc': 'renginde',
        'pred.3sg': 'renktir',
    },
    'çocuk': {  # k → ğ, çok-heceli, arka/yuvarlak
        'acc': 'çocuğu', 'dat': 'çocuğa', 'loc': 'çocukta', 'abl': 'çocuktan', 'gen': 'çocuğun',
        'ins': 'çocukla',
        'pl.nom': 'çocuklar', 'pl.loc': 'çocuklarda',
        'poss.1sg': 'çocuğum', 'poss.3sg': 'çocuğu', 'poss.3pl': 'çocukları',
        'poss.3sg.loc': 'çocuğunda', 'poss.3sg.dat': 'çocuğuna',
        'pred.3sg': 'çocuktur',
        'ca': 'çocukça',
    },
    'dolap': {  # p → b, çok-heceli, arka/düz
        'acc': 'dolabı', 'dat': 'dolaba', 'loc': 'dolapta', 'abl': 'dolaptan', 'gen': 'dolabın',
        'ins': 'dolapla',
        'pl.nom': 'dolaplar',
        'poss.1sg': 'dolabım', 'poss.3sg': 'dolabı', 'poss.3pl': 'dolapları',
        'poss.3sg.loc': 'dolabında',
        'pred.3sg': 'dolaptır',
    },

    # === Grup 4: Softens-YOK tuzağı (çok-heceli ama SERT kalan / tek-heceli sert) ===
    'sepet': {  # SOFTEN_NO: sepet → sepeti (t SERT)
        'acc': 'sepeti', 'dat': 'sepete', 'loc': 'sepette', 'abl': 'sepetten', 'gen': 'sepetin',
        'ins': 'sepetle',
        'pl.nom': 'sepetler',
        'poss.1sg': 'sepetim', 'poss.3sg': 'sepeti', 'poss.3pl': 'sepetleri',
        'poss.3sg.loc': 'sepetinde',
        'pred.3sg': 'sepettir',
    },
    'top': {  # tek-heceli SERT: top → topu
        'acc': 'topu', 'dat': 'topa', 'loc': 'topta', 'abl': 'toptan', 'gen': 'topun',
        'ins': 'topla',
        'pl.nom': 'toplar',
        'poss.1sg': 'topum', 'poss.3sg': 'topu', 'poss.3pl': 'topları',
        'poss.3sg.loc': 'topunda',
        'pred.3sg': 'toptur',
    },
    'saat': {  # SOFTEN_NO: saat → saati (t SERT)
        'acc': 'saati', 'dat': 'saate', 'loc': 'saatte', 'abl': 'saatten', 'gen': 'saatin',
        'ins': 'saatle',
        'pl.nom': 'saatler',
        'poss.1sg': 'saatim', 'poss.3sg': 'saati', 'poss.3pl': 'saatleri',
        'poss.3sg.loc': 'saatinde',
        'pred.3sg': 'saattir',
    },
    'at': {  # tek-heceli SERT: at → atı
        'acc': 'atı', 'dat': 'ata', 'loc': 'atta', 'abl': 'attan', 'gen': 'atın',
        'ins': 'atla',
        'pl.nom': 'atlar',
        'poss.1sg': 'atım', 'poss.3sg': 'atı', 'poss.3pl': 'atları',
        'poss.3sg.loc': 'atında',
        'pred.3sg': 'attır',
    },
    'millet': {  # SOFTEN_NO: millet → milleti (t SERT)
        'acc': 'milleti', 'dat': 'millete', 'loc': 'millette', 'abl': 'milletten', 'gen': 'milletin',
        'ins': 'milletle',
        'pl.nom': 'milletler',
        'poss.1sg': 'milletim', 'poss.3sg': 'milleti', 'poss.3pl': 'milletleri',
        'poss.3sg.loc': 'milletinde',
        'pred.3sg': 'millettir',
    },
    'park': {  # tek-heceli SERT (nk ama sert): park → parkı
        'acc': 'parkı', 'dat': 'parka', 'loc': 'parkta', 'abl': 'parktan', 'gen': 'parkın',
        'ins': 'parkla',
        'pl.nom': 'parklar',
        'poss.1sg': 'parkım', 'poss.3sg': 'parkı', 'poss.3pl': 'parkları',
        'poss.3sg.loc': 'parkında',
        'pred.3sg': 'parktır',
    },

    # === Grup 5: Ünlü düşmesi (drops_vowel: son hece ünlüsü ünlü önünde düşer) ===
    'burun': {  # burun → burn-, arka/yuvarlak
        'acc': 'burnu', 'dat': 'burna', 'loc': 'burunda', 'abl': 'burundan', 'gen': 'burnun',
        'ins': 'burunla',
        'pl.nom': 'burunlar',  # ünsüz-başlı çoğul → ünlü KORUNUR
        'poss.1sg': 'burnum', 'poss.2sg': 'burnun', 'poss.3sg': 'burnu',
        'poss.1pl': 'burnumuz', 'poss.3pl': 'burunları',  # -lArI ünsüz → ünlü KORUNUR
        'poss.3sg.loc': 'burnunda', 'poss.3sg.dat': 'burnuna',
        'pred.3sg': 'burundur',
    },
    'şehir': {  # şehir → şehr-, drops ama softens DEĞİL (r zaten yumuşak), ön/düz
        'acc': 'şehri', 'dat': 'şehre', 'loc': 'şehirde', 'abl': 'şehirden', 'gen': 'şehrin',
        'ins': 'şehirle',
        'pl.nom': 'şehirler',
        'poss.1sg': 'şehrim', 'poss.3sg': 'şehri', 'poss.3pl': 'şehirleri',
        'poss.3sg.loc': 'şehrinde', 'poss.3sg.dat': 'şehrine',
        'pred.3sg': 'şehirdir',
    },
    'ağız': {  # ağız → ağz-, arka/düz
        'acc': 'ağzı', 'dat': 'ağza', 'loc': 'ağızda', 'abl': 'ağızdan', 'gen': 'ağzın',
        'ins': 'ağızla',
        'pl.nom': 'ağızlar',
        'poss.1sg': 'ağzım', 'poss.3sg': 'ağzı', 'poss.3pl': 'ağızları',
        'poss.3sg.loc': 'ağzında',
        'pred.3sg': 'ağızdır',
    },
    'oğul': {  # oğul → oğl-, arka/yuvarlak
        'acc': 'oğlu', 'dat': 'oğla', 'loc': 'oğulda', 'abl': 'oğuldan', 'gen': 'oğlun',
        'ins': 'oğulla',
        'pl.nom': 'oğullar',
        'poss.1sg': 'oğlum', 'poss.3sg': 'oğlu', 'poss.3pl': 'oğulları',
        'poss.3sg.loc': 'oğlunda',
        'pred.3sg': 'oğuldur',
    },
    'akıl': {  # akıl → akl-, arka/düz
        'acc': 'aklı', 'dat': 'akla', 'loc': 'akılda', 'abl': 'akıldan', 'gen': 'aklın',
        'ins': 'akılla',
        'pl.nom': 'akıllar',
        'poss.1sg': 'aklım', 'poss.3sg': 'aklı', 'poss.3pl': 'akılları',
        'poss.3sg.loc': 'aklında', 'poss.3sg.dat': 'aklına',
        'pred.3sg': 'akıldır',
    },
    'gönül': {  # gönül → gönl-, ön/yuvarlak
        'acc': 'gönlü', 'dat': 'gönle', 'loc': 'gönülde', 'abl': 'gönülden', 'gen': 'gönlün',
        'ins': 'gönülle',
        'pl.nom': 'gönüller',
        'poss.1sg': 'gönlüm', 'poss.3sg': 'gönlü', 'poss.3pl': 'gönülleri',
        'poss.3sg.loc': 'gönlünde',
        'pred.3sg': 'gönüldür',
    },
    'vakit': {  # vakit → vakt-, drops AMA softens YOK (t SERT kalır: vakti)
        'acc': 'vakti', 'dat': 'vakte', 'loc': 'vakitte', 'abl': 'vakitten', 'gen': 'vaktin',
        'ins': 'vakitle',
        'pl.nom': 'vakitler',
        'poss.1sg': 'vaktim', 'poss.3sg': 'vakti', 'poss.3pl': 'vakitleri',
        'poss.3sg.loc': 'vaktinde',
        'pred.3sg': 'vakittir',
    },

    # === Grup 6: İkizleşme (doubles: son ünsüz ünlü önünde ikizleşir) ===
    'hak': {  # hak → hakk-, arka/düz
        'acc': 'hakkı', 'dat': 'hakka', 'loc': 'hakta', 'abl': 'haktan', 'gen': 'hakkın',
        'ins': 'hakla',
        'pl.nom': 'haklar',
        'poss.1sg': 'hakkım', 'poss.3sg': 'hakkı', 'poss.3pl': 'hakları',
        'poss.3sg.loc': 'hakkında',
        'pred.3sg': 'haktır',
    },
    'his': {  # his → hiss-, ön/düz
        'acc': 'hissi', 'dat': 'hisse', 'loc': 'histe', 'abl': 'histen', 'gen': 'hissin',
        'ins': 'hisle',
        'pl.nom': 'hisler',
        'poss.1sg': 'hissim', 'poss.3sg': 'hissi', 'poss.3pl': 'hisleri',
        'poss.3sg.loc': 'hissinde',
        'pred.3sg': 'histir',
    },
    'af': {  # af → aff-, arka/düz
        'acc': 'affı', 'dat': 'affa', 'loc': 'afta', 'abl': 'aftan', 'gen': 'affın',
        'ins': 'afla',
        'pl.nom': 'aflar',
        'poss.1sg': 'affım', 'poss.3sg': 'affı', 'poss.3pl': 'afları',
        'poss.3sg.loc': 'affında',
        'pred.3sg': 'aftır',
    },

    # === Grup 8: Zamir / özel istisnalar (SPEC §8) ===
    'ben': {
        'acc': 'beni', 'dat': 'bana', 'loc': 'bende', 'abl': 'benden', 'gen': 'benim',
        'ins': 'benimle',
        # 'ben' çoğulu suppletif (biz/bizler) — üretken sistem dışı; SPEC §8
        # zamir çoğulunu kapsam-dışı bırakır (hakem kararı 2026-07-11).
    },
    'sen': {
        'acc': 'seni', 'dat': 'sana', 'loc': 'sende', 'abl': 'senden', 'gen': 'senin',
        'ins': 'seninle',
    },
    'o': {  # gövde on- (pronominal n)
        'acc': 'onu', 'dat': 'ona', 'loc': 'onda', 'abl': 'ondan', 'gen': 'onun',
        'ins': 'onunla',
        'pl.nom': 'onlar',
    },
    'bu': {  # gövde bun-
        'acc': 'bunu', 'dat': 'buna', 'loc': 'bunda', 'abl': 'bundan', 'gen': 'bunun',
        'ins': 'bununla',
        'pl.nom': 'bunlar',
    },
    'şu': {  # gövde şun-
        'acc': 'şunu', 'dat': 'şuna', 'loc': 'şunda', 'abl': 'şundan', 'gen': 'şunun',
        'ins': 'şununla',
        'pl.nom': 'şunlar',
    },
    'biz': {  # düzenli
        'acc': 'bizi', 'dat': 'bize', 'loc': 'bizde', 'abl': 'bizden', 'gen': 'bizim',
        'ins': 'bizimle',
    },
    'siz': {  # düzenli
        'acc': 'sizi', 'dat': 'size', 'loc': 'sizde', 'abl': 'sizden', 'gen': 'sizin',
        'ins': 'sizinle',
    },
    'ne': {  # buffer -y- (ne-y-i), ön/düz
        'acc': 'neyi', 'dat': 'neye', 'loc': 'nede', 'abl': 'neden', 'gen': 'neyin',  # ? loc 'nede'/'neyde' ikisi de; abl 'neden' düzensiz
        'ins': 'neyle',
    },
    'su': {  # gen buffer -y- DÜZENSİZ (suyun; normalde ünlü-final gen -n- olurdu)
        'acc': 'suyu', 'dat': 'suya', 'loc': 'suda', 'abl': 'sudan', 'gen': 'suyun',
        'ins': 'suyla',
        'pl.nom': 'sular',
        'poss.1sg': 'suyum', 'poss.3sg': 'suyu',  # ? 3sg iyelik 'suyu' (su-y-u); homograf acc ile
        'poss.3sg.loc': 'suyunda',
        'pred.3sg': 'sudur',
    },
}
