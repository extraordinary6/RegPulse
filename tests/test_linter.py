"""Tests for the advisory register-spec linter."""

from __future__ import annotations

import tempfile

import pandas as pd

from src.lint import Linter, LintSeverity
from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank
from src.parser.excel_parser import ExcelParser


def test_parse_description_column():
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["CTRL"],
        "Offset": ["0x00"],
        "Field": ["ENABLE"],
        "Bits": ["0"],
        "Access": ["RW"],
        "Reset": ["0"],
        "Description": ["Enable bit"],
    })
    df.to_excel(path, index=False)

    bank = ExcelParser(path, block_name="test").parse()

    assert "description" in bank.source_columns
    assert bank.registers[0].description == "Enable bit"
    assert bank.registers[0].fields[0].description == "Enable bit"


def test_linter_reports_naming_and_keyword_issues():
    bank = RegisterBank("lint_bank")
    reg = Register("ctrl", 0x00)
    reg.add_field(Field("input", "0", "RW", 0))
    bank.add_register(reg)

    findings = Linter(bank).lint()
    rules = {finding.rule_id for finding in findings}

    assert "N1" in rules
    assert "N2" in rules
    assert "N3" in rules


def test_linter_reports_address_layout_findings():
    bank = RegisterBank("lint_bank")
    reg0 = Register("CTRL", 0x04)
    reg0.add_field(Field("EN", "0", "RW", 0))
    bank.add_register(reg0)

    reg1 = Register("STATUS", 0x20)
    reg1.add_field(Field("DONE", "0", "RO", 0, hardware_interface="input"))
    bank.add_register(reg1)

    findings = Linter(bank).lint()
    rules = {finding.rule_id for finding in findings}

    assert {"A2", "A3", "A4"} <= rules


def test_linter_reports_block_size_overflow():
    bank = RegisterBank("lint_bank", block_size=4)
    reg = Register("CTRL", 0x04)
    reg.add_field(Field("EN", "0", "RW", 0))
    bank.add_register(reg)

    findings = Linter(bank).lint()

    assert any(f.rule_id == "A5" and f.severity == LintSeverity.ERROR for f in findings)


def test_linter_reports_interrupt_pair_issues():
    bank = RegisterBank("lint_bank")

    src_reg = Register("INT_STS", 0x00)
    src = Field("DONE", "1:0", "RS", 0, hardware_interface="input")
    src.interrupt_role = "source"
    src_reg.add_field(src)
    bank.add_register(src_reg)

    en_reg = Register("INT_EN", 0x04)
    en = Field("DONE", "0", "RO", 0, hardware_interface="output")
    en.interrupt_role = "enable"
    en_reg.add_field(en)
    bank.add_register(en_reg)

    findings = Linter(bank).lint()
    rules = {finding.rule_id for finding in findings}

    assert "I3" in rules
    assert "I4" in rules
    assert "I5" in rules


def test_linter_reports_hw_signal_collision():
    bank = RegisterBank("lint_bank")

    reg_a = Register("A_B", 0x00)
    reg_a.add_field(Field("C", "0", "RW", 0, hardware_interface="output"))
    bank.add_register(reg_a)

    reg_b = Register("A", 0x04)
    reg_b.add_field(Field("B_C", "0", "RW", 0, hardware_interface="output"))
    bank.add_register(reg_b)

    findings = Linter(bank).lint()

    assert any(f.rule_id == "H3" and f.severity == LintSeverity.ERROR for f in findings)


def test_linter_reports_description_and_side_effect_findings():
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["CTRL"],
        "Offset": ["0x00"],
        "Field": ["ENABLE"],
        "Bits": ["0"],
        "Access": ["RW"],
        "Reset": ["0"],
        "Description": [""],
        "Side Effect": ["Triggers update"],
    })
    df.to_excel(path, index=False)

    bank = ExcelParser(path, block_name="test").parse()
    findings = Linter(bank).lint()
    rules = {finding.rule_id for finding in findings}

    assert "D1" in rules
    assert "D2" in rules


def test_sample_bank_lint_has_no_error_findings(sample_bank):
    findings = Linter(sample_bank).lint()

    assert not any(f.severity == LintSeverity.ERROR for f in findings)
