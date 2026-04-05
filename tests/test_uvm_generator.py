"""Tests for the UVM RAL generator."""

import tempfile

from src.generators.uvm_generator import UvmGenerator


def test_hdl_path_input_uses_st_signal(sample_bank):
    """hw input fields should reference _st port in hdl_path."""
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert '"status_done_st"' in code
    assert '"status_busy_st"' in code
    assert '"int_sts_overrun_st"' in code
    assert '"err_sts_parity_st"' in code


def test_hdl_path_output_uses_reg_bits(sample_bank):
    """hw output fields should reference register bits in hdl_path."""
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert '"ctrl[0:0]"' in code
    assert '"ctrl[3:1]"' in code


def test_ro_register_not_rand(sample_bank):
    """RO-effective registers should not be declared rand."""
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "rand test_top_STATUS_reg STATUS" not in code
    assert "rand test_top_ERR_STS_reg ERR_STS" not in code
    assert "rand test_top_CTRL_reg CTRL" in code


def test_volatile_set_for_special_access(sample_bank):
    """W1C/RC/RS fields and hw input fields must be volatile(1)."""
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert ".volatile(1)" in code


def test_effective_access_mapping(sample_bank):
    """STATUS (RO+RS) should map as RO; CTRL (RW) as RW."""
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert 'add_reg(STATUS, 32\'h004, "RO")' in code
    assert 'add_reg(CTRL, 32\'h000, "RW")' in code


def test_uvm_include_guard(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "`ifndef TEST_TOP_REG_BLOCK_SV" in code
    assert "`endif // TEST_TOP_REG_BLOCK_SV" in code
