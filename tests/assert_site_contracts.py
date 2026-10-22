#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点契约的产物断言（原名 assert_product_states.py——2026-10 职责扩张后改名，
ADR 与历史 handoff 里的旧名即本脚本）。覆盖五类职责：
产品状态模块（ADR-0004）· 产品索引接口（ADR-0006）· 主题契约 B7-B13（ADR-0008）
· reveal 产物面（ADR-0007）· 文章精选（候选 7 工单 0036-0040 决议）。

测试缝（预先商定，勿在未确认的缝上写测试）：
  · 渲染产物 seam —— fixture 构建的 products.html（控件态 / 文案 / data-price）
    与 index.html（「可下载产品」计数、首页精选区 featured 分栏）
  · 文章精选 seam —— 独立 fixture 构建（tests/hugo.test.posts.toml，只覆盖
    contentDir）：首页精选区的 3 条 featured、与「最近更新」网格互斥且并集全量、
    0 篇 featured 时精选区整块不渲染、featured 非布尔即构建失败
  · 契约 seam —— tests/fixtures/bad/ 下每个用例的构建必须失败；
    逐用例钉错误子串（BAD_CASE_EXPECT）：产品状态模块（「产品状态：」前缀）、
    产品索引数据门禁（「产品索引数据：」前缀，含产品 id 与坏值）
  · 调用方 seam —— 经真实调用链（短代码 / 直接调 partial）触发的契约失败
  · 空态 seam —— 产品数据整体缺席时渲染「暂无资源」而非崩溃或静默空页
  · 真实数据 seam —— 生产配置构建的 products.html / index.html，线上回归守门
  · 主题层契约 seam —— 全站 no-js 基线 / post_meta 显式时区格式 / 菜单渲染序 /
    RSS 只收 posts / search DOM 挂点 / ogImage 兜底 / 站点与主题同路径不变量
    （候选 6 工单 0032 决议；B7-B13，逐条变异检验）

用法：
  python3 tests/assert_site_contracts.py          # 全套
  python3 tests/assert_site_contracts.py --quick  # 跳过真实数据构建（本地快速迭代）

Hugo 版本纪律：模块必须保持 0.164 语义（单变量 + 根级单条 return）。本机 hugo
可能为 0.167 而 CI 钉 0.164——0.164 风格代码两端一致，但 0.166+ 的条件多
return 写法本地过、CI 红。本脚本只消费构建产物，与 Hugo 版本无关。

期望值均为独立字面量（决策规则的直写），不是对实现的重算——防止同义反复测试。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp"

FIXTURE_CONFIG = "hugo.toml,tests/hugo.test.toml"
REAL_CONFIG = "hugo.toml,config.production.toml"

# ---- 期望值：决策规则的字面量，独立于实现 ----
# 控件语义（ADR-0004 形状 B）：已上架+免费→可点「免费获取」；已上架+付费→可点「购买」；
# 未上架→禁用「即将上架」（与价格无关）。
FIXTURE_ROWS = {
    "fx-listed-paid": {
        "name": "已上架+付费 → 可点「购买」",
        "control": "link", "label": "购买", "href": "https://example.com/fx-listed-paid",
        "data_price": "paid", "price_text": "¥39", "aria_disabled": None,
    },
    "fx-listed-free": {
        "name": "已上架+免费 → 可点「免费获取」",
        "control": "link", "label": "免费获取", "href": "https://example.com/fx-listed-free",
        "data_price": "free", "price_text": "免费", "aria_disabled": None,
    },
    "fx-unlisted-paid": {
        "name": "未上架+付费 → 禁用「即将上架」+ data-price=paid",
        "control": "disabled", "label": "即将上架", "href": None,
        "data_price": "paid", "price_text": "¥49", "aria_disabled": "true",
    },
    "fx-unlisted-free": {
        "name": "未上架+免费 → 禁用「即将上架」+ data-price=free",
        "control": "disabled", "label": "即将上架", "href": None,
        "data_price": "free", "price_text": "免费", "aria_disabled": "true",
    },
    "fx-unlisted-plain": {
        "name": "非 featured 对照行 → 禁用「即将上架」（产品页可见、不上首页）",
        "control": "disabled", "label": "即将上架", "href": None,
        "data_price": "free", "price_text": "免费", "aria_disabled": "true",
    },
}
FIXTURE_LISTED_COUNT = 2   # 5 条 fixture 中已上架 2 个产品
FIXTURE_PAGE_ROW_COUNT = 5  # 产品页（短代码默认 limit=0）经 product-items 渲染全部产品
FIXTURE_NON_FEATURED_ID = "fx-unlisted-plain"  # featured: false 对照行：必须不上首页
FIXTURE_HOME_FEATURED_IDS = ["fx-listed-paid", "fx-listed-free", "fx-unlisted-paid"]  # 4 条 featured，首页 limit=3 截断后按数据序取前 3
FIXTURE_HOME_TRUNCATED_ID = "fx-unlisted-free"  # featured=true 但被 limit=3 截断，必须不上首页
EMPTY_STATE_TEXT = "暂无资源"  # 渲染 seam 的空态文案（空 slice 时；存量 UI 文案）
REAL_ROW_COUNT = 5         # data/products.yaml 现有 5 个产品
REAL_LISTED_COUNT = 0      # 迁移后全部未上架（占位），可下载产品为 0（工单 0004：显示 0）
# 真实数据首页精选（0019 评审补漏）：fixture 改全 featured 后 where featured 分支
# 只剩真实数据这一层回归保护——3 条 featured（yaml 序），limit=3 不截断但保过滤。
REAL_HOME_FEATURED_IDS = ["n8n-dify-workflows", "sre-learning-docs", "sre-interview-bank"]

# 文章精选 fixture（工单 0039 决议：独立构建，contentDir 覆盖；不动既有 fixture 环境）。
# 6 篇：4 篇 featured（limit=3 截断 1 篇）+ 1 篇未声明 + 1 篇显式 false。
# 最新一篇（02-10）故意不标 featured——用于区分「按日期取前 3」（旧行为）与「真精选」。
POSTS_FIXTURE_CONFIG = "hugo.toml,tests/hugo.test.posts.toml"
POSTS_FIXTURE_FEATURED = ["fx-post-feat-d", "fx-post-feat-c", "fx-post-feat-b"]
POSTS_FIXTURE_TRUNCATED = "fx-post-feat-a"
POSTS_FIXTURE_REST = ["fx-post-newest", "fx-post-false", "fx-post-feat-a"]
POSTS_FIXTURE_ALL = sorted(["fx-post-feat-a", "fx-post-feat-b", "fx-post-feat-c",
                            "fx-post-feat-d", "fx-post-false", "fx-post-newest"])
POSTS_EMPTY_CONTENT = "tests/fixtures/content-posts-none"  # 两篇均未标 featured
POSTS_ALL_FEATURED_CONTENT = "tests/fixtures/content-posts-all"  # 两篇都标 featured
POSTS_BAD_CONTENT = "tests/fixtures/content-posts-bad"     # featured 写成字符串
POSTS_BAD_INT_CONTENT = "tests/fixtures/content-posts-bad-int"  # featured 写成整数
POSTS_BAD_FEATURED_EXPECT = "文章精选数据："

# 契约坏用例的逐条期望子串（0018 事实底座：旧判定只匹配模块统一前缀，偏弱；
# 此表按用例钉归属，与 SOP 脚本的逐用例子串登记同型）。缺省沿用产品状态模块前缀。
# 0016 决议：产品索引数据门禁的消息必须含产品 id 与坏 kind——断言子串照钉。
BAD_CASE_EXPECT = {
    "listed-no-url": "产品状态：",
    "missing-listed": "产品状态：",
    "missing-price": "产品状态：",
    "unlisted-with-url": "产品状态：",
    "unknown-kind": '产品索引数据："fx-unknown-kind" 的 kind="poster"',
    "missing-kind": '产品索引数据："fx-missing-kind" 的 kind="<缺失>"',
    "featured-not-bool": '产品索引数据："fx-featured-not-bool" 的 featured 必须是布尔值',
}

# 调用方级契约（0015 决议：limit 负数即 errorf，不允许静默全量）。
# 经真实调用链触发：临时 contentDir 里的一个页面调短代码，走完
# product-items → 契约执法，不是直接调 partial。
CALLER_LIMIT_NEGATIVE_EXPECT = "产品索引数据：limit 不能为负数"

# 渲染 seam 的输入契约：items 必填（施工期按「无缺省」宗教补的守卫，
# 留工单 0020 追认）。经 layoutsDir 覆盖直接调 partial 触发。
CALLER_MISSING_ITEMS_EXPECT = "产品索引：items 必填"

# uid 必填（工单 0017 决议：显式必填，删 default "mf-idx" 死缺省）。
CALLER_MISSING_UID_EXPECT = "产品索引：uid 必填"

# 主题层契约（0032 决议）的独立字面量：post_meta 的 title 属性必须是显式时区格式，
# 不是 Go 的 time.Time.String()（后者由构建机时区决定输出字节）。
POST_META_TITLE_RE = re.compile(r"title='\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}'")

# 菜单渲染契约（0032 决议 B9）：hugo.toml 有 13 条 menu.main，但 header.html 只渲染
# 顶层项——4 个 categories 子项（parent=categories）当前不渲染，属既有事实。
# 期望值 = 实际渲染的 9 项，按 weight 序；内部链接必须符合 uglyURLs 形态（.html 或 /）。
MENU_RENDERED_KEYS = [
    "/", "/posts/", "/categories/", "/tags/", "/about.html", "/search.html",
    "/products.html", "https://github.com/thomasChen9691", "mailto:test@example.com",
]


def _nav_key(href):
    """把构建产物里的绝对 href 归一成菜单键（站点子路径 /mapleFlow/ 之后的部分）。"""
    if href.startswith(("mailto:", "https://github.com/")):
        return href
    if "/mapleFlow/" in href:
        return "/" + href.split("/mapleFlow/", 1)[1]
    return href


class ProductRowParser(HTMLParser):
    """抽取 products.html 中每条 mf-row 的产品状态可观测面。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = {}
        self._row = None
        self._capture = None
        self._buf = []
        self._li_depth = 0  # mf-row 内嵌套 <li>（meta 列表）的深度，防止行被提前闭合

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "li" and "mf-row" in classes:
            self._row = {"id": a.get("id"), "data_price": a.get("data-price"),
                         "price_text": "", "control": None, "href": None, "label": "",
                         "aria_disabled": None}
            self._li_depth = 0
        elif self._row is not None:
            if tag == "li":
                self._li_depth += 1
            elif tag == "span" and "mf-price" in classes:
                self._capture = "price"
            elif tag == "a" and "mf-cta" in classes:
                self._row["control"] = "link"
                self._row["href"] = a.get("href")
                self._capture = "cta"
            elif tag == "span" and "mf-cta-ghost" in classes:
                self._row["control"] = "disabled"
                self._row["aria_disabled"] = a.get("aria-disabled")
                self._capture = "cta"

    def handle_data(self, data):
        if self._capture is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._row is None:
            return
        if tag == "li":
            if self._li_depth > 0:
                self._li_depth -= 1
            else:
                self.rows[self._row["id"]] = self._row
                self._row = None
            return
        if self._capture is not None and tag in ("span", "a"):
            text = "".join(self._buf).strip()
            if self._capture == "price":
                self._row["price_text"] = text
            else:
                self._row["label"] = text
            self._capture = None
            self._buf = []


def parse_rows(path):
    parser = ProductRowParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.rows


def _post_slug(href):
    """把文章链接归一成 slug（fixture 断言用；uglyURLs 下形如 /posts/<slug>.html）。"""
    m = re.search(r"/posts/([^/#?]+)\.html", href)
    return m.group(1) if m else href


def parse_home_featured_slugs(html):
    """首页「精选文章」区的 slug 序。

    按标题锚定区块，不取「第一个 mf-rows」——产品精选区同用该 class，
    0 篇 featured 时第一个 mf-rows 就是产品区（会把空态断言变成假红）。
    """
    anchor = re.search(r"精选文章", html)
    if not anchor:
        return []
    block = re.search(r'<ol class=["\']?mf-rows["\']?>(.*?)</ol>', html[anchor.start():], re.S)
    if not block:
        return []
    return [_post_slug(h) for h in re.findall(r'mf-row-title"><a href=["\']?([^"\'> ]+)', block.group(1))]


def parse_home_grid_slugs(html):
    """首页「最近更新」卡片网格的 slug 序（entry-link 是整卡点击层）。"""
    return [_post_slug(h) for h in re.findall(r'class="entry-link"[^>]*href="([^"]+)"', html)]


def parse_spec_count(html, label_contains):
    """从首页数据条取某个指标的数字（按 label 文本定位）。"""
    for item in re.findall(r'<div class="mf-spec-item">(.*?)</div>', html, re.DOTALL):
        num = re.search(r'mf-spec-num[^>]*>\s*(\d+)\s*<', item)
        label = re.search(r'mf-spec-label[^>]*>([^<]*)<', item)
        if num and label and label_contains in label.group(1):
            return int(num.group(1))
    return None


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def build(config, dest, flags=None):
    return run(["hugo", "--cleanDestinationDir", "--config", config, "-d", str(dest)]
               + (flags or []))


class Report:
    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self):
        return [i for i in self.items if not i[0]]


def assert_search_index(report, dest):
    """产品搜索索引的 tag 必须用标准术语「产品」（CONTEXT.md；资源为禁用词）。"""
    index = json.loads((dest / "index.json").read_text(encoding="utf-8"))
    product_entries = [e for e in index if "products.html#" in (e.get("permalink") or "")]
    if not product_entries:
        report.check("搜索索引含产品", False, "index.json 里没有 products.html# 锚点")
        return
    bad = [e for e in product_entries if e.get("tags") != ["产品"]]
    report.check(f"产品搜索索引 tag = [\"产品\"]（{len(product_entries)} 条）", not bad,
                 "" if not bad else "got: " + "; ".join(str(e.get("tags")) for e in bad))


def assert_reveal_artifacts(report, dest):
    """reveal 协议产物面（工单 0022 决议④ B 类；施工期 provisional，待 0023 追认）。

    引擎源码在 assets/js/mf-reveal/（scroll-in.js / filter.js，经 app.js 入口
    js.Build 打包），行为断言在 tests/assert_reveal.mjs；本函数只守产物面：
    基线类、接线、DOM 挂点、降级 CSS 规则。
    """
    products_html = (dest / "products.html").read_text(encoding="utf-8")
    home_html = (dest / "index.html").read_text(encoding="utf-8")

    # B1 no-js 基线（ADR-0002）：<html> 默认带 no-js；head 内联脚本立刻换成 js
    report.check("B1 html 基线类 no-js 在（产品页）",
                 re.search(r'<html[^>]*class=["\']?[^"\'>]*no-js', products_html) is not None,
                 "html tag missing class=no-js")
    report.check("B1 head swap 内联脚本在（no-js→js）",
                 "classList.remove('no-js')" in products_html and "classList.add('js')" in products_html,
                 "inline swap script not found in head")

    # B2 js.Build 接线：页面引用引擎脚本且文件真实落盘
    m = re.search(r'<script[^>]+src=["\']?([^"\'\s>]*mf-reveal[^"\'\s>]*\.js)', products_html)
    report.check("B2 产品页引用 reveal 引擎脚本（js.Build 产出）", m is not None,
                 "no <script src=...mf-reveal...> in products.html")
    if m:
        rel = re.sub(r'^(/|mapleFlow/)', '', m.group(1))
        report.check("B2 引擎脚本文件已落盘", (dest / rel).exists(), f"missing {dest / rel}")

    # B3 DOM 契约挂点：产品行 .reveal、首页 hero mf-rise（含三档延迟类）
    report.check("B3 产品行带 .reveal 进场类", 'mf-row reveal' in products_html,
                 "no 'mf-row reveal' in products.html")
    missing_mrise = [c for c in ('mf-rise d1', 'mf-rise d2', 'mf-rise d3') if c not in home_html]
    report.check("B3 首页 hero 带 .mf-rise 进场类（d1/d2/d3 三档）",
                 'mf-rise' in home_html and not missing_mrise,
                 f"missing {missing_mrise}")

    # B4 筛选数据挂点（协议层读、渲染 seam 写）
    hooks = ['data-group="kind"', 'data-value="workflow"', 'data-kind=', 'data-price=']
    missing = [h for h in hooks if h not in products_html]
    report.check("B4 筛选数据挂点齐（data-group/value/kind/price）", not missing,
                 f"missing {missing}")

    # B5 筛选按钮词汇集（kind 三值 + price 两值；ADR-0006 封闭词表的执行区）
    values = sorted(re.findall(r'data-value="([^"]+)"', products_html))
    expect = sorted(["all", "workflow", "document", "question-bank", "free", "paid"])
    report.check("B5 mf-filter 按钮词汇集 = kind 三值 + price 两值（精确集合）",
                 values == expect, f"got {values}")

    # B6 no-js 降级 CSS 规则在产物里（基线兜底：无 JS 时内容可见）
    css_text = "\n".join(p.read_text(encoding="utf-8") for p in dest.rglob("*.css"))
    report.check("B6 产物 CSS 含 .no-js .reveal 降级规则", ".no-js .reveal" in css_text,
                 "missing .no-js .reveal rule")
    report.check("B6 产物 CSS 含 .no-js .mf-rise 降级规则", ".no-js .mf-rise" in css_text,
                 "missing .no-js .mf-rise rule")


def assert_fixture(report):
    dest = TMP / "fixture"
    proc = build(FIXTURE_CONFIG, dest)
    report.check("fixture 构建成功", proc.returncode == 0, proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    rows = parse_rows(dest / "products.html")
    report.check(f"fixture 产品页渲染全部 {FIXTURE_PAGE_ROW_COUNT} 条（limit 缺省=全量）",
                 len(rows) == FIXTURE_PAGE_ROW_COUNT,
                 f"got {len(rows)}: {sorted(rows)}")
    for pid, exp in FIXTURE_ROWS.items():
        row = rows.get(pid)
        if row is None:
            report.check(f"fixture[{pid}] 渲染出产品行", False, "products.html 中找不到该 id")
            continue
        ok = (row["control"] == exp["control"] and row["label"] == exp["label"]
              and row["data_price"] == exp["data_price"] and row["price_text"] == exp["price_text"]
              and row["href"] == exp["href"] and row["aria_disabled"] == exp["aria_disabled"])
        report.check(exp["name"], ok,
                     f"got control={row['control']} label={row['label']!r} data-price={row['data_price']} "
                     f"price={row['price_text']!r} href={row['href']!r} aria-disabled={row['aria_disabled']!r}")
    home_rows = parse_rows(dest / "index.html")
    # 首页同时渲染文章列表（li.mf-row 无 id），只取产品行（有 id = 产品锚点）
    home_product_ids = [pid for pid in home_rows if pid]
    report.check("首页精选区 featured 分栏 = 前 3 条 featured 产品（0019 截断覆盖）",
                 home_product_ids == FIXTURE_HOME_FEATURED_IDS,
                 f"got {home_product_ids}")
    report.check(f"非 featured 产品不上首页（{FIXTURE_NON_FEATURED_ID}，where featured 分支回归）",
                 FIXTURE_NON_FEATURED_ID not in home_product_ids,
                 f"got {home_product_ids}")
    report.check(f"首页 limit=3 截断：{FIXTURE_HOME_TRUNCATED_ID} 不上首页",
                 FIXTURE_HOME_TRUNCATED_ID not in home_product_ids,
                 f"got {home_product_ids}")
    # 被截断的产品仍上产品页（短代码默认 limit=0 全量）——截断只发生在首页调用点
    report.check(f"被截断产品仍在产品页（{FIXTURE_HOME_TRUNCATED_ID}）",
                 FIXTURE_HOME_TRUNCATED_ID in rows, f"products rows={sorted(rows)}")
    count = parse_spec_count((dest / "index.html").read_text(encoding="utf-8"), "可下载产品")
    report.check("fixture 首页计数 = 已上架条数（2）", count == FIXTURE_LISTED_COUNT, f"got {count}")
    # filters 开关差异（0019 决议）：产品页（短代码缺省 filters=true）出筛选控件；
    # 首页精选区（index.html 传 filters=false）不出——渲染 seam 自身分支
    products_html = (dest / "products.html").read_text(encoding="utf-8")
    home_html = (dest / "index.html").read_text(encoding="utf-8")
    has_filters_products = "mf-filter" in products_html
    has_filters_home = "mf-filter" in home_html
    report.check("产品页渲染筛选控件（filters 缺省=true）", has_filters_products,
                 f"got products_html has mf-filter={has_filters_products}")
    report.check("首页精选区不出筛选控件（filters=false）", not has_filters_home,
                 f"got index.html has mf-filter={has_filters_home}")
    assert_reveal_artifacts(report, dest)
    assert_search_index(report, dest)


def assert_post_featured(report):
    """文章精选（工单 0036-0039 决议）：fixture 独立构建，断言首页精选区与网格两片。

    期望值为独立字面量（fixture 的 slug 与日期是手写事实），不从实现重算。
    """
    dest = TMP / "posts-fixture"
    proc = build(POSTS_FIXTURE_CONFIG, dest)
    report.check("精选 fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    html = (dest / "index.html").read_text(encoding="utf-8")
    featured = parse_home_featured_slugs(html)
    report.check("精选区 = 3 条 featured 按日期倒序（limit 截断生效）",
                 featured == POSTS_FIXTURE_FEATURED, f"got {featured}")
    report.check(f"第 4 条 featured 被截断不上精选区（{POSTS_FIXTURE_TRUNCATED}）",
                 POSTS_FIXTURE_TRUNCATED not in featured, f"got {featured}")
    grid = parse_home_grid_slugs(html)
    report.check("最近更新网格 = 未入选文章（剔除精选，按日期倒序）",
                 grid == POSTS_FIXTURE_REST, f"got {grid}")
    overlap = sorted(set(featured) & set(grid))
    report.check("精选与网格互斥（同页不重复展示）", not overlap, f"overlap {overlap}")
    union = sorted(set(featured) | set(grid))
    report.check(f"精选 ∪ 网格 = 全量 {len(POSTS_FIXTURE_ALL)} 篇（无遗漏）",
                 union == POSTS_FIXTURE_ALL, f"got {union}")


def assert_post_featured_empty(report):
    """0 篇 featured 时精选区整块不渲染（0037 决议：不写空态文案）。"""
    dest = TMP / "posts-fixture-none"
    proc = build(POSTS_FIXTURE_CONFIG, dest, ["--contentDir", POSTS_EMPTY_CONTENT])
    report.check("无 featured fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    html = (dest / "index.html").read_text(encoding="utf-8")
    report.check("0 篇 featured → 精选区整块不渲染（无标题、无空态文案）",
                 "精选文章" not in html and parse_home_featured_slugs(html) == [],
                 "区块仍渲染（标题在或行非空）")


def assert_post_featured_bad(report):
    """featured 写成非布尔 → 构建失败（0036 决议：静默排除属静默失效类）。"""
    proc = build(POSTS_FIXTURE_CONFIG, TMP / "posts-fixture-bad",
                 ["--contentDir", POSTS_BAD_CONTENT])
    report_build_failure(report, "文章精选[featured 非布尔·字符串]", proc, POSTS_BAD_FEATURED_EXPECT)


def assert_post_featured_bad_int(report):
    """同上，整数坏值单开一例（0039 必锚④点名「字符串/整数」两类）。"""
    proc = build(POSTS_FIXTURE_CONFIG, TMP / "posts-fixture-bad-int",
                 ["--contentDir", POSTS_BAD_INT_CONTENT])
    report_build_failure(report, "文章精选[featured 非布尔·整数]", proc, POSTS_BAD_FEATURED_EXPECT)


def assert_post_grid_empty(report):
    """全部文章均入选时，「最近更新」网格整块不渲染（0037 决议第 1 条边界）。"""
    dest = TMP / "posts-fixture-all"
    proc = build(POSTS_FIXTURE_CONFIG, dest, ["--contentDir", POSTS_ALL_FEATURED_CONTENT])
    report.check("全 featured fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    html = (dest / "index.html").read_text(encoding="utf-8")
    # 注意：不能用「最近更新」文案子串判定——数据条的同名标签（月度更新）恒在。
    # 判定锚点是网格容器 class=mf-posts 与卡片点击层 entry-link。
    report.check("全部入选 → 精选区渲染 2 行、网格整块不渲染",
                 parse_home_featured_slugs(html) == ["all-feat-b", "all-feat-a"]
                 and "mf-posts" not in html and parse_home_grid_slugs(html) == [],
                 "grid/featured state unexpected")


def assert_empty_state(report):
    """空态守门：产品数据整体缺席（hugo.Data.products 为 nil）时，
    product-items 返回空 slice，渲染 seam 出「暂无资源」——nil 路径
    （0018 缺口清单第 6 项）不得变成崩溃或静默空页。

    dataDir 覆盖只丢 products：同目录放 fixture 的 sop.yaml 镜像，
    否则 SOP 适配器生成 0 页、首页索引页 ref 解析失败（与 fixture 同构，
    见 tests/fixtures/data/sop.yaml 头注释的踩坑记录）。
    """
    empty = TMP / "empty-data"
    empty.mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / "tests" / "fixtures" / "data" / "sop.yaml", empty / "sop.yaml")
    cfg = TMP / "empty-state.toml"
    cfg.write_text('dataDir = "tests/tmp/empty-data"\n', encoding="utf-8")
    proc = build("hugo.toml,%s" % cfg.relative_to(REPO), TMP / "empty-state")
    if proc.returncode != 0:
        report.check("空态构建成功", False, proc.stderr[-300:])
        return
    html = (TMP / "empty-state" / "products.html").read_text(encoding="utf-8")
    report.check(f"空态渲染「{EMPTY_STATE_TEXT}」", EMPTY_STATE_TEXT in html, "")


def assert_bad_cases(report):
    """每个坏 fixture 的构建必须失败——契约执法（模块内 errorf）。

    只发现本模块的用例：目录内含 products.yaml。tests/fixtures/bad/ 是
    共享空间（SOP 管线的 sop-* 用例同住），按内容归属过滤，防止互相扫入。
    """
    bad_root = REPO / "tests" / "fixtures" / "bad"
    cases = sorted(p.name for p in bad_root.iterdir()
                   if p.is_dir() and (p / "products.yaml").is_file()) if bad_root.is_dir() else []
    if not cases:
        report.check("存在契约坏用例", False, "tests/fixtures/bad/ 下没有用例")
        return
    for case in cases:
        cfg = TMP / f"bad-{case}.toml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text('dataDir = "tests/fixtures/bad/%s"\n' % case, encoding="utf-8")
        proc = build("hugo.toml,%s" % cfg.relative_to(REPO), TMP / f"bad-{case}")
        expect = BAD_CASE_EXPECT.get(case, "产品状态")
        report_build_failure(report, f"契约[{case}]", proc, expect)


def report_build_failure(report, label, proc, expect):
    """构建必须失败且输出含 expect——契约执法的统一判定（三种 seam 共用）。"""
    ok = proc.returncode != 0 and expect in (proc.stderr + proc.stdout)
    report.check(f"{label} → 构建失败且错误含 {expect!r}", ok,
                 "" if ok else "exit=%d stderr=%s" % (proc.returncode, (proc.stderr or proc.stdout)[-300:]))


def assert_bad_caller_limit(report):
    """调用方级坏用例：页面经短代码传 limit=-1，构建必须失败。

    构造 tests/tmp/content-limit-negative/ 作为 contentDir 覆盖，
    其中的页面 {{< product-index limit="-1" >}} 走完整调用链
    （短代码 → product-items → errorf）。只覆盖 dataDir/contentDir，
    layouts/其余配置用真实站点。契约落点：layouts/partials/product-items.html。
    """
    content = TMP / "content-limit-negative"
    content.mkdir(parents=True, exist_ok=True)
    (content / "limit-negative.md").write_text(
        "+++\ntitle = \"fixture-limit-negative\"\ndraft = false\n+++\n\n"
        '{{< product-index limit="-1" >}}\n', encoding="utf-8")
    cfg = TMP / "caller-limit-negative.toml"
    cfg.write_text('dataDir = "tests/fixtures/data"\n'
                   'contentDir = "tests/tmp/content-limit-negative"\n', encoding="utf-8")
    proc = build("hugo.toml,%s" % cfg.relative_to(REPO), TMP / "caller-limit-negative")
    report_build_failure(report, "调用方[limit=-1]", proc, CALLER_LIMIT_NEGATIVE_EXPECT)


def assert_bad_caller_direct(report, case, label, expect, single_html):
    """调用方级坏用例（直调 partial 族）：layoutsDir/contentDir flag + dataDir
    配置文件构造最小站点，临时 single.html 直接调渲染 seam。partial 解析根随
    layoutsDir 走，故把被测 partial 复制进临时布局树（仓库真实文件的副本）。

    注：layoutsDir 写在追加配置文件里不生效（Hugo 合并语义，实测），必须走
    CLI flag；dataDir 无 CLI flag，走配置文件。二者组合使用。

    现役两格：items 缺失（0018 缺口第 6 项）、uid 缺失（0017 决议）。
    """
    layout_root = TMP / f"layouts-{case}"
    (layout_root / "partials").mkdir(parents=True, exist_ok=True)
    (layout_root / "_default").mkdir(parents=True, exist_ok=True)
    for name in ("product-index.html", "product-state.html", "product-items.html"):
        shutil.copy(REPO / "layouts" / "partials" / name, layout_root / "partials" / name)
    (layout_root / "_default" / "single.html").write_text(single_html, encoding="utf-8")
    content = TMP / f"content-{case}"
    content.mkdir(parents=True, exist_ok=True)
    (content / "page.md").write_text('+++\ntitle = "t"\ndraft = false\n+++\n', encoding="utf-8")
    cfg = TMP / f"caller-{case}.toml"
    cfg.write_text('dataDir = "tests/fixtures/data"\n', encoding="utf-8")
    proc = build("hugo.toml,%s" % cfg.relative_to(REPO), TMP / f"caller-{case}",
                 ["--layoutDir", str(layout_root), "--contentDir", str(content)])
    report_build_failure(report, f"调用方[{label}]", proc, expect)


def assert_bad_caller_missing_items(report):
    assert_bad_caller_direct(
        report, "items", "items 缺失", CALLER_MISSING_ITEMS_EXPECT,
        '{{ partial "product-index.html" (dict "filters" false "uid" "mf-x") }}\n')


def assert_bad_caller_missing_uid(report):
    assert_bad_caller_direct(
        report, "uid", "uid 缺失", CALLER_MISSING_UID_EXPECT,
        '{{- $items := partial "product-items.html" (dict) -}}\n'
        '{{ partial "product-index.html" (dict "items" $items "filters" false) }}\n')


def assert_real(report):
    dest = TMP / "real"
    proc = build(REAL_CONFIG, dest)
    report.check("真实数据构建成功（生产配置）", proc.returncode == 0, proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    rows = parse_rows(dest / "products.html")
    all_unlisted = len(rows) == REAL_ROW_COUNT and all(
        r["control"] == "disabled" and r["label"] == "即将上架" and r["aria_disabled"] == "true"
        for r in rows.values())
    report.check(f"真实数据 {REAL_ROW_COUNT} 条全部「即将上架」", all_unlisted,
                 f"got {len(rows)} rows: " + ", ".join("%s=%s/%s" % (k, v["control"], v["label"]) for k, v in rows.items()))
    count = parse_spec_count((dest / "index.html").read_text(encoding="utf-8"), "可下载产品")
    report.check(f"真实数据可下载产品计数 = {REAL_LISTED_COUNT}", count == REAL_LISTED_COUNT, f"got {count}")
    home_ids = [pid for pid in parse_rows(dest / "index.html") if pid]
    report.check("真实数据首页精选 = 3 条 featured 产品（yaml 序）", home_ids == REAL_HOME_FEATURED_IDS,
                 f"got {home_ids}")
    assert_theme_contract(report, dest)


def assert_theme_contract(report, dest):
    """主题层契约（0032 决议：B7-B12）。期望值为独立字面量，不从实现重算。"""
    # B7: no-js 基线全站面——每页 <html> 带 no-js，且含内联 no-js→js 交换脚本。
    # 排除 Hugo 的别名/跳转页（page/1.html 等，meta refresh，不走 baseof）。
    pages = sorted(p for p in dest.rglob("*.html")
                   if 'http-equiv="refresh"' not in p.read_text(encoding="utf-8"))
    bad_class, bad_swap = [], []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if not re.search(r"<html[^>]*class=[\"']?no-js", html):
            bad_class.append(page.relative_to(dest).as_posix())
        if "classList.remove(" not in html or "no-js" not in html:
            bad_swap.append(page.relative_to(dest).as_posix())
    report.check(f"全站 {len(pages)} 页均带 no-js 基线类", not bad_class,
                 f"缺类: {', '.join(bad_class[:3])}")
    report.check(f"全站 {len(pages)} 页均含内联 no-js→js 交换脚本", not bad_swap,
                 f"缺脚本: {', '.join(bad_swap[:3])}")

    # B8: post_meta 的 title 属性为显式时区格式（手写文章；SOP golden 不覆盖此路径，
    # 且 golden 的规范化器刻意容忍两种时区形态——回归牙口由本条提供）。
    post = dest / "posts" / "aiops-state-and-tools.html"
    post_html = post.read_text(encoding="utf-8") if post.exists() else ""
    report.check("post_meta title 属性为显式时区格式（YYYY-MM-DD HH:MM:SS +0800）",
                 bool(POST_META_TITLE_RE.search(post_html)),
                 "未匹配显式时区格式（可能回退为裸 .Date）")

    # B9: 菜单渲染契约——9 个顶层项按 weight 序；内部链接符合 uglyURLs 形态。
    # 注意：测试构建不带 --minify（属性带引号），public/ 产物是 minify 的（属性无引号），
    # 正则必须两种形态都吃。
    menu = re.search(r"<ul id=[\"']?menu[\"']?>(.*?)</ul>", post_html, re.S)
    keys = ([_nav_key(h) for h in re.findall(r"<a href=[\"']?([^\"' >]+)", menu.group(1))]
            if menu else [])
    report.check(f"菜单渲染 {len(MENU_RENDERED_KEYS)} 项且顺序正确",
                 keys == MENU_RENDERED_KEYS, f"got {keys}")
    bad_urls = [k for k in keys if not (k.endswith(".html") or k.endswith("/")
                                        or k.startswith(("mailto:", "https://github.com/")))]
    report.check("菜单内部链接符合 uglyURLs 形态（.html 或 / 结尾）", not bad_urls,
                 f"bad: {bad_urls}")

    # B10: 首页 RSS 只收 posts（内容策略，站点 rss.xml 的核心语义）。
    rss_path = dest / "index.xml"
    rss = rss_path.read_text(encoding="utf-8") if rss_path.exists() else ""
    items = re.findall(r"<item>.*?<link>(.*?)</link>", rss, re.S)
    report.check(f"首页 RSS {len(items)} 条 item 全部为 posts", bool(items) and all("/posts/" in link for link in items),
                 f"非 posts 条目: {[l for l in items if '/posts/' not in l][:3]}")

    # B11: search 页 DOM 三挂点（fastsearch 的挂点契约；坏了搜索静默失效）。
    search_path = dest / "search.html"
    search_html = search_path.read_text(encoding="utf-8") if search_path.exists() else ""
    missing = [anchor for anchor in ("searchbox", "searchInput", "searchResults")
               if not re.search(rf"id=[\"']?{anchor}[\"' >]", search_html)]
    report.check("search 页三挂点齐全（searchbox/searchInput/searchResults）", not missing,
                 f"缺: {missing}")

    # B12: og:image 兜底——无封面图的页面也输出 og:image（来自 site.Params.ogImage）。
    about_path = dest / "about.html"
    about_html = about_path.read_text(encoding="utf-8") if about_path.exists() else ""
    report.check("无封面页仍输出 og:image（ogImage 兜底）",
                 'property="og:image"' in about_html and "img/og-cover.png" in about_html,
                 "about.html 缺 og:image 或未命中 ogImage 值")


def assert_single_copy(report):
    """0030 决策的永久断言：站点层与主题层不得有同相对路径文件（覆盖层已消除）。

    覆盖层复活 = 两份文件、两种真相、同步义务回归——本断言把它变成构建前可发现的错误。
    """
    site_root = REPO / "layouts"
    theme_root = REPO / "themes" / "maplemod" / "layouts"
    site = {p.relative_to(site_root).as_posix() for p in site_root.rglob("*") if p.is_file()}
    theme = {p.relative_to(theme_root).as_posix() for p in theme_root.rglob("*") if p.is_file()}
    dup = sorted(site & theme)
    report.check("站点层与主题层无同相对路径文件（覆盖层已消除）", not dup, f"重复: {dup}")


def main():
    parser = argparse.ArgumentParser(description="产品状态模块产物断言")
    parser.add_argument("--quick", action="store_true", help="跳过真实数据构建")
    args = parser.parse_args()

    if shutil.which("hugo") is None:
        print("ERROR: hugo 不在 PATH（CI 由 peaceiris/actions-hugo 提供）")
        return 2

    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)

    report = Report()
    assert_single_copy(report)
    assert_fixture(report)
    assert_post_featured(report)
    assert_post_featured_empty(report)
    assert_post_featured_bad(report)
    assert_post_featured_bad_int(report)
    assert_post_grid_empty(report)
    assert_empty_state(report)
    assert_bad_cases(report)
    assert_bad_caller_limit(report)
    assert_bad_caller_missing_items(report)
    assert_bad_caller_missing_uid(report)
    if not args.quick:
        assert_real(report)

    width = max(len(name) for _, name, _ in report.items)
    for ok, name, detail in report.items:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name.ljust(width)}" + (f"  {detail}" if detail and not ok else ""))
    failed = report.failed
    print(f"\n{len(report.items) - len(failed)}/{len(report.items)} passed")
    if failed:
        print("RED — %d 个行为未满足" % len(failed))
        return 1
    print("GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
