# Fit examples

`simple_example.py` fits the whole of `original_demos/test_data/V405_Dra.dat`
and `original_demos/test_data/KP_Lyn-2.dat` with AP, WSAP, WSL and A.

```bash
python examples/simple_example.py
```

The PNGs are written under `examples/output/`. Matplotlib is required
(`pip install ".[cli]"`). The magnitude axis has the faint direction
downward. The left wing is `#6a3d9a`, the core `#33a02c`, the right
wing `#ff7f00`. C4 and C5 are dotted maroon lines. A filled time is a
`#e7298a` dashed line. When the uncertainty of that time is finite, the
same colour shades the interval and draws a dotted line at each edge.
An empty time is not marked.

`tess_s71.py` uses a real TESS light curve,
`data/TIC388995726_s71_TESS-SPOC_part.vot`. That file needs volightcurve
0.1.0 or newer, which is not part of this package. It can be installed
from https://github.com/olgavoz1971/volightcurve.git. The script reads it
with volightcurve and keeps the SAP flux. The epoch in the file is only
the reference for the phase count. The script bins the folded SAP flux,
smooths it, and takes the two minima of that smooth curve. Those phases
centre the windows. The phase half-width is the constant `HALF_PHASE`.
The folded light curve is `examples/output/s71_folded.png`. It is drawn
in magnitudes and shows the windows around both minima. The magnitudes
come from the PHOTCAL declared in the VOTable:
`photdms["sap_flux"].photcal.flux_to_mag`. Every eclipse of both minima
is then fitted with
WSL, WSAP and AP in flux. Those pictures are in `examples/output/fits/`,
one file per eclipse and method. The title follows the MAVKA review
card: `ToM (MJD)`, `σ_t` in seconds, and the residual `rms`. The
horizontal axis is MJD.

```bash
python examples/tess_s71.py
```
