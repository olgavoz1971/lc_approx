---
name: lc-approx
description: >-
  Fit one light-curve extremum with lc_approx (AP, WSAP, WSL, A) via
  fit_extremum from ila_code. Use when a time of extremum, its formal
  error, a maximum or minimum of the supplied series, or a failed window
  is required. Do not add an approximation method or edit the model functions.
---

# lc_approx fits

Call `fit_extremum` from `ila_code`. Do not call `approx` and then stop the batch on the first exception. Do not add another approximation method. Do not edit `f_AP`, `f_WSAP`, `f_WSL`, `f_A`, `approx`, or the files under `approx_output/golden/`.

```python
from ila_code import fit_extremum, FitResult
```

`approx`, `method_result` and the evaluators `f_AP_a`, `f_WSAP_a`, `f_WSL_a`, `f_A_a` stay in `ila_code.ila`. Import them from there when the task needs the model. `extremum_terms` is the vertex before the command-line wipe. Do not copy it onto a result. `original_demos/` is the original command-line bundle, not a second interface.

`tests/test_golden_cli.py` re-runs `original_demos/ila_ap.py` and compares the text files with `approx_output/golden/`. `tests/test_fit_matches_golden.py` checks that `fit_extremum` returns those times. A mismatch is a failed test. Leave the stored files in place. The capture stack is Python 3.10.12, NumPy 2.2.6 and SciPy 1.14.0.

The series is the array the caller passes. The fit is unweighted: there is no weight argument. `kind` is `maximum` or `minimum` of that array. For AP and WSAP this is the sign of C2. Negative C2 is a maximum of the array. Use the same call. Do not flip the array and do not add a maxima method.

## What the result means

- `sigma_time` is the formal covariance error of the time. `residual_rms` is the scatter of the residuals. Report `sigma_time` as the timing error. Do not scale it to the residuals.
- A filled `time` is the command-line time of extremum. That covers `accepted`, `bounds_outside`, `short_core` and `sigma_missing`. The status says what else that row carried. It does not delete a time the script kept.
- An empty `time` is the golden `nan`. `method_result` did not return a finite time (the AP or WSAP vertex was outside `[C4, C5]`, or the fit did not form a time). Do not invent one. `extremum_terms` still holds the algebraic vertex; `fit_extremum` does not copy it onto the result.
- AP time is the vertex of the parabola. WSAP time is the midpoint of C4 and C5. WSL time is the midpoint of the flat part. Method A time is the break at C4.
- Fewer points than coefficients is `too_few_points`: 5 for AP, WSAP and WSL, 4 for A. Do not impose a minimum of 6 in this package. Fit the next window anyway.
- `maxfev` on `fit_extremum` defaults to 100000, which is what `original_demos/ila_ap.py` passes. `approx` still defaults to 12000.
- The `1e-30` check before dividing by C2 is a local numerical guard, not a constant of the AP method.

Examples: `examples/minimum_ap.py`, `examples/maximum_ap.py`, `examples/wsl_sigma_missing.py`, `examples/batch_continues.py`.
