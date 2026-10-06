from datetime import date
from decimal import Decimal

from concur_sae.models import JournalLine, QuarantineRecord, SaeRecord


def test_sae_record_carries_source_accounting_fields():
    record = SaeRecord(
        batch_id="B-100",
        row_id="7",
        employee_id="E-42",
        report_key="R-9",
        transaction_date=date(2026, 10, 5),
        account="6100",
        company="100",
        branch="TOR",
        department="OPS",
        debit_credit="DR",
        amount=Decimal("125.50"),
        description="Fuel",
        currency="CAD",
    )

    assert record.amount == Decimal("125.50")
    assert record.debit_credit == "DR"


def test_journal_line_and_quarantine_record_are_serializable_dataclasses():
    journal = JournalLine(
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
    quarantine = QuarantineRecord(
        row_number=3,
        error_code="INVALID_AMOUNT",
        reason="Amount is not numeric",
        raw_row={"amount": "bad"},
    )

    assert journal.journal_id == "B-100:7"
    assert quarantine.error_code == "INVALID_AMOUNT"
