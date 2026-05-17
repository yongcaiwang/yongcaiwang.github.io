#!/usr/bin/env python3
"""从 index.html 生成 students.html（指导学生页）。"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
OUT = ROOT / "students.html"

# 非指导学生（第一作者但不在指导学生列表中）
EXCLUDE_FIRST_AUTHORS = {
    "xingfa shen",
    "chuanwen luo",
    "xingjian ding",
    "ruidong yan",
    "jiang wang",
    "xiujuan zhang",
    "yupeng li",
    "guoyao rao",
}

# 第一作者别名 → 规范姓名（合并条目并修正作者行）
FIRST_AUTHOR_ALIASES = {
    "haodi wang": "Haodi Ping",
    "xuedong cai": "Xudong Cai",
}

AUTHOR_NAME_FIXES = [
    (re.compile(r"\bHaodi Wang\b"), "Haodi Ping"),
    (re.compile(r"\bXuedong Cai\b"), "Xudong Cai"),
]

PROF = {"yongcai wang"}

DEFAULT_STUDENT_DEGREE = "Master Student"

# 学生学位（未列出的默认为 Master Student）
STUDENT_DEGREES: Dict[str, str] = {
    name: "Ph.D."
    for name in [
        "Shuo Wang",
        "Hongyu Sun",
        "Xudong Cai",
        "Haodi Ping",
        "Wanting Li",
        "Xiaojia Xu",
        "Zhe Huang",
        "Peng Wang",
        "Xuewei Bai",
        "Hualong Cao",
        "Kang Yang",
        "Lei Song",
        "Shuai Liu",
        "Xiao Qi",
        "Yance Fang",
    ]
}
STUDENT_DEGREES["Zhixian Lei"] = "Bachelor Student"
STUDENT_DEGREES["Tongyang Li"] = "Bachelor Student"

# 学生所在单位（未列出的默认为中国人民大学信息学院）
THIIIS_STUDENTS = {
    "Tongyang Li",
    "Xiaohong Hao",
    "Zhixian Lei",
    "Lei Song",
    "Xiao Qi",
    "Zhiqi Yang",
    "Liwen Xu",
}

AFFILIATIONS = [
    ("ruc", "中国人民大学信息学院"),
    ("thiiis", "清华大学交叉信息研究院"),
]

DEGREE_ORDER = ("Ph.D.", "Master Student", "Bachelor Student")

DEGREE_GROUP_LABELS = {
    "Ph.D.": "博士研究生",
    "Master Student": "硕士研究生",
    "Bachelor Student": "本科生",
}

# 学生个人主页（经检索核实；无独立主页者不列入）
STUDENT_HOMEPAGES: Dict[str, str] = {
    "Shuo Wang": "https://markinruc.github.io/",
    "Hongyu Sun": "https://auniquesun.github.io/",
    "Xudong Cai": "https://master-cai.github.io/",
    "Peng Wang": "https://penk1ng.github.io/",
    "Haodi Ping": "https://haodi-ping.github.io/",
    "Xiaowei Lv": "https://gom168.github.io/",
}

# 主页代表性论文未收录、但与王永才合作且该生为第一作者的论文（来源：DBLP / researchr / 课题组主页）
EXTRA_PAPERS: Dict[str, List[dict]] = {
    "Wanting Li": [
        {
            "title": "TrackPuzzle: Efficient registration of unlabeled PDR trajectories for learning indoor route graph",
            "link": "https://doi.org/10.1016/j.future.2023.07.019",
            "venue": "FGCS",
            "tag_cls": "ccfb",
            "auth_html": "Wanting Li, <strong>Yongcai Wang*</strong>, Yu Shao, Gaowei Hu, Deying Li. Future Gener. Comput. Syst. 149, 171-183 (2023)",
            "year": 2023,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span>',
        },
        {
            "title": "MCM: A Robust Map Matching Method by Tracking Multiple Road Candidates",
            "link": "https://doi.org/10.1007/978-3-031-16081-3_20",
            "venue": "AAIM",
            "tag_cls": "",
            "auth_html": "Wanting Li, <strong>Yongcai Wang*</strong>, Deying Li, Xiaojia Xu. AAIM 2022",
            "year": 2022,
            "tags_html": "",
        },
    ],
    "Xiaojia Xu": [
        {
            "title": "LSA: Understanding the Threat of Link-Based Scapegoating Attack in Network Tomography",
            "link": "https://ieeexplore.ieee.org/document/10109847",
            "venue": "TNSE",
            "tag_cls": "ccfb",
            "auth_html": "Xiaojia Xu, <strong>Yongcai Wang*</strong>, Lanling Xu, Deying Li. IEEE TNSE 10(6), 3670-3681 (2023)",
            "year": 2023,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span>',
        },
        {
            "title": "Defense of Scapegoating Attack in Network Tomography",
            "link": "https://doi.org/10.1007/978-3-031-16081-3_15",
            "venue": "AAIM",
            "tag_cls": "",
            "auth_html": "Xiaojia Xu, <strong>Yongcai Wang*</strong>, Yu Zhang, Deying Li. AAIM 2022",
            "year": 2022,
            "tags_html": "",
        },
    ],
    "Xuewei Bai": [
        {
            "title": "A Geometric and Hypothesis-Based Method for Low-Overlap, Sparse, and Featureless Point Set Matching",
            "link": "https://doi.org/10.1145/3746453",
            "venue": "TOSN",
            "tag_cls": "ccfb",
            "auth_html": "Xuewei Bai, <strong>Yongcai Wang*</strong>, Peng Wang, Chunxu Li, Shuo Wang, Xudong Cai, Deying Li. ACM TOSN (2025)",
            "year": 2025,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span>',
        },
    ],
    "Zhe Huang": [
        {
            "title": "Collaborative 3D object detection by smart vehicles considering semantic information and agent heterogeneity",
            "link": "https://www.sciencedirect.com/science/article/abs/pii/S1474034625002447",
            "venue": "ADVEI",
            "tag_cls": "ccfb",
            "auth_html": "Zhe Huang, <strong>Yongcai Wang*</strong>, Deying Li, Yunjun Han, Lei Wang. Adv. Eng. Informatics 65 (2025)",
            "year": 2025,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span><a class="link-badge" href="https://github.com/HuangZhe885/Collaborative-Perception" target="_blank">Code</a>',
        },
        {
            "title": "Boundary-Aware Set Abstraction for 3D Object Detection",
            "link": "https://doi.org/10.1109/IJCNN54540.2023.10191728",
            "venue": "IJCNN",
            "tag_cls": "",
            "auth_html": "Zhe Huang, <strong>Yongcai Wang*</strong>, Xingui Tang, Hongyu Sun. IJCNN 2023",
            "year": 2023,
            "tags_html": '<a class="link-badge" href="https://github.com/HuangZhe885/Boundary-Aware-SA" target="_blank">Code</a>',
        },
    ],
    "Hualong Cao": [
        {
            "title": "IPT: Iterative Pairing and Transformation for Multiple Point Cloud Registration",
            "link": "https://doi.org/10.1109/TVCG.2024.3509896",
            "venue": "TVCG",
            "tag_cls": "ccfa",
            "auth_html": "Hualong Cao, <strong>Yongcai Wang*</strong>, Deying Li. IEEE TVCG 31(9), 6321-6336 (2025)",
            "year": 2025,
            "tags_html": '<span class="ccf-badge ccf-a">CCF A</span>',
        },
    ],
    "Yance Fang": [
        {
            "title": "QUEST: QUasi-clique Enhanced Structure-aware Transformation for Low-overlap Point Cloud Registration",
            "link": "https://github.com/Flanture/QUEST-QUasi-clique-Enhanced-Structure-aware-Transformation-for-Low-overlap-Point-Cloud-Registration",
            "venue": "ICMR",
            "tag_cls": "ccfb",
            "auth_html": "Yance Fang, Hualong Cao, <strong>Yongcai Wang*</strong>, Haoyu Liu, Deying Li. ICMR 2025",
            "year": 2025,
            "tags_html": (
                '<span class="ccf-badge ccf-b">CCF B</span>'
                '<a class="link-badge" href="https://github.com/Flanture/QUEST-QUasi-clique-Enhanced-Structure-aware-Transformation-for-Low-overlap-Point-Cloud-Registration" target="_blank">Code</a>'
            ),
        },
    ],
    "Xiaowei Lv": [
        {
            "title": "Maximum core spanning tree maintenance for large dynamic graphs",
            "link": "https://doi.org/10.1016/j.tcs.2025.115278",
            "venue": "TCS",
            "tag_cls": "ccfb",
            "auth_html": "Xiaowei Lv, <strong>Yongcai Wang</strong>, Deying Li*. Theor. Comput. Sci. 1044, 115278, 1-13 (2025)",
            "year": 2025,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span>',
        },
        {
            "title": "DecisionLLM: Large Language Models for Long Sequence Decision Exploration",
            "link": "https://arxiv.org/abs/2601.10148",
            "venue": "ICLR workshop",
            "tag_cls": "",
            "auth_html": "Xiaowei Lv, Zhilin Zhang, Yijun Li, Yusen Huo, Siyuan Ju, Xuyan Li, Chunxiang Hong, Tianyu Wang, <strong>Yongcai Wang</strong>, Peng Sun, Chuan Yu, Jian Xu, Bo Zheng. ICLR 2026 Workshop",
            "year": 2026,
            "tags_html": "",
        },
    ],
    "Xuehan Ye": [
        {
            "title": "WarpMap: Accurate and Efficient Indoor Locating by Dynamic Warping in Sequence-type Radio-map",
            "link": "https://yongcaiwang.github.io/papers/warpmap.pdf",
            "venue": "SECON",
            "tag_cls": "ccfb",
            "auth_html": "Xuehan Ye, <strong>Yongcai Wang*</strong>, Wei Hu, Lei Song, Zhaoquan Gu, Deying Li. SECON 2016",
            "year": 2016,
            "tags_html": '<span class="ccf-badge ccf-b">CCF B</span>',
        },
    ],
}

STUDENT_CSS = """
  /* ── STUDENTS PAGE ─────────────────────── */
  .students-directory {
    margin-bottom: 40px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  .affiliation-block {
    padding: 18px 20px;
    background: var(--paper-warm);
    border: 1px solid var(--border);
    border-radius: 10px;
  }
  .affiliation-title {
    font-family: 'Noto Serif SC', serif;
    font-size: var(--text-md);
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--accent-soft);
  }
  .degree-block {
    margin-bottom: 14px;
  }
  .degree-block:last-child {
    margin-bottom: 0;
  }
  .degree-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--ink-light);
    margin: 0 0 8px;
    letter-spacing: 0.04em;
  }
  .students-toc {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 10px;
  }
  .student-card {
    margin-bottom: 32px;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    background: #fff;
  }
  .student-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 18px;
    background: var(--paper-warm);
    border-bottom: 1px solid var(--border);
  }
  .student-identity {
    display: flex;
    flex-direction: row;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 12px;
    min-width: 0;
  }
  .student-name {
    font-family: 'Noto Serif SC', serif;
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    line-height: 1.3;
    white-space: nowrap;
  }
  .student-linked-name {
    color: var(--accent);
    text-decoration: underline;
    text-underline-offset: 2px;
    text-decoration-thickness: 1px;
  }
  .student-name a.student-linked-name {
    color: var(--accent);
  }
  .student-name a.student-linked-name:hover {
    color: #8b1a1a;
  }
  .students-toc a.has-home .student-linked-name {
    font-weight: 600;
  }
  .students-toc a {
    font-size: var(--text-sm);
    color: var(--ink-light);
    text-decoration: none;
    padding: 4px 10px;
    border-radius: 4px;
    background: #fff;
    border: 1px solid var(--border);
    transition: color 0.15s, border-color 0.15s;
  }
  .students-toc a:hover {
    color: var(--accent);
    border-color: var(--accent-soft);
  }
  .student-degree {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--ink-light);
    letter-spacing: 0.02em;
    white-space: nowrap;
  }
  .student-degree.phd { color: var(--accent); }
  .student-degree.bachelor { color: #1a6b9a; }
  .students-toc .toc-degree {
    font-size: var(--text-2xs);
    color: var(--ink-faint);
    margin-left: 4px;
  }
  .student-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    flex-shrink: 0;
  }
  .student-count {
    font-size: var(--text-xs);
    color: var(--ink-faint);
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
  }
  .student-papers .paper-item {
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-top: none;
  }
  .student-papers .paper-item:last-child { border-bottom: none; }
  .students-body {
    display: flex;
    flex-direction: column;
    gap: 36px;
  }
  .students-body .affiliation-block {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
  }
  .students-body .affiliation-title {
    font-size: var(--text-xl);
    margin-bottom: 20px;
    border-bottom-color: var(--accent);
  }
  .students-body .degree-block {
    margin-bottom: 28px;
  }
  .students-body .degree-title {
    font-size: var(--text-base);
    color: var(--accent);
    margin-bottom: 12px;
  }
  .student-card-compact .student-header {
    border-bottom: none;
  }
  .thiiis-roster {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 4px 0 8px;
  }
  .thiiis-student-item {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 14px;
    padding: 12px 18px;
    background: var(--paper-warm);
    border: 1px solid var(--border);
    border-radius: 8px;
  }
  .thiiis-student-item .student-name {
    font-size: var(--text-base);
    margin: 0;
  }
  .affiliation-note {
    font-size: var(--text-sm);
    color: var(--ink-light);
    margin: -8px 0 16px;
    line-height: 1.6;
  }
"""


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def fix_author_html(auth_html: str) -> str:
    for pattern, repl in AUTHOR_NAME_FIXES:
        auth_html = pattern.sub(repl, auth_html)
    return auth_html


def normalize_first_author(name: str) -> Optional[str]:
    key = re.sub(r"\*+$", "", name).strip().lower()
    if key in PROF:
        return None
    if key in EXCLUDE_FIRST_AUTHORS:
        return None
    if key in FIRST_AUTHOR_ALIASES:
        return FIRST_AUTHOR_ALIASES[key]
    return re.sub(r"\*+$", "", name).strip()


def extract_year(auth_text: str) -> int:
    years = re.findall(r"\b(20\d{2})\b", auth_text)
    return max(int(y) for y in years) if years else 0


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def student_degree(name: str) -> str:
    return STUDENT_DEGREES.get(name, DEFAULT_STUDENT_DEGREE)


def degree_css_class(degree: str) -> str:
    if degree.startswith("Ph.D"):
        return "phd"
    if "Bachelor" in degree:
        return "bachelor"
    return "master"


def degree_short(degree: str) -> str:
    if degree.startswith("Ph.D"):
        return "Ph.D."
    if "Bachelor" in degree:
        return "B.S."
    return "M.S."


def student_affiliation(name: str) -> str:
    return "thiiis" if name in THIIIS_STUDENTS else "ruc"


def student_homepage(name: str) -> str:
    return STUDENT_HOMEPAGES.get(name, "")


def student_name_html(name: str) -> str:
    url = student_homepage(name)
    if url:
        return (
            f'<a class="student-linked-name" href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{name}</a>'
        )
    return name


def degree_sort_key(degree: str) -> int:
    try:
        return DEGREE_ORDER.index(degree)
    except ValueError:
        return len(DEGREE_ORDER)


def ccf_sort_key(paper: dict) -> int:
    """0=CCF A, 1=CCF B, 2=其它（无 CCF 标注）。"""
    tag_cls = paper.get("tag_cls", "")
    if tag_cls == "ccfa":
        return 0
    if tag_cls == "ccfb":
        return 1
    tags = paper.get("tags_html", "")
    if "ccf-a" in tags:
        return 0
    if "ccf-b" in tags:
        return 1
    return 2


def sort_student_papers(papers: List[dict]) -> List[dict]:
    return sorted(papers, key=lambda p: (ccf_sort_key(p), -p.get("year", 0)))


def group_students(
    by_student: Dict[str, List[dict]],
) -> Dict[str, Dict[str, List[tuple]]]:
    """affiliation -> degree -> [(name, papers), ...]"""
    grouped: Dict[str, Dict[str, List[tuple]]] = {
        aid: {deg: [] for deg in DEGREE_ORDER} for aid, _ in AFFILIATIONS
    }
    for name, papers in by_student.items():
        aid = student_affiliation(name)
        deg = student_degree(name)
        if deg not in grouped[aid]:
            grouped[aid][deg] = []
        grouped[aid][deg].append((name, papers))
    for aid in grouped:
        for deg in grouped[aid]:
            grouped[aid][deg].sort(key=lambda x: (-len(x[1]), x[0].lower()))
    return grouped


def render_toc_link(name: str) -> str:
    deg = student_degree(name)
    if student_homepage(name):
        return (
            f'<a class="has-home" href="#{slug(name)}">'
            f'<span class="student-linked-name">{name}</span>'
            f'<span class="toc-degree">{degree_short(deg)}</span></a>'
        )
    return (
        f'<a href="#{slug(name)}">{name}'
        f'<span class="toc-degree">{degree_short(deg)}</span></a>'
    )


def render_toc_directory(grouped: Dict[str, Dict[str, List[tuple]]]) -> str:
    parts = ['<div class="students-directory">']
    for aid, affil_label in AFFILIATIONS:
        blocks = grouped[aid]
        if not any(blocks[d] for d in DEGREE_ORDER):
            continue
        parts.append(f'<div class="affiliation-block" id="affil-{aid}">')
        parts.append(f'<h3 class="affiliation-title">{affil_label}</h3>')
        for deg in DEGREE_ORDER:
            students = blocks[deg]
            if not students:
                continue
            parts.append('<div class="degree-block">')
            parts.append(f'<h4 class="degree-title">{DEGREE_GROUP_LABELS[deg]}</h4>')
            parts.append('<div class="students-toc">')
            for name, _ in students:
                parts.append(render_toc_link(name))
            parts.append("</div></div>")
        parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def render_student_card_compact(name: str) -> str:
    deg = student_degree(name)
    dcls = degree_css_class(deg)
    return (
        f'<div class="thiiis-student-item" id="{slug(name)}">'
        f'<h3 class="student-name">{student_name_html(name)}</h3>'
        f'<span class="student-degree {dcls}">{deg}</span>'
        f"</div>"
    )


def render_student_card(name: str, student_papers: List[dict]) -> str:
    student_papers = sort_student_papers(student_papers)
    deg = student_degree(name)
    dcls = degree_css_class(deg)
    parts = [f'<article class="student-card" id="{slug(name)}">']
    parts.append(
        f'<header class="student-header">'
        f'<div class="student-identity">'
        f'<h3 class="student-name">{student_name_html(name)}</h3>'
        f'<span class="student-degree {dcls}">{deg}</span>'
        f"</div>"
        f'<div class="student-meta">'
        f'<span class="student-count">{len(student_papers)} 篇</span>'
        f"</div></header>"
    )
    parts.append('<div class="student-papers">')
    for p in student_papers:
        vtag = (
            f'<span class="paper-venue-tag {p["tag_cls"]}">{p["venue"]}</span>'
            if p["venue"]
            else ""
        )
        tags = f'<div class="paper-tags">{p["tags_html"]}</div>' if p["tags_html"] else ""
        parts.append(
            f"""<div class="paper-item">
{vtag}
<div class="paper-content">
{p['title_html']}
<div class="paper-authors">{p['auth_html']}</div>
{tags}
</div>
</div>"""
        )
    parts.append("</div></article>")
    return "\n".join(parts)


def render_students_body(grouped: Dict[str, Dict[str, List[tuple]]]) -> str:
    parts = ['<div class="students-body">']
    for aid, affil_label in AFFILIATIONS:
        blocks = grouped[aid]
        if not any(blocks[d] for d in DEGREE_ORDER):
            continue
        parts.append(f'<div class="affiliation-block" id="affil-{aid}-papers">')
        parts.append(f'<h3 class="affiliation-title">{affil_label}</h3>')
        if aid == "thiiis":
            parts.append(
                '<p class="affiliation-note">'
                "以下同学就读于清华大学交叉信息研究院，曾与王永才教授合作发表论文；"
                "此处仅列名录，不展开论文条目。"
                "</p>"
            )
        for deg in DEGREE_ORDER:
            students = blocks[deg]
            if not students:
                continue
            parts.append('<div class="degree-block">')
            parts.append(f'<h4 class="degree-title">{DEGREE_GROUP_LABELS[deg]}</h4>')
            if aid == "thiiis":
                parts.append('<div class="thiiis-roster">')
                for name, _ in students:
                    parts.append(render_student_card_compact(name))
                parts.append("</div>")
            else:
                for name, papers in students:
                    parts.append(render_student_card(name, papers))
            parts.append("</div>")
        parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def parse_papers(html: str) -> List[dict]:
    start = html.find('id="papers"')
    end = html.find("<!-- PROJECTS -->", start)
    section = html[start:end]
    items = re.findall(
        r'<div class="paper-item">([\s\S]*?)</div>\s*</div>\s*(?=\n<div class="paper-item">|</div><motion class="paper-item">|</motion><div class="paper-item">|\n</div>\n<div class="year-group">|\n</section>)',
        section,
    )

    papers = []
    for block in items:
        venue_m = re.search(r'<span class="paper-venue-tag ([^"]*)">([^<]+)</span>', block)
        tag_cls = venue_m.group(1) if venue_m else ""
        venue = venue_m.group(2).strip() if venue_m else ""

        title_m = re.search(r'<a href="([^"]*)"[^>]*>([^<]+)</a>', block)
        if title_m:
            title_html = title_m.group(0)
        else:
            title_m = re.search(r'<span style="font-weight:600[^"]*">([^<]+)</span>', block)
            title_html = title_m.group(0) if title_m else "<span>Untitled</span>"

        auth_m = re.search(r'<div class="paper-authors">([\s\S]*?)</div>', block)
        auth_html = fix_author_html(auth_m.group(1).strip()) if auth_m else ""
        auth_text = strip_tags(auth_html)

        first_raw = auth_text.split(",")[0].strip()
        student = normalize_first_author(first_raw)
        if not student:
            continue

        tags_m = re.search(r'<div class="paper-tags">([\s\S]*?)</div>', block)
        tags_html = tags_m.group(1).strip() if tags_m else ""

        papers.append(
            {
                "student": student,
                "title_html": title_html,
                "venue": venue,
                "tag_cls": tag_cls,
                "auth_html": auth_html,
                "year": extract_year(auth_text),
                "tags_html": tags_html,
            }
        )
    return papers


def _paper_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()[:80]


def extra_to_paper(student: str, spec: dict) -> dict:
    title = spec["title"]
    link = spec.get("link", "")
    title_html = (
        f'<a href="{link}">{title}</a>' if link else f"<span>{title}</span>"
    )
    return {
        "student": student,
        "title_html": title_html,
        "venue": spec.get("venue", ""),
        "tag_cls": spec.get("tag_cls", ""),
        "auth_html": spec["auth_html"],
        "year": spec.get("year", 0),
        "tags_html": spec.get("tags_html", ""),
        "_key": _paper_key(title),
    }


def merge_extra_papers(papers: List[dict]) -> List[dict]:
    existing = {_paper_key(strip_tags(p["title_html"])) for p in papers}
    merged = list(papers)
    for student, extras in EXTRA_PAPERS.items():
        for spec in extras:
            ep = extra_to_paper(student, spec)
            if ep["_key"] in existing:
                continue
            existing.add(ep["_key"])
            merged.append({k: v for k, v in ep.items() if k != "_key"})
    return merged


def merge_thiiis_roster(by_student: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """确保清华交叉信息研究院学生均出现在名录中（即使无第一作者论文收录）。"""
    merged = dict(by_student)
    for name in THIIIS_STUDENTS:
        if name not in merged:
            merged[name] = []
    return merged


def students_from_papers(papers: List[dict]) -> Dict[str, List[dict]]:
    by_student: Dict[str, List[dict]] = defaultdict(list)
    for p in papers:
        by_student[p["student"]].append(p)
    return merge_thiiis_roster(by_student)


def build_body(papers: List[dict]) -> str:
    grouped = group_students(students_from_papers(papers))
    return render_toc_directory(grouped) + "\n" + render_students_body(grouped)



def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    style_m = re.search(r"<head>[\s\S]*?<style>\s*([\s\S]*?)\s*</style>", html)
    if not style_m:
        raise SystemExit("无法在 index.html 中找到 <style>")
    style = style_m.group(1)

    papers = merge_extra_papers(parse_papers(html))
    body = build_body(papers)

    nav = """<nav>
<div class="nav-section-label">个人信息</div>
<a href="index.html#profile"><span class="nav-icon">◎</span> 个人简介</a>
<a href="index.html#background"><span class="nav-icon">◎</span> 教育和工作背景</a>
<a href="index.html#research"><span class="nav-icon">◈</span> 研究方向</a>
<a href="index.html#recruit"><span class="nav-icon">✦</span> 招生信息</a>
<div class="nav-section-label">学术动态</div>
<a href="index.html#news"><span class="nav-icon">⚡</span> 新闻动态</a>
<a href="index.html#reports"><span class="nav-icon">◉</span> 近期报告</a>
<div class="nav-section-label">教学科研</div>
<a href="index.html#teaching"><span class="nav-icon">◧</span> 教学</a>
<a href="index.html#papers"><span class="nav-icon">◆</span> 代表性论文</a>
<a href="students.html" class="active"><span class="nav-icon">◇</span> 指导学生</a>
<a href="index.html#projects"><span class="nav-icon">◈</span> 科研项目</a>
<div class="nav-section-label">服务与荣誉</div>
<a href="index.html#service"><span class="nav-icon">◐</span> 学术服务</a>
<a href="index.html#society"><span class="nav-icon">◑</span> 学会任职</a>
<a href="index.html#awards"><span class="nav-icon">★</span> 获奖</a>
<div class="nav-section-label">其他</div>
<a href="index.html#hobbies"><span class="nav-icon">◌</span> 闲暇爱好</a>
</nav>"""

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>指导学生 — 王永才</title>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&amp;family=Noto+Sans+SC:wght@300;400;500&amp;family=DM+Serif+Display:ital@0;1&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet"/>
<style>
{style}
{STUDENT_CSS}
</style>
</head>
<body>
<aside id="sidebar">
<div class="sidebar-profile">
<div class="sidebar-avatar"><img alt="王永才" src="ycw_large.jpg"/></div>
<div class="sidebar-name">王永才</div>
<div class="sidebar-title">教授 · 博士生导师<br/>计算机系副系主任</div>
<div class="sidebar-inst">中国人民大学信息学院</div>
</div>
{nav}
<div class="sidebar-footer">
<a href="index.html">← 返回主页</a><br/>
<a href="https://dblp.org/pid/04/2124.html" target="_blank">DBLP 论文目录 ↗</a><br/>
<a href="index_en.html">English Version ↗</a><br/><br/>
<a href="https://beian.miit.gov.cn/" target="_blank">京ICP备2024071883号</a>
</div>
</aside>
<main id="main">
<section class="section" id="students">
<div class="section-header">
<h2>指导学生</h2>
<div class="section-line"></div>
</div>
{body}
</section>
</main>
</body>
</html>
"""

    OUT.write_text(page, encoding="utf-8")
    n_students = len(students_from_papers(papers))
    print(f"Wrote {OUT.name}: {n_students} students, {len(papers)} papers")


if __name__ == "__main__":
    main()
