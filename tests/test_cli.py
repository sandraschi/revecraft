"""Unit and integration tests for ReveCraft CLI verbs."""

import gzip
import json
import struct
import zlib
from pathlib import Path

import pytest
from revecraft import cli


def _make_dummy_pe(path: Path) -> Path:
    """Create a minimal valid PE binary fixture for parsing tests."""
    dos_header = bytearray(b"MZ" + b"\x00" * 58)
    pe_offset = 64
    dos_header.extend(struct.pack("<I", pe_offset))

    # PE Signature
    pe_sig = b"PE\x00\x00"
    # COFF File Header: machine=AMD64(0x8664), 2 sections, time=12345, sym_ptr=0, sym_num=0, opt_hdr_size=0, flags=0
    coff_header = struct.pack("<HHIIIHH", 0x8664, 2, 12345, 0, 0, 0, 0x0002)

    # Section 1 (.text)
    s1 = b".text\x00\x00\x00" + struct.pack("<IIIIIIHHI", 0x1000, 0x1000, 0x200, 0x200, 0, 0, 0, 0, 0x60000020)
    # Section 2 (.rdata)
    s2 = b".rdata\x00\x00" + struct.pack("<IIIIIIHHI", 0x800, 0x2000, 0x200, 0x400, 0, 0, 0, 0, 0x40000040)

    # Payload with embedded strings
    payload = b"Hello ReveCraft Binary World!\x00" + "UnicodeStringTest".encode("utf-16le")

    data = bytes(dos_header) + pe_sig + coff_header + s1 + s2 + payload
    path.write_bytes(data)
    return path


def test_strings_extraction(tmp_path):
    target = tmp_path / "sample.bin"
    _make_dummy_pe(target)

    results = cli.extract_strings(target, min_len=4)
    extracted_texts = [r["string"] for r in results]

    assert any("Hello ReveCraft" in s for s in extracted_texts)
    assert any("UnicodeStringTest" in s for s in extracted_texts)


def test_entropy_calculation(tmp_path):
    # Low entropy file (all same byte)
    low_file = tmp_path / "zeros.bin"
    low_file.write_bytes(b"\x00" * 1024)

    ent_low = cli.calculate_entropy(low_file)
    assert ent_low["overall"] == 0.0
    assert len(ent_low["compressed_regions"]) > 0

    # Higher entropy file
    high_file = tmp_path / "pattern.bin"
    high_file.write_bytes(bytes([i % 256 for i in range(1024)]))

    ent_high = cli.calculate_entropy(high_file)
    assert ent_high["overall"] > 7.0


def test_pe_parsing(tmp_path):
    pe_file = tmp_path / "test.exe"
    _make_dummy_pe(pe_file)

    info = cli.parse_pe_info(pe_file)
    assert info["valid_pe"] is True
    assert info["machine"] == "AMD64"
    assert info["num_sections"] == 2
    assert len(info["sections"]) == 2
    assert info["sections"][0]["name"] == ".text"
    assert info["sections"][1]["name"] == ".rdata"


def test_dki_decoding(tmp_path):
    # Create zlib compressed fixture
    plain_text = "Directmedia DKI Test Document with UTF-8 Umlauts: Übergrößenträger."
    compressed_data = zlib.compress(plain_text.encode("utf-8"))

    dki_file = tmp_path / "TEXT.DKI"
    dki_file.write_bytes(compressed_data)

    out_file = tmp_path / "decompressed.txt"
    res = cli.decode_dki(dki_file, out_path=out_file)

    assert res["success"] is True
    assert "Übergrößenträger" in res["preview"]
    assert out_file.is_file()
    assert out_file.read_text(encoding="utf-8") == plain_text


def test_die_and_capa_smoke(tmp_path):
    target = tmp_path / "test.bin"
    target.write_bytes(b"dummy binary data")

    # Engines should safely return a dict with status (either ok or down), never raise
    die_res = cli.run_die(target)
    assert isinstance(die_res, dict)
    assert "status" in die_res

    capa_res = cli.run_capa(target)
    assert isinstance(capa_res, dict)
    assert "status" in capa_res


def test_snapshot_creation(tmp_path):
    target = tmp_path / "test.exe"
    _make_dummy_pe(target)

    snap = cli.create_snapshot(target, out_dir=tmp_path / "out")
    assert snap["size_bytes"] > 0
    assert snap["entropy"]["overall"] > 0
    assert snap["pe"]["valid_pe"] is True
    assert (tmp_path / "out" / f"{target.stem}_snapshot.json").is_file()


def test_cli_runner(tmp_path, capsys):
    target = tmp_path / "cli_test.exe"
    _make_dummy_pe(target)

    # Test entropy JSON
    rc = cli.main(["entropy", "--file", str(target), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    ent_json = json.loads(captured.out)
    assert "overall" in ent_json

    # Test pe-info JSON
    rc = cli.main(["pe-info", "--file", str(target), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    pe_json = json.loads(captured.out)
    assert pe_json["machine"] == "AMD64"

    # Test strings JSON
    rc = cli.main(["strings", "--file", str(target), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    str_json = json.loads(captured.out)
    assert len(str_json) > 0
