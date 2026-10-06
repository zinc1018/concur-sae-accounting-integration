import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .pipeline import run_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process a sanitized Concur SAE-style file")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    args = parser.parse_args(argv)

    result = run_file(args.input, args.output_dir, args.db)
    payload = {"status": result.status, "message": result.message}
    if result.summary:
        payload["summary"] = asdict(result.summary)
        payload["summary"]["source_total"] = f"{result.summary.source_total:.2f}"
        payload["summary"]["debit_total"] = f"{result.summary.debit_total:.2f}"
        payload["summary"]["credit_total"] = f"{result.summary.credit_total:.2f}"
        payload["summary"]["difference"] = f"{result.summary.difference:.2f}"
        payload["summary"]["processed_at"] = result.summary.processed_at.isoformat()
    print(json.dumps(payload, indent=2, default=str))
    return 0 if result.status in {"COMPLETED", "COMPLETED_WITH_QUARANTINE", "DUPLICATE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
