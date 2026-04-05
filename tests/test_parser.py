"""Tests for the Excel parser."""

import pytest
from src.parser.excel_parser import ExcelParser
from src.validators.validator import Validator


def test_parse_sample_excel(sample_excel):
    bank = ExcelParser(sample_excel, block_name="test").parse()
    assert bank.num_registers == 5
    assert len(bank.registers[0].fields) == 3  # CTRL


def test_parse_interrupt_column(sample_excel_with_irq):
    bank = ExcelParser(sample_excel_with_irq, block_name="test").parse()
    assert bank.interrupt_pairs
    assert len(bank.interrupt_pairs) == 1


def test_parse_missing_column(sample_excel):
    """Excel with a missing required column should raise ValueError."""
    import pandas as pd
    import tempfile
    bad_path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({"Name": ["A"], "Field": ["F"], "Bits": ["0"]})
    df.to_excel(bad_path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        ExcelParser(bad_path, block_name="test").parse()
    os.remove(bad_path) if os.path.exists(bad_path) else None


def test_parse_auto_increment():
    import pandas as pd
    import tempfile
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A", "B", "C"],
        "Offset": ["0x00", "", ""],
        "Field": ["F", "F", "F"],
        "Bits": ["7:0", "7:0", "7:0"],
        "Access": ["RW", "RW", "RW"],
        "Reset": ["0", "0", "0"],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(path, block_name="test").parse()
    assert bank.registers[0].offset == 0x00
    assert bank.registers[1].offset == 0x04
    assert bank.registers[2].offset == 0x08
    os.remove(path) if os.path.exists(path) else None


def test_parse_hex_reset():
    import pandas as pd
    import tempfile
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A"], "Offset": ["0x00"], "Field": ["F"],
        "Bits": ["7:0"], "Access": ["RW"], "Reset": ["0xFF"],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(path, block_name="test").parse()
    assert bank.registers[0].fields[0].reset_val == 0xFF
    os.remove(path) if os.path.exists(path) else None


def test_parse_invalid_access():
    import pandas as pd
    import tempfile
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A"], "Offset": ["0x00"], "Field": ["F"],
        "Bits": ["0"], "Access": ["INVALID"], "Reset": ["0"],
    })
    df.to_excel(path, index=False)
    with pytest.raises(ValueError, match="Invalid access type"):
        ExcelParser(path, block_name="test").parse()
    os.remove(path) if os.path.exists(path) else None


import os


@pytest.fixture
def sample_excel_with_irq(tmp_path):
    """Excel with Interrupt column for testing."""
    import pandas as pd
    xlsx_path = tmp_path / "test_irq.xlsx"
    data = {
        "Name": ["INT_STS", "INT_EN"],
        "Offset": ["0x00", "0x04"],
        "Field": ["DONE", "DONE"],
        "Bits": ["0", "0"],
        "Access": ["W1C", "RW"],
        "Reset": ["0", "0"],
        "Hardware Trigger": ["input", "output"],
        "Side Effect": ["", ""],
        "Interrupt": ["source", "enable"],
    }
    df = pd.DataFrame(data)
    df.to_excel(xlsx_path, index=False)
    return str(xlsx_path)
