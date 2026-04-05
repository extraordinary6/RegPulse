"""Tests for the C header generator."""

import tempfile

from src.generators.c_header_generator import CHeaderGenerator


def test_base_address(sample_bank):
    sample_bank.base_address = 0x40000000
    gen = CHeaderGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "0x40000000U" in code


def test_absolute_address_macros(sample_bank):
    gen = CHeaderGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "TEST_TOP_CTRL_ADDR" in code
    assert "TEST_TOP_BASE" in code


def test_reset_format_consistent(sample_bank):
    gen = CHeaderGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # RESET should use 08X format like MASK
    assert "_RESET  (0x00000000U)" in code


def test_access_macros(sample_bank):
    gen = CHeaderGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "TEST_TOP_CTRL_EN_GET" in code
    assert "TEST_TOP_CTRL_EN_SET" in code


def test_include_guard(sample_bank):
    gen = CHeaderGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "#ifndef TEST_TOP_H" in code
    assert "#endif /* TEST_TOP_H */" in code
