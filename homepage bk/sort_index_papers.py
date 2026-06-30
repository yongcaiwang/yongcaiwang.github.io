#!/usr/bin/env python3
"""在同一 year-group 内将论文按 CCF A → CCF B → 其它排序。"""

import re
import sys
from pathlib import Path

def ccf_rank(block: str) -> int:
    m = re.search(r'paper-venue-tag ([^"]*)', block)
    cls = m.group(1) if m else ""
    if cls == "ccfa":
        return 0
    if cls == "ccfb":
        return 1
    if "ccf-a" in block:
        return 0
    if "ccf-b" in block:
        return 1
    return 2


def extract_paper_items(html):
    items = []
    pos = 0
    open_tag = '<div class="paper-item">'
    n = len(html)
    while pos < n:
        start = html.find(open_tag, pos)
        if start < 0:
            break
        depth = 0
        i = start
        while i < n:
            if html.startswith("<div", i):
                depth += 1
                i = html.find(">", i) + 1
                continue
            if html.startswith("</div>", i):
                depth -= 1
                i += 6
                if depth == 0:
                    items.append(html[start:i])
                    pos = i
                    break
                continue
            i += 1
        else:
            break
    return items


def sort_year_group_content(combined: str) -> str:
    m = re.match(r'(<div class="year-group">\s*)([\s\S]*)', combined)
    if not m:
        return combined
    open_tag, body = m.group(1), m.group(2)
    label_m = re.match(r'(<div class="year-label">[\s\S]*?</div>\s*)', body)
    if not label_m:
        return combined
    prefix = open_tag + label_m.group(1)
    rest = body[label_m.end() :]
    items = extract_paper_items(rest)
    if not items:
        return combined
    sorted_items = sorted(items, key=ccf_rank)
    consumed = 0
    for item in items:
        idx = rest.find(item, consumed)
        consumed = idx + len(item)
    tail = rest[consumed:]
    if not tail.startswith("\n"):
        tail = "\n" + tail.lstrip("\n")
    return prefix + "\n".join(sorted_items) + tail


def process_file(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    start = html.find('id="papers"')
    end = html.find("<!-- PROJECTS -->", start)
    section = html[start:end]
    chunks = re.split(r'(<div class="year-group">\s*)', section)
    rebuilt = [chunks[0]]
    for i in range(1, len(chunks), 2):
        if i + 1 >= len(chunks):
            rebuilt.append(chunks[i])
            break
        rebuilt.append(sort_year_group_content(chunks[i] + chunks[i + 1]))
    path.write_text(html[:start] + "".join(rebuilt) + html[end:], encoding="utf-8")
    print(f"Sorted {path.name}")


def main() -> None:
    root = Path(__file__).resolve().parent
    paths = [root / "index.html", root / "index_en.html"]
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    for p in paths:
        process_file(p)


if __name__ == "__main__":
    main()
