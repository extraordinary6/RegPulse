# RegPulse

RegPulse generates bus-agnostic register file cores, optional bus protocol wrappers, and UVM RAL models from Excel register specifications.

## Features

- Excel-driven workflow: define registers in `.xlsx`, then generate RTL and verification artifacts
- Bus-agnostic register core with generic `clk/rst_n/addr/wdata/wen/wstrb/ren/rdata/ready` interface
- Optional APB4, AHB-Lite, and AXI4-Lite wrappers
- Data-width aware generation for 8/16/32/64-bit register banks
- Byte-strobe masking for sub-word writes
- UVM RAL output with backdoor path mapping
- Verilog, SystemVerilog, C header, JSON, Markdown, and HTML outputs
- Structural validation plus optional advisory lint checks
- Access types: `RW`, `RO`, `WO`, `W1C`, `W1S`, `W0C`, `RC`, `RS`
- Hardware sideband ports and interrupt aggregation support

## Quick Start

Common ways to run RegPulse:

- From a source checkout: `python main.py ...`
- After installation: `regpulse ...`

```bash
# Install dependencies
pip install pandas openpyxl jinja2

# Generate register core + all default formats
python main.py --input_excel spec.xlsx --output_dir ./output

# Generate with a bus wrapper
python main.py --input_excel spec.xlsx --output_dir ./output --bus apb
python main.py --input_excel spec.xlsx --output_dir ./output --bus ahb
python main.py --input_excel spec.xlsx --output_dir ./output --bus axi

# Generate selected formats only
python main.py --input_excel spec.xlsx --output_dir ./output --format rtl,uvm,c_header

# Parse + validate only
python main.py --input_excel spec.xlsx --output_dir ./output --dry_run

# Run advisory lint checks
python main.py --input_excel spec.xlsx --output_dir ./output --lint

# Generate a blank Excel template
python main.py --input_excel template.xlsx --output_dir ./output --template_excel
```

## Architecture

RegPulse separates register logic from bus protocol:

```text
chip_regs_{apb,ahb,axi}_wrapper  ->  bus protocol to generic interface bridge
chip_regs_regfile_core           ->  bus-agnostic register file
```

- `regfile_core`: always generated, contains register logic, sideband ports, and interrupt aggregation
- `bus_wrapper`: optional, maps the selected bus to the generic core interface

## Excel Specification Format

Required columns:

| Column | Description |
|--------|-------------|
| `Name` | Register name |
| `Offset` | Byte offset, for example `0x000` or `0x004` |
| `Field` | Field name within the register |
| `Bits` | Bit position, for example `"0"` or `"3:1"` |
| `Access` | `RW`, `RO`, `WO`, `W1C`, `W1S`, `W0C`, `RC`, `RS` |
| `Reset` | Reset value |

Optional columns:

- `Description`
- `Hardware Trigger` with values `input` or `output`
- `Side Effect`
- `Interrupt` with values `source` or `enable`

## Output Files

| File | Description |
|------|-------------|
| `{name}_regfile_core.v` | Bus-agnostic register file core |
| `{name}_apb_wrapper.v` | APB4 wrapper |
| `{name}_ahb_wrapper.v` | AHB-Lite wrapper |
| `{name}_axi_wrapper.v` | AXI4-Lite wrapper |
| `{name}_reg_block.sv` | UVM RAL model |
| `{name}.h` | C header |
| `{name}.json` | Machine-readable register map |
| `{name}.md` | Markdown documentation |
| `{name}.html` | HTML documentation |

## CLI Reference

Use either form:

```text
python main.py --input_excel <file> --output_dir <dir> [options]
regpulse --input_excel <file> --output_dir <dir> [options]

Required:
  --input_excel FILE     Input .xlsx register specification
  --output_dir DIR       Output directory

Optional:
  --block_name NAME         Module/block name (default: reg_top)
  --base_address ADDR       Base address, e.g. 0x8000_0000 (default: 0x0)
  --block_size ADDR         Optional declared block size for lint checks
  --data_width N            Data width: 8, 16, 32, or 64 (default: 32)
  --bus {none,apb,ahb,axi}  Bus protocol wrapper (default: none)
  --format FMTS             Comma-separated formats: rtl,uvm,c_header,json,html,markdown
  --rtl_only                Shorthand for --format rtl
  --uvm_only                Shorthand for --format uvm
  --template_excel          Generate blank Excel template and exit
  --dry_run                 Parse and validate only
  --lint                    Run advisory lint checks and print findings
  --lint_strict             Treat warning-level lint findings as failures
  --verbose                 Enable debug logging
  --version                 Show version
```

## Project Structure

```text
Register/
├── src/
│   ├── models/          # Field, Register, RegisterBank data models
│   ├── parser/          # Excel parser
│   ├── validators/      # Structural validation
│   ├── generators/      # RTL, wrappers, UVM, C header, JSON, Markdown, HTML
│   ├── lint/            # Advisory lint rules and reporting
│   └── templates/       # Jinja2 templates
├── main.py              # Command-line entrypoint
├── tests/               # Pytest test suite
├── output/              # Example generated output
└── pyproject.toml
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
