"""A real TESS light curve: fold it, then fit two minima.

The file is a cleaned part of TIC 388995726, sector 71, 200 s cadence.
Points with MJD from 60234 to 60240 are kept. Reading it needs
volightcurve 0.1.0 or newer. The fits use SAP
flux. The folded figure uses magnitudes from that same column. The epoch
in the file is only the reference for the phase count. The two minima are
read from the smoothed folded SAP flux, and the windows are centred there.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import volightcurve
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import binned_statistic
from volightcurve import read_lightcurve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.figures import save_fit_figure
from ila_code import FitResult, fit_extremum

logger = logging.getLogger(__name__)

DATA = Path(__file__).resolve().parent / "data" / "TIC388995726_s71_TESS-SPOC_part.vot"
OUTPUT = Path(__file__).resolve().parent / "output"
FITS = OUTPUT / "fits"
SAP = "sap_flux"

# Half-width in phase of the window centred on each minimum found below.
HALF_PHASE = 0.07

# The folded SAP flux is averaged in this many equal phase bins before smoothing.
N_PHASE_BINS = 200

# Width of the Savitzky-Golay smooth, in phase. The filter wraps, because
# phase 0 and phase 1 are the same point. This width is not a secondary phase.
SMOOTH_PHASE = 0.04

# Bins closer than this are one dip counted twice. It does not place either minimum.
MIN_SEPARATION = 0.05

METHODS = ("WSL", "WSAP", "AP")


def main() -> None:
    """Load the series, draw the folded magnitudes, and fit every eclipse.

    Returns:
        None.
    """
    series = _load()
    # The epoch in the file is the researcher's reference for the phase count.
    # A period change moves the minima away from that epoch, and the secondary
    # minimum can sit at any phase. Both phases come from the smoothed flux.
    minima = _folded_minima(series)
    logger.info(
        "reference epoch is not a minimum; primary phase %.4f, secondary phase %.4f",
        minima["primary"],
        minima["secondary"],
    )
    _plot_folded(series, minima)
    # Every eclipse of both dips, not one example of each. The window is the
    # same half-width, centred on the phase found above.
    for name in ("primary", "secondary"):
        centres = _centres(series, minima[name])
        logger.info("%s: %d eclipses", name, len(centres))
        for cycle, centre in centres:
            selected = np.abs(series["mjd"] - centre) <= HALF_PHASE * series["period"]
            # A centre can fall in a gap. There is nothing to fit there.
            if not np.any(selected):
                logger.info("%s cycle %d has no points in the window", name, cycle)
                continue
            for method in METHODS:
                # The fitter sees SAP flux, not magnitudes, and no photometric errors.
                result = fit_extremum(
                    method, series["mjd"][selected], series["flux"][selected]
                )
                caption = _caption(method, result)
                logger.info("%s cycle %d %s", name, cycle, caption.replace("\n", " | "))
                save_fit_figure(
                    FITS / f"{name}_{cycle}_{method}.png",
                    series["mjd"][selected],
                    series["flux"][selected],
                    result,
                    name,
                    ylabel=f"SAP flux ({series['flux_unit']})",
                    invert=False,
                    xlabel="MJD",
                    title=caption,
                    plain_time=True,
                )


def _load() -> dict:
    """Read the VOTable with volightcurve and keep the SAP flux.

    Returns:
        dict: MJD, SAP flux, magnitudes, period, epoch and the flux unit.

    Raises:
        SystemExit: If the time description, the SAP column, or the
            magnitude conversion is not usable.
    """
    version = tuple(int(part) for part in volightcurve.__version__.split(".")[:3])
    if version < (0, 1, 0):
        raise SystemExit(f"volightcurve {volightcurve.__version__} is older than 0.1.0")

    # strict=True uses only what the file declares. Nothing is guessed.
    volc = read_lightcurve(DATA, filename=DATA.name, strict=True)
    problems = volc.time_problems()
    if problems:
        raise SystemExit(f"time description: {problems}")
    logger.info(
        "time scale %s, reference position %s, origin %s",
        volc.timesys.timescale,
        volc.timesys.refposition,
        volc.timesys.timeorigin,
    )

    # Absolute MJD from the declared origin. The time column is not shifted by hand.
    mjd = np.asarray(volc.get_observation_mjd(), dtype=float)
    epoch = volc.get_epoch_mjd()
    period = volc.table.meta.get("period")
    if epoch is None or period is None:
        raise SystemExit("the file does not declare both an epoch and a period")
    period = float(period)
    logger.info("epoch MJD %.5f, period %.5f d, %d points", epoch, period, mjd.size)

    # Two flux columns are present. This example uses sap_flux and leaves pdcsap_flux.
    flux_columns = volc.get_flux_colnames()
    if SAP not in flux_columns:
        raise SystemExit(f"{SAP} is not a flux column: {flux_columns}")
    conversion = volc.conversion_problems(SAP)
    if conversion:
        raise SystemExit(f"SAP flux cannot be turned into magnitude: {conversion}")

    flux_column = volc.table[SAP]
    flux = np.asarray(flux_column.value, dtype=float)
    if not np.isfinite(flux).all() or np.any(flux <= 0.0):
        raise SystemExit("SAP flux has a non-finite or non-positive value")
    magnitude = volc.photdms[SAP].photcal.flux_to_mag(flux_column.quantity)
    return {
        "mjd": mjd,
        "flux": flux,
        "magnitude": np.asarray(magnitude.value, dtype=float),
        "period": period,
        "epoch": float(epoch),
        "flux_unit": str(flux_column.unit),
        "unit": flux_column.unit,
        "photcal": volc.photdms[SAP].photcal,
    }


def _folded_minima(series: dict) -> dict:
    """Smooth the folded SAP flux and return its two minima.

    Phase 0 is the reference epoch from the file. It is not searched for,
    and it is not treated as a minimum. The secondary is the shallower of
    the two dips, wherever that dip sits.

    Args:
        series (dict): Values returned by ``_load``.

    Returns:
        dict: ``primary`` and ``secondary`` phases, the bin centres, and the
        smoothed flux turned into magnitude for the figure.

    Raises:
        SystemExit: If a bin is empty, or the smooth curve does not have
            two distinct minima.
    """
    phase = np.mod((series["mjd"] - series["epoch"]) / series["period"], 1.0)
    binned = binned_statistic(
        phase,
        series["flux"],
        statistic="mean",
        bins=N_PHASE_BINS,
        range=(0.0, 1.0),
    )
    centres = 0.5 * (binned.bin_edges[:-1] + binned.bin_edges[1:])
    mean_flux = np.asarray(binned.statistic, dtype=float)
    if not np.isfinite(mean_flux).all():
        raise SystemExit("a phase bin of the folded SAP flux is empty")

    # Savitzky-Golay asks for an odd window. One extra bin keeps the width asked for.
    window = int(round(SMOOTH_PHASE * N_PHASE_BINS))
    if window % 2 == 0:
        window += 1
    if window <= 2 or window >= N_PHASE_BINS:
        raise SystemExit(f"smooth window is {window} bins, which cannot be used")
    smooth = savgol_filter(mean_flux, window_length=window, polyorder=2, mode="wrap")

    # The search is repeated on three copies so a dip that crosses phase 0 is one dip.
    separation = max(1, int(round(MIN_SEPARATION * N_PHASE_BINS)))
    extended = np.concatenate((smooth, smooth, smooth))
    found, _ = find_peaks(-extended, distance=separation)
    found = found[(found >= N_PHASE_BINS) & (found < 2 * N_PHASE_BINS)] - N_PHASE_BINS
    found = np.unique(found)
    if found.size != 2:
        raise SystemExit(
            f"the smoothed folded flux has {found.size} minima, and two are required"
        )

    order = found[np.argsort(smooth[found])]
    deeper, shallower = int(order[0]), int(order[1])
    if smooth[deeper] == smooth[shallower]:
        raise SystemExit("the two minima have the same smoothed flux")
    if np.any(smooth <= 0.0):
        raise SystemExit("the smoothed SAP flux is not positive")
    smooth_magnitude = series["photcal"].flux_to_mag(smooth * series["unit"])
    logger.info(
        "smoothed SAP flux minima at phases %.4f and %.4f",
        centres[deeper],
        centres[shallower],
    )
    return {
        "primary": float(centres[deeper]),
        "secondary": float(centres[shallower]),
        "bin_phase": centres,
        "smooth_magnitude": np.asarray(smooth_magnitude.value, dtype=float),
    }


def _centres(series: dict, phase: float) -> list[tuple[int, float]]:
    """List every eclipse of one phase that has both sides inside the series.

    Args:
        series (dict): Values returned by ``_load``.
        phase (float): Phase of this minimum on the smoothed folded flux.

    Returns:
        list[tuple[int, float]]: Cycle counted from the reference epoch, and
        the centre as MJD.

    Raises:
        SystemExit: If no such eclipse exists.
    """
    epoch = series["epoch"]
    period = series["period"]
    half_days = HALF_PHASE * period
    first = float(np.min(series["mjd"]))
    last = float(np.max(series["mjd"]))
    n_first = int(np.floor((first - epoch) / period)) - 2
    n_last = int(np.ceil((last - epoch) / period)) + 2
    found: list[tuple[int, float]] = []
    for cycle in range(n_first, n_last + 1):
        centre = epoch + (cycle + phase) * period
        if centre - half_days < first or centre + half_days > last:
            continue
        found.append((cycle, centre))
    if not found:
        raise SystemExit(f"phase {phase} has no eclipse inside the series")
    return found


def _caption(method: str, result: FitResult) -> str:
    """Title used on the MAVKA review card.

    ``ToM (MJD)`` is the time of minimum, as on the MAVKA review card.
    ``σ_t`` is the uncertainty of that time, in seconds. ``rms`` is the
    residual RMS of the fit. A missing number is the card's dash.

    Args:
        method (str): ``WSL``, ``WSAP`` or ``AP``.
        result (FitResult): Fit of one eclipse.

    Returns:
        str: Three lines for the figure title.
    """
    if result.time is None:
        tom = "ToM (MJD):"
    else:
        tom = f"ToM (MJD): {result.time:.2f}"
    if result.sigma_time is None:
        sigma = "σ_t: —"
    else:
        seconds = (result.sigma_time * u.day).to(u.second)
        sigma = f"σ_t: {seconds.value:.1f} s"
    if result.residual_rms is None:
        rms = "rms: —"
    else:
        rms = f"rms: {result.residual_rms:.4f}"
    return f"{method}\n{tom}\n{sigma}    {rms}"


def _plot_folded(series: dict, minima: dict) -> None:
    """Draw the folded magnitudes and the windows on the two found minima.

    Phase 0 is the reference epoch. The black line is the smoothed SAP flux,
    drawn in magnitude. The windows are centred on the two minima of that line.

    Args:
        series (dict): Values returned by ``_load``.
        minima (dict): Values returned by ``_folded_minima``.
    """
    phase = np.mod((series["mjd"] - series["epoch"]) / series["period"], 1.0)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 20, "font.family": "serif"}):
        fig, ax = plt.subplots(figsize=(16, 9))
        _shade(ax, minima["primary"], HALF_PHASE, "#e7298a")
        _shade(ax, minima["secondary"], HALF_PHASE, "#1f78b4")
        for shift in (-1.0, 0.0, 1.0):
            shown = phase + shift
            keep = (shown >= -0.5) & (shown <= 1.5)
            ax.scatter(
                shown[keep],
                series["magnitude"][keep],
                s=8,
                c="0.25",
                linewidths=0,
                rasterized=True,
                zorder=2,
            )
            smooth_phase = minima["bin_phase"] + shift
            keep_smooth = (smooth_phase >= -0.5) & (smooth_phase <= 1.5)
            ax.plot(
                smooth_phase[keep_smooth],
                minima["smooth_magnitude"][keep_smooth],
                color="black",
                lw=2,
                zorder=3,
            )
        ax.set_xlim(-0.5, 1.5)
        ax.invert_yaxis()
        ax.set_xlabel("Phase from the reference epoch")
        ax.set_ylabel("TESS magnitude")
        ax.set_title("TIC 388995726, sector 71, SAP")
        fig.tight_layout()
        path = OUTPUT / "s71_folded.png"
        fig.savefig(path)
        plt.close(fig)
    logger.info("figure %s", path)


def _shade(ax, centre: float, half: float, colour: str) -> None:
    """Shade one phase interval on every cycle that meets the axis.

    Args:
        ax: Matplotlib axes.
        centre (float): Phase of the minimum.
        half (float): Half-width in phase.
        colour (str): Colour of the shade.
    """
    for shift in range(-2, 4):
        start = centre + shift - half
        stop = centre + shift + half
        if stop < -0.5 or start > 1.5:
            continue
        ax.axvspan(start, stop, color=colour, alpha=0.28, lw=0, zorder=0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
