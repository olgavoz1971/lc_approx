"""Check that ``fit_extremum`` returns the stored command-line numbers.

The series is read the same way as ``original_demos/ila_ap.py``. A filled
time is the golden time of extremum. An empty time is the golden ``nan``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ila_code.fit import FitResult, fit_extremum

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "approx_output" / "golden"
DATA = ROOT / "original_demos" / "test_data"
FILLED_STATUSES = ("accepted", "bounds_outside", "short_core", "sigma_missing")

SINGLES = (
    ("V405_Dra", "AP"),
    ("V405_Dra", "WSAP"),
    ("V405_Dra", "WSL"),
    ("V405_Dra", "A"),
    ("KP_Lyn-2", "AP"),
    ("KP_Lyn-2", "WSAP"),
    ("KP_Lyn-2", "WSL"),
    ("KP_Lyn-2", "A"),
)


def _series(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read times and values as the command-line script does.

    Args:
        path (pathlib.Path): Table with time in the first column and the
            series in the second.

    Returns:
        tuple: Times and values, sorted by time.
    """
    frame = pd.read_csv(
        path,
        comment="#",
        skip_blank_lines=True,
        sep=r"\s+",
        names=["time", "mag"],
        dtype={"time": "float64", "mag": "float64"},
        usecols=["time", "mag"],
    )
    pairs = sorted(zip(frame["time"], frame["mag"]))
    time = np.array([item[0] for item in pairs], dtype=float)
    values = np.array([item[1] for item in pairs], dtype=float)
    return time, values


def _ranges(path: Path) -> pd.DataFrame:
    """Read a batch range file as the command-line script does.

    Args:
        path (pathlib.Path): Range file.

    Returns:
        pandas.DataFrame: Columns ``time1`` and ``time2``.
    """
    return pd.read_csv(
        path,
        comment="#",
        skip_blank_lines=True,
        sep=r"\s+",
        names=["point1", "time1", "point2", "time2"],
        dtype={
            "point1": "int32",
            "time1": "float64",
            "point2": "int32",
            "time2": "float64",
        },
        usecols=["point1", "time1", "point2", "time2"],
    )


def _table(path: Path) -> list[dict[str, str]]:
    """Read one golden result table.

    Args:
        path (pathlib.Path): Stored result file.

    Returns:
        list[dict[str, str]]: Data rows keyed by the header.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        if line == "":
            continue
        parts = line.split("\t")
        assert len(parts) >= len(header), f"{path.name} has a short row"
        rows.append(dict(zip(header, parts)))
    return rows


def _recorded(text: str) -> float | None:
    """Return a finite golden number, or ``None`` for ``nan`` and ``inf``.

    Args:
        text (str): One cell of a golden file.

    Returns:
        float | None: The finite value.
    """
    number = float(text)
    if not np.isfinite(number):
        return None
    return number


def _matches(result: FitResult, row: dict[str, str], label: str) -> None:
    """Assert one fit against one golden row.

    Args:
        result (FitResult): Result of ``fit_extremum``.
        row (dict[str, str]): Golden cells.
        label (str): File and row, used when an assertion fails.

    Returns:
        None.
    """
    expected_time = _recorded(row["Time of Extremum (TOM)"])
    expected_sigma = _recorded(row["TOM Uncertainty"])
    expected_rms = _recorded(row["Sigma"])
    if expected_time is None:
        assert result.time is None, label
        assert result.status == "no_library_time", label
    else:
        assert result.time == expected_time, label
        assert result.status in FILLED_STATUSES, label
    assert result.sigma_time == expected_sigma, label
    assert result.residual_rms == expected_rms, label


def test_single_files_match_golden() -> None:
    """Fit each single-extremum file and compare it with its golden row.

    Returns:
        None.
    """
    for star, method in SINGLES:
        rows = _table(GOLDEN / f"{star}_{method}.txt")
        assert len(rows) == 1
        time, values = _series(DATA / f"{star}.dat")
        assert time.size == int(rows[0]["Points"])
        result = fit_extremum(method, time, values)
        _matches(result, rows[0], f"{star} {method}")


def test_batch_rows_match_golden() -> None:
    """Fit each stored batch window and compare time, error and scatter.

    Returns:
        None.
    """
    time, values = _series(DATA / "test_lc.tsv")
    windows = _ranges(DATA / "lc_split.!")
    for method in ("AP", "WSAP", "WSL"):
        rows = _table(GOLDEN / f"batch_{method}.txt")
        assert len(rows) == len(windows)
        for index, row in enumerate(rows):
            start = float(row["Start Time"])
            stop = float(row["End Time"])
            mask = (time >= start) & (time <= stop)
            assert int(mask.sum()) == int(row["Points"])
            result = fit_extremum(method, time[mask], values[mask])
            _matches(result, row, f"batch {method} row {index + 1}")
