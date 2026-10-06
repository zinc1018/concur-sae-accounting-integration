# Concur SAE Accounting Integration Reference

## Goal

Provide a sanitized, runnable reference implementation of an enterprise-style SAP Concur Standard Accounting Extract (SAE) integration that can deliver normalized accounting journals to any downstream accounting or ERP platform.

The repository is portfolio-oriented. It must not contain employer names, internal database names, internal file paths, credentials, private keys, customer data, or proprietary field mappings.

## Profile positioning

This project is informed by experience maintaining SAP Concur SAE integrations across multiple organizations. It demonstrates transferable integration engineering practices rather than reproducing any employer's implementation.

## Scope

The demo will process a local fixture representing a pipe-delimited SAE file. It will model the same important production stages:

1. Land an input file.
2. Record its checksum and processing state.
3. Reject duplicate files safely.
4. Validate required fields and accounting dimensions.
5. Quarantine invalid records with reasons.
6. Normalize valid records into a generic journal model.
7. Reconcile source totals to output totals.
8. Write an ERP-neutral journal export and audit summary.

The demo will not connect to a live Concur tenant, SFTP server, ERP, or cloud account.

## Architecture

```text
fixtures/incoming/*.txt
        |
        v
Landing + SHA-256 manifest
        |
        v
Pipe-delimited parser
        |
        v
Validation and quarantine
        |                    \
        |                     \ invalid rows
        v                       v
Normalized journal        quarantine.csv
        |
        v
Reconciliation + audit
        |
        v
out/journal.csv + out/run-summary.json
```

## Technical choices

- Python 3.12+
- Standard library for the core pipeline
- SQLite for a local manifest/audit store
- CSV fixtures with sanitized fictional records
- `pytest` for behavior tests
- Dockerfile for repeatable execution
- GitHub Actions for test automation

## Core behavior

### File manifest and idempotency

Each input file receives a SHA-256 checksum and a processing record. A file with an already-successful checksum must not create a second journal export.

### Validation

The demo validates:

- required employee and report identifiers
- numeric amount
- supported debit/credit code
- non-empty account, company, branch, and department dimensions
- valid transaction date

Invalid rows go to quarantine with a stable error code and human-readable reason.

### Normalized journal

The output model is accounting-system neutral:

- journal ID
- source batch ID
- source row ID
- transaction date
- employee reference
- account
- company
- branch
- department
- debit/credit
- amount
- description
- currency

An adapter boundary will make it clear where a real SAP, Oracle, Dynamics, NetSuite, or other accounting-system writer could be added.

### Reconciliation

The run summary will report:

- input file name and checksum
- input row count
- valid row count
- quarantined row count
- source total
- output debit total
- output credit total
- balancing difference
- final status

The demo succeeds only when the output is balanced within the configured decimal tolerance and no duplicate file is processed.

## Security and privacy

- No secrets in source control.
- No real employee, vendor, customer, or company data.
- No private keys or connection strings.
- Configuration uses environment variables only for optional future adapters.
- The README will include production hardening notes for SFTP key storage, PGP verification, managed secrets, restricted landing areas, and retention.

## Success criteria

- A new user can run the demo locally with one documented command.
- Tests cover successful processing, duplicate detection, invalid-row quarantine, and reconciliation failure.
- The repository clearly distinguishes the local demo from a production deployment.
- GitHub Actions runs the test suite.
- The README explains the architecture and portfolio relevance without naming employers.
