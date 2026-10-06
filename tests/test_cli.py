import shutil
from pathlib import Path

from concur_sae.cli import main


FIXTURE = Path(__file__).parent / "fixtures" / "valid_sae.txt"


def test_cli_runs_sample_file_and_prints_status(tmp_path: Path, capsys):
    input_path = tmp_path / "sample.txt"
    shutil.copy(FIXTURE, input_path)

    exit_code = main([
        "--input", str(input_path),
        "--output-dir", str(tmp_path / "out"),
        "--db", str(tmp_path / "manifest.sqlite3"),
    ])

    assert exit_code == 0
    assert '"status": "COMPLETED"' in capsys.readouterr().out
