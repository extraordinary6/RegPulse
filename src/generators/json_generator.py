"""JSON IR export generator from a RegisterBank."""

from __future__ import annotations

import json
import os
from datetime import datetime

from src.models.register_bank import RegisterBank


class JsonGenerator:
    """Export the RegisterBank internal representation as JSON."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def generate(self, output_dir: str) -> str:
        data = {
            "block_name": self.bank.name,
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_address": f"0x{self.bank.base_address:08X}",
            "data_width": self.bank.data_width,
            "num_registers": self.bank.num_registers,
            "address_space_bytes": self.bank.address_space,
            "registers": [self._reg_to_dict(r) for r in self.bank.registers],
        }

        out_path = os.path.join(output_dir, f"{self.bank.name}.json")
        with open(out_path, "w") as fh:
            json.dump(data, fh, indent=2)
        return out_path

    def _reg_to_dict(self, reg: Register) -> dict:
        return {
            "name": reg.name,
            "offset": f"0x{reg.offset:03X}",
            "offset_decimal": reg.offset,
            "width": reg.width,
            "reset_val": f"0x{reg.reset_val:08X}",
            "effective_access": reg.effective_access,
            "description": reg.description,
            "fields": [self._field_to_dict(f) for f in reg.fields],
        }

    def _field_to_dict(self, field: Field) -> dict:
        return {
            "name": field.name,
            "msb": field.msb,
            "lsb": field.lsb,
            "width": field.width,
            "access": field.access_type,
            "reset_val": field.reset_val,
            "description": field.description,
            "hw_interface": field.hardware_interface,
            "is_bus_writable": field.is_bus_writable,
            "has_read_side_effect": field.has_read_side_effect,
            "side_effect": field.side_effect,
        }


# Late imports
from src.models.field import Field  # noqa: E402
from src.models.register import Register  # noqa: E402
