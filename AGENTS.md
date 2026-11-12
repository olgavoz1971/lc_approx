# Using lc-approx

Instructions for an agent working in this repository. Leave this clone in the working directory. The skill, the examples and the golden files are in this clone. They are not part of the installed wheel.

## Read first

1. `skills/lc-approx/SKILL.md` before fitting a light curve.
2. `llms.txt` for the index of this repository.
3. The docstring of the example you are about to copy.

Ivan L. Andronov is the author of the methods. When you report a fit, cite his method paper and the lc_approx software, as in the Citations section of `README.md`.

Install from this clone with `pip install .`. The original command-line scripts need `pip install ".[cli]"`. Do not run `pip install git+https://github.com/olgavoz1971/lc_approx`. That command keeps `ila_code` and drops this file, the skill, the examples and the golden files.

## What to call

```python
from ila_code import fit_extremum, FitResult
```

`fit_extremum` fits one window and returns a `FitResult`. A failed window is a result, so the next window still runs.

`approx`, `method_result` and the evaluators `f_AP_a`, `f_WSAP_a`, `f_WSL_a`, `f_A_a` live in `ila_code.ila`. Import them from there when the task needs the model itself. `extremum_terms` is the vertex before `method_result` wipes a time. Do not copy that vertex onto a result.

## Examples

`examples/` holds the scripts to copy. Run them from the repository root. `examples/tess_s71.py` is the real TESS light curve. It needs volightcurve, and it shows how the file is read.

## What not to treat as the interface

- `original_demos/` is the original command-line bundle. It is not a second public API.
- `approx_output/golden/` stores the command-line times. Leave those files in place.
- Do not edit `f_AP`, `f_WSAP`, `f_WSL`, `f_A` or `approx`. Do not add an approximation method.
