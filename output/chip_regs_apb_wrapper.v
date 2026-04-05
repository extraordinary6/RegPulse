// ============================================================================
// RegPulse Auto-Generated APB4 Wrapper
// Module   : chip_regs_apb_wrapper
// Generated: 2026-04-05 18:27:52
// ============================================================================
module chip_regs_apb_wrapper (
    // APB4 Interface
    input  wire        pclk,
    input  wire        presetn,
    input  wire [31:0] paddr,
    input  wire        psel,
    input  wire        penable,
    input  wire        pwrite,
    input  wire [31:0] pwdata,
    input  wire [3:0]  pstrb,
    output wire [31:0] prdata,
    output wire        pready,
    output wire        pslverr,
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
    // Read stall state
    // ========================================================================
    reg read_pending;

    always @(posedge pclk or negedge presetn) begin
        if (!presetn) begin
            read_pending <= 1'b0;
        end else begin
            if (read_pending && core_ready) begin
                read_pending <= 1'b0;
            end else if (psel && penable && !pwrite && !read_pending) begin
                read_pending <= 1'b1;
            end
        end
    end

    // ========================================================================
    // APB ¡ú Core interface mapping
    // ========================================================================
    assign core_addr  = paddr[4:2];
    assign core_wdata = pwdata[31:0];
    assign core_wstrb = pstrb[3:0];
    assign core_wen   = psel && penable && pwrite && !read_pending;
    assign core_ren   = psel && penable && !pwrite && !read_pending;
    assign pready     = (psel && penable && pwrite && !read_pending) ||
                        (read_pending && core_ready);
    assign prdata     = core_rdata;
    assign pslverr    = 1'b0;

    // ========================================================================
    // Core instance
    // ========================================================================
    chip_regs_regfile_core #(
        .AW(3),
        .DW(32)
    ) u_regfile_core (
        .clk        (pclk),
        .rst_n      (presetn),
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