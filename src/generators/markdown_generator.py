"""Markdown documentation generator from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from src.models.register_bank import RegisterBank


_ACCESS_DESC = {
    "RW": "Read / Write",
    "RO": "Read Only",
    "W1C": "Write 1 to Clear",
    "RC": "Read to Clear",
    "RS": "Read to Set",
    "WO": "Write Only",
    "W1S": "Write 1 to Set",
    "W0C": "Write 0 to Clear",
}


class MarkdownGenerator:
    """Generate a Markdown register map document from a RegisterBank."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def generate(self, output_dir: str) -> str:
        lines: list[str] = []

        lines.append(f"# {self.bank.name} Register Map")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        lines.append(f"Registers: {self.bank.num_registers} | "
                     f"Address Space: {self.bank.address_space} bytes | "
                     f"Base Address: 0x{self.bank.base_address:08X}")
        lines.append("")

        # Access type legend
        lines.append("## Access Types")
        lines.append("")
        lines.append("| Type | Description |")
        lines.append("|------|-------------|")
        for at, desc in _ACCESS_DESC.items():
            lines.append(f"| {at} | {desc} |")
        lines.append("")

        # Summary table
        lines.append("## Register Summary")
        lines.append("")
        lines.append("| Name | Offset | Width | Reset | Access | Fields |")
        lines.append("|------|--------|-------|-------|--------|--------|")
        for reg in self.bank.registers:
            field_names = ", ".join(f.name for f in reg.fields)
            lines.append(f"| {reg.name} | 0x{reg.offset:03X} | {reg.width} | "
                         f"0x{reg.reset_val:08X} | {reg.effective_access} | "
                         f"{field_names} |")
        lines.append("")

        # Per-register detail
        lines.append("## Register Details")
        lines.append("")
        for reg in self.bank.registers:
            lines.append(f"### {reg.name}")
            lines.append("")
            lines.append(f"- **Offset**: 0x{reg.offset:03X}")
            lines.append(f"- **Width**: {reg.width} bits")
            lines.append(f"- **Reset**: 0x{reg.reset_val:08X}")
            lines.append(f"- **Access**: {reg.effective_access}")
            lines.append("")
            lines.append("| Field | Bits | Width | Access | Reset | HW Interface |")
            lines.append("|-------|------|-------|--------|-------|--------------|")
            for field in reg.fields:
                hw = field.hardware_interface or "-"
                lines.append(f"| {field.name} | [{field.msb}:{field.lsb}] | "
                             f"{field.width} | {field.access_type} | "
                             f"0x{field.reset_val:X} | {hw} |")
            lines.append("")

        out_path = os.path.join(output_dir, f"{self.bank.name}.md")
        with open(out_path, "w") as fh:
            fh.write("\n".join(lines))
        return out_path
