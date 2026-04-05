"""Shared pytest fixtures for RegPulse tests."""

from __future__ import annotations

import os
import tempfile

import pytest
import pandas as pd

from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank


@pytest.fixture
def sample_bank():
    """Create a minimal valid RegisterBank with multiple register types."""
    bank = RegisterBank("test_top")

    # CTRL: RW register with hw output fields
    ctrl = Register("CTRL", 0x00)
    ctrl.add_field(Field("EN", "0", "RW", 0, hardware_interface="output"))
    ctrl.add_field(Field("MODE", "3:1", "RW", 0, hardware_interface="output"))
    ctrl.add_field(Field("RSVD", "7:4", "RO", 0))
    bank.add_register(ctrl)

    # STATUS: RO register with hw input fields and RS field
    status = Register("STATUS", 0x04)
    done_field = Field("DONE", "0", "RO", 0, hardware_interface="input")
    status.add_field(done_field)
    status.add_field(Field("BUSY", "1:1", "RO", 0, hardware_interface="input"))
    pend_field = Field("PEND", "2:2", "RS", 0, hardware_interface="input")
    pend_field.side_effect = "Set on read"
    status.add_field(pend_field)
    bank.add_register(status)

    # INT_EN: RW register for interrupt enables
    int_en = Register("INT_EN", 0x08)
    int_en.add_field(Field("DONE", "0", "RW", 0, hardware_interface="output"))
    int_en.add_field(Field("BUSY", "1:1", "RW", 0, hardware_interface="output"))
    bank.add_register(int_en)

    # INT_STS: W1C register with hw input (interrupt status)
    int_sts = Register("INT_STS", 0x0C)
    overrun_field = Field("OVERRUN", "0", "W1C", 0, hardware_interface="input")
    overrun_field.side_effect = "Write-1-to-clear; hw sets"
    int_sts.add_field(overrun_field)
    bank.add_register(int_sts)

    # ERR_STS: RC register with hw input
    err_sts = Register("ERR_STS", 0x10)
    parity_field = Field("PARITY", "0", "RC", 1, hardware_interface="input")
    parity_field.side_effect = "Clear on read"
    err_sts.add_field(parity_field)
    crc_field = Field("CRC_ERR", "1:1", "RC", 1, hardware_interface="input")
    crc_field.side_effect = "Clear on read"
    err_sts.add_field(crc_field)
    bank.add_register(err_sts)

    return bank


@pytest.fixture
def sample_excel(tmp_path):
    """Create a temporary Excel file for integration tests."""
    xlsx_path = tmp_path / "test_spec.xlsx"

    data = {
        "Name": ["CTRL", "CTRL", "CTRL", "STATUS", "STATUS", "STATUS",
                 "INT_EN", "INT_EN", "INT_STS", "ERR_STS", "ERR_STS"],
        "Offset": ["0x00", "0x00", "0x00", "0x04", "0x04", "0x04",
                    "0x08", "0x08", "0x0C", "0x10", "0x10"],
        "Field": ["EN", "MODE", "RSVD", "DONE", "BUSY", "PEND",
                   "DONE", "BUSY", "OVERRUN", "PARITY", "CRC_ERR"],
        "Bits": ["0", "3:1", "7:4", "0", "1:1", "2:2",
                  "0", "1:1", "0", "0", "1:1"],
        "Access": ["RW", "RW", "RO", "RO", "RO", "RS",
                    "RW", "RW", "W1C", "RC", "RC"],
        "Reset": ["0", "0", "0", "0", "0", "0",
                   "0", "0", "0", "1", "1"],
        "Hardware Trigger": ["output", "output", "", "input", "input", "input",
                             "output", "output", "input", "input", "input"],
        "Side Effect": ["", "", "", "", "", "Set on read",
                        "", "", "Write-1-to-clear; hw sets",
                        "Clear on read", "Clear on read"],
    }
    df = pd.DataFrame(data)
    df.to_excel(xlsx_path, index=False)
    return str(xlsx_path)
