"""Release versions: a tag `vYYYY.MM.DD[.N]` and the PyPI version it publishes (`YYYY.MM.DD[.N]`).

Copied from figpress-plotly scripts/version.py at f6d48b2, without npm (no npm package yet).

    python scripts/version.py v2026.11.24          print {"pypi": ...}
    python scripts/version.py check [TAG]          exit 1 unless the Python version matches TAG
    python scripts/version.py set TAG              write the version
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"^v(\d{4})\.(\d{2})\.(\d{2})(?:\.(\d+))?$")
PY_VERSION = re.compile(r'^__version__ = "([^"]+)"$', re.M)
INIT = ROOT / "src" / "figpress_bokeh" / "__init__.py"


def versions(tag: str) -> dict[str, str]:
    m = TAG.match(tag)
    if not m:
        raise ValueError(f"{tag!r} is not a release tag vYYYY.MM.DD or vYYYY.MM.DD.N")
    year, month, day, n = m.groups()
    if n is not None and int(n) < 2:
        raise ValueError(f"{tag!r}: a same-day release number starts at 2")
    return {"pypi": f"{year}.{month}.{day}" + (f".{int(n)}" if n else "")}


def current() -> dict[str, str]:
    return {"pypi": PY_VERSION.search(INIT.read_text(encoding="utf-8")).group(1)}


def main(argv: list[str]) -> int:
    if argv[:1] == ["set"] and len(argv) == 2:
        want = versions(argv[1])
        INIT.write_text(PY_VERSION.sub(f'__version__ = "{want["pypi"]}"', INIT.read_text(encoding="utf-8")), encoding="utf-8")
        print(json.dumps(want))
        return 0
    if argv[:1] == ["check"]:
        have = current()
        tag = argv[1] if len(argv) == 2 else f"v{have['pypi']}"
        want = versions(tag)
        if have != want:
            print(f"version {have} does not match tag {tag} (expected {want})", file=sys.stderr)
            return 1
        print(f"ok: {tag} → {want}")
        return 0
    if len(argv) == 1:
        print(json.dumps(versions(argv[0])))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
