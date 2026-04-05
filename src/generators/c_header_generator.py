"""C header file generator from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from src.models.register_bank import RegisterBank


class CHeaderGenerator:
    """Generate a C header (.h) with register offsets and field masks."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def generate(self, output_dir: str) -> str:
        guard = f"{self.bank.name.upper()}_H"
        lines: list[str] = []
        lines.append(f"/*")
        lines.append(f" * RegPulse Auto-Generated Register Definitions")
        lines.append(f" * Block    : {self.bank.name}")
        lines.append(f" * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f" */")
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append(f"")
        lines.append(f"#include <stdint.h>")
        lines.append(f"")

        # Base address
        lines.append(f"/* Base Address */")
        lines.append(f"#define {self._macro('BASE')} (0x{self.bank.base_address:08X}U)")
        lines.append(f"")

        # Register offsets
        lines.append(f"/* Register Offsets */")
        for reg in self.bank.registers:
            lines.append(f"#define {self._macro(reg.name + '_OFFSET')} (0x{reg.offset:03X}U)")
        lines.append(f"")

        # Absolute addresses
        lines.append(f"/* Absolute Addresses */")
        for reg in self.bank.registers:
            lines.append(f"#define {self._macro(reg.name + '_ADDR')} "
                         f"({self._macro('BASE')} + 0x{reg.offset:03X}U)")
        lines.append(f"")

        # Total address space
        lines.append(f"#define {self._macro('ADDR_SPACE')} ({self.bank.address_space}U)")
        lines.append(f"")

        # Field definitions: mask, lsb, width
        lines.append(f"/* Field Bit Masks and Positions */")
        for reg in self.bank.registers:
            lines.append(f"/* {reg.name} */")
            for field in reg.fields:
                prefix = self._macro(f"{reg.name}_{field.name}")
                mask = ((1 << field.width) - 1) << field.lsb
                lines.append(f"#define {prefix}_MASK   (0x{mask:08X}U)")
                lines.append(f"#define {prefix}_LSB    ({field.lsb}U)")
                lines.append(f"#define {prefix}_WIDTH  ({field.width}U)")
                lines.append(f"#define {prefix}_RESET  (0x{field.reset_val:08X}U)")
            lines.append(f"")

        # Access macros
        lines.append(f"/* Access Macros */")
        for reg in self.bank.registers:
            for field in reg.fields:
                prefix = self._macro(f"{reg.name}_{field.name}")
                mask = ((1 << field.width) - 1) << field.lsb
                lines.append(f"#define {prefix}_GET(regval) "
                             f"(((regval) & 0x{mask:08X}U) >> {field.lsb}U)")
                lines.append(f"#define {prefix}_SET(regval, val) "
                             f"(((regval) & ~0x{mask:08X}U) | "
                             f"(((uint32_t)(val) << {field.lsb}U) & 0x{mask:08X}U))")
            lines.append(f"")

        lines.append(f"#endif /* {guard} */")
        lines.append(f"")

        out_path = os.path.join(output_dir, f"{self.bank.name}.h")
        with open(out_path, "w") as fh:
            fh.write("\n".join(lines))
        return out_path

    def _macro(self, name: str) -> str:
        return f"{self.bank.name.upper()}_{name.upper()}"
