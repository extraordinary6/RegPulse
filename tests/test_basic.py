"""Integration test — full flow from Excel to generated outputs."""

import tempfile

from src.parser.excel_parser import ExcelParser
from src.validators.validator import Validator
from src.generators.rtl_generator import RtlGenerator
from src.generators.uvm_generator import UvmGenerator
from src.generators.c_header_generator import CHeaderGenerator
from src.generators.json_generator import JsonGenerator
from src.generators.html_generator import HtmlGenerator
from src.generators.markdown_generator import MarkdownGenerator


def test_full_flow_with_sample_excel(sample_excel):
    parser = ExcelParser(sample_excel, block_name="chip_regs")
    bank = parser.parse()

    Validator(bank).validate()

    with tempfile.TemporaryDirectory() as tmpdir:
        # RTL
        rtl_gen = RtlGenerator(bank)
        rtl_path = rtl_gen.generate(tmpdir)
        with open(rtl_path) as f:
            rtl_code = f.read()

        # UVM
        uvm_gen = UvmGenerator(bank)
        uvm_path = uvm_gen.generate(tmpdir)
        with open(uvm_path) as f:
            uvm_code = f.read()

        # C header
        hdr_gen = CHeaderGenerator(bank)
        hdr_path = hdr_gen.generate(tmpdir)
        assert hdr_path.endswith("chip_regs.h")

        # JSON
        json_gen = JsonGenerator(bank)
        json_path = json_gen.generate(tmpdir)
        assert json_path.endswith("chip_regs.json")

        # HTML
        html_gen = HtmlGenerator(bank)
        html_path = html_gen.generate(tmpdir)
        assert html_path.endswith("chip_regs.html")

        # Markdown
        md_gen = MarkdownGenerator(bank)
        md_path = md_gen.generate(tmpdir)
        assert md_path.endswith("chip_regs.md")

        # Phase 1 bug fix assertions
        assert "Hardware Input Synchronization" in rtl_code
        assert "APB Read (with merged Read-Clear / Read-Set)" in rtl_code
        assert "Read-Clear (RC) logic" not in rtl_code

        # UVM hdl_path uses _st for inputs
        assert "status_done_st" in uvm_code

        # Bank structure
        assert bank.num_registers == 5
        assert len(bank.registers[0].fields) == 3

        # Field attributes
        ctrl_en = bank.registers[0].fields[0]
        assert ctrl_en.hardware_interface == "output"
        assert ctrl_en.is_bus_writable

        status_pend = bank.registers[1].fields[2]
        assert status_pend.access_type == "RS"
        assert status_pend.has_read_side_effect
