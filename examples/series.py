"""Small series for the fit examples.

The curve is the asymptotic parabola, evaluated with ``f_AP``, plus a
little noise. Positive curvature is a minimum of the series. Negative
curvature is a maximum of the series.
"""

from __future__ import annotations

import numpy as np

from ila_code.ila import f_AP_a


def asymptotic_series(curvature: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Build one noisy asymptotic parabola.

    Args:
        curvature (float): C2 of the model that generates the points.
        seed (int): Seed of the noise.

    Returns:
        tuple: Times and values. The core sits between 0.30 and 0.70.
    """
    time = np.linspace(0.0, 1.0, 41)
    values = np.asarray(f_AP_a(time, 10.0, curvature, 0.0, 0.30, 0.70), dtype=float)
    noise = np.random.default_rng(seed).normal(0.0, 0.02, size=time.size)
    return time, values + noise
