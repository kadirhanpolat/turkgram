# tests/golden_root_candidates_fix.py
# Motor-körü bağımsız golden — elle doğrulanmış kök aday beklentileri
# Bu yüzeyler _root_candidates() tarafından HENÜZ bulunamayan bilinen miss vakalarıdır.

GOLDEN = [
    # (yüzey, beklenen_kök, açıklama)
    ("inhiyor",     "inhimak",    "Fix1: disharmonik alıntı her iki mastar varyantı"),
    ("suyor",       "somak",      "Fix2: monosilab ünlü-düşme, taban='s' vowelsiz"),
    ("çuyor",       "çomak",      "Fix2: monosilab ünlü-düşme, taban='ç' vowelsiz"),
    ("yorgalıyor",  "yorgalamak", "Fix3: rfind — yor_idx=0 guard'ı atlatır"),
    ("yorumluyor",  "yorumlamak", "Fix3: rfind — yor ilk oluşum konumu düzeltildi"),
]
