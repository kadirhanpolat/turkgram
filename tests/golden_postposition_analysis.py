"""Bağımsız golden — edat analizi (SPEC §7). Motor-körü kuruldu.

Precision stili: postposition okuması GÖT içinde olmalı (want ⊆ got).
"""

# Tüm 23 edat postposition okuması döndürmeli (closed-set, additive)
POSTPOSITION_PRESENT = [
    "için", "ile", "gibi", "kadar", "göre", "karşı", "rağmen", "doğru",
    "dek", "değin", "üzere", "önce", "sonra", "beri", "itibaren", "başka",
    "dolayı", "ötürü", "aşkın", "dair", "ilişkin", "ait", "yana",
]

# Adversarial homograflar: postposition okuması EKLENİR ama disambiguation'da
# doğru okumayı GEÇMEZ. (yüzey, doğru_okuma_pos)
# NOT: analyze() düz sözcük için pos="adj" ÜRETMEZ; "başka"/"aşkın" bare-noun
# decline okuması pos="noun" alır (kind=decline, _KIND_PRIOR=2 > postposition=0).
HOMOGRAPH_NOT_TOP = [
    ("aşkın", "noun"),
    ("başka", "noun"),
]

# Belirsizlik: hem postposition hem başka okuma DÖNER. "göre" = gör+(-A ulaç).
# "sonra" DÜŞÜRÜLDÜ: analyze'da zarf kind'ı yok, güvenilir 2. okuma round-trip etmez.
AMBIGUOUS = [
    ("göre", "postposition"),
]
