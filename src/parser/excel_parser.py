"""Excel (.xlsx) parser that builds the internal RegisterBank model."""

from __future__ import annotations

from collections import OrderedDict

import pandas as pd

from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank


# Expected columns (case-insensitive, whitespace-tolerant)
_REQUIRED_COLUMNS = {"name", "offset", "field", "bits", "access", "reset"}
_OPTIONAL_COLUMNS = {"hardware trigger", "side effect", "interrupt"}


class ExcelParser:
    """Parse a register-specification Excel file into a RegisterBank.

    Expected Excel layout (one row per field):
        Name   | Offset | Field | Bits  | Access | Reset | [Hardware Trigger] | [Side Effect] | [Interrupt]
        CTRL   | 0x00   | EN    | 0     | RW     | 0     | output             |               |
        CTRL   | 0x00   | MODE  | 3:1   | RW     | 0     | output             |               |
        STATUS | 0x04   | DONE  | 0     | RO     | 0     | input              |               | source
        INT_EN | 0x08   | DONE  | 0     | RW     | 0     | output             |               | enable
        ...
    """

    def __init__(self, filepath: str, block_name: str = "reg_top",
                 data_width: int = 32, base_address: int = 0):
        self.filepath = filepath
        self.block_name = block_name
        self.data_width = data_width
        self.base_address = base_address

    # ------------------------------------------------------------------
    def parse(self) -> RegisterBank:
        """Read the Excel file and return a fully-populated RegisterBank."""
        df = pd.read_excel(self.filepath, dtype=str)

        # Normalise column names: strip whitespace, lowercase
        df.columns = [c.strip().lower() for c in df.columns]

        missing = _REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Excel file is missing required columns: {sorted(missing)}. "
                f"Found columns: {sorted(df.columns)}."
            )

        # Detect optional columns
        has_hw_trigger = "hardware trigger" in df.columns
        has_side_effect = "side effect" in df.columns
        has_interrupt = "interrupt" in df.columns

        # Group rows by register (name + offset)
        reg_map: OrderedDict[tuple[str, int], Register] = OrderedDict()
        last_offset = -(self.data_width // 8)  # so first auto-increment starts at 0x00
        byte_width = self.data_width // 8

        for row_idx, (_, row) in enumerate(df.iterrows()):
            reg_name = str(row["name"]).strip()
            offset_str = str(row["offset"]).strip()
            field_name = str(row["field"]).strip()
            bits_str = str(row["bits"]).strip()
            access_type = str(row["access"]).strip()
            reset_str = str(row["reset"]).strip()

            if reg_name == "" or reg_name == "nan":
                continue  # skip blank rows

            # Parse offset — blank means auto-increment from previous register
            if offset_str == "" or offset_str == "nan":
                offset = last_offset + byte_width
            else:
                try:
                    offset = int(offset_str, 0)
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Row {row_idx + 2}: cannot parse offset '{offset_str}' "
                        f"for register '{reg_name}'."
                    ) from exc

            last_offset = offset

            # Parse reset value
            try:
                reset_val = int(reset_str, 0)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Row {row_idx + 2}: cannot parse reset value '{reset_str}' "
                    f"for field '{reg_name}.{field_name}'."
                ) from exc

            # Parse optional Hardware Trigger column
            hw_interface = None
            if has_hw_trigger:
                hw_raw = str(row.get("hardware trigger", "")).strip().lower()
                if hw_raw in ("input", "output"):
                    hw_interface = hw_raw

            # Parse optional Side Effect column
            side_effect = ""
            if has_side_effect:
                side_effect = str(row.get("side effect", "")).strip()

            # Parse optional Interrupt column
            interrupt_role = None
            if has_interrupt:
                irq_raw = str(row.get("interrupt", "")).strip().lower()
                if irq_raw in ("source", "enable"):
                    interrupt_role = irq_raw

            # Get or create the Register object
            key = (reg_name, offset)
            if key not in reg_map:
                reg_map[key] = Register(reg_name, offset, data_width=self.data_width)
            reg = reg_map[key]

            # Create and attach the Field (with row context on error)
            try:
                field = Field(field_name, bits_str, access_type, reset_val,
                              hardware_interface=hw_interface)
            except ValueError as exc:
                raise ValueError(
                    f"Row {row_idx + 2} (register '{reg_name}', field '{field_name}'): "
                    f"{exc}"
                ) from exc

            field.side_effect = side_effect
            field.interrupt_role = interrupt_role
            reg.add_field(field)

        bank = RegisterBank(self.block_name,
                            data_width=self.data_width,
                            base_address=self.base_address)
        for reg in reg_map.values():
            bank.add_register(reg)

        return bank
