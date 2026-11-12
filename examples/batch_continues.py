"""Several windows, one after another.

A short AP window, a library time that is not finite, a core shorter
than its formal error, and an accepted minimum. None of the failures
stops the next window. Five points are enough for method A, which has
four coefficients.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ila_code import fit_extremum
from examples.series import asymptotic_series

logger = logging.getLogger(__name__)


def main() -> None:
    """Fit each window and stop if a later window is skipped.

    Returns:
        None.
    """
    few_time = np.linspace(0.0, 1.0, 4)
    few_values = (few_time - 0.5) ** 2
    trend_time = np.linspace(0.0, 1.0, 30)
    trend_values = 0.2 * (trend_time - 0.5) ** 2 + 8.0 * trend_time
    short_time = np.linspace(0.0, 1.0, 25)
    short_values = np.sin(np.linspace(0.0, 12.0, short_time.size))
    good_time, good_values = asymptotic_series(curvature=4.0, seed=7)
    windows = (
        ("AP, 4 points", few_time, few_values, "AP", "too_few_points"),
        ("library time not finite", trend_time, trend_values, "AP", "no_library_time"),
        ("core shorter than the error", short_time, short_values, "WSL", "short_core"),
        ("accepted minimum", good_time, good_values, "AP", "accepted"),
    )
    for name, time, values, method, expected in windows:
        result = fit_extremum(method, time, values)
        logger.info(
            "%s status=%s time=%s formal_sigma=%s message=%s",
            name,
            result.status,
            None if result.time is None else f"{result.time:.6f}",
            result.sigma_time,
            result.message,
        )
        if result.status != expected:
            raise SystemExit(f"{name}: expected {expected}, got {result.status}")
    outside = fit_extremum("AP", trend_time, trend_values)
    if outside.time is not None:
        raise SystemExit("a non-finite library time must stay empty")
    method_a = fit_extremum(
        "A",
        np.linspace(0.0, 1.0, 5),
        np.array([1.0, 0.4, 0.0, 0.5, 1.1]),
    )
    logger.info("A, 5 points status=%s time=%s", method_a.status, method_a.time)
    if method_a.status == "too_few_points":
        raise SystemExit("method A on 5 points must be passed to the optimiser")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
