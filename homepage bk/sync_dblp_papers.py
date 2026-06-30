#!/usr/bin/env python3
"""
从 DBLP 同步论文书目信息，更新 index.html / index_en.html 的 paper-authors 行。

用法:
  bash fetch_dblp_yw.sh
  python3 sync_dblp_papers.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
INDEX_CN = ROOT / "index.html"
INDEX_EN = ROOT / "index_en.html"
CACHE_CANDIDATES = [
    ROOT / "dblp_yw_raw.xml",
    ROOT / "dblp_yw_raw.json",
    ROOT / "dblp_yw_raw.bib",
]

VENUE_CN = {
    "J. Softw.": "软件学报",
    "Journal of Software": "软件学报",
    "Acta Autom. Sinica": "自动化学报",
    "ACTA AUTOMATICA SINICA": "自动化学报",
}

PUB_TAGS = {
    "article",
    "inproceedings",
    "proceedings",
    "book",
    "incollection",
    "phdthesis",
    "mastersthesis",
}

PAPER_OPEN = '<div class="paper-item">'


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
    blocks: List[str] = []
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


def parse_paper_block(block: str) -> dict:
    tm = re.search(r'<a href="([^"]*)"[^>]*>([^<]+)</a>', block)
    sm = re.search(r'<span style="font-weight:600[^>]*>([^<]+)</span>', block)
    am = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
    title = tm.group(2).strip() if tm else (sm.group(1).strip() if sm else "")
    return {
        "href": tm.group(1) if tm else "",
        "title": title,
        "authors_html": am.group(1).strip() if am else "",
    }


def split_authors_suffix(plain: str) -> Tuple[str, str]:
    plain = plain.strip()
    if not plain:
        return "", ""
    m = re.search(
        r"^(.*?)(?:\.\s+)?((?:et al\.\s+)?(?:IEEE|ACM|In |Proc\.|CVPR|ICML|NeurIPS|ICRA|AAAI|ICCV|WWW|SIGMOD|TVCG|TMC|TON|JSAC|FGCS|IJCAI|INFOCOM|MOBIHOC|SECON|EWSN|WiOpt|DASFAA|Ubicomp|ISMAR|ICDE|Theor\.|Inf\.|Adv\.|ACTA|Journal|Wireless|Comput\.|Future|Int\.|J\.).*)$",
        plain,
        re.I,
    )
    if m:
        return m.group(1).strip().rstrip(","), m.group(2).strip()
    m = re.search(r"^(.*?)(?:,\s*)?et al\.\s+(.+)$", plain, re.I)
    if m:
        return m.group(1).strip().rstrip(","), "et al. " + m.group(2).strip()
    return plain, ""


def author_prefix_html(authors_html: str) -> str:
    plain = strip_html(authors_html)
    prefix_plain, _ = split_authors_suffix(plain)
    if not prefix_plain:
        return authors_html
    out: List[str] = []
    visible = 0
    i = 0
    target = len(prefix_plain)
    while i < len(authors_html) and visible < target:
        if authors_html.startswith("<strong>", i):
            out.append("<strong>")
            i += 8
            continue
        if authors_html.startswith("</strong>", i):
            out.append("</strong>")
            i += 9
            continue
        if authors_html[i] == "<":
            m = re.match(r"<[^>]+>", authors_html[i:])
            if m:
                out.append(m.group(0))
                i += len(m.group(0))
                continue
        out.append(authors_html[i])
        visible += 1
        i += 1
    prefix = "".join(out).rstrip(" ,;")
    if prefix_plain.rstrip().endswith("et al") and "et al" not in prefix.lower():
        prefix += ", et al"
    return prefix


def short_venue(name: str) -> str:
    repl = {
        "IEEE Transactions on Mobile Computing": "IEEE TMC",
        "IEEE Journal on Selected Areas in Communications": "IEEE JSAC",
        "IEEE/ACM Transactions on Networking": "IEEE/ACM TON",
        "ACM Transactions on Sensor Networks": "ACM TOSN",
        "ACM Transactions on Knowledge Discovery from Data": "ACM TKDD",
        "IEEE Trans. Vis. Comput. Graph.": "IEEE TVCG",
        "IEEE Trans. Mob. Comput.": "IEEE TMC",
        "Proc. IEEE Int. Conf. Comput. Vis.": "ICCV",
        "IEEE/CVF Conf. Comput. Vis. Pattern Recognit.": "CVPR",
        "Int. Conf. Mach. Learn.": "ICML",
        "Adv. Neural Inf. Process. Syst.": "NeurIPS",
        "AAAI Conf. Artif. Intell.": "AAAI",
    }
    n = re.sub(r"\s+", " ", (name or "").strip())
    return repl.get(n, n)


def format_biblio(rec: dict, lang: str = "cn") -> str:
    year = (rec.get("year") or "").strip()
    pages = (rec.get("pages") or "").strip()
    vol = (rec.get("volume") or "").strip()
    num = (rec.get("number") or "").strip()
    note = (rec.get("note") or "").strip()
    venue_raw = rec.get("venue") or ""
    venue = short_venue(venue_raw)
    if lang == "cn":
        venue = VENUE_CN.get(venue_raw, venue)

    loc = (
        note
        if note
        and re.search(
            r"\b(USA|China|Germany|France|UK|Canada|Austria|Singapore|Vienna|Seattle|Montreal|Honolulu|Nashville|New Orleans|Las Vegas|San Diego|Boston|London|Paris|Tokyo|Beijing|Shanghai)\b",
            note,
            re.I,
        )
        else ""
    )

    is_journal = rec.get("type") == "article" or bool(rec.get("journal"))
    if is_journal:
        parts: List[str] = []
        if venue:
            parts.append(venue)
        if vol and num:
            parts.append(f"{vol}({num})")
        elif vol:
            parts.append(vol)
        if pages:
            parts.append(pages.replace("--", "-"))
        if year:
            parts.append(year)
        return ", ".join(parts)

    parts: List[str] = []
    if venue:
        parts.append(venue)
    if loc:
        parts.append(loc)
    if year:
        parts.append(year)
    if pages:
        p = pages.replace("--", "-")
        parts.append(p if p.lower().startswith("pp") else f"pp. {p}")
    return ", ".join(parts)


def elem_text(el: Optional[ET.Element]) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_dblp_xml(path: Path) -> List[dict]:
    root = ET.parse(path).getroot()
    records: List[dict] = []
    for r in root.findall(".//r"):
        pub = next((c for c in r if c.tag in PUB_TAGS), None)
        if pub is None:
            continue
        records.append(
            {
                "type": pub.tag,
                "title": elem_text(pub.find("title")),
                "year": elem_text(pub.find("year")),
                "pages": elem_text(pub.find("pages")),
                "volume": elem_text(pub.find("volume")),
                "number": elem_text(pub.find("number")),
                "note": elem_text(pub.find("note")),
                "venue": elem_text(pub.find("journal"))
                or elem_text(pub.find("booktitle")),
                "journal": elem_text(pub.find("journal")),
            }
        )
    return [r for r in records if r["title"]]


def parse_dblp_json(path: Path) -> List[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    hits = data.get("result", {}).get("hits", {}).get("hit", [])
    if isinstance(hits, dict):
        hits = [hits]
    out: List[dict] = []
    for h in hits:
        info = h.get("info", h)
        venue = info.get("venue", "") or ""
        out.append(
            {
                "type": "article" if "journal" in str(venue).lower() else "inproceedings",
                "title": (info.get("title") or "").strip(),
                "year": str(info.get("year", "") or ""),
                "pages": info.get("pages", "") or "",
                "volume": info.get("volume", "") or "",
                "number": info.get("number", "") or "",
                "note": info.get("note", "") or "",
                "venue": venue,
                "journal": venue if "journal" in str(venue).lower() else "",
            }
        )
    return [r for r in out if r["title"]]


def parse_dblp_bib(path: Path) -> List[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    records: List[dict] = []
    for entry in re.split(r"\n(?=@\w+\{)", text):
        m = re.match(r"@(\w+)\{[^,]*,([\s\S]*)\}\s*$", entry.strip(), re.M)
        if not m:
            continue
        typ, body = m.group(1).lower(), m.group(2)
        fields: Dict[str, str] = {}
        for fm in re.finditer(
            r"(\w+)\s*=\s*\{([^}]*)\}|(\w+)\s*=\s*\"([^\"]*)\"", body
        ):
            k = (fm.group(1) or fm.group(3)).lower()
            v = fm.group(2) or fm.group(4)
            fields[k] = v
        records.append(
            {
                "type": "article" if typ == "article" else "inproceedings",
                "title": fields.get("title", ""),
                "year": fields.get("year", ""),
                "pages": fields.get("pages", ""),
                "volume": fields.get("volume", ""),
                "number": fields.get("number", ""),
                "note": fields.get("note", ""),
                "venue": fields.get("journal") or fields.get("booktitle", ""),
                "journal": fields.get("journal", ""),
            }
        )
    return [r for r in records if r["title"]]


def load_dblp(cache: Optional[Path] = None) -> List[dict]:
    path = cache
    if path is None:
        for c in CACHE_CANDIDATES:
            if c.exists() and c.stat().st_size > 100:
                path = c
                break
    if path is None or not path.exists():
        fetch = ROOT / "fetch_dblp_yw.sh"
        if fetch.exists():
            print("未找到 DBLP 缓存，尝试 fetch_dblp_yw.sh …")
            subprocess.run(["bash", str(fetch)], check=False)
        for c in CACHE_CANDIDATES:
            if c.exists() and c.stat().st_size > 100:
                path = c
                break
    if path is None or not path.exists():
        sys.exit(
            "未找到 DBLP 数据。请在本机终端执行:\n"
            "  bash fetch_dblp_yw.sh\n"
            "  python3 sync_dblp_papers.py"
        )
    print(f"读取 DBLP: {path} ({path.stat().st_size} bytes)")
    if path.suffix == ".xml":
        return parse_dblp_xml(path)
    if path.suffix == ".json":
        return parse_dblp_json(path)
    return parse_dblp_bib(path)


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


def build_authors_html(prefix_html: str, suffix: str) -> str:
    prefix = prefix_html.rstrip(" ,;")
    if not suffix:
        return prefix
    return f"{prefix}. {suffix}"


def replace_authors_in_block(block: str, new_auth_html: str) -> str:
    return re.sub(
        r'<div class="paper-authors">[\s\S]*?</div>',
        f'<div class="paper-authors">{new_auth_html}</div>',
        block,
        count=1,
    )


def rebuild_section_items(sec: str, new_blocks: List[str]) -> str:
    pos = 0
    parts: List[str] = []
    for block in new_blocks:
        i = sec.find(PAPER_OPEN, pos)
        if i < 0:
            parts.append(sec[pos:])
            break
        inner = i + len(PAPER_OPEN)
        end = close_paper_item(sec, inner)
        parts.extend([sec[pos:i], f"{PAPER_OPEN}\n{block}\n</div>"])
        pos = end
    if pos < len(sec):
        parts.append(sec[pos:])
    return "".join(parts)


def papers_slice(html: str) -> Tuple[str, int, int, str]:
    s = html.find("<!-- PAPERS -->")
    e = html.find("<!-- PROJECTS -->", s)
    if s < 0 or e < 0:
        return html, -1, -1, ""
    return html, s, e, html[s:e]


def update_html(
    path: Path, records: List[dict], lang: str, dry_run: bool
) -> Tuple[int, int, List[str]]:
    full = path.read_text(encoding="utf-8")
    _, s, e, sec = papers_slice(full)
    if s < 0:
        print(f"跳过 {path.name}: 未找到 PAPERS 区块")
        return 0, 0, []

    blocks = extract_paper_blocks(sec)
    used: set = set()
    matched = 0
    unmatched: List[str] = []
    new_blocks: List[str] = []

    for block in blocks:
        paper = parse_paper_block(block)
        if not paper["title"]:
            new_blocks.append(block)
            continue
        rec = match_record(paper["title"], records, used)
        if rec is None:
            unmatched.append(paper["title"])
            new_blocks.append(block)
            continue
        bib = format_biblio(rec, lang)
        prefix = (
            author_prefix_html(paper["authors_html"])
            if paper["authors_html"]
            else ""
        )
        new_auth = build_authors_html(prefix, bib)
        new_blocks.append(replace_authors_in_block(block, new_auth))
        matched += 1

    new_sec = rebuild_section_items(sec, new_blocks)
    if not dry_run:
        path.write_text(full[:s] + new_sec + full[e:], encoding="utf-8")
    return matched, len(blocks), unmatched


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync DBLP bibliography into index HTML.")
    ap.add_argument("--cache", type=Path, default=None, help="DBLP cache file path")
    ap.add_argument("--dry-run", action="store_true", help="Do not write HTML files")
    args = ap.parse_args()

    records = load_dblp(args.cache)
    print(f"DBLP 记录: {len(records)} 条")

    m_cn, t_cn, u_cn = update_html(INDEX_CN, records, "cn", args.dry_run)
    m_en, t_en, u_en = update_html(INDEX_EN, records, "en", args.dry_run)
    print(f"index.html: 更新 {m_cn}/{t_cn}")
    print(f"index_en.html: 更新 {m_en}/{t_en}")
    if u_cn:
        print(f"未匹配（中文页）{len(u_cn)} 篇，示例:")
        for t in u_cn[:8]:
            print(" -", t[:70])
    if u_en and u_en != u_cn:
        print(f"未匹配（英文页）{len(u_en)} 篇，示例:")
        for t in u_en[:8]:
            print(" -", t[:70])
    if not args.dry_run:
        print("\n请运行: python3 build_students.py")


if __name__ == "__main__":
    main()
