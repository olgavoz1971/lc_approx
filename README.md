# lc_approx

Extended fork of [mpyat2/lc_approx](https://github.com/mpyat2/lc_approx). The approximation methods in `ila_code/ila.py` are the original ones. Licence: MIT. Copyright 2025 Maksym Yu. Pyatnytskyy.

## Install

The library needs NumPy and SciPy. Python 3.10 or newer.

```bash
pip install -e .
```

Distribution name `lc-approx`, version 0.1.0.

`ila_ap.py` and `split_lc.py` need the `cli` extra (pandas, matplotlib, colorama):

```bash
pip install -e ".[cli]"
```

## Import

```python
from ila_code.ila import approx, method_result, f_AP_a, f_WSAP_a, f_WSL_a, f_A_a
```

`approx(method, t_obs, m_obs, maxfev=12000)` returns `(params_opt, params_cov, param_warning)`.

`method_result(method, params_opt, params_cov, t_min, t_max)` returns the seven-value time-of-extremum tuple.

`f_AP_a`, `f_WSAP_a`, `f_WSL_a`, and `f_A_a` evaluate the fitted model and return lists.

Method ids: `AP`, `WSAP`, `WSL`, `A`.

## Golden results

Stored CLI times of extremum, and the commands that reproduce them, are in [approx_output/golden/README.md](approx_output/golden/README.md).

-------------------------------------------------------------------------------

# Original project description

The text below is the original README from mpyat2/lc_approx, unchanged.

Python scripts to approximate light curves with different approximation methods.
See, for example:

Andrych, Kateryna D.; Andronov, Ivan L.; Chinarova, Lidia L.
MAVKA: Program of Statistically Optimal Determination of Phenomenological Parameters of Extrema. Parabolic Spline Algorithm And Analysis of Variability of The Semi-Regular Star Z UMa
Journal of Physical Studies, Vol. 24, No. 1, Article 1902 [10 pages] (2020)
Bibcode: 2020JPhSt..24.1902A
DOI: 10.30970/jps.24.1902, 10.48550/arXiv.1912.07677

-------------------------------------------------------------------------------

Usage:

See examples (.bat files on Windows and .sh scripts on Linux)

1. ila_ap.py: Python script used to perform light curve approximations.
   Use ila_ap.py -h to display help.

2. split_lc.py: an auxiliary script to generate a file with time intervals for the batch mode approximation.

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------

![Screenshot1](screenshots/Screenshot1.png)
