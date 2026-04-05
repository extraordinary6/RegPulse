// ============================================================================
// RegPulse Auto-Generated AHB-Lite Wrapper
// Module   : chip_regs_ahb_wrapper
// Generated: 2026-04-05 18:28:00
// ============================================================================
module chip_regs_ahb_wrapper (
    // AHB-Lite Interface
    input  wire                        hclk,
    input  wire                        hresetn,
    input  wire [31:0]                 haddr,
    input  wire [31:0] hwdata,
    output wire [31:0] hrdata,
    input  wire                        hwrite,
    input  wire                        hsel,
    input  wire [1:0]                  htrans,
    input  wire [2:0]                  hburst,
    input  wire [2:0]                  hsize,
    input  wire [3:0] hwstrb,
    input  wire                        hready,
    output wire                        hreadyout,
    output wire [1:0]                  hresp,
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
    // AHB-Lite transaction decode
    // ========================================================================
    wire txn_valid = hsel && (htrans == 2'b10 || htrans == 2'b11);

    // ========================================================================
    // Read stall state
    // ========================================================================
    reg read_pending;

    always @(posedge hclk or negedge hresetn) begin
        if (!hresetn) begin
            read_pending <= 1'b0;
        end else begin
            if (read_pending && core_ready) begin
                read_pending <= 1'b0;
            end else if (txn_valid && !hwrite && !read_pending) begin
                read_pending <= 1'b1;
            end
        end
    end

    // ========================================================================
    // AHB -> Core interface mapping
    // ========================================================================
    assign core_addr  = haddr[4:2];
    assign core_wdata = hwdata;
    assign core_wstrb = hwstrb;
    assign core_wen   = txn_valid && hwrite && !read_pending;
    assign core_ren   = txn_valid && !hwrite && !read_pending;
    assign hrdata     = core_rdata;
    assign hreadyout  = (txn_valid && hwrite && !read_pending) ||
                        (read_pending && core_ready);
    assign hresp      = 2'b00;

    // ========================================================================
    // Core instance
    // ========================================================================
    chip_regs_regfile_core #(
        .AW(3),
        .DW(32)
    ) u_regfile_core (
        .clk        (hclk),
        .rst_n      (hresetn),
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