"""RTL Generator — produces synthesizable Verilog from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.models.register_bank import RegisterBank


class RtlGenerator:
    """Generate an APB slave Verilog module from a RegisterBank."""

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
        self.env.filters["ones"] = lambda w: str((1 << w) - 1)

    def generate(self, output_dir: str) -> str:
        """Render the Verilog and write to <output_dir>/<module_name>.v.

        Returns the path of the generated file.
        """
        template = self.env.get_template("apb_reg_bank.v.j2")

        # Compute word-address MSB for paddr decoding.
        num_words = self.bank.address_space // self.bank.byte_width
        if num_words <= 1:
            addr_msb = 2
        else:
            addr_msb = (num_words - 1).bit_length() + 1

        code = template.render(
            module_name=self.bank.name,
            registers=self.bank.registers,
            addr_msb=addr_msb,
            interrupt_pairs=self.bank.interrupt_pairs,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        out_path = os.path.join(output_dir, f"{self.bank.name}.v")
        with open(out_path, "w") as fh:
            fh.write(code)
        return out_path
