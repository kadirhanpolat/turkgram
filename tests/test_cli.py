"""CLI testleri — python -m turkgram."""
import json
import subprocess
import sys


def _run(*args, check=True):
    result = subprocess.run(
        [sys.executable, "-m", "turkgram", *args],
        capture_output=True, text=True, encoding="utf-8",
        cwd=None,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"CLI çıkış kodu {result.returncode}\nstderr: {result.stderr}"
        )
    return result


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------

def test_version():
    r = _run("version")
    assert "turkgram" in r.stdout
    assert "data:" in r.stdout
    assert "dict schema:" in r.stdout


# ---------------------------------------------------------------------------
# yardım
# ---------------------------------------------------------------------------

def test_help_no_args():
    r = _run()
    assert "analyze" in r.stdout
    assert "version" in r.stdout


# ---------------------------------------------------------------------------
# analyze — text format
# ---------------------------------------------------------------------------

def test_analyze_text_basic():
    r = _run("analyze", "okudum", "--roots", "okumak")
    assert "okumak" in r.stdout
    assert "conjugate" in r.stdout
    assert "past" in r.stdout


def test_analyze_text_segment():
    r = _run("analyze", "okudum", "--roots", "okumak")
    assert "segment:" in r.stdout
    assert "KÖK" in r.stdout


# ---------------------------------------------------------------------------
# analyze — JSON format
# ---------------------------------------------------------------------------

def test_analyze_json_valid():
    r = _run("analyze", "okudum", "--roots", "okumak", "--format", "json")
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) >= 1
    item = data[0]
    assert item["schema_version"] == "1"
    assert item["lemma"] == "okumak"
    assert item["kind"] == "conjugate"
    assert item["hypothetical"] is False
    assert "segments" in item
    assert "chain" in item


def test_analyze_json_confidence_none_without_disambiguate():
    r = _run("analyze", "okudum", "--roots", "okumak", "--format", "json")
    data = json.loads(r.stdout)
    assert data[0]["confidence"] is None


def test_analyze_json_confidence_with_disambiguate():
    r = _run("analyze", "okudum", "--roots", "okumak",
             "--format", "json", "--disambiguate", "--lexicon")
    data = json.loads(r.stdout)
    assert data[0]["confidence"] is not None
    assert 0.0 <= data[0]["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# analyze — roots filtresi
# ---------------------------------------------------------------------------

def test_roots_filter_eliminates_hypothetical():
    r = _run("analyze", "evde", "--roots", "ev", "--format", "json")
    data = json.loads(r.stdout)
    assert all(not d["hypothetical"] for d in data)
    assert all(d["lemma"] == "ev" for d in data)


def test_no_roots_yields_hypothetical():
    r = _run("analyze", "evde", "--format", "json")
    data = json.loads(r.stdout)
    assert any(d["hypothetical"] for d in data)


# ---------------------------------------------------------------------------
# analyze — zincirli türetme
# ---------------------------------------------------------------------------

def test_depth_chain():
    r = _run("analyze", "gözlükçülük", "--roots", "göz", "--depth", "5",
             "--format", "json")
    data = json.loads(r.stdout)
    chained = [d for d in data if d["chain"]]
    assert chained, "zincirli türetme bulunamadı"
    # En derin zincir: kök göz (3 katman)
    deep = [d for d in chained if d["lemma"] == "göz"]
    assert deep, "göz kökünden türetilmiş zincir bulunamadı"


# ---------------------------------------------------------------------------
# DoS koruması — max uzunluk
# ---------------------------------------------------------------------------

def test_long_input_rejected():
    long_input = "a" * 201
    r = _run("analyze", long_input, check=False)
    assert r.returncode != 0
    assert "uzun" in r.stderr


# ---------------------------------------------------------------------------
# bilinmeyen komut
# ---------------------------------------------------------------------------

def test_unknown_command():
    r = _run("foobar", check=False)
    assert r.returncode != 0
    assert "bilinmeyen" in r.stderr
