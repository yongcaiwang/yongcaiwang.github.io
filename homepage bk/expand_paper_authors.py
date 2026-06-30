#!/usr/bin/env python3
"""Expand paper-authors from DBLP cache; remove et al. while keeping venue suffix."""

from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
DBLP_XML = ROOT / "dblp_yw_raw.xml"
PAPER_OPEN = '<div class="paper-item">'

PUB_TAGS = {
    "article",
    "inproceedings",
    "proceedings",
    "book",
    "incollection",
    "phdthesis",
    "mastersthesis",
}


def norm_title(title: str) -> str:
    t = unicodedata.normalize("NFKD", title)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"<[^>]+>", "", t).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def clean_dblp_name(name: str) -> str:
    return re.sub(r"\s+\d{1,4}$", "", name.strip())


def elem_text(el) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_dblp_xml(path: Path) -> List[dict]:
    root = ET.parse(path).getroot()
    records = []
    for r in root.findall(".//r"):
        pub = next((c for c in r if c.tag in PUB_TAGS), None)
        if pub is None:
            continue
        authors = [clean_dblp_name(elem_text(a)) for a in pub.findall("author")]
        if not authors:
            continue
        records.append({"title": elem_text(pub.find("title")), "authors": authors})
    return [r for r in records if r["title"]]


def match_record(title: str, records: List[dict], used: set) -> Optional[dict]:
    best_i, best_score = -1, 0.0
    for i, rec in enumerate(records):
        if i in used:
            continue
        score = similarity(title, rec["title"])
        if score > best_score:
            best_score, best_i = score, i
    if best_i >= 0 and best_score >= 0.82:
        used.add(best_i)
        return records[best_i]
    return None


def yw_is_corresponding(authors_html: str) -> bool:
    return bool(re.search(r"<strong>\s*Yongcai Wang\s*\*", authors_html, re.I))


def extract_suffix(authors_html: str) -> str:
    plain = strip_html(authors_html)
    m = re.search(r"et al\.?\s*(.+)$", plain, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(
        r"^(?:.*?)(?:\.\s+)?((?:IEEE|ACM|In |Proc\.|CVPR|ICML|NeurIPS|ICRA|AAAI|ICCV|WWW|SIGMOD|TVCG|TMC|TON|JSAC|FGCS|IJCAI|INFOCOM|MOBIHOC|SECON|EWSN|WiOpt|DASFAA|Ubicomp|ISMAR|ICDE|Theor\.|Inf\.|Adv\.|ACTA|Journal|Wireless|Comput\.|Future|Int\.|J\.|TKDD|TOSN|IMWUT|Software).*)$",
        plain,
        re.I,
    )
    return m.group(1).strip() if m else ""


def author_to_html(name: str, corresponding: bool) -> str:
    if name.lower().startswith("yongcai wang"):
        star = "*" if corresponding else ""
        return f"<strong>Yongcai Wang{star}</strong>"
    return name


def build_authors_line(authors: List[str], suffix: str, corresponding: bool) -> str:
    body = ", ".join(author_to_html(a, corresponding) for a in authors)
    return f"{body}. {suffix}" if suffix else body


def close_paper_item(section: str, start_inner: int) -> int:
    depth = 1
    j, n = start_inner, len(section)
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


def parse_paper_block(block: str) -> dict:
    tm = re.search(r'<a href="([^"]*)"[^>]*>([^<]+)</a>', block)
    sm = re.search(r'<span style="font-weight:600[^>]*>([^<]+)</span>', block)
    am = re.search(r'<div class="paper-authors">([\s\S]*?)</motion>', block)
    am = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
    title = tm.group(2).strip() if tm else (sm.group(1).strip() if sm else "")
    return {"title": title, "authors_html": am.group(1).strip() if am else ""}


def replace_authors(block: str, new_auth: str) -> str:
    return re.sub(
        r'<div class="paper-authors">[\s\S]*?</div>',
        f'<div class="paper-authors">{new_auth}</div>',
        block,
        count=1,
    )


def extract_paper_blocks(section: str) -> List[str]:
    blocks, pos = [], 0
    while True:
        start = section.find(PAPER_OPEN, pos)
        if start < 0:
            break
        inner = start + len(PAPER_OPEN)
        end = close_paper_item(section, inner)
        blocks.append(section[inner : end - 6].strip())
        pos = end
    return blocks


def rebuild_section_items(sec: str, new_blocks: List[str]) -> str:
    spans = []
    pos = 0
    for block in new_blocks:
        i = sec.find(PAPER_OPEN, pos)
        if i < 0:
            break
        inner = i + len(PAPER_OPEN)
        end = close_paper_item(sec, inner)
        spans.append((i, end))
        pos = end
    if len(spans) != len(new_blocks):
        return sec
    out = []
    pos = 0
    for (start, end), block in zip(spans, new_blocks):
        out.append(sec[pos:start])
        out.append(f"{PAPER_OPEN}\n{block}\n</div>")
        pos = end
    out.append(sec[pos:])
    return "".join(out)


def update_section(sec: str, records: List[dict], used: set) -> Tuple[str, int, List[str]]:
    new_blocks = []
    expanded = 0
    unmatched = []
    for block in extract_paper_blocks(sec):
        paper = parse_paper_block(block)
        if not paper["authors_html"] or "et al" not in paper["authors_html"].lower():
            new_blocks.append(block)
            continue
        rec = match_record(paper["title"], records, used)
        if not rec:
            unmatched.append(paper["title"])
            new_blocks.append(block)
            continue
        new_auth = build_authors_line(
            rec["authors"],
            extract_suffix(paper["authors_html"]),
            yw_is_corresponding(paper["authors_html"]),
        )
        new_blocks.append(replace_authors(block, new_auth))
        expanded += 1
    return rebuild_section_items(sec, new_blocks), expanded, unmatched


def patch_file(path: Path, start: str, end: str, records: List[dict], used: set) -> None:
    html = path.read_text(encoding="utf-8")
    s, e = html.find(start), html.find(end, html.find(start))
    if s < 0 or e < 0:
        print(path.name, "markers missing")
        return
    new_sec, expanded, unmatched = update_section(html[s:e], records, used)
    path.write_text(html[:s] + new_sec + html[e:], encoding="utf-8")
    et = len(re.findall(r"et al\.?", path.read_text(encoding="utf-8"), re.I))
    print(f"{path.name}: expanded {expanded}, et al left {et}, unmatched {len(unmatched)}")
    for t in unmatched:
        print("  ?", t[:80])


def main() -> None:
    if not DBLP_XML.exists():
        raise SystemExit(f"缺少 {DBLP_XML}")
    records = parse_dblp_xml(DBLP_XML)
    print(f"DBLP {len(records)} records")
    patch_file(ROOT / "index.html", "<!-- PAPERS -->", "<!-- PROJECTS -->", records, set())
    patch_file(ROOT / "index_en.html", "<!-- PAPERS -->", "<!-- PROJECTS -->", records, set())

    path = ROOT / "students.html"
    html = path.read_text(encoding="utf-8")
    pos, total = 0, 0
    while True:
        i = html.find('<div class="student-papers">', pos)
        if i < 0:
            break
        j = html.find("</article>", i)
        new_sec, n, _ = update_section(html[i:j], records, set())
        html = html[:i] + new_sec + html[j:]
        total += n
        pos = i + len(new_sec)
    path.write_text(html, encoding="utf-8")
    et = len(re.findall(r"et al\.?", path.read_text(encoding="utf-8"), re.I))
    print(f"students.html: expanded {total}, et al left {et}")


if __name__ == "__main__":
    main()
