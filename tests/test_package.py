"""The package imports, says what it is, and its version maps to a tag."""

import importlib.util
from pathlib import Path

import figpress_bokeh

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("version", ROOT / "scripts" / "version.py")
version = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(version)


def test_version_and_status():
    assert figpress_bokeh.__doc__ and "early development" in figpress_bokeh.__doc__
    assert version.current() == version.versions(f"v{figpress_bokeh.__version__}")


def test_tag_mapping():
    assert version.versions("v2026.11.24.2") == {"pypi": "2026.11.24.2"}
