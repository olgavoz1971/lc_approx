"""WSL fit whose formal error is not finite.

A flat series still returns the library time, the midpoint of C4 and C5.
That filled time is the command-line time of extremum. The covariance
cannot be estimated, so the formal error is empty and the status is
``sigma_missing``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ila_code.fit import fit_extremum

logger = logging.getLogger(__name__)


def main() -> None:
    """Fit the flat line and stop if the library time or the error is wrong.

    Returns:
        None.
    """
    time = np.linspace(0.0, 1.0, 20)
    values = np.full(time.shape, 3.0)
    result = fit_extremum("WSL", time, values)
    logger.info(
        "status=%s time=%s formal_sigma=%s level=%s message=%s",
        result.status,
        result.time,
        result.sigma_time,
        result.level,
        result.message,
    )
    if result.status != "sigma_missing":
        raise SystemExit(f"expected sigma_missing, got {result.status}")
    if result.time is None or result.sigma_time is not None:
        raise SystemExit(
            "the library time should be kept and the formal error left empty"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
