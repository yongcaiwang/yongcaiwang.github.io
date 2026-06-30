#!/usr/bin/env python3
"""Export Yongcai Wang corresponding-author papers to Excel (homepage * + DBLP metadata)."""

from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Optional, Set

import xlsxwriter

ROOT = Path(__file__).resolve().parent
DBLP_XML = ROOT / "dblp_yw_raw.xml"
INDEX_CANDIDATES = [
    ROOT / "index.html",
    Path("/Users/wangyongcai/Documents/[18]博客/个人主页/yongcaiwang.github.io/index.html"),
]
OUT_XLSX = ROOT / "王永才_通讯作者与第一通讯作者论文_DBLP.xlsx"

PAPER_OPEN = '<div class="paper-item">'
PUB_TAGS = {"article", "inproceedings", "incollection", "book", "phdthesis", "mastersthesis"}
CHINESE_HINTS = re.compile(
    r"[\u4e00-\u9fff]|软件学报|自动化学报|计算机学报|电子学报|通信学报|中国科学"
)


def norm_title(title: str) -> str:
    t = unicodedata.normalize("NFKD", title)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"<[^>]+>", "", t).lower()
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", t)
    return " ".join(t.split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def clean_dblp_name(name: str) -> str:
    return re.sub(r"\s+\d{1,4}$", "", name.strip())


def elem_text(el) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_dblp(path: Path) -> List[dict]:
    root = ET.parse(path).getroot()
    rows = []
    for r in root.findall(".//r"):
        pub = next((c for c in r if c.tag in PUB_TAGS), None)
        if pub is None:
            continue
        journal = elem_text(pub.find("journal"))
        informal = pub.get("publtype") == "informal" or journal in {"CoRR", "arXiv"}
        authors = [clean_dblp_name(elem_text(a)) for a in pub.findall("author")]
        title = elem_text(pub.find("title"))
        if not authors or not title:
            continue
        rows.append(
            {
                "title": title.rstrip("."),
                "authors": authors,
                "venue": journal or elem_text(pub.find("booktitle")),
                "year": elem_text(pub.find("year")),
                "month": elem_text(pub.find("month")),
                "informal": informal,
            }
        )
    return rows


def format_date(year: str, month: str) -> str:
    if not year:
        return ""
    if month:
        m = month.strip()
        if m.isdigit():
            return f"{year}-{int(m):02d}"
        month_map = {
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
        }
        mm = month_map.get(m.lower())
        if mm:
            return f"{year}-{mm}"
    return year


def lang_label(title: str, venue: str) -> str:
    return "中文" if CHINESE_HINTS.search(f"{title} {venue}") else "英文"


def yw_is_corresponding(authors_html: str) -> bool:
    return bool(re.search(r"<strong>\s*Yongcai Wang\s*\*", authors_html, re.I))


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


def extract_homepage_papers(html: str) -> List[dict]:
    s = html.find("<!-- PAPERS -->")
    e = html.find("<!-- PROJECTS -->", s)
    if s < 0 or e < 0:
        return []
    sec = html[s:e]
    papers = []
    pos = 0
    while True:
        start = sec.find(PAPER_OPEN, pos)
        if start < 0:
            break
        inner = start + len(PAPER_OPEN)
        end = close_paper_item(sec, inner)
        block = sec[inner : end - 6]
        tm = re.search(r'<a href="[^"]*"[^>]*>([^<]+)</a>', block)
        sm = re.search(r'<span style="font-weight:600[^>]*>([^<]+)</span>', block)
        am = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
        title = (tm.group(1) if tm else sm.group(1) if sm else "").strip()
        auth = am.group(1) if am else ""
        if title and yw_is_corresponding(auth):
            papers.append({"title": title, "authors_html": auth})
        pos = end
    return papers


def match_dblp(title: str, records: List[dict], used: Set[int]) -> Optional[dict]:
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


def parse_fallback(authors_html: str) -> tuple[List[str], str, str]:
    plain = strip_html(authors_html)
    parts = plain.split(".")
    authors_part = parts[0]
    suffix = parts[1].strip() if len(parts) > 1 else ""
    authors = [re.sub(r"\s*\*+$", "", a.strip()) for a in authors_part.split(",") if a.strip()]
    ym = re.search(r"\b(20\d{2})\b", suffix)
    pub_date = ym.group(1) if ym else ""
    return authors, suffix, pub_date


def main() -> None:
    if not DBLP_XML.exists():
        raise SystemExit(f"缺少 DBLP 文件: {DBLP_XML}")
    html_path = next((p for p in INDEX_CANDIDATES if p.exists()), None)
    if not html_path:
        raise SystemExit("找不到 index.html")

    all_dblp = parse_dblp(DBLP_XML)
    dblp = [r for r in all_dblp if not r["informal"]]
    dblp_informal = [r for r in all_dblp if r["informal"]]
    homepage = extract_homepage_papers(html_path.read_text(encoding="utf-8"))
    used: Set[int] = set()
    used_inf: Set[int] = set()
    rows = []
    unmatched = []

    for p in homepage:
        rec = match_dblp(p["title"], dblp, used)
        if not rec:
            rec = match_dblp(p["title"], dblp_informal, used_inf)
            if rec:
                rec = {**rec, "venue": rec["venue"] or "CoRR (preprint)"}
        if rec:
            authors = ", ".join(rec["authors"])
            venue = rec["venue"]
            pub_date = format_date(rec["year"], rec["month"])
            title = rec["title"]
        else:
            unmatched.append(p["title"])
            alist, venue, pub_date = parse_fallback(p["authors_html"])
            authors = ", ".join(alist)
            title = p["title"]

        rows.append(
            {
                "title": title,
                "authors": authors,
                "venue": venue,
                "pub_date": pub_date,
                "lang": lang_label(title, venue),
            }
        )

    rows.sort(key=lambda r: r["pub_date"], reverse=True)

    wb = xlsxwriter.Workbook(str(OUT_XLSX))
    ws = wb.add_worksheet("通讯作者论文")
    header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1, "text_wrap": True})
    cell_fmt = wb.add_format({"border": 1, "text_wrap": True, "valign": "top"})
    headers = ["序号", "中文/英文", "论文题目", "全部作者姓名", "发表刊物名称全称", "正式发表时间"]
    for col, h in enumerate(headers):
        ws.write(0, col, h, header_fmt)
    ws.set_column(0, 0, 6)
    ws.set_column(1, 1, 10)
    ws.set_column(2, 2, 50)
    ws.set_column(3, 3, 45)
    ws.set_column(4, 4, 38)
    ws.set_column(5, 5, 14)
    for i, r in enumerate(rows, start=1):
        ws.write(i, 0, i, cell_fmt)
        ws.write(i, 1, r["lang"], cell_fmt)
        ws.write(i, 2, r["title"], cell_fmt)
        ws.write(i, 3, r["authors"], cell_fmt)
        ws.write(i, 4, r["venue"], cell_fmt)
        ws.write(i, 5, r["pub_date"], cell_fmt)
    ws.freeze_panes(1, 0)
    note = wb.add_worksheet("说明")
    note.write(
        0,
        0,
        "DBLP 不含通讯作者标记。本表依据主页「代表性论文」中 Yongcai Wang* 条目，"
        "与 dblp.org/pid/04/2124 导出 XML 匹配；已排除 CoRR/arXiv 预印本。"
        "凡标注 * 者均视为通讯作者/第一通讯作者（* 仅用于王永才）。",
    )
    wb.close()

    print(f"主页标注通讯作者: {len(homepage)} 篇")
    print(f"已写入: {OUT_XLSX} ({len(rows)} 篇)")
    if unmatched:
        print(f"未匹配 DBLP ({len(unmatched)} 篇):")
        for t in unmatched:
            print(f"  - {t[:75]}")


if __name__ == "__main__":
    main()
