"""Regenerate one home's offline snapshot from the RUNNING server.

Usage: .venv/bin/python scripts/regen_home.py <Name> [verdict_file]
  <Name>        e.g. TowerB → writes data/out/fengshuiTowerB.html
  verdict_file  optional HTML fragment injected as its OWN first tab
                ("Verdict 结论", the landing tab)

The active data/house.json + data/rooms.json + floorplan.jpeg must already
hold the home being generated (swap → restart server → run this → restore).
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def inject_verdict_tab(html: str, verdict: str) -> str:
    """Verdict becomes its own primary tab and the landing pane (not a banner
    above every tab)."""
    old_btn = '<button class="tab active" data-tab="forme">'
    new_btn = ('<button class="tab active" data-tab="verdict">📋 Verdict 结论'
               '</button>\n    <button class="tab" data-tab="forme">')
    old_pane = '<section id="tab-forme" class="tabpane active"></section>'
    new_pane = ('<section id="tab-verdict" class="tabpane active">'
                f'{verdict}</section>\n  '
                '<section id="tab-forme" class="tabpane"></section>')
    assert old_btn in html and old_pane in html, "index.html structure changed"
    return html.replace(old_btn, new_btn).replace(old_pane, new_pane)


def main() -> None:
    name = sys.argv[1]
    verdict_file = sys.argv[2] if len(sys.argv) > 2 else None
    html = urllib.request.urlopen(
        "http://localhost:8808/snapshot?year=2026").read().decode("utf8")
    html = html.replace("fengshuiTowerA.html", f"fengshui{name}.html")
    if verdict_file:
        html = inject_verdict_tab(html, (ROOT / verdict_file).read_text("utf8"))
    out = ROOT / "data/out" / f"fengshui{name}.html"
    out.write_text(html, "utf8")
    print(f"{out} written ({len(html)} bytes)")


if __name__ == "__main__":
    main()
