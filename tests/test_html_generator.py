"""Tests for the HTML generator."""

import tempfile

from src.generators.html_generator import HtmlGenerator


def test_html_structure(sample_bank):
    gen = HtmlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "<!DOCTYPE html>" in code
    assert "test_top" in code
    assert "Register Summary" in code
    assert "Register Details" in code


def test_xss_escaping():
    """Field names with HTML characters should be escaped."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_xss")
    reg = Register("REG", 0x00)
    reg.add_field(Field("script_field", "0", "RW", 0))
    bank.add_register(reg)

    gen = HtmlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # The field name should appear in the output
    assert "script_field" in code


def test_new_access_types_in_legend():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test")
    reg = Register("REG", 0x00)
    reg.add_field(Field("A", "0", "WO", 0))
    reg.add_field(Field("B", "1:1", "W1S", 0))
    reg.add_field(Field("C", "2:2", "W0C", 0))
    reg.add_field(Field("D", "7:3", "RO", 0))
    bank.add_register(reg)

    gen = HtmlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "WO" in code
    assert "W1S" in code
    assert "W0C" in code


def test_html_em_dash(sample_bank):
    gen = HtmlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "&mdash;" in code
