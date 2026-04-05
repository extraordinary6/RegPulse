"""RegisterBank — top-level container for all registers in a block."""

from __future__ import annotations


class RegisterBank:
    """Represents a complete register bank / block.

    Attributes:
        name:         Block name used for module and class naming (e.g. "chip_reg_top").
        data_width:   Register data width in bits (default 32).
        base_address: Base byte address of the register bank (default 0).
        registers:    Ordered list of Register objects.
    """

    def __init__(self, name: str, data_width: int = 32, base_address: int = 0,
                 block_size: int | None = None):
        self.name = name
        self.data_width = data_width
        self.base_address = base_address
        self.block_size = block_size
        self.source_columns: set[str] = set()
        self.registers: list[Register] = []

    def add_register(self, reg: Register) -> None:
        """Add a Register to this bank."""
        self.registers.append(reg)

    @property
    def byte_width(self) -> int:
        """Register width in bytes."""
        return self.data_width // 8

    @property
    def num_registers(self) -> int:
        return len(self.registers)

    @property
    def address_space(self) -> int:
        """Total address span in bytes."""
        if not self.registers:
            return 0
        last = max(r.offset for r in self.registers)
        return last + self.byte_width

    @property
    def hw_output_fields(self) -> list[tuple[Register, Field]]:
        """All fields that need output ports (control fields)."""
        result = []
        for reg in self.registers:
            for field in reg.fields:
                if field.hardware_interface == "output":
                    result.append((reg, field))
        return result

    @property
    def hw_input_fields(self) -> list[tuple[Register, Field]]:
        """All fields that need input ports (status fields)."""
        result = []
        for reg in self.registers:
            for field in reg.fields:
                if field.hardware_interface == "input":
                    result.append((reg, field))
        return result

    @property
    def interrupt_pairs(self) -> list[tuple[Field, Register, Field, Register]]:
        """Return matched interrupt (source, src_reg, enable, en_reg) tuples.

        Pairs are matched by field name across all registers.
        Sources and enables are stored in lists so that duplicate field names
        across different registers are preserved instead of being silently
        overwritten.
        """
        sources: dict[str, list[tuple[Field, Register]]] = {}
        enables: dict[str, list[tuple[Field, Register]]] = {}
        for reg in self.registers:
            for field in reg.fields:
                if field.interrupt_role == "source":
                    sources.setdefault(field.name, []).append((field, reg))
                elif field.interrupt_role == "enable":
                    enables.setdefault(field.name, []).append((field, reg))

        pairs = []
        for name, src_list in sources.items():
            if name in enables:
                en_list = enables[name]
                for src_field, src_reg in src_list:
                    for en_field, en_reg in en_list:
                        pairs.append((src_field, src_reg, en_field, en_reg))
        return pairs

    def __repr__(self):
        return f"RegisterBank(name={self.name!r}, num_registers={self.num_registers})"


# Late import to avoid circular dependency
from src.models.field import Field  # noqa: E402
from src.models.register import Register  # noqa: E402
