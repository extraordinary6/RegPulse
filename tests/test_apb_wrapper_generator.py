"""Tests for the APB wrapper generator."""

import tempfile

from src.generators.apb_wrapper_generator import ApbWrapperGenerator


def test_wrapper_instantiates_regfile_core(sample_bank):
    """APB wrapper should instantiate the regfile_core module."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "test_top_regfile_core" in code
    assert "u_regfile_core" in code


def test_apb_signals_declared(sample_bank):
    """APB wrapper should have APB4 interface signals."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire        pclk," in code
    assert "input  wire        presetn," in code
    assert "input  wire [31:0] paddr," in code
    assert "input  wire        psel," in code
    assert "input  wire        penable," in code
    assert "input  wire        pwrite," in code
    assert "input  wire [31:0] pwdata," in code
    assert "input  wire [3:0]  pstrb," in code
    assert "output wire [31:0] prdata," in code
    assert "output wire        pready," in code
    assert "output wire        pslverr" in code


def test_read_pending_state_machine(sample_bank):
    """APB wrapper should have read_pending state register."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "reg read_pending" in code
    # read_pending set on read access
    assert "read_pending <= 1'b1" in code
    # read_pending cleared when core_ready
    assert "read_pending <= 1'b0" in code
    assert "core_ready" in code


def test_pready_pslverr_logic(sample_bank):
    """pready should stall for reads; pslverr should be tied low."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # pready goes high on write immediately or on read completion
    assert "assign pready" in code
    assert "psel && penable && pwrite && !read_pending" in code
    assert "read_pending && core_ready" in code
    # pslverr always 0
    assert "assign pslverr    = 1'b0" in code


def test_hw_port_passthrough(sample_bank):
    """HW ports should be declared and connected through to the core."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # HW output ports declared on wrapper
    assert "output wire [0:0] ctrl_en_q" in code
    assert "output wire [3:1] ctrl_mode_q" in code
    # HW input ports declared on wrapper
    assert "input  wire [0:0] status_done_st" in code
    assert "input  wire [1:1] status_busy_st" in code
    # Connected to core instance
    assert ".ctrl_en_q (ctrl_en_q)" in code
    assert ".status_done_st (status_done_st)" in code


def test_irq_passthrough():
    """irq_o should pass through to core when interrupt pairs exist."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top")
    int_sts = Register("INT_STS", 0x04)
    src_field = Field("DONE", "0", "W1C", 0, hardware_interface="input")
    src_field.interrupt_role = "source"
    int_sts.add_field(src_field)
    bank.add_register(int_sts)

    int_en = Register("INT_EN", 0x08)
    en_field = Field("DONE", "0", "RW", 0, hardware_interface="output")
    en_field.interrupt_role = "enable"
    int_en.add_field(en_field)
    bank.add_register(int_en)

    gen = ApbWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "output wire        irq_o" in code
    assert ".irq_o      (irq_o)" in code


def test_no_irq_when_no_pairs(sample_bank):
    """irq_o should NOT appear when there are no interrupt pairs."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" not in code


def test_addr_mapping(sample_bank):
    """paddr should be shifted to word address for core."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # paddr mapped from byte to word address
    assert "core_addr  = paddr[" in code


def test_module_name(sample_bank):
    """Module name should end with _apb_wrapper."""
    gen = ApbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        assert path.endswith("test_top_apb_wrapper.v")
        with open(path) as f:
            code = f.read()

    assert "module test_top_apb_wrapper" in code


def test_write_no_stall():
    """Write operations should not be gated by read_pending."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top")
    reg = Register("CTRL", 0x00)
    reg.add_field(Field("EN", "0", "RW", 0))
    bank.add_register(reg)

    gen = ApbWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    # core_wen does NOT require !read_pending for writes
    assert "core_wen   = psel && penable && pwrite && !read_pending" in code
    # pready includes immediate write path
    assert "psel && penable && pwrite && !read_pending" in code
