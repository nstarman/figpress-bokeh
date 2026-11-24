"""The web figure: a page folder, and the same page as one self-contained HTML file. Nothing is loaded
from another host: BokehJS, the runtime and the fonts are included at their versions.

The layout of the folder follows figpress-plotly src/figpress_plotly/web.py at f6d48b2.
"""

import html
import json
import shutil
from pathlib import Path

import bokeh
from bokeh.resources import Resources

from . import __version__
from .page import PAGE, RUNTIME, spec, standalone


def write_web(built, out: Path, single_file: Path | None = None) -> Path:
    """Write the page folder `out` (index.html, figure.json, fonts/, vendor/) for a figure built for
    "web"; with `single_file`, also the page as one HTML file. Returns `out`. The folder must be
    served over http (browsers refuse ES module imports from file://); the single file opens from disk."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "fonts").mkdir(parents=True)
    files = built.fonts.files()
    for family, path in files.items():
        shutil.copyfile(path, out / "fonts" / f"{family}{path.suffix}")
    s = spec(built, {fam: f"fonts/{fam}{p.suffix}" for fam, p in files.items()})
    (out / "figure.json").write_text(json.dumps(s), encoding="utf-8")
    bokeh_js = f"vendor/bokeh-{bokeh.__version__}.min.js"
    runtime = f"vendor/figpress-bokeh-{__version__}/index.js"
    (out / runtime).parent.mkdir(parents=True)
    (out / bokeh_js).write_text(Resources(mode="inline", components=["bokeh"]).js_raw[0], encoding="utf-8")
    shutil.copyfile(RUNTIME, out / runtime)
    boot = (f'<script type="module">\nimport {{ mount }} from "./{runtime}";\n'
            'const spec = await (await fetch("figure.json")).json();\n'
            'window.fbFigure = await mount(document.getElementById("figure"), spec);\n</script>')
    (out / "index.html").write_text(PAGE.format(title=html.escape(built.name), version=__version__, style="",
                                                bokeh=f'<script src="{bokeh_js}"></script>', boot=boot),
                                    encoding="utf-8")
    if single_file is not None:
        Path(single_file).parent.mkdir(parents=True, exist_ok=True)
        Path(single_file).write_text(standalone(built), encoding="utf-8")
    return out
