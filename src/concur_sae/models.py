from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class SaeRecord:
    batch_id: str
    row_id: str
    employee_id: str
    report_key: str
    transaction_date: date
    account: str
    company: str
    branch: str
    department: str
    debit_credit: str
    amount: Decimal
    description: str
    currency: str


@dataclass(frozen=True)
class JournalLine:
    journal_id: str
    batch_id: str
    source_row_id: str
    transaction_date: date
    employee_reference: str
    account: str
    company: str
    branch: str
    department: str
    debit_credit: str
    amount: Decimal
    description: str
    currency: str


@dataclass(frozen=True)
class QuarantineRecord:
    row_number: int
    error_code: str
    reason: str
    raw_row: dict[str, str]


@dataclass(frozen=True)
class RunSummary:
    input_file: str
    checksum: str
    input_rows: int
    valid_rows: int
    quarantined_rows: int
    source_total: Decimal
    debit_total: Decimal
    credit_total: Decimal
    difference: Decimal
    status: str
    processed_at: datetime


@dataclass(frozen=True)
class ProcessResult:
    status: str
    message: str
    summary: RunSummary | None = None
