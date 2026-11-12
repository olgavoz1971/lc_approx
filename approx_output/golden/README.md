# Golden CLI results

Numeric output of `ila_ap.py` before the tree is turned into an installable
package. A later change is acceptable when a fresh run matches the
`Time of Extremum (TOM)` column in these files.

Captured with Python 3.10.12, NumPy 2.2.6, SciPy 1.14.0. A second run of
every command below matched these files byte for byte.

`ila.py`, the demo shell scripts, and `MAXFEV` in `ila_ap.py` were not
edited. `--no-plot` is passed only on these capture commands. HTML
previews are written outside this directory and are not part of the check.
Method `0` (plot only) is omitted.

Run the commands from the repository root. `MPLBACKEND=Agg` keeps
matplotlib off the display.

## Single extremum

V405 Dra (`testV405_Dra_AP.sh`, `testV405_Dra_WSAP.sh`,
`testV405_Dra_WSL.sh`, `testV405_Dra_A.sh`):

```bash
python3 ila_ap.py test_data/V405_Dra.dat --method=AP --no-plot \
  --result approx_output/golden/V405_Dra_AP.txt \
  --preview /tmp/lc_approx_preview/V405_Dra_AP.html

python3 ila_ap.py test_data/V405_Dra.dat --method=WSAP --no-plot \
  --result approx_output/golden/V405_Dra_WSAP.txt \
  --preview /tmp/lc_approx_preview/V405_Dra_WSAP.html

python3 ila_ap.py test_data/V405_Dra.dat --method=WSL --no-plot \
  --result approx_output/golden/V405_Dra_WSL.txt \
  --preview /tmp/lc_approx_preview/V405_Dra_WSL.html

python3 ila_ap.py test_data/V405_Dra.dat --method=A --no-plot \
  --result approx_output/golden/V405_Dra_A.txt \
  --preview /tmp/lc_approx_preview/V405_Dra_A.html
```

KP Lyn-2. The shell scripts call AP and A only
(`testKP_Lyn-2_AP.sh`, `testKP_Lyn-2_A.sh`). WSAP and WSL use the same
file so each page method is on record:

```bash
python3 ila_ap.py test_data/KP_Lyn-2.dat --method=AP --no-plot \
  --result approx_output/golden/KP_Lyn-2_AP.txt \
  --preview /tmp/lc_approx_preview/KP_Lyn-2_AP.html

python3 ila_ap.py test_data/KP_Lyn-2.dat --method=WSAP --no-plot \
  --result approx_output/golden/KP_Lyn-2_WSAP.txt \
  --preview /tmp/lc_approx_preview/KP_Lyn-2_WSAP.html

python3 ila_ap.py test_data/KP_Lyn-2.dat --method=WSL --no-plot \
  --result approx_output/golden/KP_Lyn-2_WSL.txt \
  --preview /tmp/lc_approx_preview/KP_Lyn-2_WSL.html

python3 ila_ap.py test_data/KP_Lyn-2.dat --method=A --no-plot \
  --result approx_output/golden/KP_Lyn-2_A.txt \
  --preview /tmp/lc_approx_preview/KP_Lyn-2_A.html
```

## Batch

Same inputs as `test_batch_approx.sh`: `test_data/test_lc.tsv` with
ranges `test_data/lc_split.!`, methods AP, WSAP, and WSL. That script
does not run method A.

```bash
python3 ila_ap.py --method=AP --no-plot \
  --ranges=test_data/lc_split.! test_data/test_lc.tsv \
  --result approx_output/golden/batch_AP.txt \
  --preview /tmp/lc_approx_preview/batch_AP.html

python3 ila_ap.py --method=WSAP --no-plot \
  --ranges=test_data/lc_split.! test_data/test_lc.tsv \
  --result approx_output/golden/batch_WSAP.txt \
  --preview /tmp/lc_approx_preview/batch_WSAP.html

python3 ila_ap.py --method=WSL --no-plot \
  --ranges=test_data/lc_split.! test_data/test_lc.tsv \
  --result approx_output/golden/batch_WSL.txt \
  --preview /tmp/lc_approx_preview/batch_WSL.html
```

Each batch file has a header plus 61 data rows. Warning rows are stored
as the CLI wrote them, including `nan` times of extremum.
