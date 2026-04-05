"""APB Wrapper Generator — produces APB4-to-regfile-core bridge Verilog."""

from __future__ import annotations

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.models.register_bank import RegisterBank


class ApbWrapperGenerator:
    """Generate an APB4 wrapper Verilog module from a RegisterBank."""

    def __init__(self, bank: RegisterBank, template_dir: str | None = None):
        self.bank = bank
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        template_dir = os.path.abspath(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, output_dir: str) -> str:
        """Render the Verilog and write to <output_dir>/<module_name>_apb_wrapper.v.

        Returns the path of the generated file.
        """
        template = self.env.get_template("apb_wrapper.v.j2")

        dw = self.bank.data_width
        byte_width = dw // 8
        strb_width = byte_width
        num_words = self.bank.address_space // byte_width
        addr_width = max(1, (num_words - 1).bit_length()) if num_words > 0 else 1

        code = template.render(
            module_name=self.bank.name,
            registers=self.bank.registers,
            data_width=dw,
            byte_width=byte_width,
            strb_width=strb_width,
            addr_width=addr_width,
            interrupt_pairs=self.bank.interrupt_pairs,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        out_path = os.path.join(output_dir, f"{self.bank.name}_apb_wrapper.v")
        with open(out_path, "w") as fh:
            fh.write(code)
        return out_path
