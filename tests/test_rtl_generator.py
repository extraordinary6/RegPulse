"""Tests for the RTL Verilog generator."""

import tempfile

from src.generators.rtl_generator import RtlGenerator


def test_hw_input_synchronization(sample_bank):
    """HW input fields must be continuously latched every clock."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # RO hw input: direct latch
    assert "STATUS[0:0] <= status_done_st" in code
    assert "STATUS[1:1] <= status_busy_st" in code
    # RS hw input: OR latch
    assert "STATUS[2:2] <= STATUS[2:2] | status_pend_st" in code
    # W1C hw input: OR latch
    assert "INT_STS[0:0] <= INT_STS[0:0] | int_sts_overrun_st" in code
    # RC hw input: OR latch
    assert "ERR_STS[0:0] <= ERR_STS[0:0] | err_sts_parity_st" in code


def test_rc_rs_merged_into_read_block(sample_bank):
    """RC/RS must be in the read always block, not separate blocks."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # No separate RC/RS blocks
    assert "Read-Clear (RC) logic" not in code
    assert "Read-Set (RS) logic" not in code
    # Merged into read block
    assert "Read (with merged Read-Clear / Read-Set)" in code
    # RC clear inside read case
    assert "ERR_STS[0:0] <= 1'd0" in code
    assert "ERR_STS[1:1] <= 1'd0" in code
    # RS set inside read case
    assert "STATUS[2:2] <= 1'd1" in code


def test_w1c_write_no_hw_or(sample_bank):
    """W1C write path should NOT OR hw input (moved to hw sync block)."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "| int_sts_overrun_st" not in code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]


def test_rdata_reset(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "rdata_reg <= 32'h0" in code


def test_hw_output_assignments(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "assign ctrl_en_q = CTRL[0:0]" in code
    assert "assign ctrl_mode_q = CTRL[3:1]" in code


def test_interrupt_aggregation():
    """irq_o should be generated when interrupt pairs exist."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top")
    # Status register with DONE as source
    int_sts = Register("INT_STS", 0x04)
    src_field = Field("DONE", "0", "W1C", 0, hardware_interface="input")
    src_field.interrupt_role = "source"
    int_sts.add_field(src_field)
    int_sts.add_field(Field("PAD", "7:1", "RO", 0))
    bank.add_register(int_sts)

    # Enable register with DONE as enable (same field name = paired)
    int_en = Register("INT_EN", 0x08)
    en_field = Field("DONE", "0", "RW", 0, hardware_interface="output")
    en_field.interrupt_role = "enable"
    int_en.add_field(en_field)
    int_en.add_field(Field("PAD", "7:1", "RO", 0))
    bank.add_register(int_en)

    gen = RtlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" in code
    assert "assign irq_o" in code
    assert "INT_STS[0:0] & INT_EN[0:0]" in code


def test_no_interrupt_when_no_pairs(sample_bank):
    """irq_o should NOT be generated when there are no interrupt pairs."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" not in code


def test_wo_w1s_w0c_access_types():
    """New access types should generate correct RTL logic."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_wo")
    reg = Register("WO_REG", 0x00)
    reg.add_field(Field("CMD", "0", "WO", 0, hardware_interface="output"))
    reg.add_field(Field("SET", "1:1", "W1S", 0))
    reg.add_field(Field("CLR", "2:2", "W0C", 0))
    reg.add_field(Field("PAD", "7:3", "RO", 0))
    bank.add_register(reg)

    gen = RtlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    write_section = code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]
    # WO: same as RW
    assert "WO_REG[0:0] <= wdata[0:0]" in write_section
    # W1S: reg | wdata
    assert "WO_REG[1:1] <= WO_REG[1:1] | wdata[1:1]" in write_section
    # W0C: reg & wdata
    assert "WO_REG[2:2] <= WO_REG[2:2] & wdata[2:2]" in write_section
    # WO read returns 0
    read_section = code.split("Read (with merged")[1]
    assert "rdata_reg[0:0] <= 1'd0" in read_section


def test_module_name_has_regfile_core(sample_bank):
    """Generated module name should end with _regfile_core."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "module test_top_regfile_core" in code


def test_generic_interface_signals(sample_bank):
    """Core should use generic interface signals, not APB signals."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # Generic signals present
    assert "input  wire             clk," in code
    assert "input  wire             rst_n," in code
    assert "input  wire             wen," in code
    assert "input  wire             ren," in code
    assert "output wire             ready" in code
    assert "output wire [DW-1:0]    rdata," in code
    # No APB signals
    assert "pclk" not in code
    assert "psel" not in code
    assert "penable" not in code
    assert "pwrite" not in code
    assert "prdata" not in code
    assert "pready" not in code


def test_wstrb_masking(sample_bank):
    """Write path should include wstrb checks."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    write_section = code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]
    assert "wstrb[0:0] != 1'd0" in write_section


def test_read_ready_timing(sample_bank):
    """Read should use ready_reg and rdata_reg for 1-cycle latency."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "ready_reg <= 1'b1" in code
    assert "ready_reg <= 1'b0" in code
    assert "rdata = rdata_reg" in code
    assert "ready = ready_reg" in code


def test_addr_is_word_address(sample_bank):
    """Address should use word addressing (no byte shift)."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # Should be case (addr[...]), not case (paddr[...:2])
    assert "case (addr[" in code
    # No paddr references
    assert "paddr" not in code
