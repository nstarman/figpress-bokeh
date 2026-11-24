"""The print figure: Chrome prints the figure's page (drawn at K px per pt), and pdfium places that
page, scaled by 1/(0.75 K), on a page of exactly the figure's size (research R4).

The Chrome lookup is copied from figpress-plotly src/figpress_plotly/pdf.py at f6d48b2.
"""

import subprocess
import tempfile
from pathlib import Path

import pypdfium2 as pdfium

from .units import K


def chrome() -> str:
    """The Chrome or Chromium on this machine."""
    from choreographer.browsers.chromium import Chromium

    path = Chromium.find_browser(skip_local=False)
    if not path:
        raise RuntimeError("no Chrome or Chromium found: install one, or run `choreo_get_chrome` to fetch it")
    return path


def print_page(html: str, path: Path, page: tuple[float, float], budget_ms: int = 5000) -> Path:
    """Print `html` (a page from page.html) as a one-page PDF of exactly `page` pt at `path`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src, big = Path(tmp) / "print.html", Path(tmp) / "big.pdf"
        src.write_text(html, encoding="utf-8")
        r = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-sandbox",
                            f"--virtual-time-budget={budget_ms}", f"--print-to-pdf={big}", src.as_uri()],
                           capture_output=True, text=True)
        # Chrome can fail on its way out after writing the PDF: judge by the PDF, not the exit code.
        if not big.is_file() or big.stat().st_size == 0:
            raise RuntimeError(f"Chrome could not print the figure (exit {r.returncode}):\n{r.stderr[-2000:]}")
        _place(big, path, page)
    return path


def _place(big: Path, path: Path, page: tuple[float, float]) -> None:
    """Put the first page of `big` on a new page of `page` pt, scaled by 1/(0.75 K)."""
    src = pdfium.PdfDocument(str(big))
    if len(src) != 1:
        raise RuntimeError(f"Chrome printed {len(src)} pages; the figure's content leaves its page")
    dst = pdfium.PdfDocument.new()
    out = dst.new_page(*page)
    obj = src.page_as_xobject(0, dst).as_pageobject()
    obj.transform(pdfium.PdfMatrix().scale(1 / (0.75 * K), 1 / (0.75 * K)))
    out.insert_obj(obj)
    out.gen_content()
    dst.save(str(path))
