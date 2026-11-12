"""AP fit of a maximum of the supplied series.

The same call as a minimum. Negative C2 is a maximum of that series.
There is no separate maxima method, and the series is not reversed.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ila_code import fit_extremum
from examples.series import asymptotic_series

logger = logging.getLogger(__name__)


def main() -> None:
    """Fit the maximum and stop if the curvature is not reported as one.

    Returns:
        None.
    """
    time, values = asymptotic_series(curvature=-4.0, seed=8)
    result = fit_extremum("AP", time, values)
    logger.info(
        "status=%s kind=%s time=%.6f formal_sigma=%.6f C2=%.4f level=%.4f",
        result.status,
        result.kind,
        result.time,
        result.sigma_time,
        result.params[1],
        result.level,
    )
    if result.status != "accepted" or result.kind != "maximum":
        raise SystemExit(
            f"expected an accepted maximum, got {result.status} {result.kind}"
        )
    if result.params[1] >= 0.0:
        raise SystemExit("C2 is not negative")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
