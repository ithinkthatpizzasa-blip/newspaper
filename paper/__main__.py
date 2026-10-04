"""Command line for The Morning Newspaper.

    python3 -m paper gather                  # weather, headlines, calendar -> build/<date>/sources.json
    python3 -m paper render build/<date>/edition.json
    python3 -m paper sample                  # render the bundled sample edition
    python3 -m paper avatars                 # the A-D avatar picker sheet
    python3 -m paper avatar                  # preview the reader's avatar
    python3 -m paper print editions/<file>.pdf
    python3 -m paper check                   # what works on this machine
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from . import gather as gather_mod
from . import profile as prof
from .avatar import avatar_standalone
from .browser import BrowserMissing, chromium, find_executable
from .render import BUILD, fonts_css, render

PICKER = [
    ("A", {"hair_style": "bob", "hair_color": "black"}),
    ("B", {"hair_style": "long", "hair_color": "blonde"}),
    ("C", {"hair_style": "spiky", "hair_color": "black"}),
    ("D", {"hair_style": "side-part", "hair_color": "light"}),
]


def _load_profile(path: str | None) -> dict:
    try:
        return prof.load(path)
    except prof.ProfileMissing as exc:
        sys.exit(str(exc))


def _sheet_png(cells: list[tuple[str, str]], out: Path, title: str, cols: int = 2) -> Path:
    tiles = "".join(f'<figure><div class="art">{svg}</div><figcaption>{label}</figcaption></figure>'
                    for label, svg in cells)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css()}
    body{{margin:0;padding:18px;background:#fff;font-family:'Oswald',sans-serif;width:{cols * 230 + 36}px}}
    h1{{font:600 20px/1 'Oswald';text-transform:uppercase;letter-spacing:.08em;margin:0 0 12px;text-align:center}}
    .grid{{display:grid;grid-template-columns:repeat({cols},230px);gap:0;border:2px solid #141414;width:max-content;margin:0 auto}}
    figure{{margin:0;border:1px solid #141414;position:relative}}
    figure .art svg{{display:block;width:100%;height:auto}}
    figcaption{{position:absolute;top:6px;left:8px;font:600 22px/1 'Oswald'}}
    </style></head><body><h1>{title}</h1><div class="grid">{tiles}</div></body></html>"""
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".html")
    tmp.write_text(html)
    with chromium() as browser:
        page = browser.new_page(device_scale_factor=2)
        page.goto(tmp.resolve().as_uri())
        page.evaluate("document.fonts.ready.then(() => true)")
        page.locator("body").screenshot(path=str(out))
    tmp.unlink()
    return out


def cmd_gather(args) -> None:
    profile = _load_profile(args.profile)
    day = date.fromisoformat(args.date) if args.date else None
    path = gather_mod.write(profile, day)
    data = json.loads(path.read_text())
    print(f"Wrote {path}")
    print(f"  weather:   {'yes' if data.get('weather') else 'no'}")
    if data.get("top_headlines"):
        print(f"  {data['top_headlines']['title']}: {len(data['top_headlines']['items'])} items")
    print(f"  headlines: {', '.join(f'{k} ({len(v)})' for k, v in data['headlines'].items()) or 'none'}")
    if "calendar" in data:
        print(f"  calendar:  {len(data['calendar']['today'])} today, {len(data['calendar']['upcoming'])} coming up")
    for problem in data["problems"]:
        print(f"  ! {problem}")


def _report(result, allow_overflow: bool) -> int:
    print(f"PDF:      {result.pdf}  ({result.pages} pages, {result.pdf.stat().st_size // 1024} KB)")
    for png in result.previews:
        print(f"Preview:  {png}")
    if result.pages != 2:
        print(f"! Expected 2 pages, got {result.pages}.")
    for f in result.fit:
        verb = "trim about" if f["problem"] == "too long" else "room for about"
        print(f"! {f['box']}: {f['problem']} ({f['words']} words; {verb} {f['change']} words)")
    if not result.fit:
        print("Everything fits.")
    return 3 if result.overflow and not allow_overflow else 0


def cmd_render(args) -> None:
    profile = _load_profile(args.profile)
    edition = json.loads(Path(args.edition).read_text())
    try:
        result = render(profile, edition, out_dir=args.out, previews=not args.no_previews)
    except BrowserMissing as exc:
        sys.exit(str(exc))
    sys.exit(_report(result, args.allow_overflow))


def cmd_sample(args) -> None:
    profile = json.loads(prof.EXAMPLE_PATH.read_text())
    edition = json.loads((Path(__file__).parent / "samples" / "sample-edition.json").read_text())
    result = render(profile, edition, out_dir=BUILD / "sample", build_dir=BUILD / "sample")
    sys.exit(_report(result, True))


def cmd_avatars(args) -> None:
    cells = [(label, avatar_standalone(look, "happy", size=230)) for label, look in PICKER]
    print(_sheet_png(cells, Path(args.out), "Pick your avatar"))


def cmd_avatar(args) -> None:
    profile = _load_profile(args.profile)
    look = profile.get("avatar") or {}
    moods = args.moods.split(",")
    cells = [(m, avatar_standalone(look, m, size=230)) for m in moods]
    print(_sheet_png(cells, Path(args.out), f"{prof.reader(profile)}'s character", cols=min(len(cells), 3)))


def cmd_print(args) -> None:
    lp = shutil.which("lp")
    if not lp:
        sys.exit("No printing system here (this is probably a cloud machine). Print from your own computer instead.")
    printers = subprocess.run(["lpstat", "-p", "-d"], capture_output=True, text=True).stdout
    if "printer" not in printers:
        sys.exit("No printers found on this computer.")
    cmd = [lp, "-o", "media=A4", "-o", "fit-to-page"]
    if args.printer:
        cmd += ["-d", args.printer]
    cmd.append(args.pdf)
    out = subprocess.run(cmd, capture_output=True, text=True)
    print(out.stdout.strip() or out.stderr.strip())
    sys.exit(out.returncode)


def cmd_check(args) -> None:
    ok = True
    try:
        profile = prof.load(args.profile)
        print(f"profile:   {prof.paper_name(profile)} for {prof.reader(profile)} in {prof.city(profile)}")
    except prof.ProfileMissing as exc:
        profile = json.loads(prof.EXAMPLE_PATH.read_text())
        print(f"profile:   missing ({exc})")
        ok = False
    exe = find_executable()
    try:
        import playwright  # noqa: F401
        print(f"browser:   playwright installed; chromium at {exe or 'Playwright default'}")
    except ImportError:
        print("browser:   playwright missing (python3 -m pip install -r requirements.txt)")
        ok = False
    probes = {
        "weather": "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=0&daily=weather_code&forecast_days=1",
        "headlines": "https://feeds.bbci.co.uk/news/rss.xml",
    }
    for name, url in probes.items():
        try:
            gather_mod._get(url, timeout=8)
            print(f"{name + ':':<10} reachable")
        except gather_mod.SourceError as exc:
            print(f"{name + ':':<10} not reachable: {exc} (Claude can use web search instead)")
    print(f"printing:  {'available' if shutil.which('lp') else 'not available here'}")
    sys.exit(0 if ok else 1)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python3 -m paper", description="The Morning Newspaper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gather", help="fetch weather, headlines and calendar")
    g.add_argument("--date")
    g.add_argument("--profile")
    g.set_defaults(fn=cmd_gather)

    r = sub.add_parser("render", help="turn an edition.json into the PDF paper")
    r.add_argument("edition")
    r.add_argument("--profile")
    r.add_argument("--out", help="folder for the PDF (default: editions/)")
    r.add_argument("--no-previews", action="store_true")
    r.add_argument("--allow-overflow", action="store_true", help="exit 0 even if some text doesn't fit")
    r.set_defaults(fn=cmd_render)

    s = sub.add_parser("sample", help="render the bundled sample edition")
    s.set_defaults(fn=cmd_sample)

    a = sub.add_parser("avatars", help="draw the A-D avatar picker")
    a.add_argument("--out", default=str(BUILD / "avatars.png"))
    a.set_defaults(fn=cmd_avatars)

    v = sub.add_parser("avatar", help="preview the reader's avatar")
    v.add_argument("--profile")
    v.add_argument("--moods", default="happy,excited,thinking")
    v.add_argument("--out", default=str(BUILD / "avatar.png"))
    v.set_defaults(fn=cmd_avatar)

    p = sub.add_parser("print", help="send a PDF to a printer (on your own computer)")
    p.add_argument("pdf")
    p.add_argument("--printer")
    p.set_defaults(fn=cmd_print)

    c = sub.add_parser("check", help="see what works on this machine")
    c.add_argument("--profile")
    c.set_defaults(fn=cmd_check)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
