import json
import shutil
from pathlib import Path

from concur_sae.pipeline import run_file


FIXTURES = Path(__file__).parent / "fixtures"


def test_run_file_writes_journal_and_summary(tmp_path: Path):
    result = run_file(FIXTURES / "valid_sae.txt", tmp_path / "out", tmp_path / "manifest.sqlite3")

    assert result.status == "COMPLETED"
    assert result.summary is not None
    assert result.summary.valid_rows == 2
    assert result.summary.quarantined_rows == 0
    assert (tmp_path / "out" / "journal.csv").exists()
    assert json.loads((tmp_path / "out" / "run-summary.json").read_text())["status"] == "COMPLETED"


def test_run_file_quarantines_invalid_rows(tmp_path: Path):
    result = run_file(FIXTURES / "invalid_sae.txt", tmp_path / "out", tmp_path / "manifest.sqlite3")

    assert result.status == "COMPLETED_WITH_QUARANTINE"
    assert result.summary is not None
    assert result.summary.quarantined_rows == 1
    quarantine = (tmp_path / "out" / "quarantine.csv").read_text()
    assert "INVALID_DEBIT_CREDIT" in quarantine


def test_run_file_rejects_duplicate_successful_file(tmp_path: Path):
    input_path = tmp_path / "input.txt"
    shutil.copy(FIXTURES / "valid_sae.txt", input_path)
    output_dir = tmp_path / "out"
    db_path = tmp_path / "manifest.sqlite3"

    first = run_file(input_path, output_dir, db_path)
    second = run_file(input_path, output_dir, db_path)

    assert first.status == "COMPLETED"
    assert second.status == "DUPLICATE"
    assert "already processed" in second.message


def test_repeated_successful_execution_does_not_append_journal_rows(tmp_path: Path):
    input_path = tmp_path / "input.txt"
    shutil.copy(FIXTURES / "valid_sae.txt", input_path)
    output_dir = tmp_path / "out"
    db_path = tmp_path / "manifest.sqlite3"

    run_file(input_path, output_dir, db_path)
    journal_before = (output_dir / "journal.csv").read_text()
    run_file(input_path, output_dir, db_path)

    assert (output_dir / "journal.csv").read_text() == journal_before


def test_repeated_quarantined_execution_is_also_idempotent(tmp_path: Path):
    input_path = tmp_path / "input.txt"
    shutil.copy(FIXTURES / "invalid_sae.txt", input_path)
    output_dir = tmp_path / "out"
    db_path = tmp_path / "manifest.sqlite3"

    first = run_file(input_path, output_dir, db_path)
    second = run_file(input_path, output_dir, db_path)

    assert first.status == "COMPLETED_WITH_QUARANTINE"
    assert second.status == "DUPLICATE"
