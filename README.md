# Concur SAE Accounting Integration

Sanitized reference implementation for processing a SAP Concur Standard Accounting Extract (SAE)-style file and producing an ERP-neutral accounting journal.

This project is informed by experience maintaining Concur SAE integrations across multiple organizations. It contains no employer names, production paths, credentials, private keys, customer data, or proprietary accounting mappings.

## What it demonstrates

- Pipe-delimited SAE-style file ingestion
- SHA-256 file identity and SQLite processing manifest
- Idempotent duplicate-file handling
- Decimal-safe accounting amounts
- Required-field, date, amount, and debit/credit validation
- Quarantine output with stable error codes
- ERP-neutral journal normalization
- Debit/credit reconciliation
- JSON run summary and CSV outputs
- Docker and GitHub Actions support

## Architecture

```text
SAE-style file
    |
    v
Landing + SHA-256 manifest
    |
    v
Parser and validation
    |-----------------------> quarantine.csv
    v
Normalized journal
    |
    v
Reconciliation + audit summary
    |
    +------------------------> journal.csv
    +------------------------> run-summary.json
```

In a production deployment, the local landing folder could be replaced by a managed SFTP connector or integration platform. The journal writer could be replaced by an adapter for SAP, Oracle, Dynamics, NetSuite, or another accounting system.

## Run locally

Requires Python 3.12 or newer.

```powershell
$env:PYTHONPATH = "src"
python -m pip install -e ".[test]"
python -m pytest -q
python -m concur_sae.cli `
  --input fixtures/incoming/sample_sae.txt `
  --output-dir out `
  --db out/manifest.sqlite3
```

The command writes:

- `out/journal.csv` — normalized accounting lines
- `out/quarantine.csv` — invalid source rows and reasons
- `out/run-summary.json` — counts, totals, checksum, and status
- `out/manifest.sqlite3` — local idempotency/audit state

The sample is balanced, so the expected status is `COMPLETED`.

## Run with Docker

```powershell
docker build -t concur-sae-accounting-integration .
docker run --rm -v "${PWD}/out:/app/out" concur-sae-accounting-integration
```

## Production hardening considerations

This repository intentionally uses local files and SQLite for portability. A production implementation should add:

1. Managed SFTP with SSH-key authentication and host-key verification.
2. PGP signature/decryption verification where required by the exchange contract.
3. A managed secrets store rather than files or environment values on shared servers.
4. Immutable landing/archive storage and retention controls.
5. File manifests with checksum, source batch, row count, and processing status.
6. Explicit entity routing before processing multiple legal entities.
7. Retry and quarantine workflows that cannot create duplicate postings.
8. Monitoring for missing files, duplicate files, row-count changes, reconciliation failures, and downstream acknowledgement failures.
9. An accounting-system adapter with an acknowledgement or document identifier.
10. Access controls and audit logging for reprocessing and exception correction.

## Portfolio context

The project demonstrates transferable integration experience: understanding an accounting extract, building a safe ingestion boundary, validating business dimensions, preserving auditability, preventing duplicates, and reconciling outputs before posting to an ERP.
