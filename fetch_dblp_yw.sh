#!/usr/bin/env bash
set -euo pipefail
export NO_PROXY='*' no_proxy='*'
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy SOCKS_PROXY SOCKS5_PROXY socks_proxy socks5_proxy GIT_HTTP_PROXY GIT_HTTPS_PROXY 2>/dev/null || true

OUT_DIR="${1:-/Users/wangyongcai/Downloads}"
mkdir -p "$OUT_DIR"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

try_fetch() {
  local out="$1" url="$2"
  curl --noproxy '*' -fsSL -o "$out" "$url" 2>/dev/null && [[ -s "$out" ]]
}

URLS_JSON=(
  "https://dblp.org/search/publ/api?q=author:Yongcai_Wang:&format=json&h=1000"
  "https://dblp.uni-trier.de/search/publ/api?q=author:Yongcai_Wang:&format=json&h=1000"
)
URLS_XML=(
  "https://dblp.org/pid/04/2124.xml"
  "https://dblp.uni-trier.de/pid/04/2124.xml"
)
URLS_BIB=(
  "https://dblp.org/pid/04/2124.bib"
  "https://dblp.uni-trier.de/pid/04/2124.bib"
)

for u in "${URLS_JSON[@]}"; do try_fetch "$TMP/search.json" "$u" && break; done
echo "Fetching pid XML..."
for u in "${URLS_XML[@]}"; do try_fetch "$TMP/pid.xml" "$u" && break; done
echo "Fetching pid BIB..."
for u in "${URLS_BIB[@]}"; do try_fetch "$TMP/pid.bib" "$u" && break; done

# Pick best: prefer pid XML (complete author page), else search JSON, else bib
best=""
for cand in pid.xml search.json pid.bib; do
  if [[ -f "$TMP/$cand" ]]; then
    sz=$(wc -c < "$TMP/$cand" | tr -d ' ')
    echo "$cand size=$sz"
  else
    echo "$cand size=0 (missing)"
  fi
done

if [[ -s "$TMP/pid.xml" ]]; then
  cp "$TMP/pid.xml" "$OUT_DIR/dblp_yw_raw.xml"
  best="$OUT_DIR/dblp_yw_raw.xml"
elif [[ -s "$TMP/search.json" ]]; then
  cp "$TMP/search.json" "$OUT_DIR/dblp_yw_raw.json"
  best="$OUT_DIR/dblp_yw_raw.json"
elif [[ -s "$TMP/pid.bib" ]]; then
  cp "$TMP/pid.bib" "$OUT_DIR/dblp_yw_raw.bib"
  best="$OUT_DIR/dblp_yw_raw.bib"
else
  echo "错误：无法从 dblp.org 下载数据（请检查网络，或在浏览器打开 https://dblp.org/pid/04/2124.xml 另存为 $OUT_DIR/dblp_yw_raw.xml）" >&2
  exit 1
fi

echo "Saved: $best ($(wc -c < "$best" | tr -d ' ') bytes)"
python3 <<'PY'
import json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

out_dir = Path("/Users/wangyongcai/Downloads")
for name in ("dblp_yw_raw.xml", "dblp_yw_raw.json", "dblp_yw_raw.bib"):
    p = out_dir / name
    if not p.exists():
        continue
    print("FILE", p, "SIZE", p.stat().st_size)
    if name.endswith(".json"):
        data = json.loads(p.read_text())
        hits = data.get("result", {}).get("hits", {})
        total = hits.get("@total", hits.get("total", "?"))
        hit = hits.get("hit", [])
        if isinstance(hit, dict):
            hit = [hit]
        print("PUBLICATIONS", total, "hits_in_page", len(hit))
        for h in hit[:2]:
            info = h.get("info", h)
            print("--- sample ---")
            for k in ("title", "year", "pages", "volume", "venue"):
                print(k, info.get(k))
    elif name.endswith(".xml"):
        root = ET.parse(p).getroot()
        pubs = root.findall(".//r")
        print("PUBLICATIONS", len(pubs))
        ns = {"dblp": "https://dblp.org/xml/dblp.dtd"}
        for r in pubs[:2]:
            print("--- sample ---")
            for tag in ("title", "year", "pages", "volume", "journal", "booktitle"):
                el = r.find(f".//{tag}")
                if el is not None and (el.text or "").strip():
                    print(tag, (el.text or "").strip())
            v = r.find(".//journal") or r.find(".//booktitle")
            if v is not None:
                print("venue", (v.text or "").strip())
    break
PY
