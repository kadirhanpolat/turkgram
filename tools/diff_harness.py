"""Diferansiyel değerlendirme harness'i (Faz 2b, madde A).

Dört-yollu karşılaştırma: çarpımsal / HMM / kural / [opsiyonel gold].
SPEC: spec/statistical-disambiguation-spec.md §4

Kullanım (geliştirme aracı; pakete gömülmez):
  python tools/diff_harness.py --sentences "üç gelin" "kırmızı gül"
  python tools/diff_harness.py --trmor-gold tools/trmor2018/TrMor2018/handtagged/
  python tools/diff_harness.py --corpus-sample N

Ayrışma sınıfları (SPEC §4):
  çarpımsal ≠ HMM        → dizi-bağlamı belirleyici → kurala K-kuralı adayı
  HMM ≠ kural            → kuralın açığı VEYA HMM hatası → gold'a bak
  hepsi ≠ gold           → tüm sinyaller yetersiz
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# Repo kök
sys.path.insert(0, str(Path(__file__).parent.parent))

from turkgram import analysis as an, context as ctx, disambiguation as dis, lexicon as lx
from turkgram.statistical import (
    load_model, viterbi, rank_statistical, parse_oflazer,
    _SENTENCE_START, _SENTENCE_END,
)

# ---------------------------------------------------------------------------
# Yardımcı — tek cümle analiz
# ---------------------------------------------------------------------------

def _analyze_sentence(tokens: List[str], roots) -> List[List]:
    return [an.analyze(t, roots=roots) for t in tokens]


def _top1_lemma(ranked: List) -> str:
    if not ranked:
        return "<boş>"
    return ranked[0].lemma


def _top1_kind(ranked: List) -> str:
    if not ranked:
        return "<boş>"
    return ranked[0].kind


# ---------------------------------------------------------------------------
# Dört-yollu karşılaştırma
# ---------------------------------------------------------------------------

class DiffResult:
    """Tek bir cümle için dört-yollu karşılaştırma sonucu."""

    def __init__(
        self,
        tokens: List[str],
        product_top1: List[str],   # her token için çarpımsal top-1 lemma
        hmm_top1: List[str],       # Viterbi top-1 lemma
        rule_top1: List[str],      # context.rank_in_context top-1 lemma
        gold_top1: Optional[List[str]] = None,  # TrMor gold lemması (varsa)
    ):
        self.tokens = tokens
        self.product_top1 = product_top1
        self.hmm_top1 = hmm_top1
        self.rule_top1 = rule_top1
        self.gold_top1 = gold_top1

    def divergences(self) -> List[Dict]:
        """Token bazlı ayrışma listesi döndür."""
        divs = []
        for i, tok in enumerate(self.tokens):
            p = self.product_top1[i] if i < len(self.product_top1) else None
            h = self.hmm_top1[i]    if i < len(self.hmm_top1)     else None
            r = self.rule_top1[i]   if i < len(self.rule_top1)    else None
            g = (self.gold_top1[i]  if self.gold_top1 and i < len(self.gold_top1)
                 else None)

            product_hmm_agree = (p == h)
            hmm_rule_agree    = (h == r)
            all_agree         = (p == h == r) and (g is None or g == p)

            if all_agree:
                continue

            divs.append({
                "token":   tok,
                "idx":     i,
                "product": p,
                "hmm":     h,
                "rule":    r,
                "gold":    g,
                "product_hmm_agree": product_hmm_agree,
                "hmm_rule_agree":    hmm_rule_agree,
                "class":   _divergence_class(p, h, r, g),
            })
        return divs


def _divergence_class(p, h, r, g) -> str:
    """SPEC §4 ayrışma sınıfı."""
    if p == h and h == r:
        return "gold_only"          # yalnız gold farklı
    if p != h:
        return "product_hmm_split"  # dizi-bağlamı belirleyici
    if h != r:
        return "hmm_rule_split"     # kural açığı veya HMM hatası
    return "all_differ"


def compare_sentence(
    tokens: List[str],
    roots,
    model,
    pm,
) -> DiffResult:
    """Tek cümle dört-yollu karşılaştır."""
    per_token = _analyze_sentence(tokens, roots)

    # Çarpımsal
    product_ranked = [
        rank_statistical(cands, model, surface=tok)
        for tok, cands in zip(tokens, per_token)
    ]
    product_top1 = [_top1_lemma(r) for r in product_ranked]

    # HMM Viterbi
    hmm_ranked  = viterbi(tokens, per_token, model)
    hmm_top1    = [_top1_lemma(r) for r in hmm_ranked]

    # Kural (context.rank_in_context)
    rule_ranked = ctx.rank_in_context(tokens, per_token, pos=pm)
    rule_top1   = [_top1_lemma(r) for r in rule_ranked]

    return DiffResult(tokens, product_top1, hmm_top1, rule_top1)


# ---------------------------------------------------------------------------
# Raporlama
# ---------------------------------------------------------------------------

def print_report(results: List[DiffResult]) -> None:
    n_tokens    = sum(len(r.tokens) for r in results)
    n_sentences = len(results)
    divs_all    = [d for r in results for d in r.divergences()]

    # Sınıf sayımları
    class_counts: Dict[str, int] = defaultdict(int)
    for d in divs_all:
        class_counts[d["class"]] += 1

    n_agree = n_tokens - len(divs_all)

    print(f"\n{'='*60}")
    print(f"DİFERANSİYEL HARNESS RAPORU")
    print(f"{'='*60}")
    print(f"Cümle sayısı : {n_sentences:,}")
    print(f"Token sayısı : {n_tokens:,}")
    print(f"Uzlaşılan    : {n_agree:,} ({100*n_agree/max(n_tokens,1):.1f}%)")
    print(f"Ayrışan      : {len(divs_all):,} ({100*len(divs_all)/max(n_tokens,1):.1f}%)")
    print()
    print("Ayrışma sınıfları:")
    for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / max(len(divs_all), 1)
        print(f"  {cls:<25} {cnt:>6,}  ({pct:.1f}%)")

    print()
    print("İlk 20 ayrışma örneği:")
    print(f"{'Token':<15} {'Çarp.':<15} {'HMM':<15} {'Kural':<15} {'Gold':<15} Sınıf")
    print("-" * 90)
    for d in divs_all[:20]:
        print(
            f"{d['token']:<15} {str(d['product']):<15} {str(d['hmm']):<15} "
            f"{str(d['rule']):<15} {str(d['gold']):<15} {d['class']}"
        )
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# TrMor gold okuyucu (handtagged)
# ---------------------------------------------------------------------------

def _iter_gold(gold_dir: Path):
    """TrMor2018 handtagged dizinindeki .txt dosyalarından cümleleri verir.
    Format: trmor2018.train ile aynı (word TAB correct_analysis TAB ...).
    """
    for fpath in sorted(gold_dir.glob("*.txt")):
        sentence: list = []
        in_sentence = False
        with open(fpath, encoding="cp1254", errors="replace") as f:
            for line in f:
                line = line.rstrip("\r\n")
                if line.startswith("<S"):
                    in_sentence = True
                    sentence = []
                elif line.startswith("</S>"):
                    if sentence:
                        yield sentence
                    sentence = []
                    in_sentence = False
                elif line.startswith("<") or not line.strip():
                    continue
                elif in_sentence:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        surface = parts[0].strip()
                        correct = parts[1].strip()
                        sentence.append((surface, correct))
        if sentence:
            yield sentence


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Dört-yollu diferansiyel harness")
    parser.add_argument(
        "--sentences", nargs="+", metavar="SENTENCE",
        help="Analiz edilecek cümleler (boşlukla ayrılmış tokenlar, ; ile cümle sınırı)",
    )
    parser.add_argument(
        "--trmor-gold", metavar="DIR",
        help="TrMor handtagged dizini (gold karşılaştırması için)",
    )
    parser.add_argument(
        "--corpus-sample", type=int, default=0, metavar="N",
        help="TrMor train'den rastgele N cümle örnekle (0=hepsi)",
    )
    parser.add_argument(
        "--emission",  default=None, help="Özel emisyon TSV yolu"
    )
    parser.add_argument(
        "--transition", default=None, help="Özel geçiş TSV yolu"
    )
    args = parser.parse_args()

    print("Model yükleniyor...", file=sys.stderr)
    model = load_model(args.emission, args.transition)
    print(f"  Emisyon: {len(model.emission):,}, Geçiş: {len(model.transition):,}",
          file=sys.stderr)

    print("Leksikon yükleniyor...", file=sys.stderr)
    roots = lx.load()
    pm    = lx.pos_map()

    results: List[DiffResult] = []

    # --- Manuel cümleler ---
    if args.sentences:
        for sentence_str in args.sentences:
            # ";" varsa cümle sınırı; yoksa boşluk ile tokenize
            if ";" in sentence_str:
                parts = sentence_str.split(";")
                for part in parts:
                    tokens = part.strip().split()
                    if tokens:
                        results.append(compare_sentence(tokens, roots, model, pm))
            else:
                tokens = sentence_str.split()
                if tokens:
                    results.append(compare_sentence(tokens, roots, model, pm))

    # --- TrMor train corpus sample ---
    elif args.corpus_sample > 0 or (not args.sentences and not args.trmor_gold):
        n = args.corpus_sample or 500
        train_path = Path(__file__).parent / "trmor2018" / "TrMor2018" / "trmor2018.train"
        if not train_path.exists():
            print(f"Uyarı: {train_path} bulunamadı — örnek atlandı.", file=sys.stderr)
        else:
            from turkgram.statistical import _iter_sentences as _iter  # type: ignore
            # build_disambig_model'den içe aktarma (yerel import)
            sys.path.insert(0, str(Path(__file__).parent))
            from build_disambig_model import _iter_sentences
            count = 0
            for sentence in _iter_sentences(train_path):
                if count >= n:
                    break
                tokens = [s for s, _ in sentence]
                results.append(compare_sentence(tokens, roots, model, pm))
                count += 1
            print(f"  {count} cümle işlendi.", file=sys.stderr)

    # --- TrMor gold ---
    if args.trmor_gold:
        gold_dir = Path(args.trmor_gold)
        if not gold_dir.exists():
            print(f"Hata: gold dizini bulunamadı: {gold_dir}", file=sys.stderr)
            sys.exit(1)
        for sentence in _iter_gold(gold_dir):
            tokens   = [s for s, _ in sentence]
            gold_top1 = [parse_oflazer(a)[0] for _, a in sentence]  # gold lemma
            res = compare_sentence(tokens, roots, model, pm)
            res.gold_top1 = gold_top1
            results.append(res)

    if not results:
        print("Analiz edilecek cümle yok. --sentences veya --corpus-sample kullanın.",
              file=sys.stderr)
        sys.exit(0)

    print_report(results)


if __name__ == "__main__":
    main()
