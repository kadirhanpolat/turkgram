# tests/golden_phonology.py
# Motor-körü bağımsız golden — Türkçe IPA transkripsiyon

IPA_CHARS = [
    # (girdi_char, beklenen_ipa_substring)
    ("a",  "a"),
    ("b",  "b"),
    ("c",  "dʒ"),
    ("ç",  "tʃ"),
    ("d",  "d"),
    ("e",  "e"),
    ("f",  "f"),
    ("g",  "ɡ"),
    ("h",  "h"),
    ("ı",  "ɯ"),
    ("i",  "i"),
    ("j",  "ʒ"),
    ("k",  "k"),    # bağımsız → art-ünlü varsayılan
    ("l",  "l"),    # bağımsız → ön-ünlü varsayılan
    ("m",  "m"),
    ("n",  "n"),
    ("o",  "o"),
    ("ö",  "ø"),
    ("p",  "p"),
    ("r",  "ɾ"),
    ("s",  "s"),
    ("ş",  "ʃ"),
    ("t",  "t"),
    ("u",  "u"),
    ("ü",  "y"),
    ("v",  "v"),
    ("y",  "j"),
    ("z",  "z"),
]

IPA_WORDS = [
    # (sözcük, beklenen_ipa)
    ("merhaba",   "meɾhaba"),
    ("Türkiye",   "tyɾcije"),
    ("öğrenci",   "øːɾendʒi"),   # ğ → önceki ö uzar (kelime-ortası)
    ("dağ",       "da"),           # kelime-sonu ğ sessiz (uzama yok)
    ("kırk",      "kɯɾk"),        # art-ünlü: k→/k/
    ("kelime",    "celime"),       # ön-ünlü: k→/c/
    ("gül",       "ɡyl"),
    ("çay",       "tʃaj"),
    ("şeker",     "ʃeceɾ"),       # k ön-ünlü yanında → /c/
]
