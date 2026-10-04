"""Find a Chromium/Chrome to turn the HTML paper into a PDF (via Playwright)."""

from __future__ import annotations

import glob
import os
import shutil
from contextlib import contextmanager
from pathlib import Path

CANDIDATES = [
    os.environ.get("NEWSPAPER_CHROME", ""),
    "/opt/pw-browsers/chromium",
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
    shutil.which("google-chrome") or "",
]


class BrowserMissing(RuntimeError):
    pass


def find_executable() -> str | None:
    for path in CANDIDATES:
        if path and Path(path).exists():
            return path
    return None


@contextmanager
def chromium():
    """Yield a launched Playwright Chromium browser.

    Tries Playwright's own browser first, then any Chrome/Chromium found on disk.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on the machine
        raise BrowserMissing(
            "Playwright isn't installed. Run: python3 -m pip install -r requirements.txt"
        ) from exc

    with sync_playwright() as p:
        browser = None
        errors = []
        exe = find_executable()
        attempts = [{"executable_path": exe}] if exe else []
        attempts.append({})
        for kwargs in attempts:
            try:
                browser = p.chromium.launch(**kwargs)
                break
            except Exception as exc:  # noqa: BLE001 - report every failed attempt
                errors.append(str(exc).splitlines()[0])
        if browser is None:
            raise BrowserMissing(
                "Couldn't start Chromium. Install it with `python3 -m playwright install chromium` "
                "or set NEWSPAPER_CHROME to a Chrome/Chromium binary.\n  " + "\n  ".join(errors)
            )
        try:
            yield browser
        finally:
            browser.close()
