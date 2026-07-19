"""Değerlendirme harness'i — statistical.py'yi TrMor2018 gold'a karşı ölç.

Amaç (SPEC §9 CRF-gate ön koşulu): disambiguation yöntemlerinin gold'a karşı
DOĞRULUĞUNU ölç + HMM'in nerede/neden battığını teşhis et → CRF'in gerekli olup
olmadığını KANITLA. Geliştirme aracı; pakete gömülmez.

Yöntemler (major-POS, cümle-düzeyi):
  isolated : disambiguation.rank (bağlamsız dilbilimsel öncelik)
  rule     : context.rank_in_context (kural-tabanlı sözdizimsel katman)
  hmm      : statistical.viterbi (Artım-1 major-POS HMM)

Kritik ayrım — RECALL-MISS vs DISAMBIGUATION-HATASI:
  Analizör gold-doğru major_pos'u ADAY olarak hiç üretmediyse (recall-miss),
  bu disambiguation'ın suçu DEĞİL. Harness ikisini ayrı raporlar:
    - coverage : gold-doğru POS adaylar arasında var mı? (analizör tavanı)
    - accuracy(covered) : yalnız coverage=True token'larda yöntem doğruluğu

Kullanım:
  PYTHONUTF8=1 python tools/eval_statistical.py [--limit N] [--roots]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from turkgram import analysis as an, context as ctx, disambiguation as dis, lexicon as lx
from turkgram.statistical import (
    load_model, viterbi, parse_oflazer, _analysis_pos, _analysis_pos_lex,
    augment_function_candidates, augment_oov_candidates,
)

_GOLD = Path(__file__).parent / "trmor2018" / "TrMor2018" / "handtagged" / "trmor2018.gold"


def iter_gold(path: Path):
    """<S>…</S> bloklarını (surface, correct_oflazer) listesi olarak ver.

    Her satır: surface TAB correct TAB alt1 TAB alt2 … → ilk analiz DOĞRU.
    """
    sent: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if line.startswith("<S"):
            sent = []
        elif line.startswith("</S>"):
            if sent:
                yield sent
            sent = []
        elif not line or line.startswith("<"):
            continue
        else:
            parts = line.split("\t")
            if len(parts) >= 2:
                sent.append((parts[0].strip(), parts[1].strip()))


def _gold_pos(correct: str) -> str:
    return parse_oflazer(correct)[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="ilk N cümle (0=hepsi)")
    ap.add_argument("--lex", action="store_true",
                    help="lexicon-aware POS (decline-noun → pos_map ile refine)")
    ap.add_argument("--full-roots", action="store_true",
                    help="tüm POS'ları roots'a al (conj/det/postp/interj dahil → "
                         "fonksiyon sözcükleri aday üretir; B-cover)")
    ap.add_argument("--funcwords", action="store_true",
                    help="çok-POS fonksiyon sözcüklerine sentetik POS adayları enjekte et "
                         "(bir/çok/o/ne… → HMM bağlamla seçer)")
    ap.add_argument("--oov-noun", action="store_true",
                    help="OOV (aday üretilmeyen) token → Noun adayı (özel-ad/alıntı fallback)")
    args = ap.parse_args()

    if args.full_roots:
        roots = lx.load(pos={"noun", "verb", "adj", "adv", "pron", "num",
                             "conj", "postp", "det", "interj"})
    else:
        roots = lx.load()  # leksikon güdümlü aday üretimi (recall için şart)
    model = load_model()  # Artım-1 major-POS emisyon+geçiş
    freq = lx.load_freq()

    # POS eşleme fonksiyonu: düz (_analysis_pos) veya lexicon-aware (_analysis_pos_lex)
    _pm = lx.pos_map() if args.lex else None
    pos_of = (lambda a: _analysis_pos_lex(a, _pm)) if args.lex else _analysis_pos

    methods = ("isolated", "rule", "hmm")
    correct = {m: 0 for m in methods}
    covered_correct = {m: 0 for m in methods}
    n_tok = 0
    n_punct = 0
    n_covered = 0
    n_no_cand = 0
    # HMM özel teşhis
    hmm_conf = Counter()          # (gold_pos, hmm_pos) — covered & hmm yanlış
    rule_beats_hmm = Counter()    # covered: rule doğru & hmm yanlış → (gold_pos)
    hmm_beats_rule = Counter()
    gold_pos_dist = Counter()
    our_pos_dist = Counter()      # analizörün ürettiği aday POS'ları (coverage teşhisi)

    n_sent = 0
    for sent in iter_gold(_GOLD):
        if args.limit and n_sent >= args.limit:
            break
        n_sent += 1
        tokens = [w for w, _ in sent]
        golds = [c for _, c in sent]
        # analizör adayları (leksikon güdümlü)
        cand = [an.analyze(t, roots=roots) for t in tokens]
        if args.funcwords:
            cand = [augment_function_candidates(tok, c, _pm)
                    for tok, c in zip(tokens, cand)]
        if args.oov_noun:
            cand = [augment_oov_candidates(tok, c) for tok, c in zip(tokens, cand)]

        iso = [dis.rank(c) for c in cand]
        rule = ctx.rank_in_context(tokens, cand, freq=freq)
        hmm = viterbi(tokens, cand, model, pos_fn=pos_of)

        picks = {"isolated": iso, "rule": rule, "hmm": hmm}

        for i, (tok, g) in enumerate(zip(tokens, golds)):
            gp = _gold_pos(g)
            if gp == "Punc":
                n_punct += 1
                continue
            n_tok += 1
            gold_pos_dist[gp] += 1

            cand_i = cand[i]
            if not cand_i:
                n_no_cand += 1
                continue
            cand_pos = {pos_of(a) for a in cand_i}
            our_pos_dist.update(cand_pos)
            is_covered = gp in cand_pos
            if is_covered:
                n_covered += 1

            method_pos = {}
            for m in methods:
                top = picks[m][i]
                mp = pos_of(top[0]) if top else None
                method_pos[m] = mp
                if mp == gp:
                    correct[m] += 1
                    if is_covered:
                        covered_correct[m] += 1

            # HMM teşhis (yalnız covered — recall-miss'i dışla)
            if is_covered:
                hp, rp = method_pos["hmm"], method_pos["rule"]
                if hp != gp:
                    hmm_conf[(gp, hp)] += 1
                if rp == gp and hp != gp:
                    rule_beats_hmm[gp] += 1
                if hp == gp and rp != gp:
                    hmm_beats_rule[gp] += 1

    # ---- Rapor ----
    print(f"\n{'='*64}\nDEĞERLENDİRME — statistical.py vs TrMor2018 gold\n{'='*64}")
    print(f"Cümle           : {n_sent:,}")
    print(f"Token (punc-dışı): {n_tok:,}   (punc atlandı: {n_punct:,})")
    print(f"Aday yok (OOV)  : {n_no_cand:,} ({100*n_no_cand/max(n_tok,1):.1f}%)")
    print(f"Coverage        : {n_covered:,} ({100*n_covered/max(n_tok,1):.1f}%) "
          f"— gold-POS adaylar arasında (analizör tavanı)")
    print(f"\n{'Yöntem':<10} {'acc(tüm)':>10} {'acc(covered)':>14}")
    print("-" * 36)
    for m in methods:
        a_all = 100 * correct[m] / max(n_tok, 1)
        a_cov = 100 * covered_correct[m] / max(n_covered, 1)
        print(f"{m:<10} {a_all:>9.1f}% {a_cov:>13.1f}%")

    print(f"\nGold major-POS dağılımı (top 12):")
    for p, c in gold_pos_dist.most_common(12):
        print(f"  {p:<10} {c:>6,} ({100*c/max(n_tok,1):.1f}%)")
    print(f"\nAnalizörün ürettiği aday major-POS (coverage darboğazı teşhisi):")
    for p, c in our_pos_dist.most_common():
        print(f"  {p:<10} {c:>6,}")

    print(f"\nHMM covered-yanlış confusion (gold→hmm, top 12):")
    for (gp, hp), c in hmm_conf.most_common(12):
        print(f"  {gp:<8} → {str(hp):<8} {c:>5,}")
    print(f"\nrule doğru & HMM yanlış (covered) top 8: "
          f"{dict(rule_beats_hmm.most_common(8))}")
    print(f"HMM doğru & rule yanlış (covered) top 8: "
          f"{dict(hmm_beats_rule.most_common(8))}")
    print(f"{'='*64}\n")


if __name__ == "__main__":
    main()
