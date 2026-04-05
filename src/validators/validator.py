"""Validation logic for parsed register definitions."""

from __future__ import annotations

from src.models.register_bank import RegisterBank


class ValidationError(Exception):
    """Raised when register definitions fail structural checks."""

    pass


class Validator:
    """Validates a RegisterBank for address overlaps, bit-field collisions,
    and semantic correctness."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def validate(self) -> None:
        """Run all validation checks. Raises ValidationError on failure."""
        self._check_address_overlap()
        self._check_bitfield_collisions()
        self._check_register_name_uniqueness()
        self._check_field_name_uniqueness()
        self._check_empty_registers()
        self._check_max_width()
        self._check_uncovered_bits()
        self._check_ro_hw_interface()
        self._check_wo_hw_interface()

    def _check_address_overlap(self) -> None:
        offsets: dict[int, str] = {}
        for reg in self.bank.registers:
            if reg.offset in offsets:
                raise ValidationError(
                    f"Address overlap: registers '{offsets[reg.offset]}' and "
                    f"'{reg.name}' both map to offset 0x{reg.offset:03X}."
                )
            offsets[reg.offset] = reg.name

    def _check_bitfield_collisions(self) -> None:
        for reg in self.bank.registers:
            occupied: set[int] = set()
            for field in reg.fields:
                bits = set(range(field.lsb, field.msb + 1))
                overlap = occupied & bits
                if overlap:
                    raise ValidationError(
                        f"Bit-field collision in register '{reg.name}': "
                        f"field '{field.name}' uses bits {sorted(overlap)} "
                        f"already occupied by another field."
                    )
                occupied |= bits

    def _check_register_name_uniqueness(self) -> None:
        names: list[str] = []
        for reg in self.bank.registers:
            if reg.name in names:
                raise ValidationError(
                    f"Duplicate register name '{reg.name}'. "
                    f"Register names must be unique."
                )
            names.append(reg.name)

    def _check_field_name_uniqueness(self) -> None:
        for reg in self.bank.registers:
            names: list[str] = []
            for field in reg.fields:
                if field.name in names:
                    raise ValidationError(
                        f"Duplicate field name '{field.name}' in register "
                        f"'{reg.name}'. Field names must be unique per register."
                    )
                names.append(field.name)

    def _check_empty_registers(self) -> None:
        for reg in self.bank.registers:
            if not reg.fields:
                raise ValidationError(
                    f"Register '{reg.name}' at offset 0x{reg.offset:03X} "
                    f"has no fields."
                )

    def _check_max_width(self) -> None:
        max_w = self.bank.data_width
        for reg in self.bank.registers:
            if reg.width > max_w:
                raise ValidationError(
                    f"Register '{reg.name}' spans {reg.width} bits, "
                    f"exceeding the {max_w}-bit limit."
                )

    def _check_uncovered_bits(self) -> None:
        for reg in self.bank.registers:
            if not reg.fields:
                continue
            occupied: set[int] = set()
            for field in reg.fields:
                occupied |= set(range(field.lsb, field.msb + 1))
            max_bit = max(f.msb for f in reg.fields)
            all_bits = set(range(0, max_bit + 1))
            uncovered = all_bits - occupied
            if uncovered:
                raise ValidationError(
                    f"Register '{reg.name}' has uncovered bit positions: "
                    f"{sorted(uncovered)}. All bits from 0 to {max_bit} "
                    f"must be covered by a field."
                )

    def _check_ro_hw_interface(self) -> None:
        """RO fields explicitly marked as 'output' are a semantic error.
        RO fields with hw_interface='input' are correct (hw drives status).
        RO fields with hw_interface=None are acceptable (e.g. reserved fields)."""
        for reg in self.bank.registers:
            for field in reg.fields:
                if (field.access_type == "RO"
                        and field.hardware_interface == "output"):
                    raise ValidationError(
                        f"RO field '{reg.name}.{field.name}' is marked as "
                        f"hardware output, but RO fields cannot drive hardware. "
                        f"Use hw_interface='input' or leave unspecified."
                    )

    def _check_wo_hw_interface(self) -> None:
        """WO fields with hw_interface='input' are a semantic error.
        WO means the bus writes the field; hw_interface='input' means hw
        drives the value — these conflict."""
        for reg in self.bank.registers:
            for field in reg.fields:
                if (field.access_type == "WO"
                        and field.hardware_interface == "input"):
                    raise ValidationError(
                        f"WO field '{reg.name}.{field.name}' is marked as "
                        f"hardware input, but WO fields are bus-written only."
                    )
