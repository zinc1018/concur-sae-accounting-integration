# Concur SAE Accounting Pipeline Implementation Plan

**Goal:** Build a sanitized, runnable Python reference pipeline that ingests a pipe-delimited Concur SAE-style file and produces idempotent, validated, reconciled, ERP-neutral journal output.

**Architecture:** A small standard-library Python package will separate file hashing/manifest tracking, parsing and validation, journal normalization, and output reporting. SQLite will store file-processing state; CSV and JSON outputs will make the run inspectable without an external accounting system.

**Tech Stack:** Python 3.12+, standard library, SQLite, pytest, Docker, GitHub Actions.

**Spec:** `docs/design.md`

## Global Constraints

- No employer names, internal database names, internal file paths, credentials, private keys, customer data, or proprietary field mappings.
- The demo must not connect to a live Concur tenant, SFTP server, ERP, or cloud account.
- A duplicate successful file must not create a second journal export.
- Invalid records must be quarantined with a stable error code and readable reason.
- Output must use an accounting-system-neutral journal model.
- The demo must report source totals, debit totals, credit totals, difference, and final status.

## Review Focus

- Duplicate input file: return an explicit duplicate result and do not append journal rows.
- Malformed numeric amount: quarantine the row rather than aborting the entire file.
- Unsupported debit/credit code: quarantine with a stable validation code.
- Unbalanced journal: fail reconciliation and report the difference.
- Repeated execution after success: remain idempotent and preserve the original manifest result.

---

### Task 1: Project scaffold and domain models

**Files:**
- Create: `pyproject.toml`
- Create: `src/concur_sae/__init__.py`
- Create: `src/concur_sae/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces dataclasses `SaeRecord`, `JournalLine`, `QuarantineRecord`, `RunSummary`, and `ProcessResult` for later tasks.

- [ ] **Step 1: Write the failing tests** for model construction and serialization-friendly fields in `tests/test_models.py`.
- [ ] **Step 2: Run `python -m pytest tests/test_models.py -q` and verify failure because the package/models do not exist.**
- [ ] **Step 3: Implement typed dataclasses and minimal package exports.**
- [ ] **Step 4: Run the focused tests and verify they pass.**
- [ ] **Step 5: Commit as `feat: add pipeline domain models`.**

### Task 2: Validation, normalization, and reconciliation

**Files:**
- Create: `src/concur_sae/transform.py`
- Test: `tests/test_transform.py`

**Interfaces:**
- Consumes: `SaeRecord` from `models.py`.
- Produces: `parse_record(row: dict[str, str], row_number: int) -> SaeRecord | QuarantineRecord`, `to_journal_line(record: SaeRecord) -> JournalLine`, and `reconcile(lines: list[JournalLine], source_total: Decimal) -> tuple[Decimal, Decimal, Decimal]`.

- [ ] **Step 1: Write failing tests** for valid conversion, malformed amount quarantine, unsupported debit/credit quarantine, and unbalanced reconciliation.
- [ ] **Step 2: Run `python -m pytest tests/test_transform.py -q` and verify expected failures.**
- [ ] **Step 3: Implement minimal parsing, validation, normalization, and reconciliation functions using `Decimal`.**
- [ ] **Step 4: Run the focused tests and verify they pass.**
- [ ] **Step 5: Commit as `feat: add SAE validation and journal normalization`.**

### Task 3: Idempotent file pipeline and SQLite manifest

**Files:**
- Create: `src/concur_sae/pipeline.py`
- Create: `src/concur_sae/store.py`
- Test: `tests/test_pipeline.py`
- Create: `tests/fixtures/valid_sae.txt`
- Create: `tests/fixtures/invalid_sae.txt`

**Interfaces:**
- Consumes: transform functions from `transform.py` and domain models from `models.py`.
- Produces: `run_file(input_path: Path, output_dir: Path, db_path: Path) -> ProcessResult`.

- [ ] **Step 1: Write failing tests** for successful output, quarantine output, duplicate detection, and repeated successful execution.
- [ ] **Step 2: Run `python -m pytest tests/test_pipeline.py -q` and verify expected failures.**
- [ ] **Step 3: Implement SQLite manifest tables, SHA-256 tracking, pipe-delimited reading, output CSV/JSON writing, and idempotent status handling.**
- [ ] **Step 4: Run the focused tests and verify they pass.**
- [ ] **Step 5: Commit as `feat: add idempotent file processing pipeline`.**

### Task 4: CLI, sample data, documentation, and CI

**Files:**
- Create: `src/concur_sae/cli.py`
- Create: `fixtures/incoming/sample_sae.txt`
- Create: `Dockerfile`
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `run_file` from `pipeline.py`.
- Produces: `python -m concur_sae.cli --input ... --output-dir ... --db ...` command with JSON result and non-zero exit on failed reconciliation or processing error.

- [ ] **Step 1: Write failing CLI test** for a sample run producing a summary and output files.
- [ ] **Step 2: Run `python -m pytest tests/test_cli.py -q` and verify expected failure.**
- [ ] **Step 3: Implement CLI, sample fixture, Docker execution, CI workflow, and portfolio-oriented README.**
- [ ] **Step 4: Run the focused CLI test and verify it passes.**
- [ ] **Step 5: Run the full suite with `python -m pytest -q`.**
- [ ] **Step 6: Commit as `feat: add runnable CLI and portfolio documentation`.**

### Task 5: Final verification

**Files:**
- Modify: documentation or code only if verification exposes a required defect.

- [ ] **Step 1: Run `python -m pytest -q`.**
- [ ] **Step 2: Run the sample CLI command from the README.**
- [ ] **Step 3: Build the Docker image if Docker is available.**
- [ ] **Step 4: Review `git diff --check` and confirm no secrets or employer-specific identifiers are present.**
- [ ] **Step 5: Commit any verification-only fixes and prepare the repository for push.**
