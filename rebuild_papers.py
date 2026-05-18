#!/usr/bin/env python3
"""Normalize paper items: strip per-paper CCF badges; stack venue + links in paper-labels.

Site policy (do not revert):
- Never add CCF A / CCF B text badges (<span class="ccf-badge">) in paper lists.
- CCF level = paper-venue-tag color only (ccfa red, ccfb blue).
- Keep paper-labels left column equal width (--paper-label-col) and link-badge--code/project/news colors.
Run after any bulk paper HTML edits: python3 rebuild_papers.py
"""
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
CCF = re.compile(r'<span class="ccf-badge ccf-[ab]">CCF [AB]</span>\s*', re.I)
PAPER_OPEN = '<div class="paper-item">'

LEGEND_CN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>红色标签代表 CCF A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>蓝色标签代表 CCF B</span>
</p>"""

LEGEND_EN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>Red labels indicate CCF Class A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>Blue labels indicate CCF Class B</span>
</p>"""


def norm_title(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip().lower()[:120]


def paper_keys(block: str, title_html: str) -> list:
    keys = []
    hm = re.search(r'<a href="([^"]*)"', block)
    if hm:
        keys.append(hm.group(1))
    t = norm_title(title_html)
    if t:
        keys.append(t)
    return keys


def enhance_links(s: str) -> str:
    if not s:
        return s
    s = re.sub(
        r'<a class="link-badge"([^>]*)>Code</a>',
        r'<a class="link-badge link-badge--code"\1>Code</a>',
        s,
    )
    s = re.sub(
        r'<a class="link-badge"([^>]*)>Project</a>',
        r'<a class="link-badge link-badge--project"\1>Project</a>',
        s,
    )
    s = re.sub(
        r'<a class="link-badge"([^>]*)>News</a>',
        r'<a class="link-badge link-badge--news"\1>News</a>',
        s,
    )
    return s


def close_paper_item(section: str, start_inner: int) -> int:
    depth = 1
    j = start_inner
    n = len(section)
    while j < n and depth > 0:
        if section.startswith("<div", j):
            depth += 1
            j += 4
        elif section.startswith("</div>", j):
            depth -= 1
            j += 6
        else:
            j += 1
    return j


def extract_paper_blocks(section: str) -> List[str]:
    blocks = []
    pos = 0
    while True:
        start = section.find(PAPER_OPEN, pos)
        if start < 0:
            break
        inner = start + len(PAPER_OPEN)
        end = close_paper_item(section, inner)
        blocks.append(section[inner : end - 6].strip())
        pos = end
    return blocks


def parse_block(block: str) -> dict:
    block = CCF.sub("", block)
    vm = re.search(r'<span class="paper-venue-tag[^>]*>[^<]+</span>', block)
    venue = vm.group(0) if vm else ""
    tm = re.search(
        r'(<a href="[^"]*"[^>]*>[\s\S]*?</a>|<span style="font-weight:600[^>]*>[\s\S]*?</span>)',
        block,
    )
    title = tm.group(0) if tm else ""
    am = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
    authors = f'<div class="paper-authors">{am.group(1).strip()}</div>' if am else ""
    ptm = re.search(r'<div class="paper-tags">([\s\S]*?)</div>', block)
    tags = enhance_links(CCF.sub("", ptm.group(1)).strip()) if ptm else ""
    if not tags:
        links = re.findall(r'<a class="link-badge[^"]*"[^>]*>[^<]+</a>', block)
        tags = enhance_links("\n".join(links)) if links else ""
    return {
        "venue": venue,
        "title": title,
        "authors": authors,
        "tags": tags,
        "keys": paper_keys(block, title),
    }


def render_item(it: dict) -> str:
    tags_html = f'<div class="paper-tags">{it["tags"]}</div>' if it["tags"] else ""
    return (
        f'<div class="paper-item">\n'
        f'<div class="paper-labels">\n{it["venue"]}\n{tags_html}\n</div>\n'
        f'<div class="paper-content">\n{it["title"]}\n{it["authors"]}\n</div>\n'
        f'</div>'
    )


def build_author_db(paths: List[Path]) -> Dict:
    db = {}
    for path in paths:
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        sections = []
        ps = html.find('id="papers"')
        if ps >= 0:
            pe = html.find("<!-- PROJECTS -->", ps)
            if pe < 0:
                pe = html.find("</section>", ps)
            sections.append(html[ps:pe])
        sections.extend(
            re.findall(r'<div class="student-papers">([\s\S]*?)</article>', html)
        )
        for sec in sections:
            for block in extract_paper_blocks(sec):
                it = parse_block(block)
                if not it["authors"]:
                    continue
                for k in it["keys"]:
                    db[k] = it["authors"]
    return db


def fill_authors(it: dict, db: dict) -> dict:
    if it["authors"]:
        return it
    for k in it["keys"]:
        if k in db:
            it["authors"] = db[k]
            break
    return it


def replace_paper_items(section: str, db: dict) -> str:
    spans = []
    rendered = []
    pos = 0
    while True:
        start = section.find(PAPER_OPEN, pos)
        if start < 0:
            break
        inner = start + len(PAPER_OPEN)
        end = close_paper_item(section, inner)
        block = section[inner : end - 6]
        rendered.append(render_item(fill_authors(parse_block(block), db)))
        spans.append((start, end))
        pos = end
    for (start, end), html in zip(reversed(spans), reversed(rendered)):
        section = section[:start] + html + section[end:]
    return section


def rebuild_section(section: str, db: dict, legend: str) -> str:
    out = replace_paper_items(section, db)
    if "papers-ccf-legend" not in out:
        out = re.sub(
            r'(<div class="section-header">\s*<h2>[\s\S]*?</h2>\s*<div class="section-line"></div>\s*</div>)',
            r"\1\n" + legend,
            out,
            count=1,
        )
    return out


def papers_slice(html: str):
    s = html.find("<!-- PAPERS -->")
    e = html.find("<!-- PROJECTS -->", s)
    return html, s, e, html[s:e]


def rebuild_page(path: Path, db: dict, legend: str) -> None:
    html, s, e, sec = papers_slice(path.read_text(encoding="utf-8"))
    sec = rebuild_section(sec, db, legend)
    path.write_text(html[:s] + sec + html[e:], encoding="utf-8")
    out = path.read_text(encoding="utf-8")
    print(
        path.name,
        "items",
        out.count('class="paper-item"'),
        "authors",
        out.count("paper-authors"),
        "ccf_badges",
        len(re.findall(r'<span class="ccf-badge', out)),
    )


def rebuild_students(path: Path, db: dict) -> None:
    html = path.read_text(encoding="utf-8")
    pos, parts = 0, []
    while True:
        i = html.find('<div class="student-papers">', pos)
        if i < 0:
            parts.append(html[pos:])
            break
        j = html.find("</article>", i)
        chunk = replace_paper_items(html[i:j], db)
        parts += [html[pos:i], chunk]
        pos = j
    path.write_text("".join(parts), encoding="utf-8")
    out = path.read_text(encoding="utf-8")
    print(
        path.name,
        "labels",
        out.count("paper-labels"),
        "ccf_badges",
        len(re.findall(r'<span class="ccf-badge', out)),
    )


if __name__ == "__main__":
    backups = [ROOT / f"index_{i}.html" for i in (1, 2, 3)]
    extra = Path(
        "/Users/wangyongcai/Documents/[18]博客/个人主页/yongcaiwang.github.io/students.html"
    )
    db = build_author_db(backups + [extra, ROOT / "students.html"])
    rebuild_page(ROOT / "index.html", db, LEGEND_CN)
    rebuild_page(ROOT / "index_en.html", db, LEGEND_EN)
    rebuild_students(ROOT / "students.html", db)
