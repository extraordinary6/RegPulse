"""HTML documentation generator from a RegisterBank."""

from __future__ import annotations

import html as html_mod
import os
from datetime import datetime

from src.models.register_bank import RegisterBank


_ACCESS_COLORS = {
    "RW": "#4CAF50",
    "RO": "#2196F3",
    "W1C": "#FF9800",
    "RC": "#F44336",
    "RS": "#9C27B0",
    "WO": "#795548",
    "W1S": "#FF5722",
    "W0C": "#607D8B",
}

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


class HtmlGenerator:
    """Generate an HTML register map document from a RegisterBank."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def generate(self, output_dir: str) -> str:
        lines: list[str] = []
        esc = html_mod.escape

        lines.append("<!DOCTYPE html>")
        lines.append('<html lang="en">')
        lines.append("<head>")
        lines.append("  <meta charset='UTF-8'>")
        lines.append(f"  <title>{esc(self.bank.name)} &mdash; Register Map</title>")
        lines.append("  <style>")
        lines.append(self._css())
        lines.append("  </style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append(f"  <h1>{esc(self.bank.name)} &mdash; Register Map</h1>")
        lines.append(f"  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                     f"| Registers: {self.bank.num_registers} | "
                     f"Address Space: {self.bank.address_space} bytes</p>")
        lines.append("")

        # Legend
        lines.append("  <div class='legend'>")
        lines.append("    <strong>Access Types:</strong>")
        for at, desc in _ACCESS_DESC.items():
            color = _ACCESS_COLORS.get(at, "#999")
            lines.append(f"    <span class='badge' style='background:{color}'>{esc(at)}</span> {esc(desc)}")
        lines.append("  </div>")
        lines.append("")

        # Summary table
        lines.append("  <h2>Register Summary</h2>")
        lines.append("  <table>")
        lines.append("    <tr><th>Name</th><th>Offset</th><th>Width</th>"
                     "<th>Reset</th><th>Access</th><th>Fields</th></tr>")
        for reg in self.bank.registers:
            field_names = ", ".join(esc(f.name) for f in reg.fields)
            lines.append("    <tr>")
            lines.append(f"      <td><code>{esc(reg.name)}</code></td>")
            lines.append(f"      <td>0x{reg.offset:03X}</td>")
            lines.append(f"      <td>{reg.width}</td>")
            lines.append(f"      <td>0x{reg.reset_val:08X}</td>")
            lines.append(f"      <td>{esc(reg.effective_access)}</td>")
            lines.append(f"      <td>{field_names}</td>")
            lines.append("    </tr>")
        lines.append("  </table>")
        lines.append("")

        # Per-register detail
        lines.append("  <h2>Register Details</h2>")
        for reg in self.bank.registers:
            lines.append("  <div class='reg-section'>")
            lines.append(f"    <h3>{esc(reg.name)} <small>offset 0x{reg.offset:03X}, "
                         f"reset 0x{reg.reset_val:08X}</small></h3>")
            if reg.description:
                lines.append(f"    <p>{esc(reg.description)}</p>")
            lines.append("    <table>")
            lines.append("      <tr><th>Field</th><th>Bits</th><th>Width</th>"
                         "<th>Access</th><th>Reset</th><th>HW Interface</th>"
                         "<th>Description</th><th>Side Effect</th></tr>")
            for field in reg.fields:
                color = _ACCESS_COLORS.get(field.access_type, "#999")
                hw = esc(field.hardware_interface) if field.hardware_interface else "&mdash;"
                desc = esc(field.description) if field.description else "&mdash;"
                side_effect = esc(field.side_effect) if field.side_effect else "&mdash;"
                lines.append("      <tr>")
                lines.append(f"        <td><code>{esc(field.name)}</code></td>")
                lines.append(f"        <td>[{field.msb}:{field.lsb}]</td>")
                lines.append(f"        <td>{field.width}</td>")
                lines.append(f"        <td><span class='badge' style='background:{color}'>"
                             f"{esc(field.access_type)}</span></td>")
                lines.append(f"        <td>0x{field.reset_val:X}</td>")
                lines.append(f"        <td>{hw}</td>")
                lines.append(f"        <td>{desc}</td>")
                lines.append(f"        <td>{side_effect}</td>")
                lines.append("      </tr>")
            lines.append("    </table>")
            lines.append("  </div>")

        lines.append("</body>")
        lines.append("</html>")

        out_path = os.path.join(output_dir, f"{self.bank.name}.html")
        with open(out_path, "w") as fh:
            fh.write("\n".join(lines))
        return out_path

    def _css(self) -> str:
        return """
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 2em; color: #333; }
    h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { margin-top: 2em; color: #555; }
    h3 { margin-bottom: 0.3em; }
    h3 small { color: #888; font-weight: normal; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1.5em; }
    th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
    th { background: #f5f5f5; font-weight: 600; }
    tr:nth-child(even) { background: #fafafa; }
    code { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 0.95em; }
    .badge { color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; font-weight: 600; }
    .legend { margin: 1em 0 2em; font-size: 0.9em; }
    .legend .badge { margin-right: 4px; }
    .reg-section { margin-bottom: 2em; padding: 1em; border: 1px solid #e0e0e0; border-radius: 4px; }
"""
