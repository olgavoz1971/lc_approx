"""Phenomenological approximations of variable-star light curves.

The root exports the everyday fit. ``approx``, ``method_result`` and the
model evaluators stay in ``ila_code.ila``. The command-line helpers stay
in ``ila_code.utils`` and are not imported here.
"""

from ila_code.fit import FitResult, fit_extremum

__all__ = ["FitResult", "fit_extremum"]
