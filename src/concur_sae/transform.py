from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .models import JournalLine, QuarantineRecord, SaeRecord


REQUIRED_FIELDS = (
    "batch_id",
    "row_id",
    "employee_id",
    "report_key",
    "transaction_date",
    "account",
    "company",
    "branch",
    "department",
    "debit_credit",
    "amount",
    "description",
    "currency",
)


def _quarantine(row: dict[str, str], row_number: int, code: str, reason: str) -> QuarantineRecord:
    return QuarantineRecord(row_number=row_number, error_code=code, reason=reason, raw_row=row)


def parse_record(row: dict[str, str], row_number: int) -> SaeRecord | QuarantineRecord:
    for field in REQUIRED_FIELDS:
        if not (row.get(field) or "").strip():
            return _quarantine(row, row_number, "MISSING_REQUIRED_FIELD", f"Missing required field: {field}")

    try:
        transaction_date = date.fromisoformat(row["transaction_date"].strip())
    except ValueError:
        return _quarantine(row, row_number, "INVALID_DATE", "Transaction date must use YYYY-MM-DD")

    try:
        amount = Decimal(row["amount"].strip()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return _quarantine(row, row_number, "INVALID_AMOUNT", "Amount must be numeric")

    if amount < 0:
        return _quarantine(row, row_number, "INVALID_AMOUNT", "Amount cannot be negative")

    debit_credit = row["debit_credit"].strip().upper()
    if debit_credit not in {"DR", "CR"}:
        return _quarantine(row, row_number, "INVALID_DEBIT_CREDIT", "Debit/credit code must be DR or CR")

    return SaeRecord(
        batch_id=row["batch_id"].strip(),
        row_id=row["row_id"].strip(),
        employee_id=row["employee_id"].strip(),
        report_key=row["report_key"].strip(),
        transaction_date=transaction_date,
        account=row["account"].strip(),
        company=row["company"].strip(),
        branch=row["branch"].strip(),
        department=row["department"].strip(),
        debit_credit=debit_credit,
        amount=amount,
        description=row["description"].strip(),
        currency=row["currency"].strip().upper(),
    )


def to_journal_line(record: SaeRecord) -> JournalLine:
    return JournalLine(
        journal_id=f"{record.batch_id}:{record.row_id}",
        batch_id=record.batch_id,
        source_row_id=record.row_id,
        transaction_date=record.transaction_date,
        employee_reference=record.employee_id,
        account=record.account,
        company=record.company,
        branch=record.branch,
        department=record.department,
        debit_credit=record.debit_credit,
        amount=record.amount,
        description=record.description,
        currency=record.currency,
    )


def reconcile(lines: list[JournalLine], source_total: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    del source_total
    debit_total = sum((line.amount for line in lines if line.debit_credit == "DR"), Decimal("0.00"))
    credit_total = sum((line.amount for line in lines if line.debit_credit == "CR"), Decimal("0.00"))
    difference = (debit_total - credit_total).quantize(Decimal("0.01"))
    return debit_total, credit_total, difference
