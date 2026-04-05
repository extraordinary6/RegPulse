"""Tests for the Validator using pytest conventions."""

import pytest

from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank
from src.validators.validator import Validator, ValidationError


def _make_field(name, bits, access, hw=None):
    return Field(name, bits, access, 0, hardware_interface=hw)


def _make_bank_with(reg_name, reg_offset, fields):
    bank = RegisterBank("test")
    reg = Register(reg_name, reg_offset)
    for f in fields:
        reg.add_field(f)
    bank.add_register(reg)
    return bank


# --- Negative tests ---

def test_duplicate_register_names():
    bank = RegisterBank("test")
    bank.add_register(Register("DUP", 0x00))
    bank.add_register(Register("DUP", 0x04))
    with pytest.raises(ValidationError, match="Duplicate register name"):
        Validator(bank).validate()


def test_duplicate_field_names():
    bank = _make_bank_with("REG", 0x00, [
        _make_field("A", "0", "RW"),
        _make_field("A", "1:1", "RW"),
    ])
    with pytest.raises(ValidationError, match="Duplicate field name"):
        Validator(bank).validate()


def test_empty_register():
    bank = RegisterBank("test")
    bank.add_register(Register("EMPTY", 0x00))
    with pytest.raises(ValidationError, match="no fields"):
        Validator(bank).validate()


def test_width_exceeds_limit():
    bank = _make_bank_with("WIDE", 0x00, [
        Field("BIG", "35:0", "RW", 0),
    ])
    with pytest.raises(ValidationError, match="32-bit limit"):
        Validator(bank).validate()


def test_width_exceeds_custom_data_width():
    bank = RegisterBank("test", data_width=16)
    reg = Register("WIDE", 0x00, data_width=16)
    reg.add_field(Field("BIG", "17:0", "RW", 0))
    bank.add_register(reg)
    with pytest.raises(ValidationError, match="16-bit limit"):
        Validator(bank).validate()


def test_uncovered_bits():
    bank = _make_bank_with("GAP", 0x00, [
        _make_field("A", "0", "RW"),
        _make_field("B", "7:4", "RW"),
    ])
    with pytest.raises(ValidationError, match="uncovered"):
        Validator(bank).validate()


def test_address_overlap():
    bank = RegisterBank("test")
    bank.add_register(Register("A", 0x00))
    bank.add_register(Register("B", 0x00))
    with pytest.raises(ValidationError, match="Address overlap"):
        Validator(bank).validate()


def test_ro_marked_as_output():
    bank = _make_bank_with("BAD_RO", 0x00, [
        Field("STAT", "0", "RO", 0, hardware_interface="output"),
    ])
    with pytest.raises(ValidationError, match="hardware output"):
        Validator(bank).validate()


def test_wo_marked_as_input():
    bank = _make_bank_with("BAD_WO", 0x00, [
        Field("WR", "0", "WO", 0, hardware_interface="input"),
    ])
    with pytest.raises(ValidationError, match="WO field"):
        Validator(bank).validate()


def test_bitfield_collision():
    bank = _make_bank_with("COLLIDE", 0x00, [
        _make_field("A", "3:0", "RW"),
        _make_field("B", "1:1", "RW"),
    ])
    with pytest.raises(ValidationError, match="Bit-field collision"):
        Validator(bank).validate()


# --- Positive tests ---

def test_valid_register():
    bank = _make_bank_with("OK", 0x00, [
        _make_field("A", "0", "RW", hw="output"),
        _make_field("B", "3:1", "RW", hw="output"),
        _make_field("C", "7:4", "RO", hw="input"),
    ])
    Validator(bank).validate()


def test_ro_without_hw_ok():
    bank = _make_bank_with("OK_RO", 0x00, [
        Field("RSVD", "0", "RO", 0),
    ])
    Validator(bank).validate()


def test_wo_with_output_ok():
    bank = _make_bank_with("OK_WO", 0x00, [
        Field("CMD", "0", "WO", 0, hardware_interface="output"),
        Field("PAD", "7:1", "RO", 0),
    ])
    Validator(bank).validate()


def test_new_access_types_valid():
    bank = _make_bank_with("NEW", 0x00, [
        Field("A", "0", "WO", 0, hardware_interface="output"),
        Field("B", "1:1", "W1S", 0),
        Field("C", "2:2", "W0C", 0),
        Field("D", "7:3", "RO", 0),
    ])
    Validator(bank).validate()
