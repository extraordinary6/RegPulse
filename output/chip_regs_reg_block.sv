// ============================================================================
// RegPulse Auto-Generated UVM RAL Model
// Block    : chip_regs_reg_block
// Generated: 2026-04-05 18:27:43
// ============================================================================
`ifndef CHIP_REGS_REG_BLOCK_SV
`define CHIP_REGS_REG_BLOCK_SV

class chip_regs_reg_block extends uvm_reg_block;

    `uvm_object_utils(chip_regs_reg_block)

    // ========================================================================
    // Register declarations
    // ========================================================================
    rand chip_regs_CTRL_reg CTRL;
    chip_regs_STATUS_reg STATUS;
    rand chip_regs_INT_EN_reg INT_EN;
    rand chip_regs_INT_STS_reg INT_STS;
    rand chip_regs_DMA_CTRL_reg DMA_CTRL;
    chip_regs_ERR_STS_reg ERR_STS;

    // ========================================================================
    // Constructor
    // ========================================================================
    function new(string name = "chip_regs_reg_block");
        super.new(name, UVM_NO_COVERAGE);
    endfunction

    // ========================================================================
    // build()
    // ========================================================================
    virtual function void build();
        CTRL = chip_regs_CTRL_reg::type_id::create("CTRL");
        CTRL.configure(this, null, "CTRL");
        CTRL.build();
        STATUS = chip_regs_STATUS_reg::type_id::create("STATUS");
        STATUS.configure(this, null, "STATUS");
        STATUS.build();
        INT_EN = chip_regs_INT_EN_reg::type_id::create("INT_EN");
        INT_EN.configure(this, null, "INT_EN");
        INT_EN.build();
        INT_STS = chip_regs_INT_STS_reg::type_id::create("INT_STS");
        INT_STS.configure(this, null, "INT_STS");
        INT_STS.build();
        DMA_CTRL = chip_regs_DMA_CTRL_reg::type_id::create("DMA_CTRL");
        DMA_CTRL.configure(this, null, "DMA_CTRL");
        DMA_CTRL.build();
        ERR_STS = chip_regs_ERR_STS_reg::type_id::create("ERR_STS");
        ERR_STS.configure(this, null, "ERR_STS");
        ERR_STS.build();
    endfunction

    // ========================================================================
    // set_default_map - caller should assign base address
    // ========================================================================
    function void set_default_map(uvm_reg_map map);
        this.default_map = map;
        this.default_map.set_base_addr('h0);
        this.default_map.add_reg(CTRL, 32'h000, "RW");
        this.default_map.add_reg(STATUS, 32'h004, "RO");
        this.default_map.add_reg(INT_EN, 32'h008, "RW");
        this.default_map.add_reg(INT_STS, 32'h00C, "RW");
        this.default_map.add_reg(DMA_CTRL, 32'h010, "RW");
        this.default_map.add_reg(ERR_STS, 32'h014, "RO");
    endfunction

endclass

// ============================================================================
// Individual Register Classes
// ============================================================================

class chip_regs_CTRL_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_CTRL_reg)

    rand uvm_reg_field EN;
    rand uvm_reg_field MODE;
    uvm_reg_field RESERVED;

    function new(string name = "CTRL");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        EN = uvm_reg_field::type_id::create("EN");
        EN.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("RW"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(1)
        );
        MODE = uvm_reg_field::type_id::create("MODE");
        MODE.configure(
            .parent(this),
            .size(3),
            .lsb_pos(1),
            .access("RW"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(1)
        );
        RESERVED = uvm_reg_field::type_id::create("RESERVED");
        RESERVED.configure(
            .parent(this),
            .size(4),
            .lsb_pos(4),
            .access("RO"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        // Backdoor path mapping
        add_hdl_path_slice("ctrl[0:0]", 0, 1);
        add_hdl_path_slice("ctrl[3:1]", 1, 3);
    endfunction

endclass

class chip_regs_STATUS_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_STATUS_reg)

    uvm_reg_field DONE;
    uvm_reg_field BUSY;
    uvm_reg_field PEND;

    function new(string name = "STATUS");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        DONE = uvm_reg_field::type_id::create("DONE");
        DONE.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("RO"),
            .volatile(1),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        BUSY = uvm_reg_field::type_id::create("BUSY");
        BUSY.configure(
            .parent(this),
            .size(1),
            .lsb_pos(1),
            .access("RO"),
            .volatile(1),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        PEND = uvm_reg_field::type_id::create("PEND");
        PEND.configure(
            .parent(this),
            .size(1),
            .lsb_pos(2),
            .access("RS"),
            .volatile(1),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        // Backdoor path mapping
        add_hdl_path_slice("status_done_st", 0, 1);
        add_hdl_path_slice("status_busy_st", 1, 1);
        add_hdl_path_slice("status_pend_st", 2, 1);
    endfunction

endclass

class chip_regs_INT_EN_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_INT_EN_reg)

    rand uvm_reg_field DONE;
    rand uvm_reg_field TIMER;

    function new(string name = "INT_EN");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        DONE = uvm_reg_field::type_id::create("DONE");
        DONE.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("RW"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(1)
        );
        TIMER = uvm_reg_field::type_id::create("TIMER");
        TIMER.configure(
            .parent(this),
            .size(1),
            .lsb_pos(1),
            .access("RW"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(1)
        );
        // Backdoor path mapping
        add_hdl_path_slice("int_en[0:0]", 0, 1);
        add_hdl_path_slice("int_en[1:1]", 1, 1);
    endfunction

endclass

class chip_regs_INT_STS_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_INT_STS_reg)

    uvm_reg_field OVERRUN;

    function new(string name = "INT_STS");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        OVERRUN = uvm_reg_field::type_id::create("OVERRUN");
        OVERRUN.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("W1C"),
            .volatile(1),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        // Backdoor path mapping
        add_hdl_path_slice("int_sts_overrun_st", 0, 1);
    endfunction

endclass

class chip_regs_DMA_CTRL_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_DMA_CTRL_reg)

    uvm_reg_field START;
    uvm_reg_field RSVD;
    rand uvm_reg_field LEN;

    function new(string name = "DMA_CTRL");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        START = uvm_reg_field::type_id::create("START");
        START.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("RS"),
            .volatile(1),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        RSVD = uvm_reg_field::type_id::create("RSVD");
        RSVD.configure(
            .parent(this),
            .size(7),
            .lsb_pos(1),
            .access("RO"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(0)
        );
        LEN = uvm_reg_field::type_id::create("LEN");
        LEN.configure(
            .parent(this),
            .size(8),
            .lsb_pos(8),
            .access("RW"),
            .volatile(0),
            .reset(0),
            .has_reset(1),
            .is_rand(1)
        );
        // Backdoor path mapping
        add_hdl_path_slice("dma_ctrl[0:0]", 0, 1);
        add_hdl_path_slice("dma_ctrl[15:8]", 8, 8);
    endfunction

endclass

class chip_regs_ERR_STS_reg extends uvm_reg;

    `uvm_object_utils(chip_regs_ERR_STS_reg)

    uvm_reg_field PARITY;
    uvm_reg_field CRC_ERR;

    function new(string name = "ERR_STS");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction

    virtual function void build();
        PARITY = uvm_reg_field::type_id::create("PARITY");
        PARITY.configure(
            .parent(this),
            .size(1),
            .lsb_pos(0),
            .access("RC"),
            .volatile(1),
            .reset(1),
            .has_reset(1),
            .is_rand(0)
        );
        CRC_ERR = uvm_reg_field::type_id::create("CRC_ERR");
        CRC_ERR.configure(
            .parent(this),
            .size(1),
            .lsb_pos(1),
            .access("RC"),
            .volatile(1),
            .reset(1),
            .has_reset(1),
            .is_rand(0)
        );
        // Backdoor path mapping
        add_hdl_path_slice("err_sts_parity_st", 0, 1);
        add_hdl_path_slice("err_sts_crc_err_st", 1, 1);
    endfunction

endclass


`endif // CHIP_REGS_REG_BLOCK_SV