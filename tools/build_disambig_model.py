"""TrMor2018 train verisinden kompakt istatistiksel disambiguation modeli üretir.

Kullanım:
  python tools/build_disambig_model.py [--data tools/trmor2018/TrMor2018/trmor2018.train]
                                       [--out-dir turkgram/data]
                                       [--min-count 2]
                                       [--verbose]

Çıktı (turkgram/data/):
  disambig_emission_tr.tsv    — major_pos TAB surface TAB log_prob
  disambig_transition_tr.tsv  — prev_pos  TAB next_pos TAB log_prob

SPEC: spec/statistical-disambiguation-spec.md §7
Lisans notu: TrMor2018 MIT lisanslı; yalnız türetilmiş sayım/olgu çıkarılır,
ham metin pakete girmez. THIRD_PARTY_LICENSES.md güncellenmeli.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

# Build scriptinden turkgram modülüne erişim için repo kökü ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from turkgram.statistical import (
    parse_oflazer, parse_oflazer_full, _fine_state_from_oflazer,
    model_from_counts, _SENTENCE_START, _SENTENCE_END,
)

_DEFAULT_TRAIN = Path(__file__).parent / "trmor2018" / "TrMor2018" / "trmor2018.train"
_DEFAULT_OUT   = Path(__file__).parent.parent / "turkgram" / "data"


# ---------------------------------------------------------------------------
# TrMor2018 ayrıştırıcı
# ---------------------------------------------------------------------------

def _iter_sentences(path: Path):
    """TrMor2018 formatındaki dosyayı cümle-cümle verir.

    Her cümle: [(yüzey, doğru_analiz), ...] listesi.
    İlk sekme-ayrılmış alan = doğru analiz (SPEC §2: "ilk analiz = DOĞRU").
    XML sınır satırları (<S>, </S>, <DATA> vb.) atlanır.
    Encoding: cp1254 (Türkçe Windows; hata toleranslı).
    """
    sentence: list = []
    in_sentence = False

    with open(path, encoding="cp1254", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")

            # XML sınır kontrolleri
            if line.startswith("<S ") or line == "<S>":
                in_sentence = True
                sentence = []
                continue
            if line.startswith("</S>"):
                if sentence:
                    yield sentence
                sentence = []
                in_sentence = False
                continue
            if line.startswith("<") or not line.strip():
                continue

            if not in_sentence:
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue  # yalnız yüzey (belirsiz değil, tek analiz olabilir)

            surface  = parts[0].strip()
            # İlk analiz = doğru (SPEC §2)
            correct  = parts[1].strip()
            sentence.append((surface, correct))

    # Dosya sonu kapanmamış cümle
    if sentence:
        yield sentence


# ---------------------------------------------------------------------------
# Sayım aşaması
# ---------------------------------------------------------------------------

def build_counts(train_path: Path, verbose: bool = False):
    """Eğitim verisinden emisyon + geçiş sayımlarını döndürür."""
    emission: defaultdict  = defaultdict(int)
    transition: defaultdict = defaultdict(int)

    n_sentences = 0
    n_tokens    = 0

    for sentence in _iter_sentences(train_path):
        n_sentences += 1
        if verbose and n_sentences % 10_000 == 0:
            print(f"  {n_sentences:,} cümle, {n_tokens:,} token...", file=sys.stderr)

        prev_pos = _SENTENCE_START
        for surface, correct_analysis in sentence:
            _, pos = parse_oflazer(correct_analysis)
            surf_low = surface.lower()

            emission[(pos, surf_low)] += 1
            transition[(prev_pos, pos)] += 1
            prev_pos = pos
            n_tokens += 1

        transition[(prev_pos, _SENTENCE_END)] += 1

    if verbose:
        print(
            f"  Toplam: {n_sentences:,} cümle, {n_tokens:,} token "
            f"({len(emission):,} emisyon, {len(transition):,} geçiş).",
            file=sys.stderr,
        )
    return dict(emission), dict(transition)


def build_counts_fine(train_path: Path, verbose: bool = False):
    """Artım-2: ince-taneli durum ("Verb:past", "Noun:acc") kullanarak sayar.

    _fine_state_from_oflazer() → durum; geride kalan her şey Artım-1 ile aynı.
    """
    emission: defaultdict  = defaultdict(int)
    transition: defaultdict = defaultdict(int)

    n_sentences = 0
    n_tokens    = 0

    for sentence in _iter_sentences(train_path):
        n_sentences += 1
        if verbose and n_sentences % 10_000 == 0:
            print(f"  [fine] {n_sentences:,} cümle, {n_tokens:,} token...", file=sys.stderr)

        prev_state = _SENTENCE_START
        for surface, correct_analysis in sentence:
            fine_state = _fine_state_from_oflazer(correct_analysis)
            surf_low   = surface.lower()

            emission[(fine_state, surf_low)] += 1
            transition[(prev_state, fine_state)] += 1
            prev_state = fine_state
            n_tokens += 1

        transition[(prev_state, _SENTENCE_END)] += 1

    if verbose:
        print(
            f"  [fine] Toplam: {n_sentences:,} cümle, {n_tokens:,} token "
            f"({len(emission):,} emisyon, {len(transition):,} geçiş).",
            file=sys.stderr,
        )
    return dict(emission), dict(transition)


# ---------------------------------------------------------------------------
# Budama + normalize
# ---------------------------------------------------------------------------

def _normalize_emission(
    emission: dict,
    min_count: int = 2,
    smoothing: float = 1e-9,
) -> dict:
    """Emisyon sayımlarını budayıp log-prob'a çevir.

    min_count altındaki (pos, surface) çiftleri atlanır (model boyutu azaltır).
    Budama YALNIZ nadir yüzeyler için; tüm pos'lar korunur.
    """
    # Budanmış sayımlar
    pruned = {k: v for k, v in emission.items() if v >= min_count}

    # pos toplamları
    pos_total: dict = {}
    surf_per_pos: dict = {}
    for (pos, surf), cnt in pruned.items():
        pos_total[pos]   = pos_total.get(pos, 0) + cnt
        surf_per_pos.setdefault(pos, set()).add(surf)

    result: dict = {}
    for (pos, surf), cnt in pruned.items():
        v     = len(surf_per_pos[pos])
        denom = pos_total[pos] + v * smoothing
        result[(pos, surf)] = math.log((cnt + smoothing) / denom)
    return result


def _normalize_transition(
    transition: dict,
    smoothing: float = 1e-9,
) -> dict:
    """Geçiş sayımlarını log-prob'a çevir (budama yok; geçiş matrisi küçük)."""
    prev_total: dict = {}
    next_per_prev: dict = {}
    for (prev, nxt), cnt in transition.items():
        prev_total[prev] = prev_total.get(prev, 0) + cnt
        next_per_prev.setdefault(prev, set()).add(nxt)

    result: dict = {}
    for (prev, nxt), cnt in transition.items():
        s     = len(next_per_prev[prev])
        denom = prev_total[prev] + s * smoothing
        result[(prev, nxt)] = math.log((cnt + smoothing) / denom)
    return result


# ---------------------------------------------------------------------------
# TSV yazıcı
# ---------------------------------------------------------------------------

def write_emission_tsv(log_probs: dict, path: Path) -> None:
    """(pos, surface) → log_prob tablosunu TSV olarak yaz."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Emisyon modeli: major_pos TAB surface TAB log_prob\n")
        f.write("# Kaynak: TrMor2018 (ai-ku, MIT) — türetilmiş sayım\n")
        # Deterministik sıra (pos, surface)
        for (pos, surf), lp in sorted(log_probs.items()):
            f.write(f"{pos}\t{surf}\t{lp:.8f}\n")


def write_transition_tsv(log_probs: dict, path: Path) -> None:
    """(prev_pos, next_pos) → log_prob tablosunu TSV olarak yaz."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Geçiş modeli: prev_pos TAB next_pos TAB log_prob\n")
        f.write("# Kaynak: TrMor2018 (ai-ku, MIT) — türetilmiş sayım\n")
        for (prev, nxt), lp in sorted(log_probs.items()):
            f.write(f"{prev}\t{nxt}\t{lp:.8f}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TrMor2018 → disambig_emission_tr.tsv + disambig_transition_tr.tsv"
    )
    parser.add_argument(
        "--data", default=str(_DEFAULT_TRAIN),
        help="TrMor2018 eğitim dosyası (varsayılan: %(default)s)",
    )
    parser.add_argument(
        "--out-dir", default=str(_DEFAULT_OUT),
        help="Çıktı dizini (varsayılan: %(default)s)",
    )
    parser.add_argument(
        "--min-count", type=int, default=2,
        help="Emisyon budama eşiği (varsayılan: %(default)s)",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--fine", action="store_true",
        help="Artım-2: ince-taneli (Verb:past, Noun:acc) fine model de üret",
    )
    args = parser.parse_args()

    train_path = Path(args.data)
    out_dir    = Path(args.out_dir)

    if not train_path.exists():
        print(f"HATA: Eğitim dosyası bulunamadı: {train_path}", file=sys.stderr)
        print("  TrMor2018'i tools/trmor2018/ altına klonlayın:", file=sys.stderr)
        print("    git clone https://github.com/ai-ku/TrMor2018 tools/trmor2018/TrMor2018",
              file=sys.stderr)
        sys.exit(1)

    print(f"Sayımlar hesaplanıyor: {train_path}", file=sys.stderr)
    emission_raw, transition_raw = build_counts(train_path, verbose=args.verbose)

    print(f"Normalize ediliyor (min_count={args.min_count})...", file=sys.stderr)
    emission_lp   = _normalize_emission(emission_raw, min_count=args.min_count)
    transition_lp = _normalize_transition(transition_raw)

    ep = out_dir / "disambig_emission_tr.tsv"
    tp = out_dir / "disambig_transition_tr.tsv"

    print(f"Yazılıyor: {ep} ({len(emission_lp):,} giriş)", file=sys.stderr)
    write_emission_tsv(emission_lp, ep)

    print(f"Yazılıyor: {tp} ({len(transition_lp):,} giriş)", file=sys.stderr)
    write_transition_tsv(transition_lp, tp)

    print("Tamamlandı.", file=sys.stderr)

    # Artım-2: ince-taneli model
    if args.fine:
        print(f"\n[Artım-2] İnce-taneli sayımlar hesaplanıyor...", file=sys.stderr)
        fine_emission_raw, fine_transition_raw = build_counts_fine(
            train_path, verbose=args.verbose
        )
        print(f"[Artım-2] Normalize ediliyor (min_count={args.min_count})...",
              file=sys.stderr)
        fine_emission_lp   = _normalize_emission(fine_emission_raw,
                                                  min_count=args.min_count)
        fine_transition_lp = _normalize_transition(fine_transition_raw)

        fine_ep = out_dir / "disambig_emission_fine_tr.tsv"
        fine_tp = out_dir / "disambig_transition_fine_tr.tsv"

        print(f"[Artım-2] Yazılıyor: {fine_ep} ({len(fine_emission_lp):,} giriş)",
              file=sys.stderr)
        write_emission_tsv(fine_emission_lp, fine_ep)

        print(f"[Artım-2] Yazılıyor: {fine_tp} ({len(fine_transition_lp):,} giriş)",
              file=sys.stderr)
        write_transition_tsv(fine_transition_lp, fine_tp)

        print("[Artım-2] Tamamlandı.", file=sys.stderr)


if __name__ == "__main__":
    main()
