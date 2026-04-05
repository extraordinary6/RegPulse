/*
 * RegPulse Auto-Generated Register Definitions
 * Block    : chip_regs
 * Generated: 2026-04-05 18:27:43
 */
#ifndef CHIP_REGS_H
#define CHIP_REGS_H

#include <stdint.h>

/* Base Address */
#define CHIP_REGS_BASE (0x00000000U)

/* Register Offsets */
#define CHIP_REGS_CTRL_OFFSET (0x000U)
#define CHIP_REGS_STATUS_OFFSET (0x004U)
#define CHIP_REGS_INT_EN_OFFSET (0x008U)
#define CHIP_REGS_INT_STS_OFFSET (0x00CU)
#define CHIP_REGS_DMA_CTRL_OFFSET (0x010U)
#define CHIP_REGS_ERR_STS_OFFSET (0x014U)

/* Absolute Addresses */
#define CHIP_REGS_CTRL_ADDR (CHIP_REGS_BASE + 0x000U)
#define CHIP_REGS_STATUS_ADDR (CHIP_REGS_BASE + 0x004U)
#define CHIP_REGS_INT_EN_ADDR (CHIP_REGS_BASE + 0x008U)
#define CHIP_REGS_INT_STS_ADDR (CHIP_REGS_BASE + 0x00CU)
#define CHIP_REGS_DMA_CTRL_ADDR (CHIP_REGS_BASE + 0x010U)
#define CHIP_REGS_ERR_STS_ADDR (CHIP_REGS_BASE + 0x014U)

#define CHIP_REGS_ADDR_SPACE (24U)

/* Field Bit Masks and Positions */
/* CTRL */
#define CHIP_REGS_CTRL_EN_MASK   (0x00000001U)
#define CHIP_REGS_CTRL_EN_LSB    (0U)
#define CHIP_REGS_CTRL_EN_WIDTH  (1U)
#define CHIP_REGS_CTRL_EN_RESET  (0x00000000U)
#define CHIP_REGS_CTRL_MODE_MASK   (0x0000000EU)
#define CHIP_REGS_CTRL_MODE_LSB    (1U)
#define CHIP_REGS_CTRL_MODE_WIDTH  (3U)
#define CHIP_REGS_CTRL_MODE_RESET  (0x00000000U)
#define CHIP_REGS_CTRL_RESERVED_MASK   (0x000000F0U)
#define CHIP_REGS_CTRL_RESERVED_LSB    (4U)
#define CHIP_REGS_CTRL_RESERVED_WIDTH  (4U)
#define CHIP_REGS_CTRL_RESERVED_RESET  (0x00000000U)

/* STATUS */
#define CHIP_REGS_STATUS_DONE_MASK   (0x00000001U)
#define CHIP_REGS_STATUS_DONE_LSB    (0U)
#define CHIP_REGS_STATUS_DONE_WIDTH  (1U)
#define CHIP_REGS_STATUS_DONE_RESET  (0x00000000U)
#define CHIP_REGS_STATUS_BUSY_MASK   (0x00000002U)
#define CHIP_REGS_STATUS_BUSY_LSB    (1U)
#define CHIP_REGS_STATUS_BUSY_WIDTH  (1U)
#define CHIP_REGS_STATUS_BUSY_RESET  (0x00000000U)
#define CHIP_REGS_STATUS_PEND_MASK   (0x00000004U)
#define CHIP_REGS_STATUS_PEND_LSB    (2U)
#define CHIP_REGS_STATUS_PEND_WIDTH  (1U)
#define CHIP_REGS_STATUS_PEND_RESET  (0x00000000U)

/* INT_EN */
#define CHIP_REGS_INT_EN_DONE_MASK   (0x00000001U)
#define CHIP_REGS_INT_EN_DONE_LSB    (0U)
#define CHIP_REGS_INT_EN_DONE_WIDTH  (1U)
#define CHIP_REGS_INT_EN_DONE_RESET  (0x00000000U)
#define CHIP_REGS_INT_EN_TIMER_MASK   (0x00000002U)
#define CHIP_REGS_INT_EN_TIMER_LSB    (1U)
#define CHIP_REGS_INT_EN_TIMER_WIDTH  (1U)
#define CHIP_REGS_INT_EN_TIMER_RESET  (0x00000000U)

/* INT_STS */
#define CHIP_REGS_INT_STS_OVERRUN_MASK   (0x00000001U)
#define CHIP_REGS_INT_STS_OVERRUN_LSB    (0U)
#define CHIP_REGS_INT_STS_OVERRUN_WIDTH  (1U)
#define CHIP_REGS_INT_STS_OVERRUN_RESET  (0x00000000U)

/* DMA_CTRL */
#define CHIP_REGS_DMA_CTRL_START_MASK   (0x00000001U)
#define CHIP_REGS_DMA_CTRL_START_LSB    (0U)
#define CHIP_REGS_DMA_CTRL_START_WIDTH  (1U)
#define CHIP_REGS_DMA_CTRL_START_RESET  (0x00000000U)
#define CHIP_REGS_DMA_CTRL_RSVD_MASK   (0x000000FEU)
#define CHIP_REGS_DMA_CTRL_RSVD_LSB    (1U)
#define CHIP_REGS_DMA_CTRL_RSVD_WIDTH  (7U)
#define CHIP_REGS_DMA_CTRL_RSVD_RESET  (0x00000000U)
#define CHIP_REGS_DMA_CTRL_LEN_MASK   (0x0000FF00U)
#define CHIP_REGS_DMA_CTRL_LEN_LSB    (8U)
#define CHIP_REGS_DMA_CTRL_LEN_WIDTH  (8U)
#define CHIP_REGS_DMA_CTRL_LEN_RESET  (0x00000000U)

/* ERR_STS */
#define CHIP_REGS_ERR_STS_PARITY_MASK   (0x00000001U)
#define CHIP_REGS_ERR_STS_PARITY_LSB    (0U)
#define CHIP_REGS_ERR_STS_PARITY_WIDTH  (1U)
#define CHIP_REGS_ERR_STS_PARITY_RESET  (0x00000001U)
#define CHIP_REGS_ERR_STS_CRC_ERR_MASK   (0x00000002U)
#define CHIP_REGS_ERR_STS_CRC_ERR_LSB    (1U)
#define CHIP_REGS_ERR_STS_CRC_ERR_WIDTH  (1U)
#define CHIP_REGS_ERR_STS_CRC_ERR_RESET  (0x00000001U)

/* Access Macros */
#define CHIP_REGS_CTRL_EN_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_CTRL_EN_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))
#define CHIP_REGS_CTRL_MODE_GET(regval) (((regval) & 0x0000000EU) >> 1U)
#define CHIP_REGS_CTRL_MODE_SET(regval, val) (((regval) & ~0x0000000EU) | (((uint32_t)(val) << 1U) & 0x0000000EU))
#define CHIP_REGS_CTRL_RESERVED_GET(regval) (((regval) & 0x000000F0U) >> 4U)
#define CHIP_REGS_CTRL_RESERVED_SET(regval, val) (((regval) & ~0x000000F0U) | (((uint32_t)(val) << 4U) & 0x000000F0U))

#define CHIP_REGS_STATUS_DONE_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_STATUS_DONE_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))
#define CHIP_REGS_STATUS_BUSY_GET(regval) (((regval) & 0x00000002U) >> 1U)
#define CHIP_REGS_STATUS_BUSY_SET(regval, val) (((regval) & ~0x00000002U) | (((uint32_t)(val) << 1U) & 0x00000002U))
#define CHIP_REGS_STATUS_PEND_GET(regval) (((regval) & 0x00000004U) >> 2U)
#define CHIP_REGS_STATUS_PEND_SET(regval, val) (((regval) & ~0x00000004U) | (((uint32_t)(val) << 2U) & 0x00000004U))

#define CHIP_REGS_INT_EN_DONE_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_INT_EN_DONE_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))
#define CHIP_REGS_INT_EN_TIMER_GET(regval) (((regval) & 0x00000002U) >> 1U)
#define CHIP_REGS_INT_EN_TIMER_SET(regval, val) (((regval) & ~0x00000002U) | (((uint32_t)(val) << 1U) & 0x00000002U))

#define CHIP_REGS_INT_STS_OVERRUN_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_INT_STS_OVERRUN_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))

#define CHIP_REGS_DMA_CTRL_START_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_DMA_CTRL_START_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))
#define CHIP_REGS_DMA_CTRL_RSVD_GET(regval) (((regval) & 0x000000FEU) >> 1U)
#define CHIP_REGS_DMA_CTRL_RSVD_SET(regval, val) (((regval) & ~0x000000FEU) | (((uint32_t)(val) << 1U) & 0x000000FEU))
#define CHIP_REGS_DMA_CTRL_LEN_GET(regval) (((regval) & 0x0000FF00U) >> 8U)
#define CHIP_REGS_DMA_CTRL_LEN_SET(regval, val) (((regval) & ~0x0000FF00U) | (((uint32_t)(val) << 8U) & 0x0000FF00U))

#define CHIP_REGS_ERR_STS_PARITY_GET(regval) (((regval) & 0x00000001U) >> 0U)
#define CHIP_REGS_ERR_STS_PARITY_SET(regval, val) (((regval) & ~0x00000001U) | (((uint32_t)(val) << 0U) & 0x00000001U))
#define CHIP_REGS_ERR_STS_CRC_ERR_GET(regval) (((regval) & 0x00000002U) >> 1U)
#define CHIP_REGS_ERR_STS_CRC_ERR_SET(regval, val) (((regval) & ~0x00000002U) | (((uint32_t)(val) << 1U) & 0x00000002U))

#endif /* CHIP_REGS_H */
