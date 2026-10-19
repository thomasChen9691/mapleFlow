#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOP golden fixture 的共享抽取逻辑。

捕获脚本（tests/capture_sop_golden.py）与断言脚本（tests/assert_sop_pipeline.py）
共用本模块——两边抽取规则漂移是 golden 机制的隐形死法（捕获「成功」而断言仍红）。
只放与 golden 相关的部分；结构断言用的 markdown 工具留在断言脚本内。
"""

import re
import subprocess
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REAL_CONFIG = "hugo.toml,config.production.toml"
GOLDEN_DIR = REPO / "tests" / "fixtures" / "sop-golden"


# 形如「2026-01-28 20:00:00 +0800 CST」的时间戳属性值：base + 任意个时区标记
_DT_ATTR = re.compile(
    r"^(?P<base>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"
    r"(?P<rest>(?:\s+[+-]\d{2}:?\d{2}|\s+[A-Za-z]{2,5})*)$")
_OFFSET = re.compile(r"[+-]\d{2}:?\d{2}")


def _normalize_attr_value(value):
    """时间戳属性值 → 只保留数字偏移，丢弃时区缩写/重复偏移。

    为什么：Go 解析带偏移量的时间戳时，只有偏移量与**运行机器的本地时区**一致
    才会用命名时区，否则造一个无名固定区——同一个时间戳 String() 出来在本机
    （Asia/Shanghai）是 `... +0800 CST`，在 CI runner（UTC）是 `... +0800 +0800`。
    这是构建环境元数据，不是内容差异（hugo.toml 的 timeZone 管不到这条路径：
    它影响语言级日期格式化，不改变已带偏移量的 time.Time 的 Location）。
    模板侧已改为显式格式（layouts/partials/post_meta.html，消掉不确定性），
    这里保留容错，使旧 golden 与未来任何 .Date 字符串化不再产生同类假红。
    """
    m = _DT_ATTR.match(value)
    if not m:
        return value
    offsets = _OFFSET.findall(m.group("rest") or "")
    return m.group("base") + (" " + offsets[0] if offsets else "")


class _Canonicalizer(HTMLParser):
    """把 HTML 归一到 token 序列：标签名 + 排序后的属性 + 折叠空白后的文本。

    忽略的属性面 = 渲染器版本差异（属性引号/顺序、空白、实体写法）与
    时间戳的时区标记（见 _normalize_attr_value）；
    保留的属性面 = 一切内容与结构变化（标签、class/id/href 等、文本）。
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tokens = []

    def handle_starttag(self, tag, attrs):
        norm = tuple(sorted((k, v if v is None else _normalize_attr_value(v))
                            for k, v in attrs))
        self.tokens.append(("tag", tag, norm))

    # 自闭合写法（<br/> 与 <br>）视为同一 token——minify 版本会换写法
    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        self.tokens.append(("end", tag, ()))

    def handle_data(self, data):
        if data.strip():
            self.tokens.append(("text", " ".join(data.split()), ()))

    def handle_comment(self, data):
        self.tokens.append(("comment", " ".join(data.split()), ()))


def canonical(html):
    """HTML → 规范化 token 序列（版本无关的比对形式）。

    为什么不是逐字节：项目政策是「CI 钉 0.164、本机 0.167」（地图 Notes），
    而 golden 由本机渲染捕获——Chroma / minify / goldmark 的版本差异会改变
    属性引号、空白与代码高亮标签写法，逐字节比对在 CI 必红（2026-10-16 实测）。
    规范化后仍能抓住一切真实变化：标签、属性值、文本。
    """
    p = _Canonicalizer()
    p.feed(html or "")
    p.close()
    return p.tokens


def first_divergence(want, got, window=2):
    """两个 token 序列的首个分歧点，带小窗口上下文——诊断信息。

    CI 日志需认证，本串随断言详情进 GitHub 注解，使「哪一处渲染不同」
    无需日志权限即可读出（2026-10-16 首次 CI 诊断靠它定位）。
    """
    for i, (a, b) in enumerate(zip(want, got)):
        if a != b:
            lo = max(0, i - window)
            return ("token %d: want %r got %r | context want=%r got=%r"
                    % (i, a, b, want[lo:i + window + 1], got[lo:i + window + 1]))
    if len(want) != len(got):
        i = min(len(want), len(got))
        longer, label = (want, "want") if len(want) > len(got) else (got, "got")
        return ("length differs (%d vs %d); %s extra from token %d: %r"
                % (len(want), len(got), label, i, longer[i:i + 3]))
    return ""


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
