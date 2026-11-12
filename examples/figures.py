"""Figures for the example fits.

Draws the points, the model split at C4 and C5, and a line at a filled
time. An empty time is left unmarked. Magnitude axes are drawn with the
faint direction downward, as the command-line preview does.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ila_code.fit import FitResult
from ila_code.ila import f_A_a, f_AP_a, f_WSAP_a, f_WSL_a

logger = logging.getLogger(__name__)

_EVALUATE = {"AP": f_AP_a, "WSAP": f_WSAP_a, "WSL": f_WSL_a, "A": f_A_a}
_PIECE_COLOUR = {"left": "#6a3d9a", "core": "#33a02c", "right": "#ff7f00"}
_TIME_COLOUR = "#e7298a"
_MISSING_SIGMA_COLOUR = "#ff7f00"


def save_fit_figure(
    path: Path,
    time: np.ndarray,
    values: np.ndarray,
    result: FitResult,
    star: str,
) -> Path:
    """Save one fit figure.

    Args:
        path (pathlib.Path): PNG path.
        time (numpy.ndarray): Times of the points.
        values (numpy.ndarray): Magnitudes at those times.
        result (FitResult): Fit of that series.
        star (str): File stem, used in the title.

    Returns:
        pathlib.Path: The written PNG.

    Raises:
        RuntimeError: If the file is missing after the save.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 20, "font.family": "serif"}):
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.scatter(time, values, s=28, c="0.35", linewidths=0, zorder=2)
        _draw_model(ax, result, float(np.min(time)), float(np.max(time)))
        _draw_time(ax, result)
        ax.invert_yaxis()
        ax.set_title(_title(star, result))
        ax.set_xlabel("Time")
        ax.set_ylabel("Magnitude")
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"figure was not written: {path}")
    logger.info("figure %s", path)
    return path


def _draw_model(ax, result: FitResult, t_min: float, t_max: float) -> None:
    """Draw the fitted model in left, core and right colours.

    Args:
        ax: Matplotlib axes.
        result (FitResult): Fit. No model is drawn when the coefficients
            are missing.
        t_min (float): First time in the series.
        t_max (float): Last time in the series.
    """
    if result.params is None:
        return
    params = tuple(float(value) for value in result.params)
    if not np.isfinite(params).all():
        return
    evaluate = _EVALUATE.get(result.method)
    if evaluate is None:
        return
    for name, grid in _pieces(result.method, params, t_min, t_max):
        model = np.asarray(evaluate(grid, *params), dtype=float)
        if not np.isfinite(model).all():
            continue
        ax.plot(grid, model, color=_PIECE_COLOUR[name], lw=2.5, zorder=3)


def _pieces(
    method: str, params: tuple[float, ...], t_min: float, t_max: float
) -> list[tuple[str, np.ndarray]]:
    """Split the series at the fitted edges.

    Args:
        method (str): Method id.
        params (tuple[float, ...]): Fitted coefficients.
        t_min (float): First time in the series.
        t_max (float): Last time in the series.

    Returns:
        list[tuple[str, numpy.ndarray]]: Piece name and time grid.
    """
    if method == "A":
        edge = params[3]
        pieces: list[tuple[str, np.ndarray]] = []
        if min(edge, t_max) > t_min:
            pieces.append(("left", np.linspace(t_min, min(edge, t_max), 200)))
        if t_max > max(edge, t_min):
            pieces.append(("right", np.linspace(max(edge, t_min), t_max, 200)))
        return pieces
    c4, c5 = params[3], params[4]
    if not np.isfinite([c4, c5]).all() or c5 <= c4:
        return []
    pieces = []
    if min(c4, t_max) > t_min:
        pieces.append(("left", np.linspace(t_min, min(c4, t_max), 200)))
    core_lo = max(c4, t_min)
    core_hi = min(c5, t_max)
    if core_hi > core_lo:
        pieces.append(("core", np.linspace(core_lo, core_hi, 200)))
    if t_max > max(c5, t_min):
        pieces.append(("right", np.linspace(max(c5, t_min), t_max, 200)))
    return pieces


def _draw_time(ax, result: FitResult) -> None:
    """Mark a filled time. An empty time is left unmarked.

    Args:
        ax: Matplotlib axes.
        result (FitResult): Fit.
    """
    if result.time is None:
        return
    colour = _TIME_COLOUR if result.sigma_time is not None else _MISSING_SIGMA_COLOUR
    ax.axvline(result.time, color=colour, lw=2, zorder=4)


def _title(star: str, result: FitResult) -> str:
    """One-line title from the status and the time.

    Args:
        star (str): File stem.
        result (FitResult): Fit.

    Returns:
        str: Title text.
    """
    kind = f", {result.kind}" if result.kind else ""
    if result.time is None:
        return f"{star} {result.method} {result.status}{kind}\ntime empty"
    if result.sigma_time is None:
        return (
            f"{star} {result.method} {result.status}{kind}\n"
            f"time {result.time:.6f}, formal error empty"
        )
    return (
        f"{star} {result.method} {result.status}{kind}\n"
        f"time {result.time:.6f}, formal error {result.sigma_time:.6f}"
    )
