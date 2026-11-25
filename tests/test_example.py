"""The example's print figure matches its matplotlib reference within 1 pt (SC-001)."""

from pathlib import Path

from figpress_bokeh import compare

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


def test_matches_the_reference(example_pdf, tmp_path):
    path, _ = example_pdf
    result = compare(path, EXAMPLE / "reference.pdf", tol=1.0, overlay=tmp_path / "overlay.png")
    assert result.ok, result.report()
    assert len([e for e in result.elements if e.kind == "frame"]) == 4


def test_the_grid_matches_its_reference(grid_pdf, tmp_path):
    """Four panels, shared axes, panel labels, one legend (SC-002): within 1 pt, every frame line
    within 0.3 pt (BokehJS draws outlines up to 0.25 pt inside the frame)."""
    path, _ = grid_pdf
    result = compare(path, ROOT / "examples" / "grid" / "reference.pdf", tol=1.0, overlay=tmp_path / "overlay.png")
    assert result.ok, result.report()
    frames = [e for e in result.elements if e.kind == "frame"]
    assert len(frames) == 8 and all(abs(e.dx) <= 0.3 and abs(e.dy) <= 0.3 for e in frames), result.report()
