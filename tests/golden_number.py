# -*- coding: utf-8 -*-
"""Bağımsız golden veri — sayı sıfatları (Faz 5 D1): ordinal + distributif + decline round-trip.

Bu MODÜL saf VERİdir: test_* fonksiyon İÇERMEZ (pytest doğrudan toplamaz).
Runner ayrı dosyada (tests/test_number.py) bu listeleri tüketir.

Beklentiler MOTORDAN BAĞIMSIZ, dilbilgisinden elle doğrulanmıştır (spec/number-spec.md):

  Ordinal  -(I)ncI :
    - ünsüz-final gövde → +IncI  (I = yüksek 4'lü: ı/i/u/ü; son ünlüye göre)
    - ünlü-final gövde  → +ncI   (baştaki I düşer)
    - C daima c (n sonrası sedalı; asla ç)
    - dört → dördüncü  (t→d yumuşama), on → onuncu (o→u yuvarlak-yüksek)

  Distributif  -(ş)Ar :
    - ünlü-final → +şAr  (A = alçak 2'li: a/e)
    - ünsüz-final → +Ar  (ş yok)
    - son ünsüz sedalılaşması YALNIZ {t:d}: dört → dörder
      (üç, kırk, beş: sedalılaşma OLMAZ — üçer, kırkar, beşer)
    - üç ünsüz-finaldir (ç) → üçer (ş YOK)

  Decline round-trip: ordinal biçim ünlü-final (…ncı/…üncü/…uncu) → -y-/-n- kaynaştırma.
"""

# Ordinal golden: (girdi_kök, beklenen_ordinal)
ORDINAL_CASES = [
    ("sıfır", "sıfırıncı"),
    ("bir", "birinci"),
    ("iki", "ikinci"),
    ("üç", "üçüncü"),
    ("dört", "dördüncü"),
    ("beş", "beşinci"),
    ("altı", "altıncı"),
    ("yedi", "yedinci"),
    ("sekiz", "sekizinci"),
    ("dokuz", "dokuzuncu"),
    ("on", "onuncu"),
    ("yirmi", "yirminci"),
    ("otuz", "otuzuncu"),
    ("kırk", "kırkıncı"),
    ("elli", "ellinci"),
    ("altmış", "altmışıncı"),
    ("yetmiş", "yetmişinci"),
    ("seksen", "sekseninci"),
    ("doksan", "doksanıncı"),
    ("yüz", "yüzüncü"),
    ("bin", "bininci"),
    ("milyon", "milyonuncu"),
    # bileşik: son sözcük eki alır
    ("yirmi bir", "yirmi birinci"),
    ("kırk beş", "kırk beşinci"),
    ("yüz on", "yüz onuncu"),
    ("bin dokuz yüz", "bin dokuz yüzüncü"),
]

# Distributif golden: (girdi_kök, beklenen_distributif)
DISTRIBUTIVE_CASES = [
    ("bir", "birer"),
    ("iki", "ikişer"),
    ("üç", "üçer"),
    ("dört", "dörder"),
    ("beş", "beşer"),
    ("altı", "altışar"),
    ("yedi", "yedişer"),
    ("sekiz", "sekizer"),
    ("dokuz", "dokuzar"),
    ("on", "onar"),
    ("yirmi", "yirmişer"),
    ("otuz", "otuzar"),
    ("kırk", "kırkar"),
    ("elli", "ellişer"),
    ("altmış", "altmışar"),
    ("yetmiş", "yetmişer"),
    ("seksen", "seksener"),
    ("doksan", "doksanar"),
    ("yüz", "yüzer"),
    ("bin", "biner"),
    ("milyon", "milyonar"),
    # bileşik: son sözcük eki alır
    ("yirmi bir", "yirmi birer"),
    ("kırk iki", "kırk ikişer"),
    ("yüz beş", "yüz beşer"),
]

# Decline round-trip: (ordinal_form, durum_kodu, beklenen_çekilmiş)
# durum kodları: "gen", "dat", "acc", "abl", "loc", "ins"
DECLINE_CASES = [
    ("birinci", "gen", "birincinin"),
    ("birinci", "dat", "birinciye"),
    ("birinci", "acc", "birinciyi"),
    ("birinci", "abl", "birinciden"),
    ("birinci", "loc", "birincide"),
    ("birinci", "ins", "birinciyle"),
    ("üçüncü", "gen", "üçüncünün"),
    ("üçüncü", "dat", "üçüncüye"),
    ("üçüncü", "acc", "üçüncüyü"),
    ("onuncu", "acc", "onuncuyu"),
    ("onuncu", "dat", "onuncuya"),
    ("onuncu", "loc", "onuncuda"),
    ("dördüncü", "abl", "dördüncüden"),
    ("dördüncü", "ins", "dördüncüyle"),
    ("beşinci", "gen", "beşincinin"),
    ("beşinci", "loc", "beşincide"),
]
