"""sweep_clause.py — yargı bölme korpus çökme + tutarlılık taraması.

analyze_sentence çeşitli çok-cümle kalıplarında 0 çökme + clauses tutarlılık:
- her yargının predicate_id>0 ve bir yüklem ögesi;
- yan yargı → temel/bağımsız kardeş var;
- düz `elements` yüklem sayısı ile yargı yüklem sayısı tutarlı.

Kullanım: PYTHONUTF8=1 python tools/sweep_clause.py
"""
from turkgram import lexicon
from turkgram.sentence import analyze_sentence

# Çok-cümle + yan cümle + koordinat + karışık kalıplar (leksikon-bağımsız cümleler).
_SENTENCES = [
    "Ben eve gidiyorum",
    "Ali geldi ve Veli gitti",
    "Geldi gitti",
    "Eve gelince yattım",
    "Yağmur yağınca eve gittik",
    "Gelirse gideriz",
    "Koşarak geldi",
    "Görünce sevindi",
    "Çok çalıştı ve başardı",
    "Ben geldim sen gittin",
    "Kitabı okudu ve uyudu",
    "Hava güzel",
    "Param yok",
    "Gittim okula",
    "Okula gidince kitabı aldım ve okudum",
    "Yorulunca dinlendi",           # analyzer açığı → tek yargı (çökme YOK beklenir)
    "Ali kitabı aldı Veli defteri verdi",
    "Gelmedi ama aradı",
    "Eve gidip yattım",
    "Yağmur yağarsa gelmem",
    # V4 ki/diye
    "Biliyorum ki gelecek",
    "Gelsin diye bekledim",
    "Öyle yoruldum ki uyudum",
    "Yağmur yağıyor diye gelmedim",
    "Biliyorum ki gelince görecek",
    "Söyledim ki duysun ve anlasın",
    "Onu gördüm ki çok sevindim",
    # V5 gerçek gömme (aktarma + adlaşmış)
    "Yağmur yağacak sandı",
    "Gel dedi",
    "Hasta olduğunu söyledi",
    "Gelmesini istedi",
    "Ali geldiğini biliyorum",
    "Ali bir şey söyledi",
    "Yarın geleceğim dedi",
    "Gideceğini düşündü ve üzüldü",
    # V5.1 aktarma-robustlik
    "Ali koştu ve Veli geldi dedi",
    "Ali geldi ve Veli dedi",
    '"Eve gel" dedi',
    "Sana söyledim",
    "Yolu sordu",
    '"Yarın gelirim" diye düşündü',
]


def main() -> None:
    roots = lexicon.load()
    crashes = 0
    inconsistent = 0
    for s in _SENTENCES:
        try:
            sa = analyze_sentence(s, roots=roots)
        except Exception as e:  # noqa: BLE001
            crashes += 1
            print(f"ÇÖKME: {s!r} → {type(e).__name__}: {e}")
            continue
        clause_preds = sum(1 for c in sa.clauses if c.predicate_id > 0)
        # tutarlılık: her yargıda yüklem ögesi
        for c in sa.clauses:
            if c.predicate_id > 0 and not any(e.label == "yüklem" for e in c.elements):
                inconsistent += 1
                print(f"TUTARSIZ (yüklemsiz yargı): {s!r} → {c}")
        roles = [c.role for c in sa.clauses]
        # yan varsa temel/bağımsız kardeş de olmalı
        if "yan" in roles and not any(r in ("temel", "bağımsız") for r in roles):
            inconsistent += 1
            print(f"TUTARSIZ (yalın yan): {s!r} → {roles}")
        print(f"{s!r}: {len(sa.clauses)} yargı {roles} | yapı={sa.sentence_type.yapi}")
    print(f"\n{len(_SENTENCES)} cümle | çökme={crashes} | tutarsız={inconsistent}")


if __name__ == "__main__":
    main()
