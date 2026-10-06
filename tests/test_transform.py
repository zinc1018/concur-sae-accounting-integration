from datetime import date
from decimal import Decimal

from concur_sae.transform import parse_record, reconcile, to_journal_line
from concur_sae.models import JournalLine, QuarantineRecord, SaeRecord


def valid_row() -> dict[str, str]:
    return {
        "batch_id": "B-100",
        "row_id": "7",
        "employee_id": "E-42",
        "report_key": "R-9",
        "transaction_date": "2026-10-05",
        "account": "6100",
        "company": "100",
        "branch": "TOR",
        "department": "OPS",
        "debit_credit": "DR",
        "amount": "125.50",
        "description": "Fuel",
        "currency": "CAD",
    }


def test_parse_record_and_normalize_valid_row():
    parsed = parse_record(valid_row(), row_number=2)

    assert isinstance(parsed, SaeRecord)
    assert parsed.transaction_date == date(2026, 10, 5)
    assert to_journal_line(parsed).journal_id == "B-100:7"


def test_parse_record_quarantines_malformed_amount():
    row = valid_row()
    row["amount"] = "not-a-number"

    result = parse_record(row, row_number=4)

    assert isinstance(result, QuarantineRecord)
    assert result.error_code == "INVALID_AMOUNT"


def test_parse_record_quarantines_unsupported_debit_credit_code():
    row = valid_row()
    row["debit_credit"] = "XX"

    result = parse_record(row, row_number=5)

    assert isinstance(result, QuarantineRecord)
    assert result.error_code == "INVALID_DEBIT_CREDIT"


def test_reconcile_reports_unbalanced_journal():
    line = JournalLine(
        journal_id="B-100:7",
        batch_id="B-100",
        source_row_id="7",
        transaction_date=date(2026, 10, 5),
        employee_reference="E-42",
        account="6100",
        company="100",
        branch="TOR",
        department="OPS",
        debit_credit="DR",
        amount=Decimal("125.50"),
        description="Fuel",
        currency="CAD",
    )

    debit, credit, difference = reconcile([line], Decimal("125.50"))

    assert debit == Decimal("125.50")
    assert credit == Decimal("0.00")
    assert difference == Decimal("125.50")
