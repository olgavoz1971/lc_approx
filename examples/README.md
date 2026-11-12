# Fit examples

`simple_example.py` fits the whole of `original_demos/test_data/V405_Dra.dat`
and `original_demos/test_data/KP_Lyn-2.dat` with AP, WSAP, WSL and A.

```bash
python examples/simple_example.py
```

The PNGs are written under `examples/output/`. Matplotlib is required
(`pip install ".[cli]"`). The magnitude axis has the faint direction
downward. The left wing is `#6a3d9a`, the core `#33a02c`, the right
wing `#ff7f00`. A filled time with a formal error is a `#e7298a` line.
A filled time whose formal error is empty is a `#ff7f00` line. An empty
time is not marked.

The earlier synthetic examples are in `examples/temporal_back/`.
