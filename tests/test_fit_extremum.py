"""Status checks for ``fit_extremum`` on small series.

The last digits of a successful fit move between SciPy versions. The
numeric lock for the methods is the golden files. These tests lock the
status, whether the time is filled, and which series is a maximum.
"""

from __future__ import annotations

import numpy as np

from examples.series import asymptotic_series
from ila_code.fit import fit_extremum


def test_accepted_minimum() -> None:
    """Keep an accepted minimum and both error numbers.

    Returns:
        None.
    """
    time, values = asymptotic_series(curvature=4.0, seed=7)
    result = fit_extremum("AP", time, values)
    assert result.status == "accepted"
    assert result.kind == "minimum"
    assert result.time is not None
    assert result.sigma_time is not None and result.sigma_time > 0.0
    assert result.residual_rms is not None


def test_accepted_maximum() -> None:
    """Report negative C2 as a maximum of the supplied series.

    Returns:
        None.
    """
    time, values = asymptotic_series(curvature=-4.0, seed=8)
    result = fit_extremum("AP", time, values)
    assert result.status == "accepted"
    assert result.kind == "maximum"
    assert result.params is not None and result.params[1] < 0.0


def test_flat_wsl_keeps_the_library_time() -> None:
    """Keep the midpoint when the formal error is not finite.

    Returns:
        None.
    """
    time = np.linspace(0.0, 1.0, 20)
    result = fit_extremum("WSL", time, np.full(time.shape, 3.0))
    assert result.status == "sigma_missing"
    assert result.time == 0.5
    assert result.sigma_time is None
    assert result.level == 3.0
    assert result.residual_rms == 0.0


def test_short_window_does_not_stop_the_next() -> None:
    """Return a result for each window, including the ones that fail.

    Returns:
        None.
    """
    few_time = np.linspace(0.0, 1.0, 4)
    few = fit_extremum("AP", few_time, (few_time - 0.5) ** 2)
    assert few.status == "too_few_points"
    assert few.time is None

    trend_time = np.linspace(0.0, 1.0, 30)
    trend_values = 0.2 * (trend_time - 0.5) ** 2 + 8.0 * trend_time
    trend = fit_extremum("AP", trend_time, trend_values)
    assert trend.status == "no_library_time"
    assert trend.time is None

    short_time = np.linspace(0.0, 1.0, 25)
    short_values = np.sin(np.linspace(0.0, 12.0, short_time.size))
    short = fit_extremum("WSL", short_time, short_values)
    assert short.status == "short_core"
    assert short.time is not None
    assert short.sigma_time is not None

    good_time, good_values = asymptotic_series(curvature=4.0, seed=7)
    good = fit_extremum("AP", good_time, good_values)
    assert good.status == "accepted"


def test_method_a_on_five_points_is_fitted() -> None:
    """Pass five points to method A, which has four coefficients.

    Returns:
        None.
    """
    result = fit_extremum(
        "A",
        np.linspace(0.0, 1.0, 5),
        np.array([1.0, 0.4, 0.0, 0.5, 1.1]),
    )
    assert result.status == "accepted"
    assert result.time is not None
