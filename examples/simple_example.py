"""Fit V405 Dra and KP Lyn-2 and draw each method.

Each file is fitted as a whole with AP, WSAP, WSL and A. The files are
``original_demos/test_data/V405_Dra.dat`` and
``original_demos/test_data/KP_Lyn-2.dat``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.figures import save_fit_figure
from ila_code import fit_extremum

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "original_demos" / "test_data"
OUTPUT = Path(__file__).resolve().parent / "output"
STARS = ("V405_Dra", "KP_Lyn-2")
METHODS = ("AP", "WSAP", "WSL", "A")


def read_series(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read times and magnitudes as the command-line script does.

    Args:
        path (pathlib.Path): Table with time in the first column and
            magnitude in the second.

    Returns:
        tuple: Times and magnitudes, sorted by time.
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


def fit_file(star: str) -> None:
    """Fit one file with AP, WSAP, WSL and A, then save the figures.

    Args:
        star (str): ``V405_Dra`` or ``KP_Lyn-2``.

    Returns:
        None.
    """
    time, values = read_series(DATA / f"{star}.dat")
    for method in METHODS:
        result = fit_extremum(method, time, values)
        logger.info(
            "%s %s status=%s time=%s formal_sigma=%s",
            star,
            method,
            result.status,
            None if result.time is None else f"{result.time:.8f}",
            result.sigma_time,
        )
        save_fit_figure(OUTPUT / f"{star}_{method}.png", time, values, result, star)


def main() -> None:
    """Fit both files.

    Returns:
        None.
    """
    for star in STARS:
        fit_file(star)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
