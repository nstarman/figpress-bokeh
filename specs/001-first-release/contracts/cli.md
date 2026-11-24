# Contract: command line

```bash
figpress-bokeh build figures.py:grid --out build/                 # grid.pdf, grid/, grid.html
figpress-bokeh build figures.py:grid --out build/ --target pdf    # or --target web
figpress-bokeh compare build/grid.pdf reference.pdf --tol 1 --overlay overlay.png
```

Exit 0 on success; 1 when a comparison fails (the report names each element beyond `--tol`);
2 for usage errors. Errors are one line naming what is wrong.
