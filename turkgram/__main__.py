"""python -m turkgram — komut satırı arayüzü.

Kullanım:
    python -m turkgram analyze <yüzey> [seçenekler]
    python -m turkgram version

Windows'ta Türkçe karakter için PYTHONUTF8=1 gerekmez;
bu modül stdout/stderr'i UTF-8'e zorlar.
"""
from __future__ import annotations

import io
import json
import sys

# Windows cp1254 tuzağı (CLAUDE.md §5) — stdout/stderr UTF-8'e zorla.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_MAX_SURFACE_LEN = 200  # H-07: DoS koruması


def _die(msg: str, code: int = 1) -> None:
    print(f"hata: {msg}", file=sys.stderr)
    sys.exit(code)


def _fmt_text(analyses, *, disambiguated=None) -> str:
    """İnsan-okunabilir çıktı."""
    lines = []
    conf_map: dict = {}
    if disambiguated:
        conf_map = {id(a): c for a, c in disambiguated}

    for i, a in enumerate(analyses, 1):
        conf = conf_map.get(id(a))
        conf_str = f"  [güven: {conf:.2f}]" if conf is not None else ""
        lines.append(f"{i}. {a.lemma} [{a.kind} | {a.pos}]{conf_str}")
        if a.kwargs:
            kw_str = " | ".join(f"{k}: {v}" for k, v in a.kwargs.items())
            lines.append(f"   {kw_str}")
        if a.segments:
            segs = "|".join(s.surface for s in a.segments)
            labels = " + ".join(s.label for s in a.segments)
            lines.append(f"   segment: {segs}  ({labels})")
        if a.chain:
            chain_lemmalar = " → ".join(c.lemma for c in a.chain)
            lines.append(f"   zincir: {chain_lemmalar}")
        if a.hypothetical:
            lines.append("   [varsayımsal]")
    return "\n".join(lines)


def _fmt_json(analyses, *, disambiguated=None) -> str:
    """JSON çıktı — analysis_to_dict() şemasıyla."""
    from turkgram.analysis import analysis_to_dict

    conf_map: dict = {}
    if disambiguated:
        conf_map = {id(a): c for a, c in disambiguated}

    dicts = [analysis_to_dict(a, confidence=conf_map.get(id(a))) for a in analyses]
    return json.dumps(dicts, ensure_ascii=False, indent=2)


def cmd_analyze(args: list[str]) -> None:
    import argparse
    from turkgram import analyze
    from turkgram.disambiguation import disambiguate
    from turkgram import lexicon as _lexicon

    p = argparse.ArgumentParser(
        prog="python -m turkgram analyze",
        description="Türkçe yüzey biçimini çözümle.",
    )
    p.add_argument("surface", help="Çözümlenecek yüzey biçim (ör. 'okudum')")
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        dest="fmt", help="Çıktı formatı (varsayılan: text)"
    )
    p.add_argument(
        "--roots", default=None,
        help="Virgülle ayrılmış kök listesi (ör. okumak,gitmek)"
    )
    p.add_argument(
        "--depth", type=int, default=1, metavar="N",
        help="Zincirli türetme derinliği (varsayılan: 1)"
    )
    p.add_argument(
        "--disambiguate", action="store_true",
        help="Disambiguation uygula; güven skorunu göster"
    )
    p.add_argument(
        "--lexicon", action="store_true",
        help="Gömülü leksikonu roots olarak kullan (--roots verilmemişse)"
    )
    ns = p.parse_args(args)

    surface: str = ns.surface
    if len(surface) > _MAX_SURFACE_LEN:
        _die(f"yüzey çok uzun (max {_MAX_SURFACE_LEN} karakter)")

    # Roots çözümleme
    roots = None
    if ns.roots:
        roots = frozenset(r.strip() for r in ns.roots.split(",") if r.strip())
    elif ns.lexicon:
        roots = _lexicon.load()

    analyses = analyze(surface, roots=roots, max_derivation_depth=ns.depth)

    if not analyses:
        print("çözümleme bulunamadı.", file=sys.stderr)
        sys.exit(0)

    disambiguated = None
    if ns.disambiguate:
        freq = _lexicon.load_freq()
        pos = _lexicon.pos_map()
        disambiguated = disambiguate(analyses, freq=freq, pos=pos)
        # Sırayı güven sırasına göre yeniden düzenle
        analyses = [a for a, _ in disambiguated]

    if ns.fmt == "json":
        print(_fmt_json(analyses, disambiguated=disambiguated))
    else:
        print(_fmt_text(analyses, disambiguated=disambiguated))


def cmd_version() -> None:
    from turkgram import __version__, DATA_VERSION, ANALYSIS_DICT_SCHEMA_VERSION
    print(f"turkgram {__version__}")
    print(f"  data: {DATA_VERSION}")
    print(f"  dict schema: {ANALYSIS_DICT_SCHEMA_VERSION}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Kullanım: python -m turkgram <komut> [seçenekler]")
        print()
        print("Komutlar:")
        print("  analyze <yüzey>  Yüzey biçimini çözümle")
        print("  version          Sürüm bilgisi")
        print()
        print("Örnek:")
        print("  python -m turkgram analyze okudum")
        print("  python -m turkgram analyze okudum --format json")
        print("  python -m turkgram analyze gözlükçülük --roots göz --depth 5")
        print("  python -m turkgram analyze okudum --disambiguate --lexicon")
        sys.exit(0)

    cmd, *rest = args
    if cmd == "analyze":
        cmd_analyze(rest)
    elif cmd == "version":
        cmd_version()
    else:
        _die(f"bilinmeyen komut: {cmd!r}. 'analyze' veya 'version' kullanın.")


if __name__ == "__main__":
    main()
