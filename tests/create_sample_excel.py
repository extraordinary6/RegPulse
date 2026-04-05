"""Create a sample Excel register specification for testing."""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

import pandas as pd

OUTPUT_DIR = os.path.join(SCRIPT_DIR, "tests", "sample_spec.xlsx")

data = {
    "Name": [
        "CTRL", "CTRL", "CTRL",
        "STATUS", "STATUS", "STATUS",
        "INT_EN", "INT_EN",
        "INT_STS",
        "DMA_CTRL", "DMA_CTRL", "DMA_CTRL",
        "ERR_STS", "ERR_STS",
    ],
    "Offset": [
        "0x00", "0x00", "0x00",
        "0x04", "0x04", "0x04",
        "0x08", "0x08",
        "0x0C",
        "0x10", "0x10", "0x10",
        "0x14", "0x14",
    ],
    "Field": [
        "EN", "MODE", "RESERVED",
        "DONE", "BUSY", "PEND",
        "DONE", "TIMER",
        "OVERRUN",
        "START", "RSVD", "LEN",
        "PARITY", "CRC_ERR",
    ],
    "Bits": [
        "0", "3:1", "7:4",
        "0", "1:1", "2:2",
        "0", "1:1",
        "0",
        "0", "7:1", "15:8",
        "0", "1:1",
    ],
    "Access": [
        "RW", "RW", "RO",
        "RO", "RO", "RS",
        "RW", "RW",
        "W1C",
        "RS", "RO", "RW",
        "RC", "RC",
    ],
    "Reset": [
        "0", "0", "0",
        "0", "0", "0",
        "0", "0",
        "0",
        "0", "0", "0",
        "1", "1",
    ],
    "Hardware Trigger": [
        "output", "output", "",
        "input", "input", "input",
        "output", "output",
        "input",
        "output", "", "output",
        "input", "input",
    ],
    "Side Effect": [
        "", "", "",
        "", "", "Set on read",
        "", "",
        "Write-1-to-clear; hw sets",
        "Set on read", "", "",
        "Clear on read", "Clear on read",
    ],
    "Interrupt": [
        "", "", "",
        "", "", "",
        "enable", "enable",
        "source",
        "", "", "",
        "", "",
    ],
}

df = pd.DataFrame(data)
df.to_excel(OUTPUT_DIR, index=False)
print(f"Sample spec written to {OUTPUT_DIR}")
