#!/usr/bin/env python3
"""Remove per-paper CCF A/B badges; add legend at top of papers section."""

import re
import sys
from pathlib import Path

LEGEND_CN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>红色标签代表 CCF A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>蓝色标签代表 CCF B</span>
</p>"""

LEGEND_EN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>Red labels indicate CCF Class A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>Blue labels indicate CCF Class B</span>
</p>"""

CSS = """
  .papers-ccf-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px 28px;
    margin: 0 0 22px;
    font-size: var(--text-sm);
    color: var(--ink-light);
    line-height: 1.6;
  }

  .papers-ccf-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .papers-ccf-legend-swatch {
    min-width: 40px;
    margin: 0;
    flex-shrink: 0;
  }
"""

CCF_BADGE_RE = re.compile(
    r'<span class="ccf-badge ccf-[ab]">CCF [AB]</span>\s*',
    re.IGNORECASE,
)
EMPTY_TAGS_RE = re.compile(r'<div class="paper-tags">\s*</motion>\s*</motion>', re.MULTILINE)
EMPTY_TAGS_RE = re.compile(r'<div class="paper-tags">\s*</motion>', re.MULTILINE)


def strip_badges_in_papers(html: str) -> str:
    start = html.find('id="papers"')
    if start < 0:
        return html
    end = html.find("<!-- PROJECTS -->", start)
    if end < 0:
        return html
    section = html[start:end]
    section = CCF_BADGE_RE.sub("", section)
    section = re.sub(r"<div class=\"paper-tags\">\s*</div>", "", section)
    return html[:start] + section + html[end:]


def add_legend(html: str, legend: str) -> str:
    marker = '<motion class="papers-ccf-legend">'
    if "papers-ccf-legend" in html:
        return html
    insert_after = '<motion class="section-line"></motion>\n</motion>\n<div class="year-group">'
    # actual pattern
    pattern = r'(<section class="section" id="papers">[\s\S]*?<div class="section-line"></div>\s*</div>)'
    m = re.search(pattern, html)
    if not m:
        return html
    return html[: m.end()] + "\n" + legend + html[m.end() :]


def add_css(html: str) -> str:
    if ".papers-ccf-legend" in html:
        return html
    anchor = "  .year-group { margin-bottom: 32px; }"
    if anchor not in html:
        anchor = "  .year-label {"
    return html.replace(anchor, CSS + "\n" + anchor, 1)


def process(path: Path, legend: str) -> None:
    html = path.read_text(encoding="utf-8")
    html = strip_badges_in_papers(html)
    html = add_legend(html, legend)
    html = add_css(html)
    path.write_text(html, encoding="utf-8")
    print("updated", path.name)


def main() -> None:
    root = Path(__file__).resolve().parent
    files = [
        (root / "index.html", LEGEND_CN),
        (root / "index_en.html", LEGEND_EN),
    ]
    if len(sys.argv) > 1:
        files = [(Path(p), LEGEND_EN if "en" in p.name else LEGEND_CN) for p in sys.argv[1:]]
    for path, legend in files:
        process(path, legend)


if __name__ == "__main__":
    main()
