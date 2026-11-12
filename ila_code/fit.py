"""One fit result for AP, WSAP, WSL and A.

Calls ``approx`` and ``method_result``. It does not repeat their vertex
or their Jacobians. A failed window is a result, so the next window
still runs.

``approx`` keeps its own default ``maxfev`` of 12000. This function
defaults to 100000, which is what ``ila_ap.py`` passes.

A filled ``time`` is the command-line time of extremum. That covers
``accepted``, ``bounds_outside``, ``short_core`` and ``sigma_missing``.
The status says what else that row carried. An empty ``time`` is the
golden ``nan``. This function does not fill a time ``method_result``
left non-finite.
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass

import numpy as np

from ila_code.ila import (
    approx,
    f_A,
    f_A_a,
    f_AP_a,
    f_WSAP_a,
    f_WSL,
    f_WSL_a,
    method_result,
)

logger = logging.getLogger(__name__)

MAXFEV = 100000
_METHODS = ("AP", "WSAP", "WSL", "A")
# Local guard so method_result is not asked to divide by a vanishing C2.
# Not a constant of the AP method.
_C2_DIVISOR = 1e-30


@dataclass(frozen=True)
class FitResult:
    """Outcome of one extremum fit.

    Attributes:
        method (str): ``AP``, ``WSAP``, ``WSL`` or ``A``.
        status (str): ``accepted``, ``sigma_missing``, ``short_core``,
            ``bounds_outside``, ``no_library_time``, ``zero_curvature``,
            ``bad_c4_c5``, ``too_few_points``, ``maxfev``, ``bad_data`` or
            ``fit_failed``.
        time (float | None): Time returned by ``method_result``. This is the
            command-line time of extremum whenever it is filled. Empty when
            that function does not return a finite time, which is the golden
            ``nan``.
        sigma_time (float | None): Formal covariance error of ``time``.
            Empty when that error is not finite. An exact zero is kept.
        level (float | None): Model value at ``time``, from ``method_result``.
        sigma_level (float | None): Formal covariance error of ``level``.
        kind (str | None): ``maximum`` or ``minimum`` of the supplied series.
            For AP and WSAP this is the sign of C2.
        residual_rms (float | None): Root-mean-square of the residuals. This
            is not the error of the time.
        warning (str | None): Sentence returned by the library. The status
            is not chosen by matching this sentence.
        message (str | None): Why the status is not ``accepted``.
        params (tuple[float, ...] | None): Fitted coefficients in absolute
            time, when the optimiser returned them.
    """

    method: str
    status: str
    time: float | None
    sigma_time: float | None
    level: float | None
    sigma_level: float | None
    kind: str | None
    residual_rms: float | None
    warning: str | None
    message: str | None
    params: tuple[float, ...] | None


def fit_extremum(
    method: str,
    t_obs: np.ndarray,
    y_obs: np.ndarray,
    maxfev: int = MAXFEV,
) -> FitResult:
    """Fit one window and return a status instead of raising.

    Args:
        method (str): ``AP``, ``WSAP``, ``WSL`` or ``A``.
        t_obs (numpy.ndarray): Times of the points in the window.
        y_obs (numpy.ndarray): Values at those times. The fit is unweighted.
        maxfev (int): Optimiser iteration limit. Default 100000.

    Returns:
        FitResult: The library time, its formal error, the level, and a
        status. ``approx`` is not given a new formula.
    """
    method = method.upper()
    if method not in _METHODS:
        return _empty(method, "fit_failed", f"Unsupported method: {method}")

    time, values, problem = _series(t_obs, y_obs)
    if problem is not None:
        return _empty(method, "bad_data", problem)
    n_coeff = _n_coeff(method)
    if time.size < n_coeff:
        return _empty(
            method,
            "too_few_points",
            f"{method} needs at least {n_coeff} points.",
        )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            params_opt, _params_cov, param_warning = approx(
                method, time, values, maxfev=maxfev
            )
        except Exception as exc:
            status, message = _exception_status(exc)
            logger.info("%s %s: %s", method, status, message)
            return _empty(method, status, message)
    for item in caught:
        logger.debug("%s", item.message)

    params = tuple(float(value) for value in params_opt)
    warning = None if param_warning is None else str(param_warning)
    if _bad_edges(method, params):
        return _from_params(
            method,
            "bad_c4_c5",
            params,
            values,
            time,
            warning=warning,
            message="C5 is not greater than C4.",
        )
    if method == "AP" and abs(params[1]) < _C2_DIVISOR:
        return _from_params(
            method,
            "zero_curvature",
            params,
            values,
            time,
            warning=warning,
            message="C2 is too small to divide.",
        )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        library = method_result(
            method, params_opt, _params_cov, float(np.min(time)), float(np.max(time))
        )
    for item in caught:
        logger.debug("%s", item.message)

    warning = _join(warning, None if library[6] is None else str(library[6]))
    fitted_time = _finite(library[0])
    sigma_time = _finite(library[1])
    fitted_level = _finite(library[2])
    sigma_level = _finite(library[3])
    status, message = _status(
        method,
        params,
        float(np.min(time)),
        float(np.max(time)),
        fitted_time,
        sigma_time,
    )
    kind = _kind(method, params, fitted_time) if fitted_time is not None else None
    result = FitResult(
        method=method,
        status=status,
        time=fitted_time,
        sigma_time=sigma_time,
        level=fitted_level,
        sigma_level=sigma_level,
        kind=kind,
        residual_rms=_residual(method, params, time, values),
        warning=warning,
        message=message,
        params=params,
    )
    logger.info(
        "%s %s time=%s sigma=%s kind=%s",
        method,
        status,
        result.time,
        result.sigma_time,
        result.kind,
    )
    return result


def _n_coeff(method: str) -> int:
    """Number of coefficients ``approx`` fits.

    Args:
        method (str): Method id.

    Returns:
        int: 4 for A, 5 for AP, WSAP and WSL.
    """
    if method == "A":
        return 4
    return 5


def _empty(method: str, status: str, message: str) -> FitResult:
    """Build a result that has no coefficients.

    Args:
        method (str): Method id, already upper case.
        status (str): Failure status.
        message (str): Sentence stored on the result.

    Returns:
        FitResult: Empty time and no parameters.
    """
    return FitResult(
        method=method,
        status=status,
        time=None,
        sigma_time=None,
        level=None,
        sigma_level=None,
        kind=None,
        residual_rms=None,
        warning=None,
        message=message,
        params=None,
    )


def _from_params(
    method: str,
    status: str,
    params: tuple[float, ...],
    values: np.ndarray,
    time: np.ndarray,
    warning: str | None,
    message: str,
) -> FitResult:
    """Build a result that keeps the coefficients and has no time.

    Args:
        method (str): Method id.
        status (str): Failure status.
        params (tuple[float, ...]): Fitted coefficients.
        values (numpy.ndarray): Series, used only for the residual.
        time (numpy.ndarray): Times of the points.
        warning (str | None): Library warning, if one was already set.
        message (str): Sentence stored on the result.

    Returns:
        FitResult: No time of extremum.
    """
    return FitResult(
        method=method,
        status=status,
        time=None,
        sigma_time=None,
        level=None,
        sigma_level=None,
        kind=None,
        residual_rms=_residual(method, params, time, values),
        warning=warning,
        message=message,
        params=params,
    )


def _series(
    t_obs: np.ndarray, y_obs: np.ndarray
) -> tuple[np.ndarray, np.ndarray, str | None]:
    """Copy the window into two float arrays.

    Args:
        t_obs (numpy.ndarray): Times.
        y_obs (numpy.ndarray): Series values.

    Returns:
        tuple: Times, values, and an error sentence, or ``None`` when the
        arrays can be fitted.
    """
    time = np.asarray(t_obs, dtype=float).reshape(-1)
    values = np.asarray(y_obs, dtype=float).reshape(-1)
    if time.size != values.size:
        return time, values, "Time and values have different lengths."
    if time.size == 0:
        return time, values, "The window is empty."
    if not np.isfinite(time).all() or not np.isfinite(values).all():
        return time, values, "The series contains a non-finite time or value."
    return time, values, None


def _exception_status(exc: Exception) -> tuple[str, str]:
    """Classify an exception from ``approx``.

    Args:
        exc (Exception): Whatever ``approx`` raised.

    Returns:
        tuple: Status and the exception text.
    """
    text = str(exc)
    if "maxfev" in text:
        return "maxfev", text
    if "must not exceed the number of data points" in text:
        return "too_few_points", text
    return "fit_failed", text


def _bad_edges(method: str, params: tuple[float, ...]) -> bool:
    """Report whether C5 is at or below C4.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.

    Returns:
        bool: True when the parabolic or flat interval is empty.
    """
    if method == "A":
        return False
    return params[4] <= params[3]


def _outside_data(
    method: str, params: tuple[float, ...], t_min: float, t_max: float
) -> bool:
    """Report whether C4 or C5 lies outside the data interval.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients in absolute time.
        t_min (float): First data time.
        t_max (float): Last data time.

    Returns:
        bool: True when an edge coefficient is outside ``[t_min, t_max]``.
    """
    c4 = params[3]
    if c4 < t_min or c4 > t_max:
        return True
    if method == "A":
        return False
    c5 = params[4]
    return c5 < t_min or c5 > t_max


def _status(
    method: str,
    params: tuple[float, ...],
    t_min: float,
    t_max: float,
    fitted_time: float | None,
    sigma_time: float | None,
) -> tuple[str, str | None]:
    """Choose the status from the coefficients and the library numbers.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.
        t_min (float): First data time.
        t_max (float): Last data time.
        fitted_time (float | None): Finite time from ``method_result``.
        sigma_time (float | None): Finite formal error from ``method_result``.

    Returns:
        tuple: Status and the message that explains it.
    """
    if fitted_time is None:
        return "no_library_time", "method_result did not return a finite time."
    if _outside_data(method, params, t_min, t_max):
        return "bounds_outside", "C4 or C5 lies outside the data interval."
    if (
        method != "A"
        and sigma_time is not None
        and abs(params[4] - params[3]) < sigma_time
    ):
        return "short_core", "The core is shorter than the formal error."
    if sigma_time is None:
        return "sigma_missing", "The formal timing uncertainty is not finite."
    return "accepted", None


def _kind(method: str, params: tuple[float, ...], fitted_time: float) -> str | None:
    """Say whether the extremum is a maximum or a minimum of the series.

    For AP and WSAP this is the sign of C2. A negative C2 is a maximum
    of the array that was passed. For WSL and A the model is compared
    with its own wings.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.
        fitted_time (float): Time of extremum from ``method_result``.

    Returns:
        str | None: ``maximum``, ``minimum``, or ``None`` when the wings
        disagree.
    """
    if method in {"AP", "WSAP"}:
        curvature = params[1]
        if curvature < 0.0:
            return "maximum"
        if curvature > 0.0:
            return "minimum"
        return None
    if method == "WSL":
        c1, c2, c3, c4, c5 = params
        centre = float(f_WSL(fitted_time, c1, c2, c3, c4, c5))
        half = c5 - c4
        left = float(f_WSL(c4 - half, c1, c2, c3, c4, c5))
        right = float(f_WSL(c5 + half, c1, c2, c3, c4, c5))
        return _wing_kind(centre, left, right)
    if method == "A":
        c1, c2, c3, c4 = params
        centre = float(f_A(fitted_time, c1, c2, c3, c4))
        left = float(f_A(c4 - 1.0, c1, c2, c3, c4))
        right = float(f_A(c4 + 1.0, c1, c2, c3, c4))
        return _wing_kind(centre, left, right)
    return None


def _wing_kind(centre: float, left: float, right: float) -> str | None:
    """Classify an extremum from the model on either side.

    Args:
        centre (float): Model at the extremum.
        left (float): Model on the left wing.
        right (float): Model on the right wing.

    Returns:
        str | None: ``minimum`` when both wings are higher, ``maximum``
        when both are lower.
    """
    if not np.isfinite([centre, left, right]).all():
        return None
    if left > centre and right > centre:
        return "minimum"
    if left < centre and right < centre:
        return "maximum"
    return None


def _residual(
    method: str,
    params: tuple[float, ...],
    time: np.ndarray,
    values: np.ndarray,
) -> float | None:
    """Root-mean-square residual used by the command-line table.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.
        time (numpy.ndarray): Times of the points.
        values (numpy.ndarray): Series values.

    Returns:
        float | None: Residual scatter, or ``None`` when the degrees of
        freedom are not positive or the model is not finite.
    """
    degrees = int(time.size - len(params))
    if degrees <= 0:
        return None
    model = _model_at(method, params, time)
    if model is None:
        return None
    return float(np.sqrt(np.sum((values - model) ** 2) / degrees))


def _model_at(
    method: str, params: tuple[float, ...], time: np.ndarray
) -> np.ndarray | None:
    """Evaluate the fitted model on the observed times.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.
        time (numpy.ndarray): Times of the points.

    Returns:
        numpy.ndarray | None: Model values, or ``None`` when any value is
        not finite.
    """
    if method == "AP":
        model = np.asarray(f_AP_a(time, *params), dtype=float)
    elif method == "WSAP":
        model = np.asarray(f_WSAP_a(time, *params), dtype=float)
    elif method == "WSL":
        model = np.asarray(f_WSL_a(time, *params), dtype=float)
    elif method == "A":
        model = np.asarray(f_A_a(time, *params), dtype=float)
    else:
        return None
    if not np.isfinite(model).all():
        return None
    return model


def _finite(value: object) -> float | None:
    """Return a finite float, or ``None``.

    Args:
        value (object): Number from ``method_result``.

    Returns:
        float | None: The float when it is finite. Zero is finite.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(number):
        return None
    return number


def _join(first: str | None, second: str | None) -> str | None:
    """Join two warning sentences.

    Args:
        first (str | None): Warning from ``approx``.
        second (str | None): Warning from ``method_result``.

    Returns:
        str | None: Both sentences, or the one that is present.
    """
    parts = [part for part in (first, second) if part]
    if not parts:
        return None
    return "; ".join(parts)
