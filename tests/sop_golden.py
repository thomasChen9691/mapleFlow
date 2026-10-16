#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOP golden fixture 的共享抽取逻辑。

捕获脚本（tests/capture_sop_golden.py）与断言脚本（tests/assert_sop_pipeline.py）
共用本模块——两边抽取规则漂移是 golden 机制的隐形死法（捕获「成功」而断言仍红）。
只放与 golden 相关的部分；结构断言用的 markdown 工具留在断言脚本内。
"""

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REAL_CONFIG = "hugo.toml,config.production.toml"
GOLDEN_DIR = REPO / "tests" / "fixtures" / "sop-golden"


def build_real(dest):
    """生产配置构建，与 CI 命令逐字一致（golden 按 minify 后产物捕获）。"""
    return subprocess.run(
        ["hugo", "--gc", "--minify", "--cleanDestinationDir",
         "--config", REAL_CONFIG, "-d", str(dest)],
        cwd=REPO, capture_output=True, text=True)


def article_inner(html):
    """<article ...> 开标签到 </article> 之间的原文（minify 后字节级比对）。"""
    m = re.search(r"<article[^>]*>", html)
    if not m:
        return None
    end = html.find("</article>", m.end())
    return html[m.end():end] if end >= 0 else None


def extract(html):
    """从构建产物抽取 golden 三字段。"""
    title = re.search(r"<title>(.*?)</title>", html)
    desc = re.search(r'<meta name=description content="([^"]*)"', html)
    return {
        "title": title.group(1) if title else "",
        "meta_description": desc.group(1) if desc else "",
        "article_html": article_inner(html),
    }


def golden_path(slug):
    return GOLDEN_DIR / f"{slug}.json"


def existing_slugs():
    """已有 golden 的 slug 集合（重捕获的默认范围）。"""
    return sorted(p.stem for p in GOLDEN_DIR.glob("*.json"))
