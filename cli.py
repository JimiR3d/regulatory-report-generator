"""
CLI Interface for Regulatory Report Generator

Usage:
    python cli.py validate --input data/sample_return.json
    python cli.py generate --input data/sample_return.json --format pdf
    python cli.py generate --input data/sample_return.json --format html
"""

import argparse
import json
import sys
import os

from validator import validate_return_data, print_validation_report
from report_engine import render_html_report, generate_pdf_report


def load_input(filepath):
    """Load JSON input file."""
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def cmd_validate(args):
    """Run validation on input data."""
    data = load_input(args.input)
    bank_type = args.bank_type or "non_d_sib"

    print(f"\n── Validating: {args.input} ──")
    print(f"   Bank type: {bank_type}")

    is_valid, errors = validate_return_data(data, bank_type=bank_type)
    print_validation_report(is_valid, errors)

    return 0 if is_valid else 1


def cmd_generate(args):
    """Validate and generate report."""
    data = load_input(args.input)
    bank_type = args.bank_type or "non_d_sib"

    # Validate first
    print(f"\n── Validating data ──")
    is_valid, errors = validate_return_data(data, bank_type=bank_type)
    print_validation_report(is_valid, errors)

    if not is_valid:
        print("✗ Cannot generate report: validation errors exist.")
        return 1

    # Generate report
    fmt = args.format or "pdf"
    output = args.output

    print(f"── Generating {fmt.upper()} report ──")

    if fmt == "pdf":
        output = output or "output/car_report.pdf"
        generate_pdf_report(data, output_path=output)
    elif fmt == "html":
        output = output or "output/car_report.html"
        render_html_report(data, output_path=output)
    else:
        print(f"✗ Unknown format: {fmt}. Use 'pdf' or 'html'.")
        return 1

    print(f"\n✓ Report generated successfully: {output}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="CBN Regulatory Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py validate --input data/sample_return.json
  python cli.py generate --input data/sample_return.json --format pdf
  python cli.py generate --input data/sample_return.json --format html
  python cli.py generate --input data/sample_return.json --format pdf --bank-type d_sib
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate subcommand
    val_parser = subparsers.add_parser("validate", help="Validate input data")
    val_parser.add_argument("--input", "-i", required=True, help="Path to JSON input file")
    val_parser.add_argument("--bank-type", choices=["d_sib", "non_d_sib"],
                            default="non_d_sib", help="Bank classification (default: non_d_sib)")

    # Generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate regulatory report")
    gen_parser.add_argument("--input", "-i", required=True, help="Path to JSON input file")
    gen_parser.add_argument("--format", "-f", choices=["pdf", "html"],
                            default="pdf", help="Output format (default: pdf)")
    gen_parser.add_argument("--output", "-o", help="Output file path")
    gen_parser.add_argument("--bank-type", choices=["d_sib", "non_d_sib"],
                            default="non_d_sib", help="Bank classification (default: non_d_sib)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "generate":
        return cmd_generate(args)


if __name__ == "__main__":
    sys.exit(main())
