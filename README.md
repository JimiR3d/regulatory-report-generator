# Regulatory Report Generator

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

A Python CLI tool that takes structured CSV financial data, validates it, and generates formatted PDF reports matching the style of CBN (Central Bank of Nigeria) monthly prudential returns. Also outputs a summary JSON for programmatic use.

Feed it raw bank metrics. Get back a publication-ready regulatory report.

## Who this is for

Nigerian bank compliance officers, regulatory reporting teams, fintech data engineers, and anyone who currently builds CBN prudential returns manually in Excel.

## How it works

```bash
python generate_report.py \
  --input data/bank_metrics.csv \
  --output reports/june_2026.pdf \
  --bank "First Continental Bank"
```

1. **Reads** a structured CSV of financial metrics
2. **Validates** the data — checks for missing fields, out-of-range values, and formatting issues
3. **Renders** a formatted PDF report using HTML templates styled to match CBN monthly prudential returns
4. **Exports** a summary JSON alongside the PDF for programmatic downstream use

## Tech stack

- **Python** — core logic
- **Pandas** — data processing and validation
- **Click** — CLI framework
- **Jinja2** — HTML report templating
- **WeasyPrint** — HTML → PDF rendering

## How to run locally

```bash
# Clone the repo
git clone https://github.com/JimiR3d/regulatory-report-generator.git
cd regulatory-report-generator

# Install dependencies
pip install -r requirements.txt

# Generate a sample report
python generate_report.py --input data/sample_input.csv --output reports/sample.pdf --bank "First Continental Bank"
```

## Sample output

Check [`examples/sample_output.pdf`](examples/sample_output.pdf) to see what the generated report looks like — no setup required.

## Project structure

```
regulatory-report-generator/
├── generate_report.py      # CLI entry point
├── validator.py            # Input data validation
├── renderer.py             # Jinja2 → HTML → PDF logic
├── templates/
│   └── cbn_report.html     # Report HTML template
├── data/
│   └── sample_input.csv    # Sample input data
├── examples/
│   └── sample_output.pdf   # Pre-generated example output
├── requirements.txt
└── README.md
```

## Context

Built by [Jimi Aboderin](https://github.com/JimiR3d) — a data analyst who previously automated Basel III compliance reporting pipelines for a Nigerian bank at Qucoon. This is a clean-room rebuild demonstrating the same competency with simulated data.

## License

MIT
