"""UVM RAL Generator — produces SystemVerilog register model from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.models.register_bank import RegisterBank


class UvmGenerator:
    """Generate a UVM RAL block (.sv) from a RegisterBank."""

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
        """Render the SystemVerilog and write to <output_dir>/<block_name>_reg_block.sv.

        Returns the path of the generated file.
        """
        template = self.env.get_template("uvm_reg_block.sv.j2")

        code = template.render(
            block_name=self.bank.name,
            registers=self.bank.registers,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        out_path = os.path.join(output_dir, f"{self.bank.name}_reg_block.sv")
        with open(out_path, "w") as fh:
            fh.write(code)
        return out_path
