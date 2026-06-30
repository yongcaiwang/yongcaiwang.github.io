#!/usr/bin/env python3
"""移除 CCF A/B；venue + Code/Project 竖排左列；补图例。"""

import re
from pathlib import Path

CCF = re.compile(r'<span class="ccf-badge ccf-[ab]">CCF [AB]</span>\s*', re.I)
TAIL = r'(?=\n<div class="paper-item">|\n</motion>\n<div class="year-group">|\n</div>\n<div class="year-group">|\n</div>\n</article>|\n</div>\n</section>)'
TAIL = r'(?=\n<div class="paper-item">|\n</div>\n<div class="year-group">|\n</div>\n</article>|\n</div>\n</section>)'

LEGEND_CN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>红色标签代表 CCF A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>蓝色标签代表 CCF B</span>
</p>"""

LEGEND_EN = """<p class="papers-ccf-legend">
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfa papers-ccf-legend-swatch" aria-hidden="true">A</span>Red labels indicate CCF Class A</span>
<span class="papers-ccf-legend-item"><span class="paper-venue-tag ccfb papers-ccf-legend-swatch" aria-hidden="true">B</span>Blue labels indicate CCF Class B</span>
</p>"""


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


def restructure_item(block: str) -> str:
    block = CCF.sub("", block)
    vm = re.search(r'<span class="paper-venue-tag[^>]*>[^<]+</span>', block)
    if not vm:
        return block.strip()
    venue = vm.group(0)

    tm = re.search(r'<div class="paper-tags">([\s\S]*?)</div>', block)
    tags_inner = enhance_links(CCF.sub("", tm.group(1)).strip()) if tm else ""
    tags_html = f'<motion class="paper-tags">{tags_inner}</motion>' if tags_inner else ""
    tags_html = f'<div class="paper-tags">{tags_inner}</div>' if tags_inner else ""

    body = block
    if tm:
        body = body[: tm.start()] + body[tm.end() :]
    body = body[vm.end() :]
    body = re.sub(r'<div class="paper-labels">[\s\S]*?</div>\s*', "", body, count=1)

    cm = re.search(r'<div class="paper-content">\s*([\s\S]*?)\s*</div>', body)
    inner = cm.group(1) if cm else body
    inner = re.sub(r'<div class="paper-tags">[\s\S]*?</motion>', "", inner)
    inner = re.sub(r'<div class="paper-tags">[\s\S]*?</motion>', "", inner)
    inner = re.sub(r'<div class="paper-tags">[\s\S]*?</div>', "", inner)
    inner = CCF.sub("", inner).strip()

    title_m = re.search(
        r'(<a href="[^"]*"[^>]*>[\s\S]*?</a>|<span style="font-weight:600[^>]*>[\s\S]*?</span>)',
        inner,
    )
    auth_m = re.search(r'<div class="paper-authors">[\s\S]*?</div>', inner)
    title = title_m.group(0).strip() if title_m else ""
    authors = auth_m.group(0) if auth_m else ""

    return (
        f'<div class="paper-labels">\n{venue}\n{tags_html}\n</div>\n'
        f'<div class="paper-content">\n{title}\n{authors}\n</div>'
    )


def rewrite_items(chunk: str) -> str:
    def repl(m):
        return f'<div class="paper-item">\n{restructure_item(m.group(1))}\n</div>'

    return re.sub(
        rf'<div class="paper-item">\s*([\s\S]*?)\s*</div>\s*{TAIL}',
        repl,
        chunk,
    )


def fix_papers_section(section: str, legend: str) -> str:
    section = rewrite_items(section)
    if "papers-ccf-legend" not in section:
        m = re.search(
            r'(<div class="section-header">\s*<h2>[\s\S]*?</h2>\s*<div class="section-line"></div>\s*</div>)',
            section,
        )
        if m:
            section = section[: m.end()] + "\n" + legend + section[m.end() :]
    return section


def splice_papers_page(page_path: Path, papers_source: str, legend: str) -> None:
    html = page_path.read_text(encoding="utf-8")
    start = html.find("<!-- PAPERS -->")
    end = html.find("<!-- PROJECTS -->", start)
    if start < 0 or end < 0:
        raise SystemExit(f"papers markers not found in {page_path}")
    fixed = fix_papers_section(papers_source, legend)
    html = html[:start] + fixed + html[end:]
    page_path.write_text(html, encoding="utf-8")
    sec = html[start:end]
    print(
        page_path.name,
        "authors",
        sec.count("paper-authors"),
        "ccf",
        len(CCF.findall(sec)),
        "labels",
        sec.count('class="paper-labels"'),
    )


def fix_students_file(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    pos = 0
    parts = []
    while True:
        i = html.find('<div class="student-papers">', pos)
        if i < 0:
            parts.append(html[pos:])
            break
        j = html.find("</article>", i)
        parts.append(html[pos:i])
        parts.append(rewrite_items(html[i:j]))
        pos = j
    html = "".join(parts)
    path.write_text(html, encoding="utf-8")
    print(path.name, "ccf", len(CCF.findall(html)), "labels", html.count('class="paper-labels"'))


def extract_papers_section(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    start = html.find("<!-- PAPERS -->")
    end = html.find("<!-- PROJECTS -->", start)
    return html[start:end]


def main() -> None:
    root = Path(__file__).resolve().parent
    gh = Path("/Users/wangyongcai/Documents/[18]博客/个人主页/yongcaiwang.github.io")

    cn_src = extract_papers_section(gh / "index.html")
    en_src = extract_papers_section(gh / "index_en.html")

    splice_papers_page(root / "index.html", cn_src, LEGEND_CN)
    splice_papers_page(root / "index_en.html", en_src, LEGEND_EN)

    fix_students_file(root / "students.html")

    splice_papers_page(gh / "index.html", cn_src, LEGEND_CN)
    splice_papers_page(gh / "index_en.html", en_src, LEGEND_EN)


if __name__ == "__main__":
    main()
