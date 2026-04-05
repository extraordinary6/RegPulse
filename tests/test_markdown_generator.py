"""Tests for the Markdown generator."""

import tempfile

from src.generators.markdown_generator import MarkdownGenerator


def test_markdown_structure(sample_bank):
    gen = MarkdownGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "# test_top Register Map" in code
    assert "## Register Summary" in code
    assert "## Register Details" in code
    assert "## Access Types" in code


def test_markdown_tables(sample_bank):
    gen = MarkdownGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "| CTRL |" in code
    assert "| EN |" in code
    assert "| OFFSET |" in code or "| Name |" in code


def test_markdown_base_address(sample_bank):
    sample_bank.base_address = 0x40000000
    gen = MarkdownGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "0x40000000" in code
