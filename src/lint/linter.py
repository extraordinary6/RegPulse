"""Lint checks for parsed register specifications."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
import re

from src.models.field import Field
from src.models.register import Register
from src.models.register_bank import RegisterBank


_VERILOG_KEYWORDS = {
    "always", "and", "assign", "automatic", "begin", "buf", "case", "casex",
    "casez", "cell", "config", "deassign", "default", "defparam", "design",
    "disable", "edge", "else", "end", "endcase", "endconfig", "endfunction",
    "endgenerate", "endmodule", "endprimitive", "endspecify", "endtable",
    "endtask", "event", "for", "force", "forever", "fork", "function",
    "generate", "genvar", "highz0", "highz1", "if", "ifnone", "incdir",
    "include", "initial", "inout", "input", "instance", "integer", "join",
    "large", "liblist", "library", "localparam", "macromodule", "medium",
    "module", "nand", "negedge", "nmos", "nor", "noshowcancelled", "not",
    "notif0", "notif1", "or", "output", "parameter", "pmos", "posedge",
    "primitive", "pull0", "pull1", "pulldown", "pullup", "rcmos", "real",
    "realtime", "reg", "release", "repeat", "rnmos", "rpmos", "rtran",
    "rtranif0", "rtranif1", "scalared", "showcancelled", "signed", "small",
    "specify", "specparam", "strong0", "strong1", "supply0", "supply1",
    "table", "task", "time", "tran", "tranif0", "tranif1", "tri", "tri0",
    "tri1", "triand", "trior", "trireg", "unsigned", "use", "uwire", "vectored",
    "wait", "wand", "weak0", "weak1", "while", "wire", "wor", "xnor", "xor",
    "alias", "assert", "assume", "before", "bind", "bins", "binsof", "bit",
    "break", "byte", "chandle", "class", "clocking", "const", "constraint",
    "context", "continue", "cover", "covergroup", "coverpoint", "cross",
    "dist", "do", "endclass", "endclocking", "endgroup", "endinterface",
    "endpackage", "endprogram", "endproperty", "endsequence", "enum", "expect",
    "export", "extends", "extern", "final", "first_match", "foreach", "forkjoin",
    "iff", "ignore_bins", "illegal_bins", "import", "inside", "int",
    "interface", "intersect", "logic", "longint", "matches", "modport", "new",
    "null", "package", "packed", "priority", "program", "property", "protected",
    "pure", "rand", "randc", "randcase", "randsequence", "ref", "return",
    "sequence", "shortint", "shortreal", "solve", "static", "string", "struct",
    "super", "tagged", "this", "throughout", "timeprecision", "timeunit", "type",
    "typedef", "union", "unique", "var", "virtual", "void", "with", "within",
}
_VALID_NAME_RE = re.compile(r"^[A-Z0-9_]+$")
_RESERVED_FIELD_NAMES = {"RSVD", "RESERVED", "RSV", "RES"}
_HW_INPUT_ACCESS = {"RO", "RC", "RS", "W1C", "W1S", "W0C"}
_HW_OUTPUT_ACCESS = {"RW", "WO"}
_SOURCE_ACCESS = {"W1C", "RC"}


class LintSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class LintMessage:
    rule_id: str
    severity: LintSeverity
    message: str
    register: str | None = None
    field: str | None = None

    @property
    def location(self) -> str:
        if self.register and self.field:
            return f"{self.register}.{self.field}"
        if self.register:
            return self.register
        return "-"


class Linter:
    """Run advisory and structural lint checks on a parsed RegisterBank."""

    def __init__(self, bank: RegisterBank):
        self.bank = bank

    def lint(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        findings.extend(self._check_naming())
        findings.extend(self._check_address_layout())
        findings.extend(self._check_fields_and_bits())
        findings.extend(self._check_access_semantics())
        findings.extend(self._check_interrupts())
        findings.extend(self._check_hw_interfaces())
        findings.extend(self._check_documentation())
        return findings

    def _msg(
        self,
        rule_id: str,
        severity: LintSeverity,
        message: str,
        register: Register | None = None,
        field: Field | None = None,
    ) -> LintMessage:
        return LintMessage(
            rule_id=rule_id,
            severity=severity,
            message=message,
            register=register.name if register else None,
            field=field.name if field else None,
        )

    def _check_naming(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        names = [reg.name for reg in self.bank.registers]
        for reg in self.bank.registers:
            findings.extend(self._lint_identifier("N1", reg, None))
            for field in reg.fields:
                findings.extend(self._lint_identifier("N2", reg, field))

        all_names = [(reg.name, reg, None) for reg in self.bank.registers]
        all_names.extend((field.name, reg, field) for reg in self.bank.registers for field in reg.fields)
        for name, reg, field in all_names:
            upper = name.upper()
            if upper.lower() in _VERILOG_KEYWORDS:
                findings.append(
                    self._msg("N3", LintSeverity.ERROR,
                              f"Identifier '{name}' must not use a Verilog/SystemVerilog keyword.",
                              reg, field)
                )
            if name and name[0].isdigit():
                findings.append(
                    self._msg("N4", LintSeverity.ERROR,
                              f"Identifier '{name}' must not start with a digit.",
                              reg, field)
                )
            if not _VALID_NAME_RE.fullmatch(upper):
                findings.append(
                    self._msg("N5", LintSeverity.WARNING,
                              f"Identifier '{name}' should only use A-Z, 0-9, and underscore.",
                              reg, field)
                )
            if len(name) > 32:
                findings.append(
                    self._msg("N6", LintSeverity.WARNING,
                              f"Identifier '{name}' exceeds the recommended 32-character limit.",
                              reg, field)
                )

        upper_names = sorted(set(names))
        for idx, lhs in enumerate(upper_names):
            for rhs in upper_names[idx + 1:]:
                if self._names_too_similar(lhs, rhs):
                    findings.append(
                        LintMessage(
                            "N7",
                            LintSeverity.INFO,
                            f"Register names '{lhs}' and '{rhs}' are very similar; consider clearer differentiation.",
                        )
                    )
        return findings

    def _check_address_layout(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        if not self.bank.registers:
            return findings

        regs = sorted(self.bank.registers, key=lambda reg: reg.offset)
        byte_width = self.bank.byte_width

        for reg in regs:
            if reg.offset % byte_width != 0:
                findings.append(
                    self._msg("A1", LintSeverity.ERROR,
                              f"Offset 0x{reg.offset:03X} is not aligned to {byte_width} bytes.",
                              reg)
                )

        for prev, curr in zip(regs, regs[1:]):
            gap = curr.offset - prev.offset
            if gap > byte_width:
                findings.append(
                    self._msg("A2", LintSeverity.WARNING,
                              f"Address gap detected between 0x{prev.offset:03X} and 0x{curr.offset:03X}.",
                              curr)
                )

        if self.bank.address_space > 0:
            utilization = (self.bank.num_registers * byte_width) / self.bank.address_space
            if utilization < 0.5:
                findings.append(
                    LintMessage(
                        "A3",
                        LintSeverity.INFO,
                        f"Address space utilization is {utilization:.0%}, below the recommended 50%.",
                    )
                )

        if regs[0].offset != 0:
            findings.append(
                self._msg("A4", LintSeverity.INFO,
                          f"First register starts at 0x{regs[0].offset:03X}; starting at 0x000 is recommended.",
                          regs[0])
            )

        if self.bank.block_size is not None:
            for reg in regs:
                end = reg.offset + byte_width
                if end > self.bank.block_size:
                    findings.append(
                        self._msg("A5", LintSeverity.ERROR,
                                  f"Register end offset 0x{end - 1:03X} exceeds declared block size 0x{self.bank.block_size - 1:03X}.",
                                  reg)
                    )

        return findings

    def _check_fields_and_bits(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        for reg in self.bank.registers:
            if min(field.lsb for field in reg.fields) > 0:
                findings.append(
                    self._msg("F5", LintSeverity.INFO,
                              "Bit 0 is uncovered; placing a field at bit 0 is usually clearer.",
                              reg)
                )

            if len(reg.fields) > 16:
                findings.append(
                    self._msg("F4", LintSeverity.INFO,
                              f"Register has {len(reg.fields)} fields; readability may suffer beyond 16 fields.",
                              reg)
                )

            for field in reg.fields:
                max_val = (1 << field.width) - 1
                if field.reset_val > max_val:
                    findings.append(
                        self._msg("F1", LintSeverity.ERROR,
                                  f"Reset value 0x{field.reset_val:X} exceeds the {field.width}-bit field width.",
                                  reg, field)
                    )
                if field.width > self.bank.data_width or field.msb >= self.bank.data_width:
                    findings.append(
                        self._msg("F2", LintSeverity.ERROR,
                                  f"Field width/position exceeds the {self.bank.data_width}-bit data width.",
                                  reg, field)
                    )
                if self._looks_reserved_field(field) and field.name.upper() not in _RESERVED_FIELD_NAMES:
                    findings.append(
                        self._msg("F3", LintSeverity.WARNING,
                                  f"Reserved-looking field '{field.name}' should be named RSVD or RESERVED.",
                                  reg, field)
                    )
        return findings

    def _check_access_semantics(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        for reg in self.bank.registers:
            groups = {self._access_group(field) for field in reg.fields}
            groups.discard("reserved")
            if len(groups) > 1:
                findings.append(
                    self._msg("X5", LintSeverity.WARNING,
                              "Register mixes multiple access semantics; consider splitting for clarity.",
                              reg)
                )

            for field in reg.fields:
                if field.access_type == "RO" and field.hardware_interface == "input" and field.reset_val != 0:
                    findings.append(
                        self._msg("X1", LintSeverity.WARNING,
                                  "RO field driven by hardware should usually reset to 0.",
                                  reg, field)
                    )

                if (
                    field.access_type == "RO"
                    and field.hardware_interface != "input"
                    and not self._looks_reserved_field(field)
                ):
                    findings.append(
                        self._msg("X2", LintSeverity.ERROR,
                                  "RO field should be backed by a hardware input port.",
                                  reg, field)
                    )

                if field.access_type == "WO" and field.hardware_interface == "output":
                    findings.append(
                        self._msg("X3", LintSeverity.WARNING,
                                  "WO field with hardware output is unusual; confirm this is an intended command path.",
                                  reg, field)
                    )

                if field.access_type in {"W1C", "W1S", "W0C"} and field.hardware_interface != "input":
                    findings.append(
                        self._msg("X4", LintSeverity.WARNING,
                                  f"{field.access_type} field is usually paired with a hardware input status source.",
                                  reg, field)
                    )

                if field.access_type in {"RC", "RS"} and field.width != 1:
                    findings.append(
                        self._msg("X6", LintSeverity.INFO,
                                  f"{field.access_type} is typically used for single-bit flags.",
                                  reg, field)
                    )

        return findings

    def _check_interrupts(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        sources: dict[str, list[tuple[Register, Field]]] = {}
        enables: dict[str, list[tuple[Register, Field]]] = {}

        for reg in self.bank.registers:
            for field in reg.fields:
                if field.interrupt_role == "source":
                    sources.setdefault(field.name, []).append((reg, field))
                elif field.interrupt_role == "enable":
                    enables.setdefault(field.name, []).append((reg, field))

        for name, source_list in sources.items():
            enable_list = enables.get(name, [])
            if not enable_list:
                for reg, field in source_list:
                    findings.append(
                        self._msg("I1", LintSeverity.ERROR,
                                  "Interrupt source field has no matching enable field.",
                                  reg, field)
                    )
                    continue
            for reg, field in source_list:
                if field.access_type not in _SOURCE_ACCESS:
                    findings.append(
                        self._msg("I4", LintSeverity.WARNING,
                                  "Interrupt source field should normally use W1C or RC access.",
                                  reg, field)
                    )
            for src_reg, src_field in source_list:
                for en_reg, en_field in enable_list:
                    if src_field.width != en_field.width:
                        findings.append(
                            self._msg("I3", LintSeverity.ERROR,
                                      f"Interrupt pair width mismatch: source is {src_field.width} bit(s), enable is {en_field.width} bit(s).",
                                      src_reg, src_field)
                        )

        for name, enable_list in enables.items():
            source_list = sources.get(name, [])
            if not source_list:
                for reg, field in enable_list:
                    findings.append(
                        self._msg("I2", LintSeverity.WARNING,
                                  "Interrupt enable field has no matching source field.",
                                  reg, field)
                    )
                    continue
            for reg, field in enable_list:
                if field.access_type != "RW":
                    findings.append(
                        self._msg("I5", LintSeverity.WARNING,
                                  "Interrupt enable field should normally use RW access.",
                                  reg, field)
                    )

        return findings

    def _check_hw_interfaces(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        seen_ports: dict[str, tuple[Register, Field]] = {}

        for reg in self.bank.registers:
            for field in reg.fields:
                if field.hardware_interface == "input" and field.access_type not in _HW_INPUT_ACCESS:
                    findings.append(
                        self._msg("H1", LintSeverity.WARNING,
                                  f"Input-backed field uses access {field.access_type}; expected one of {sorted(_HW_INPUT_ACCESS)}.",
                                  reg, field)
                    )

                if field.hardware_interface == "output" and field.access_type not in _HW_OUTPUT_ACCESS:
                    findings.append(
                        self._msg("H2", LintSeverity.WARNING,
                                  f"Output-backed field uses access {field.access_type}; expected one of {sorted(_HW_OUTPUT_ACCESS)}.",
                                  reg, field)
                    )

                if field.hardware_interface:
                    suffix = "st" if field.hardware_interface == "input" else "q"
                    port_name = f"{reg.name.lower()}_{field.name.lower()}_{suffix}"
                    other = seen_ports.get(port_name)
                    if other:
                        findings.append(
                            self._msg("H3", LintSeverity.ERROR,
                                      f"Generated hardware signal '{port_name}' would collide with another field.",
                                      reg, field)
                        )
                    else:
                        seen_ports[port_name] = (reg, field)

        return findings

    def _check_documentation(self) -> list[LintMessage]:
        findings: list[LintMessage] = []
        has_description = "description" in self.bank.source_columns
        if has_description:
            for reg in self.bank.registers:
                if not any(field.description.strip() for field in reg.fields):
                    findings.append(
                        self._msg("D1", LintSeverity.INFO,
                                  "Register has no populated Description text.",
                                  reg)
                    )

        for reg in self.bank.registers:
            for field in reg.fields:
                if field.side_effect and field.access_type not in {"RC", "RS", "W1C", "W1S", "W0C"}:
                    findings.append(
                        self._msg("D2", LintSeverity.INFO,
                                  "Side Effect text is present on a field without a common side-effect access type.",
                                  reg, field)
                    )
        return findings

    def _lint_identifier(self, rule_id: str, reg: Register, field: Field | None) -> list[LintMessage]:
        target = field.name if field else reg.name
        label = "Field" if field else "Register"
        if target == target.upper():
            return []
        return [
            self._msg(
                rule_id,
                LintSeverity.WARNING,
                f"{label} name '{target}' should be uppercase.",
                reg,
                field,
            )
        ]

    def _names_too_similar(self, lhs: str, rhs: str) -> bool:
        lhs_u = lhs.upper()
        rhs_u = rhs.upper()
        if lhs_u.startswith(rhs_u) or rhs_u.startswith(lhs_u):
            return True
        return SequenceMatcher(None, lhs_u, rhs_u).ratio() >= 0.85

    def _looks_reserved_field(self, field: Field) -> bool:
        return (
            field.access_type == "RO"
            and field.hardware_interface is None
            and field.interrupt_role is None
            and not field.side_effect
        )

    def _access_group(self, field: Field) -> str:
        if self._looks_reserved_field(field):
            return "reserved"
        if field.access_type in {"RW", "WO"}:
            return "control"
        if field.access_type in {"RO", "RC", "RS"}:
            return "status"
        return "sticky"
