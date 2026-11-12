"""The package root exports the everyday fit and nothing else."""

from __future__ import annotations

import ila_code
from ila_code import FitResult, fit_extremum
from ila_code.fit import FitResult as FitResultModule
from ila_code.fit import fit_extremum as fit_extremum_module


def test_root_exports_the_fit() -> None:
    """Expose ``fit_extremum`` and ``FitResult`` from the package root.

    Returns:
        None.
    """
    assert ila_code.__all__ == ["FitResult", "fit_extremum"]
    assert fit_extremum is fit_extremum_module
    assert FitResult is FitResultModule
