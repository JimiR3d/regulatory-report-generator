# 📋 Regulatory Report Generator

CLI tool that validates Nigerian bank financial data against CBN (Central Bank of Nigeria) regulatory rules and generates compliant Capital Adequacy Returns in PDF and HTML formats.

---

## Architecture

```
data/sample_return.json   →  cli.py validate   →  Validation report
                              cli.py generate   →  validator.py → report_engine.py
                                                         ↓
                                                  templates/car_report.html (Jinja2)
                                                         ↓
                                                  output/car_report.pdf
                                                  output/car_report.html
```

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| CLI | argparse | `validate` and `generate` commands |
| Validation | Custom Python | 6 rule categories, CBN threshold checks |
| Templates | Jinja2 | HTML report rendering |
| PDF | ReportLab | Styled tables, compliance badges |
| CI | GitHub Actions | Flake8 linting |

## Key Features

### Data Validator (`validator.py`)
- 9 required field checks
- Date format validation
- Numeric range and sign checks
- RWA component sum verification (1% tolerance)
- Capital hierarchy validation (CET1 ≤ Tier 1 ≤ Total)
- CBN ratio threshold checks (D-SIB vs non-D-SIB banks)
- Error severity levels (ERROR, WARNING, INFO)

### Report Engine (`report_engine.py`)
- **PDF output:** Professionally styled with Navy/Teal color scheme, 3-section layout (Capital Structure, RWA Breakdown, Compliance Status)
- **HTML output:** Jinja2-templated, Inter font, responsive design
- Compliance status badges (✓ Compliant / ✗ BREACH)
- Naira-denominated formatting (₦'000)

### CLI (`cli.py`)
```bash
# Validate data only
python cli.py validate --input data/sample_return.json

# Generate PDF report
python cli.py generate --input data/sample_return.json --format pdf

# Generate HTML report for D-SIB bank
python cli.py generate -i data/sample_return.json -f html --bank-type d_sib
```

## Quick Start

```bash
pip install -r requirements.txt

# Validate sample data
python cli.py validate --input data/sample_return.json

# Generate PDF report
python cli.py generate --input data/sample_return.json --format pdf
# Opens: output/car_report.pdf
```

## Input Format

```json
{
    "bank_name": "First Continental Bank Nigeria Plc",
    "report_date": "2025-03-31",
    "cet1_capital": 485000000,
    "additional_tier1": 35000000,
    "tier2_capital": 120000000,
    "total_rwa": 3200000000,
    "credit_rwa": 2560000000,
    "market_rwa": 320000000,
    "operational_rwa": 320000000
}
```

## CBN Thresholds

| Ratio | Non-D-SIB | D-SIB |
|-------|-----------|-------|
| CET1 | ≥ 5.0% | ≥ 7.0% |
| Tier 1 | ≥ 6.5% | ≥ 8.5% |
| Total CAR | ≥ 10.0% | ≥ 15.0% |

## Project Context

This project demonstrates:
- **RegTech development** — Automated regulatory compliance tooling
- **Data validation** — Multi-rule validation engine with severity levels
- **Report generation** — Jinja2 templating + PDF generation
- **CLI design** — Composable subcommand architecture

Built as part of my data analyst portfolio. All data is simulated; no proprietary information.

## Author

**Jimi Aboderin**  
[LinkedIn](https://www.linkedin.com/in/oluwafolajinmi-aboderin-695848249/) · [GitHub](https://github.com/JimiR3d) · folajinmi13@gmail.com
