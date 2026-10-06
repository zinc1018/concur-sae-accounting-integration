import csv
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .models import JournalLine, ProcessResult, QuarantineRecord, RunSummary
from .store import find_success, initialize, record_result
from .transform import parse_record, reconcile, to_journal_line


def _checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_journal(path: Path, lines: list[JournalLine]) -> None:
    fields = [
        "journal_id", "batch_id", "source_row_id", "transaction_date",
        "employee_reference", "account", "company", "branch", "department",
        "debit_credit", "amount", "description", "currency",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for line in lines:
            row = asdict(line)
            row["transaction_date"] = line.transaction_date.isoformat()
            row["amount"] = f"{line.amount:.2f}"
            writer.writerow(row)


def _write_quarantine(path: Path, rows: list[QuarantineRecord]) -> None:
    fields = ["row_number", "error_code", "reason", "raw_row"]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "row_number": row.row_number,
                "error_code": row.error_code,
                "reason": row.reason,
                "raw_row": json.dumps(row.raw_row, sort_keys=True),
            })


def _summary_dict(summary: RunSummary) -> dict[str, object]:
    result = asdict(summary)
    result["source_total"] = f"{summary.source_total:.2f}"
    result["debit_total"] = f"{summary.debit_total:.2f}"
    result["credit_total"] = f"{summary.credit_total:.2f}"
    result["difference"] = f"{summary.difference:.2f}"
    result["processed_at"] = summary.processed_at.isoformat()
    return result


def run_file(input_path: Path, output_dir: Path, db_path: Path) -> ProcessResult:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    db_path = Path(db_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    initialize(str(db_path))
    checksum = _checksum(input_path)

    if find_success(str(db_path), checksum):
        return ProcessResult("DUPLICATE", f"File {input_path.name} was already processed successfully")

    journal_lines: list[JournalLine] = []
    quarantined: list[QuarantineRecord] = []
    source_total = Decimal("0.00")
    with input_path.open(newline="", encoding="utf-8") as source:
        for row_number, row in enumerate(csv.DictReader(source, delimiter="|"), start=2):
            parsed = parse_record(dict(row), row_number)
            if isinstance(parsed, QuarantineRecord):
                quarantined.append(parsed)
                continue
            source_total += parsed.amount
            journal_lines.append(to_journal_line(parsed))

    debit_total, credit_total, difference = reconcile(journal_lines, source_total)
    status = "COMPLETED_WITH_QUARANTINE" if quarantined else "COMPLETED"
    if difference != Decimal("0.00"):
        status = "FAILED_RECONCILIATION"

    summary = RunSummary(
        input_file=input_path.name,
        checksum=checksum,
        input_rows=len(journal_lines) + len(quarantined),
        valid_rows=len(journal_lines),
        quarantined_rows=len(quarantined),
        source_total=source_total,
        debit_total=debit_total,
        credit_total=credit_total,
        difference=difference,
        status=status,
        processed_at=datetime.now(timezone.utc),
    )
    _write_journal(output_dir / "journal.csv", journal_lines)
    _write_quarantine(output_dir / "quarantine.csv", quarantined)
    (output_dir / "run-summary.json").write_text(json.dumps(_summary_dict(summary), indent=2) + "\n", encoding="utf-8")
    record_result(str(db_path), checksum, input_path.name, status, "File processed")
    return ProcessResult(status, "File processed", summary)
