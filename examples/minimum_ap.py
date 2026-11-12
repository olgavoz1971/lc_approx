"""AP fit of a minimum of the supplied series.

The formal error of the time and the residual scatter are printed as
two different numbers. The fit does not take weights. A filled time is
the command-line time of extremum, whatever the status.
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
    """Fit the minimum and stop if the result is not an accepted minimum.

    Returns:
        None.
    """
    time, values = asymptotic_series(curvature=4.0, seed=7)
    result = fit_extremum("AP", time, values)
    logger.info(
        "status=%s kind=%s time=%.6f formal_sigma=%.6f residual_rms=%.6f level=%.4f",
        result.status,
        result.kind,
        result.time,
        result.sigma_time,
        result.residual_rms,
        result.level,
    )
    if result.status != "accepted" or result.kind != "minimum":
        raise SystemExit(
            f"expected an accepted minimum, got {result.status} {result.kind}"
        )
    if result.sigma_time is None or result.sigma_time <= 0.0:
        raise SystemExit("the formal time error is missing")
    if result.residual_rms is None:
        raise SystemExit("the residual scatter is missing")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
