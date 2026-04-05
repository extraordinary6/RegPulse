"""Field data model representing a single bit-field within a register."""

VALID_ACCESS_TYPES = {"RW", "RO", "W1C", "RC", "RS", "WO", "W1S", "W0C"}


class Field:
    """Represents a single bit-field in a register.

    Attributes:
        name:        Field name (e.g. "EN", "MODE").
        bits:        Bit-range string or integer width (e.g. "3:0" or 4).
        lsb:         Least-significant bit position (derived).
        msb:         Most-significant bit position (derived).
        width:       Width in bits (derived).
        access_type: One of RW, RO, W1C, RC, RS, WO, W1S, W0C.
        reset_val:   Reset (power-on) value as an integer.
        hardware_interface: "input" (hw drives field), "output" (field drives hw),
                            or None (no hardware sideband).
        side_effect: Free-text description of read/write side effects.
        interrupt_role: "source", "enable", or None (for interrupt aggregation).
    """

    def __init__(self, name: str, bits, access_type: str, reset_val: int = 0,
                 hardware_interface: str = None):
        self.name = name
        self.access_type = access_type.upper()
        self.reset_val = int(reset_val)
        self.hardware_interface = hardware_interface  # "input", "output", or None
        self.side_effect: str = ""
        self.interrupt_role: str | None = None

        if self.access_type not in VALID_ACCESS_TYPES:
            raise ValueError(
                f"Invalid access type '{access_type}' for field '{name}'. "
                f"Must be one of {sorted(VALID_ACCESS_TYPES)}."
            )

        # Parse bits — three accepted forms:
        #   "msb:lsb"  e.g. "7:4" -> msb=7, lsb=4, width=4
        #   "n"        e.g. "3"  -> lsb=0, msb=2, width=3  (multi-bit at offset 0)
        #   "0"             -> lsb=0, msb=0, width=1  (single-bit at position 0)
        if isinstance(bits, str) and ":" in bits:
            parts = bits.split(":")
            self.msb = int(parts[0])
            self.lsb = int(parts[1])
            self.width = self.msb - self.lsb + 1
        else:
            n = int(bits)
            if n == 0:
                self.msb = 0
                self.lsb = 0
                self.width = 1
            else:
                self.width = n
                self.lsb = 0
                self.msb = n - 1

        # Validate reset value fits in width
        max_val = (1 << self.width) - 1
        if self.reset_val < 0 or self.reset_val > max_val:
            raise ValueError(
                f"Reset value 0x{self.reset_val:X} for field '{name}' "
                f"does not fit in {self.width} bits (max 0x{max_val:X})."
            )

    @property
    def is_bus_writable(self) -> bool:
        """True for fields the bus can modify via a write transaction."""
        return self.access_type in ("RW", "W1C", "WO", "W1S", "W0C")

    @property
    def has_read_side_effect(self) -> bool:
        """True if reading this field causes a state change."""
        return self.access_type in ("RC", "RS")

    def __repr__(self):
        return (
            f"Field(name={self.name!r}, [{self.msb}:{self.lsb}], "
            f"width={self.width}, access={self.access_type}, reset=0x{self.reset_val:X})"
        )
