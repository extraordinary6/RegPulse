// ============================================================================
// RegPulse Auto-Generated Register File Core
// Module   : chip_regs_regfile_core
// Generated: 2026-04-05 18:28:09
// ============================================================================
module chip_regs_regfile_core #(
    parameter AW = 3,
    parameter DW = 32
) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire [AW-1:0]    addr,
    input  wire [DW-1:0]    wdata,
    input  wire             wen,
    input  wire [strb_width-1:0] wstrb,
    input  wire             ren,
    output wire [DW-1:0]    rdata,
    output wire             ready,
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
    // Read data & ready registers
    // ========================================================================
    reg [DW-1:0] rdata_reg;
    reg          ready_reg;

    assign rdata = rdata_reg;
    assign ready = ready_reg;

    // ========================================================================
    // Register declarations
    // ========================================================================
    reg [DW-1:0] CTRL; // offset 0x000
    reg [DW-1:0] STATUS; // offset 0x004
    reg [DW-1:0] INT_EN; // offset 0x008
    reg [DW-1:0] INT_STS; // offset 0x00C
    reg [DW-1:0] DMA_CTRL; // offset 0x010
    reg [DW-1:0] ERR_STS; // offset 0x014

    // ========================================================================
    // Hardware output assignments
    // ========================================================================
    assign ctrl_en_q = CTRL[0:0];
    assign ctrl_mode_q = CTRL[3:1];
    assign int_en_done_q = INT_EN[0:0];
    assign int_en_timer_q = INT_EN[1:1];
    assign dma_ctrl_start_q = DMA_CTRL[0:0];
    assign dma_ctrl_len_q = DMA_CTRL[15:8];


    // ========================================================================
    // Reset
    // ========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            CTRL <= 32'h00000000;
            STATUS <= 32'h00000000;
            INT_EN <= 32'h00000000;
            INT_STS <= 32'h00000000;
            DMA_CTRL <= 32'h00000000;
            ERR_STS <= 32'h00000003;
            rdata_reg <= 32'h00000000;
            ready_reg <= 1'b0;
        end
    end

    // ========================================================================
    // Hardware Input Synchronization
    // ========================================================================
    always @(posedge clk) begin
        if (rst_n) begin
            // STATUS hw input capture
            STATUS[0:0] <= status_done_st;
            STATUS[1:1] <= status_busy_st;
            STATUS[2:2] <= STATUS[2:2] | status_pend_st;
            // INT_STS hw input capture
            INT_STS[0:0] <= INT_STS[0:0] | int_sts_overrun_st;
            // ERR_STS hw input capture
            ERR_STS[0:0] <= ERR_STS[0:0] | err_sts_parity_st;
            ERR_STS[1:1] <= ERR_STS[1:1] | err_sts_crc_err_st;
        end
    end

    // ========================================================================
    // Write (with byte-strobe masking)
    // ========================================================================
    always @(posedge clk) begin
        if (rst_n && wen) begin
            case (addr[2:0])
                0: begin
                    if (wstrb[0:0] != 1'd0)
                        CTRL[0:0] <= wdata[0:0];
                    if (wstrb[0:0] != 1'd0)
                        CTRL[3:1] <= wdata[3:1];
                end
                2: begin
                    if (wstrb[0:0] != 1'd0)
                        INT_EN[0:0] <= wdata[0:0];
                    if (wstrb[0:0] != 1'd0)
                        INT_EN[1:1] <= wdata[1:1];
                end
                3: begin
                    if (wstrb[0:0] != 1'd0)
                        INT_STS[0:0] <= INT_STS[0:0] & ~wdata[0:0];
                end
                4: begin
                    if (wstrb[1:1] != 1'd0)
                        DMA_CTRL[15:8] <= wdata[15:8];
                end
                default: ;
            endcase
        end
    end

    // ========================================================================
    // Read (with merged Read-Clear / Read-Set)
    // ========================================================================
    always @(posedge clk) begin
        if (rst_n && ren) begin
            ready_reg <= 1'b1;
            case (addr[2:0])
                0: rdata_reg <= CTRL;
                1: begin
                    rdata_reg <= STATUS;
                    STATUS[2:2] <= 1'd1;
                end
                2: rdata_reg <= INT_EN;
                3: rdata_reg <= INT_STS;
                4: begin
                    rdata_reg <= DMA_CTRL;
                    DMA_CTRL[0:0] <= 1'd1;
                end
                5: begin
                    rdata_reg <= ERR_STS;
                    ERR_STS[0:0] <= 1'd0;
                    ERR_STS[1:1] <= 1'd0;
                end
                default: rdata_reg <= 32'h00000000;
            endcase
        end else begin
            ready_reg <= 1'b0;
        end
    end

endmodule