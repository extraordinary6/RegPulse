"""Register data model representing a single hardware register."""

from __future__ import annotations


class Register:
    """Represents a single hardware register.

    Attributes:
        name:    Register name (e.g. "CTRL", "STATUS").
        offset:  Byte offset from the base address (must be aligned to data_width bytes).
        fields:  Ordered list of Field objects belonging to this register.
    """

    def __init__(self, name: str, offset: int, data_width: int = 32):
        self.name = name
        self.offset = int(offset)
        self.data_width = data_width
        self.description: str = ""
        self.fields: list[Field] = []

        byte_align = data_width // 8
        if self.offset % byte_align != 0:
            raise ValueError(
                f"Register '{name}' offset 0x{self.offset:X} is not "
                f"{byte_align}-byte aligned."
            )

    def add_field(self, field: Field) -> None:
        """Add a Field to this register."""
        self.fields.append(field)

    @property
    def width(self) -> int:
        """Return the total width spanned by all fields (up to data_width bits)."""
        if not self.fields:
            return 0
        return max(f.msb for f in self.fields) - min(f.lsb for f in self.fields) + 1

    @property
    def reset_val(self) -> int:
        """Compute the composite reset value from all fields."""
        val = 0
        for f in self.fields:
            val |= (f.reset_val & ((1 << f.width) - 1)) << f.lsb
        return val

    @property
    def effective_access(self) -> str:
        """Return 'RW' if any field is bus-writable, else 'RO'."""
        writable = {"RW", "W1C", "WO", "W1S", "W0C"}
        for f in self.fields:
            if f.access_type in writable:
                return "RW"
        return "RO"

    @property
    def has_hw_outputs(self) -> bool:
        """True if any field needs an output port (hardware reads register value)."""
        return any(f.hardware_interface == "output" for f in self.fields)

    @property
    def has_hw_inputs(self) -> bool:
        """True if any field needs an input port (hardware writes register value)."""
        return any(f.hardware_interface == "input" for f in self.fields)

    def __repr__(self):
        return (
            f"Register(name={self.name!r}, offset=0x{self.offset:03X}, "
            f"fields={self.fields})"
        )


# Late import to avoid circular dependency
from src.models.field import Field  # noqa: E402
