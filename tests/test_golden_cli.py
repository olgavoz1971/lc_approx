"""Compare a fresh command-line run with the stored golden files.

The stored files were captured with Python 3.10.12, NumPy 2.2.6 and
SciPy 1.14.0. A different SciPy can change the last digits. That is a
failed test. The files under ``approx_output/golden/`` stay as they are.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "approx_output" / "golden"

CASES = (
    ("V405_Dra_AP", ["original_demos/test_data/V405_Dra.dat", "--method=AP"]),
    ("V405_Dra_WSAP", ["original_demos/test_data/V405_Dra.dat", "--method=WSAP"]),
    ("V405_Dra_WSL", ["original_demos/test_data/V405_Dra.dat", "--method=WSL"]),
    ("V405_Dra_A", ["original_demos/test_data/V405_Dra.dat", "--method=A"]),
    ("KP_Lyn-2_AP", ["original_demos/test_data/KP_Lyn-2.dat", "--method=AP"]),
    ("KP_Lyn-2_WSAP", ["original_demos/test_data/KP_Lyn-2.dat", "--method=WSAP"]),
    ("KP_Lyn-2_WSL", ["original_demos/test_data/KP_Lyn-2.dat", "--method=WSL"]),
    ("KP_Lyn-2_A", ["original_demos/test_data/KP_Lyn-2.dat", "--method=A"]),
    (
        "batch_AP",
        [
            "--method=AP",
            "--ranges=original_demos/test_data/lc_split.!",
            "original_demos/test_data/test_lc.tsv",
        ],
    ),
    (
        "batch_WSAP",
        [
            "--method=WSAP",
            "--ranges=original_demos/test_data/lc_split.!",
            "original_demos/test_data/test_lc.tsv",
        ],
    ),
    (
        "batch_WSL",
        [
            "--method=WSL",
            "--ranges=original_demos/test_data/lc_split.!",
            "original_demos/test_data/test_lc.tsv",
        ],
    ),
)


def test_golden_directory_matches_the_cases() -> None:
    """Require every stored text file to have a command in this module.

    Returns:
        None.
    """
    stored = {path.name for path in GOLDEN.glob("*.txt")}
    expected = {f"{name}.txt" for name, _args in CASES}
    assert stored == expected


@pytest.mark.parametrize(("name", "args"), CASES, ids=[name for name, _args in CASES])
def test_cli_matches_golden(name: str, args: list[str], tmp_path: Path) -> None:
    """Re-run one stored command and compare the whole text file.

    Args:
        name (str): Golden file stem.
        args (list[str]): Arguments of ``ila_ap.py`` before ``--no-plot``.
        tmp_path (pathlib.Path): Directory for the fresh result and preview.

    Returns:
        None.
    """
    result_path = tmp_path / f"{name}.txt"
    preview_path = tmp_path / f"{name}.html"
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "original_demos" / "ila_ap.py"),
            *args,
            "--no-plot",
            "--result",
            str(result_path),
            "--preview",
            str(preview_path),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert result_path.read_text(encoding="utf-8") == (
        GOLDEN / f"{name}.txt"
    ).read_text(encoding="utf-8")
