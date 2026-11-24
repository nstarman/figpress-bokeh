import pytest

from figpress_bokeh.units import K, dash, font, pt


def test_eight_px_per_point():
    assert K == 8 and pt(3) == pytest.approx(24) and font(7) == "56px" and font(5.5) == "44px"


def test_matplotlib_dashes_scale_with_line_width():
    assert dash(":", 0.75) == [6.0, 9.9]                 # (1, 1.65) × 0.75 pt × 8 px/pt
    assert dash("--", 1.5) == [44.4, 19.2]
    assert len(dash("-.", 0.75)) == 4


def test_explicit_lengths_are_points():
    assert dash((3, 1.5)) == [24, 12]


def test_unknown_style_is_named():
    with pytest.raises(ValueError, match="'~'"):
        dash("~")
