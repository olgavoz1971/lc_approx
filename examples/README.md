# Fit examples

Run these from the repository root. They call `fit_extremum` from `ila_code`.

```bash
python examples/minimum_ap.py
python examples/maximum_ap.py
python examples/wsl_sigma_missing.py
python examples/batch_continues.py
```

`minimum_ap.py` fits an asymptotic parabola. `formal_sigma` is the
covariance error of the time. `residual_rms` is the scatter of the
residuals. A filled `time` is the command-line time of extremum.
An empty `time` is the golden `nan`.

`maximum_ap.py` is the same call on a series with negative C2. The
result says `maximum` of that series.

`wsl_sigma_missing.py` is a flat series. The time is the midpoint of
C4 and C5 and is the command-line time. The formal error is empty, and
the status is `sigma_missing`.

`batch_continues.py` fits the next window after a failure. Four points
are too few for AP. A library time that is not finite stays empty.
A core shorter than its formal error is `short_core`. Method A on five
points is passed to the optimiser.
