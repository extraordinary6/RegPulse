"""Excel (.xlsx) parser that builds the internal RegisterBank model."""

from __future__ import annotations

from collections import OrderedDict

import pandas as pd

from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank


# Expected columns (case-insensitive, whitespace-tolerant)
_REQUIRED_COLUMNS = {"name", "offset", "field", "bits", "access", "reset"}
_OPTIONAL_COLUMNS = {"hardware trigger", "side effect", "interrupt", "description"}


def _normalise_numeric_str(s: str) -> str:
    """Tolerate Excel numeric cells read as float strings.

    E.g. "1.0" -> "1", "3.0:1.0" -> "3:1", "0xFF.0" -> "0xFF",
         "0b101.0" -> "0b101".
    """
    if "." not in s:
        return s
    parts = s.split(":")
    return ":".join(
        _normalise_one(p) for p in parts
    )


def _normalise_one(s: str) -> str:
    """Normalise a single numeric token that may have a trailing '.0'."""
    if "." not in s:
        return s
    # Handle hex: "0xFF.0" -> try int(x, 0) after stripping ".0"
    base_prefixes = ("0x", "0X", "0b", "0B", "0o", "0O")
    for pfx in base_prefixes:
        if s.lower().startswith(pfx.lower()):
            int_part = s.split(".")[0]
            try:
                int(int_part, 0)
                return int_part
            except (ValueError, TypeError):
                return s
    # Plain decimal: "1.0" -> "1", "255.0" -> "255"
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s


def _optional_text(value) -> str:
    """Normalize optional cell text, treating NaN-like values as empty."""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


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
                 data_width: int = 32, base_address: int = 0,
                 block_size: int | None = None):
        self.filepath = filepath
        self.block_name = block_name
        self.data_width = data_width
        self.base_address = base_address
        self.block_size = block_size

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
        has_description = "description" in df.columns

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

            # Normalise numeric strings (Excel may store numbers as "1.0")
            offset_str = _normalise_numeric_str(offset_str)
            bits_str = _normalise_numeric_str(bits_str)
            reset_str = _normalise_numeric_str(reset_str)

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
                hw_raw = _optional_text(row.get("hardware trigger", "")).lower()
                if hw_raw in ("input", "output"):
                    hw_interface = hw_raw

            # Parse optional Side Effect column
            side_effect = ""
            if has_side_effect:
                side_effect = _optional_text(row.get("side effect", ""))

            # Parse optional Description column
            description = ""
            if has_description:
                description = _optional_text(row.get("description", ""))

            # Parse optional Interrupt column
            interrupt_role = None
            if has_interrupt:
                irq_raw = _optional_text(row.get("interrupt", "")).lower()
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
            field.description = description
            field.interrupt_role = interrupt_role
            reg.add_field(field)
            if description and not reg.description:
                reg.description = description

        bank = RegisterBank(self.block_name,
                            data_width=self.data_width,
                            base_address=self.base_address,
                            block_size=self.block_size)
        bank.source_columns = set(df.columns)
        for reg in reg_map.values():
            bank.add_register(reg)

        return bank
