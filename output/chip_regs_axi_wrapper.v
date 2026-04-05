// ============================================================================
// RegPulse Auto-Generated AXI4-Lite Wrapper
// Module   : chip_regs_axi_wrapper
// Generated: 2026-04-05 18:28:09
// ============================================================================
module chip_regs_axi_wrapper (
    // AXI4-Lite Global
    input  wire                        aclk,
    input  wire                        aresetn,

    // AXI4-Lite Write Address Channel
    input  wire                        awvalid,
    output wire                        awready,
    input  wire [31:0]                 awaddr,

    // AXI4-Lite Write Data Channel
    input  wire                        wvalid,
    output wire                        wready,
    input  wire [31:0] wdata,
    input  wire [3:0] wstrb,

    // AXI4-Lite Write Response Channel
    output wire                        bvalid,
    input  wire                        bready,
    output wire [1:0]                  bresp,

    // AXI4-Lite Read Address Channel
    input  wire                        arvalid,
    output wire                        arready,
    input  wire [31:0]                 araddr,

    // AXI4-Lite Read Data Channel
    output wire                        rvalid,
    input  wire                        rready,
    output wire [31:0] rdata,
    output wire [1:0]                  rresp,
    // Hardware Interface
    output wire [0:0] ctrl_en_q,
    output wire [3:1] ctrl_mode_q,
    input  wire [0:0] status_done_st,
    input  wire [1:1] status_busy_st,
    input  wire [2:2] status_pend_st,
    output wire [0:0] int_en_done_q,
    output wire [1:1] int_en_timer_q,
    input  wire [0:0] int_sts_overrun_st,
    output wire [0:0] dma_ctrl_start_q,
    output wire [15:8] dma_ctrl_len_q,
    input  wire [0:0] err_sts_parity_st,
    input  wire [1:1] err_sts_crc_err_st
);

    // ========================================================================
    // Internal signals
    // ========================================================================
    wire [3-1:0] core_addr;
    wire [32-1:0] core_wdata;
    wire        core_wen;
    wire [4-1:0] core_wstrb;
    wire        core_ren;
    wire [32-1:0] core_rdata;
    wire        core_ready;

    // ========================================================================
    // Write Address Channel
    // ========================================================================
    reg  awaddr_sel;
    reg  [31:0] awaddr_reg;
    wire awaddr_done = awvalid && awready;
    assign awready = awvalid && !awaddr_sel;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            awaddr_sel <= 1'b0;
            awaddr_reg <= 32'd0;
        end else if (awaddr_done) begin
            awaddr_sel <= 1'b1;
            awaddr_reg <= awaddr;
        end else if (core_wen) begin
            awaddr_sel <= 1'b0;
        end
    end

    // ========================================================================
    // Write Data Channel ¡ª accept W when AW is captured and data valid
    // ========================================================================
    reg wdata_sel;
    wire wdata_done = wvalid && wready;
    assign wready = wvalid && awaddr_sel && !wdata_sel;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn)
            wdata_sel <= 1'b0;
        else if (wdata_done)
            wdata_sel <= 1'b1;
        else if (core_wen)
            wdata_sel <= 1'b0;
    end

    // ========================================================================
    // Write Response Channel
    // ========================================================================
    reg bvalid_reg;
    assign bvalid = bvalid_reg;
    assign bresp  = 2'b00;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn)
            bvalid_reg <= 1'b0;
        else if (core_wen && bvalid_reg == 1'b0)
            bvalid_reg <= 1'b1;
        else if (bvalid && bready)
            bvalid_reg <= 1'b0;
    end

    // ========================================================================
    // Read Address Channel
    // ========================================================================
    reg ar_sel;
    reg [31:0] araddr_reg;
    wire ar_done = arvalid && arready;
    assign arready = arvalid && !ar_sel;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            ar_sel <= 1'b0;
            araddr_reg <= 32'd0;
        end else if (ar_done) begin
            ar_sel <= 1'b1;
            araddr_reg <= araddr;
        end else if (core_ren) begin
            ar_sel <= 1'b0;
        end
    end

    // ========================================================================
    // Read Data Channel
    // ========================================================================
    reg rvalid_reg;
    reg [31:0] rdata_reg;
    assign rvalid = rvalid_reg;
    assign rdata  = rdata_reg;
    assign rresp  = 2'b00;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            rvalid_reg <= 1'b0;
        end else begin
            if (ar_sel && core_ready && !rvalid_reg) begin
                rvalid_reg <= 1'b1;
                rdata_reg  <= core_rdata;
            end else if (rvalid && rready) begin
                rvalid_reg <= 1'b0;
            end
        end
    end

    // ========================================================================
    // AXI -> Core interface mapping
    // ========================================================================
    assign core_addr  = core_wen ? awaddr_reg[4:2]
                                 : araddr_reg[4:2];
    assign core_wdata = wdata;
    assign core_wstrb = wstrb;
    assign core_wen   = awaddr_sel && wdata_sel;
    assign core_ren   = ar_sel && !core_wen;

    // ========================================================================
    // Core instance
    // ========================================================================
    chip_regs_regfile_core #(
        .AW(3),
        .DW(32)
    ) u_regfile_core (
        .clk        (aclk),
        .rst_n      (aresetn),
        .addr       (core_addr),
        .wdata      (core_wdata),
        .wen        (core_wen),
        .wstrb      (core_wstrb),
        .ren        (core_ren),
        .rdata      (core_rdata),
        .ready      (core_ready),
        .ctrl_en_q (ctrl_en_q),
        .ctrl_mode_q (ctrl_mode_q),
        .status_done_st (status_done_st),
        .status_busy_st (status_busy_st),
        .status_pend_st (status_pend_st),
        .int_en_done_q (int_en_done_q),
        .int_en_timer_q (int_en_timer_q),
        .int_sts_overrun_st (int_sts_overrun_st),
        .dma_ctrl_start_q (dma_ctrl_start_q),
        .dma_ctrl_len_q (dma_ctrl_len_q),
        .err_sts_parity_st (err_sts_parity_st),
        .err_sts_crc_err_st (err_sts_crc_err_st)
    );

endmodule