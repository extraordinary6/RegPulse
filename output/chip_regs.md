# chip_regs Register Map

Generated: 2026-04-05 18:27:43  
Registers: 6 | Address Space: 24 bytes | Base Address: 0x00000000

## Access Types

| Type | Description |
|------|-------------|
| RW | Read / Write |
| RO | Read Only |
| W1C | Write 1 to Clear |
| RC | Read to Clear |
| RS | Read to Set |
| WO | Write Only |
| W1S | Write 1 to Set |
| W0C | Write 0 to Clear |

## Register Summary

| Name | Offset | Width | Reset | Access | Fields |
|------|--------|-------|-------|--------|--------|
| CTRL | 0x000 | 8 | 0x00000000 | RW | EN, MODE, RESERVED |
| STATUS | 0x004 | 3 | 0x00000000 | RO | DONE, BUSY, PEND |
| INT_EN | 0x008 | 2 | 0x00000000 | RW | DONE, TIMER |
| INT_STS | 0x00C | 1 | 0x00000000 | RW | OVERRUN |
| DMA_CTRL | 0x010 | 16 | 0x00000000 | RW | START, RSVD, LEN |
| ERR_STS | 0x014 | 2 | 0x00000003 | RO | PARITY, CRC_ERR |

## Register Details

### CTRL

- **Offset**: 0x000
- **Width**: 8 bits
- **Reset**: 0x00000000
- **Access**: RW

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| EN | [0:0] | 1 | RW | 0x0 | output | - | - |
| MODE | [3:1] | 3 | RW | 0x0 | output | - | - |
| RESERVED | [7:4] | 4 | RO | 0x0 | - | - | - |

### STATUS

- **Offset**: 0x004
- **Width**: 3 bits
- **Reset**: 0x00000000
- **Access**: RO

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| DONE | [0:0] | 1 | RO | 0x0 | input | - | - |
| BUSY | [1:1] | 1 | RO | 0x0 | input | - | - |
| PEND | [2:2] | 1 | RS | 0x0 | input | - | Set on read |

### INT_EN

- **Offset**: 0x008
- **Width**: 2 bits
- **Reset**: 0x00000000
- **Access**: RW

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| DONE | [0:0] | 1 | RW | 0x0 | output | - | - |
| TIMER | [1:1] | 1 | RW | 0x0 | output | - | - |

### INT_STS

- **Offset**: 0x00C
- **Width**: 1 bits
- **Reset**: 0x00000000
- **Access**: RW

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| OVERRUN | [0:0] | 1 | W1C | 0x0 | input | - | Write-1-to-clear; hw sets |

### DMA_CTRL

- **Offset**: 0x010
- **Width**: 16 bits
- **Reset**: 0x00000000
- **Access**: RW

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| START | [0:0] | 1 | RS | 0x0 | output | - | Set on read |
| RSVD | [7:1] | 7 | RO | 0x0 | - | - | - |
| LEN | [15:8] | 8 | RW | 0x0 | output | - | - |

### ERR_STS

- **Offset**: 0x014
- **Width**: 2 bits
- **Reset**: 0x00000003
- **Access**: RO

| Field | Bits | Width | Access | Reset | HW Interface | Description | Side Effect |
|-------|------|-------|--------|-------|--------------|-------------|-------------|
| PARITY | [0:0] | 1 | RC | 0x1 | input | - | Clear on read |
| CRC_ERR | [1:1] | 1 | RC | 0x1 | input | - | Clear on read |
