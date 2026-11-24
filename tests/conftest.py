from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


@pytest.fixture(scope="session")
def example_pdf(tmp_path_factory):
    """The example built for print once per run (it takes a few seconds: Chrome)."""
    from figpress_bokeh.cli import load

    figure = load(f"{EXAMPLE / 'figure.py'}:bands")
    return figure.write_pdf(tmp_path_factory.mktemp("bands") / "bands.pdf"), figure


@pytest.fixture(scope="session")
def grid_pdf(tmp_path_factory):
    """The 2 x 2 grid example built for print once per run."""
    from figpress_bokeh.cli import load

    figure = load(f"{ROOT / 'examples' / 'grid' / 'figure.py'}:grid")
    return figure.write_pdf(tmp_path_factory.mktemp("grid") / "grid.pdf"), figure
