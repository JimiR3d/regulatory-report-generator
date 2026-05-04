"""
CBN Report Data Validator

Validates financial return data against Central Bank of Nigeria (CBN)
regulatory reporting rules before report generation.

Checks:
    - Required fields present
    - Numeric ranges and signs
    - Cross-field consistency (e.g., CET1 <= Tier 1 Capital)
    - Date format compliance
"""

from datetime import datetime


# ── Required fields for CBN Capital Adequacy Return ──────────────────
REQUIRED_FIELDS = [
    "bank_name",
    "report_date",
    "cet1_capital",
    "additional_tier1",
    "tier2_capital",
    "total_rwa",
    "credit_rwa",
    "market_rwa",
    "operational_rwa",
]

# ── CBN regulatory thresholds ────────────────────────────────────────
CBN_THRESHOLDS = {
    "d_sib": {  # Domestic Systemically Important Banks
        "cet1_ratio": 7.0,
        "tier1_ratio": 8.5,
        "total_car": 15.0,
    },
    "non_d_sib": {  # Other commercial banks
        "cet1_ratio": 5.0,
        "tier1_ratio": 6.5,
        "total_car": 10.0,
    },
}


class ValidationError:
    """Represents a single validation error."""
    def __init__(self, field, message, severity="ERROR"):
        self.field = field
        self.message = message
        self.severity = severity  # ERROR, WARNING, INFO

    def __repr__(self):
        return f"[{self.severity}] {self.field}: {self.message}"


def validate_return_data(data, bank_type="non_d_sib"):
    """
    Validate a dictionary of CBN return data.

    Args:
        data: dict with bank financial data
        bank_type: "d_sib" or "non_d_sib"

    Returns:
        tuple: (is_valid: bool, errors: list[ValidationError])
    """
    errors = []

    # 1. Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(ValidationError(
                field, f"Required field '{field}' is missing"
            ))

    if errors:
        return False, errors  # Can't continue without required fields

    # 2. Validate report_date format
    try:
        report_date = datetime.strptime(data["report_date"], "%Y-%m-%d")
        if report_date > datetime.now():
            errors.append(ValidationError(
                "report_date", "Report date cannot be in the future",
                severity="WARNING"
            ))
    except (ValueError, TypeError):
        errors.append(ValidationError(
            "report_date",
            "Invalid date format. Expected YYYY-MM-DD"
        ))

    # 3. Validate numeric fields are positive
    numeric_fields = [
        "cet1_capital", "total_rwa", "credit_rwa",
        "market_rwa", "operational_rwa"
    ]
    for field in numeric_fields:
        val = data.get(field)
        if val is not None:
            try:
                val = float(val)
                if val < 0:
                    errors.append(ValidationError(
                        field, f"Value cannot be negative: {val}"
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    field, f"Must be a number, got: {val}"
                ))

    # 4. Validate RWA components sum
    try:
        credit = float(data.get("credit_rwa", 0))
        market = float(data.get("market_rwa", 0))
        operational = float(data.get("operational_rwa", 0))
        total = float(data.get("total_rwa", 0))

        component_sum = credit + market + operational
        tolerance = total * 0.01  # 1% tolerance

        if abs(component_sum - total) > tolerance:
            errors.append(ValidationError(
                "total_rwa",
                f"RWA components ({component_sum:,.0f}) don't sum to "
                f"total_rwa ({total:,.0f}). Diff: {abs(component_sum - total):,.0f}",
                severity="WARNING"
            ))
    except (ValueError, TypeError):
        pass  # Already caught above

    # 5. Validate capital hierarchy (CET1 <= Tier1 <= Total)
    try:
        cet1 = float(data.get("cet1_capital", 0))
        at1 = float(data.get("additional_tier1", 0))
        t2 = float(data.get("tier2_capital", 0))

        tier1 = cet1 + at1
        total_capital = tier1 + t2

        if cet1 > tier1:
            errors.append(ValidationError(
                "cet1_capital",
                "CET1 capital cannot exceed Tier 1 capital"
            ))

        # Check ratios against CBN thresholds
        total_rwa = float(data.get("total_rwa", 1))
        if total_rwa > 0:
            thresholds = CBN_THRESHOLDS.get(bank_type, CBN_THRESHOLDS["non_d_sib"])

            cet1_ratio = (cet1 / total_rwa) * 100
            tier1_ratio = (tier1 / total_rwa) * 100
            total_ratio = (total_capital / total_rwa) * 100

            if cet1_ratio < thresholds["cet1_ratio"]:
                errors.append(ValidationError(
                    "cet1_ratio",
                    f"CET1 ratio ({cet1_ratio:.2f}%) below CBN minimum "
                    f"({thresholds['cet1_ratio']}%)",
                    severity="WARNING"
                ))

            if tier1_ratio < thresholds["tier1_ratio"]:
                errors.append(ValidationError(
                    "tier1_ratio",
                    f"Tier 1 ratio ({tier1_ratio:.2f}%) below CBN minimum "
                    f"({thresholds['tier1_ratio']}%)",
                    severity="WARNING"
                ))

            if total_ratio < thresholds["total_car"]:
                errors.append(ValidationError(
                    "total_car",
                    f"Total CAR ({total_ratio:.2f}%) below CBN minimum "
                    f"({thresholds['total_car']}%)",
                    severity="WARNING"
                ))
    except (ValueError, TypeError):
        pass

    # 6. Bank name validation
    bank_name = data.get("bank_name", "")
    if len(str(bank_name).strip()) < 3:
        errors.append(ValidationError(
            "bank_name", "Bank name must be at least 3 characters"
        ))

    is_valid = not any(e.severity == "ERROR" for e in errors)
    return is_valid, errors


def print_validation_report(is_valid, errors):
    """Pretty-print validation results."""
    print("\n── Validation Report ──")
    if is_valid and not errors:
        print("✓ All checks passed. Data is valid for report generation.")
    elif is_valid:
        print("✓ Data passes required checks (with warnings).\n")
        for e in errors:
            print(f"  ⚠ {e}")
    else:
        print("✗ Validation failed. Fix the following errors:\n")
        for e in errors:
            icon = "✗" if e.severity == "ERROR" else "⚠"
            print(f"  {icon} {e}")
    print()
