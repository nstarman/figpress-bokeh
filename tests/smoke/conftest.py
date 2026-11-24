"""Smoke tests drive the built examples in a real browser: `uv run --group dev pytest -m smoke`.

Adapted from figpress-plotly tests/smoke/conftest.py at f6d48b2.
"""

import functools
import http.server
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "examples"


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """Both examples built for print and the web."""
    from figpress_bokeh.cli import load

    out = tmp_path_factory.mktemp("smoke")
    for name in ("bands", "grid"):
        figure = load(f"{ROOT / name / 'figure.py'}:{name}")
        figure.write_pdf(out / f"{name}.pdf")
        figure.write_web(out / name, single_file=out / f"{name}.html")
    return out


@pytest.fixture(scope="session")
def server(built):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(built))
    handler.log_message = lambda *a: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import Error, sync_playwright

    with sync_playwright() as p:
        try:
            b = p.chromium.launch()  # headless; CI installs Playwright's Chromium
        except Error:
            b = p.chromium.launch(channel="chrome")  # else the installed Chrome, still headless
        yield b
        b.close()


@pytest.fixture
def open_page(browser, server):
    """Open an example's folder page (or a URL) at a viewport width; record requests and console errors."""
    pages = []

    def go(name="bands", width=327, url=None, scale=1):
        page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=scale)
        page.requests, page.errors = [], []
        page.on("request", lambda r: page.requests.append(r.url))
        page.on("console", lambda m: m.type == "error" and page.errors.append(m.text))
        page.on("pageerror", lambda e: page.errors.append(str(e)))
        page.goto(url or f"{server}/{name}/index.html")
        page.wait_for_function("window.fbDrawn")
        pages.append(page)
        return page

    yield go
    for p in pages:
        p.close()
