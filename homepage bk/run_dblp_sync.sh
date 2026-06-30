#!/usr/bin/env bash
# 在本机终端运行（需能访问 dblp.org）
set -euo pipefail
cd "$(dirname "$0")"
bash fetch_dblp_yw.sh
python3 sync_dblp_papers.py
python3 build_students.py
echo "完成：index.html、index_en.html、students.html 已更新书目信息。"
