#!/usr/bin/env python3
"""Revert DBLP sync damage in index.html / index_en.html."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rebuild_papers import build_author_db, close_paper_item, extract_paper_blocks, parse_block

ROOT = Path(__file__).resolve().parent
TARGETS = [ROOT / "index.html", ROOT / "index_en.html"]
BACKUPS = [ROOT / f"index_{i}.html" for i in (1, 2, 3)]

VENUE_TAG_MAP = {"MM": "ACM MM", "SIGMOD": "SIGMOD", "WN": "Wireless Networks", "TECS": "ACM TECS"}


def authors_inner(div_html: str) -> str:
    m = re.search(r'<motion class="paper-authors">([\s\S]*?)</motion>', div_html)
    if m:
        return m.group(1).strip()
    m = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', div_html)
    return m.group(1).strip() if m else ""


def is_sync_damage(inner: str) -> bool:
    if not inner:
        return False
    if "CoRR" in inner or ", pp." in inner:
        return True
    if re.search(r"Wang\*?\.(?:\s|$)", inner):
        return True
    if inner.count("<strong>") > inner.count("</strong>"):
        return True
    if re.search(
        r"\.\s*(Theor\. Comput\. Sci\.|IEEE TMC|ACM TOSN|Inf\. Sci\.|IEEE TVCG|IEEE JSAC|IEEE/ACM TON|Proc\. ACM Manag\. Data),",
        inner,
    ):
        return True
    return False


def find_year(sec: str, block_start: int) -> str:
    years = re.findall(r'<div class="year-label">(\d{4})</div>', sec[:block_start])
    return years[-1] if years else ""


def venue_tag(block: str) -> str:
    m = re.search(r'<span class="paper-venue-tag[^>]*>([^<]+)</span>', block)
    return m.group(1).strip() if m else ""


def fix_strong(inner: str) -> str:
    inner = re.sub(
        r"<strong>Yongcai Wang\*?\.\s*",
        "<strong>Yongcai Wang*</strong>, ",
        inner,
    )
    inner = re.sub(
        r"<strong>Yongcai Wang\.\s*",
        "<strong>Yongcai Wang</strong>. ",
        inner,
    )
    if "<strong>" in inner and "</strong>" not in inner:
        if "Yongcai Wang*" in inner:
            inner = inner.replace(
                "<strong>Yongcai Wang*", "<strong>Yongcai Wang*</strong>", 1
            )
        else:
            inner = inner.replace(
                "<strong>Yongcai Wang", "<strong>Yongcai Wang</strong>", 1
            )
    return inner


def revert_journal(inner: str) -> str:
    rules = [
        (
            r"^(.*?</strong>.*?)\.\s*(IEEE TMC|IEEE/ACM TON|IEEE JSAC),\s*(\d+)\((\d+)\),\s*([\d\-]+),\s*(\d{4})\s*$",
            r"\1. \2 \3(\4), \5, \6",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(ACM TOSN),\s*(\d+)\((\d+)\),\s*([\d\-]+),\s*(\d{4})\s*$",
            r"\1. \2 \3(\4), \5, \6",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(ACM TOSN),\s*(\d+)\((\d+)\)\s*(\(\d{4}\))?\s*$",
            r"\1. \2 \3(\4) \5",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(Theor\. Comput\. Sci\.|Inf\. Sci\.),\s*(\d+),\s*[\d\-]+,\s*(\d{4})\s*$",
            r"\1. \2 \3 (\4)",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(Theor\. Comput\. Sci\.|Inf\. Sci\.),\s*(\d+)\s*(\(\d{4}\))?\s*$",
            r"\1. \2 \3\4",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(IEEE TVCG),\s*(\d+)\((\d+)\),\s*[\d\-]+,\s*(\d{4})\s*$",
            r"\1. \2 \4",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(Proc\. ACM Manag\. Data),\s*[\d\(\):,\s]+,\s*(\d{4})\s*$",
            r"\1. SIGMOD \2",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(Adv\. Eng\. Informatics|Comput\. Networks),\s*(\d+)\s*(\(\d{4}\))?\s*$",
            r"\1. \2 \3\4",
        ),
        (
            r"^(.*?</strong>.*?)\.\s*(IMWUT|TKDD),\s*(\d+)\((\d+)\)\s*(\(\d{4}\))?\s*$",
            r"\1. \2 \3(\4) \5",
        ),
    ]
    for pat, repl in rules:
        out = re.sub(pat, repl, inner, flags=re.S)
        if out != inner:
            return out
    return inner


def heuristic_revert(inner: str, block: str, sec: str, pos: int) -> str:
    inner = fix_strong(revert_journal(inner))
    if not is_sync_damage(inner):
        return inner

    year = find_year(sec, pos)
    venue = VENUE_TAG_MAP.get(venue_tag(block), venue_tag(block))

    if "CoRR" in inner or "abs/" in inner:
        prefix = re.split(r",\s*CoRR|,\s*abs/", inner)[0].rstrip(" ,.")
        prefix = fix_strong(prefix)
        if "et al" in inner.lower() and "et al" not in prefix.lower():
            prefix += ", et al"
        return f"{prefix}. {venue} {year}".strip()

    prefix = inner
    for sep in (", pp.", f", {year}"):
        i = prefix.find(sep)
        if i > 0:
            prefix = prefix[:i]
            break
    prefix = fix_strong(prefix.rstrip(" ,."))
    suffix = f"{venue} {year}"
    if "et al" in inner.lower() and "et al" not in prefix.lower():
        return f"{prefix}, et al. {suffix}"
    if prefix.endswith("."):
        return f"{prefix} {suffix}"
    return f"{prefix}. {suffix}"


def replace_authors(block: str, new_inner: str) -> str:
    return re.sub(
        r'<div class="paper-authors">[\s\S]*?</div>',
        f'<div class="paper-authors">{new_inner}</motion>',
        block,
        count=1,
    ).replace("</motion>", "</motion>")


def replace_authors(block: str, new_inner: str) -> str:
    return re.sub(
        r'<div class="paper-authors">[\s\S]*?</div>',
        f'<div class="paper-authors">{new_inner}</div>',
        block,
        count=1,
    )


def rebuild_section(sec: str, new_blocks: List[str]) -> str:
    pos, parts = 0, []
    for block in new_blocks:
        i = sec.find('<div class="paper-item">', pos)
        if i < 0:
            parts.append(sec[pos:])
            break
        inner = i + len('<div class="paper-item">')
        end = close_paper_item(sec, inner)
        parts.extend([sec[pos:i], block])
        pos = end
    if pos < len(sec):
        parts.append(sec[pos:])
    return "".join(parts)


def revert_file(path: Path, db: Dict) -> Tuple[int, int]:
    html = path.read_text(encoding="utf-8")
    s = html.find("<!-- PAPERS -->")
    if s < 0:
        s = html.find('id="papers"')
    e = html.find("<!-- PROJECTS -->", s)
    sec = html[s:e]
    blocks = extract_paper_blocks(sec)
    new_blocks: List[str] = []
    fixed = 0
    offset = 0

    for block in blocks:
        bi = sec.find(block[: min(80, len(block))], offset)
        if bi < 0:
            bi = offset
        offset = bi + len(block)

        it = parse_block(block)
        am = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
        inner = am.group(1).strip() if am else ""

        if not is_sync_damage(inner):
            new_blocks.append(block)
            continue

        restored = None
        for k in it["keys"]:
            if k in db:
                restored = authors_inner(db[k])
                break

        new_inner = restored if restored else heuristic_revert(inner, block, sec, bi)
        new_blocks.append(replace_authors(block, new_inner))
        fixed += 1

    path.write_text(html[:s] + rebuild_section(sec, new_blocks) + html[e:], encoding="utf-8")
    return fixed, len(blocks)


def main() -> None:
    db = build_author_db([p for p in BACKUPS if p.exists()])
    print(f"备份作者库: {len(db)} 条")
    for path in TARGETS:
        fixed, total = revert_file(path, db)
        print(f"{path.name}: 恢复 {fixed}/{total} 条")
    print("请运行: python3 build_students.py")


if __name__ == "__main__":
    main()
