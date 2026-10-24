#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点契约的产物断言（原名 assert_product_states.py——2026-10 职责扩张后改名，
ADR 与历史 handoff 里的旧名即本脚本）。覆盖十一类职责：
产品状态模块（ADR-0004）· 产品索引接口（ADR-0006）· 主题契约 B7-B14（ADR-0008；
B14 为候选 12 工单 0050 决议④的搜索入口菜单文案，挂真实构建）
· reveal 产物面（ADR-0007）· 文章精选（候选 7 工单 0036-0040 决议）· 搜索索引投影
（候选 8 工单 0043/0044 决议，ADR-0010）· 搜索交付面与 fastsearch 守门（候选 8
工单 0046/0047 决议，ADR-0010）· 搜索入口构件与加载面（候选 12 工单 0050
决议⑧：构件交付面 / URL 子路径 / 全站恒加载 / 第二个消费方反向守门）
· 阅读辅助 meta（2026-10-24 阅读体验批 A2：文章页含时长+字数、卡片 compact
只留时长、SOP 派生页含两者）· 主题切换过渡（2026-10-24 视觉批 D2：body 颜色
过渡 / 卡片 --card-motion 单一真源 / 次级文本 color 过渡 / reduced-motion 守卫）
· 文章目录（2026-10-24 阅读体验批 A1：条目与正文 h2 数量/文本/顺序全等；无 h2
的页面整块不渲染）。

测试缝（预先商定，勿在未确认的缝上写测试）：
  · 渲染产物 seam —— fixture 构建的 products.html（控件态 / 文案 / data-price）
    与 index.html（「可下载产品」计数、首页精选区 featured 分栏）
  · 文章精选 seam —— 独立 fixture 构建（tests/hugo.test.posts.toml，只覆盖
    contentDir）：首页精选区的 3 条 featured、与「最近更新」网格互斥且并集全量、
    0 篇 featured 时精选区整块不渲染、featured 非布尔即构建失败；**精选标识
    三面呈现（文章页 / 列表卡片 / 首页网格）与首页精选行负向**（ADR-0012）
  · 阅读辅助 seam —— 同一 posts fixture 的文章页 .post-meta 与 /posts/ 卡片
    entry-footer（两种调用形态）+ 真实构建的 SOP 派生页（site 级参数可达派生文）
  · 文章目录 seam —— 真实构建的 SOP 派生页（目录条目 == 正文 h2 序列）+ fixture
    无标题文章页（空态整块不渲染）
  · 主题切换过渡 seam —— fixture 构建产物 CSS 的 body / 卡片 / 次级文本 transition
    规则与 prefers-reduced-motion 守卫（视觉值非契约，只守规则在场）
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
return 写法本地过、CI 红。**断言只消费构建产物；版本比对是 preflight WARN**
（不进断言计数、不影响退出码），钉版真源是 `.github/workflows/deploy.yml`。

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
CI_WORKFLOW = REPO / ".github" / "workflows" / "deploy.yml"

FIXTURE_CONFIG = "hugo.toml,tests/hugo.test.toml"
REAL_CONFIG = "hugo.toml,config.production.toml"


def preflight_hugo_version():
    """Hugo 版本 skew 的 advisory 提醒——**不进断言计数、不影响退出码**。

    钉版真源是 deploy.yml 的 hugo-version（不在本文件写第二份）。不一致时只 WARN：
    本机服从 CI 是纪律，但「本机版本不同」不等于「本机产物错」——断言仍然有效，
    只是它证明不了 CI 会绿。依据 ADR-0004：0.166+ 的条件多 return 写法本地过、CI 红。
    """
    try:
        found = re.search(r"hugo-version:\s*'([^']+)'", CI_WORKFLOW.read_text(encoding="utf-8"))
    except OSError:
        return
    if not found:
        return
    pinned = found.group(1)
    try:
        out = subprocess.run(["hugo", "version"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        print(f"[WARN] 读不到本机 hugo 版本；CI 钉版 {pinned}。跳过版本比对。\n")
        return
    local = re.search(r"v(\d+\.\d+\.\d+)", out)
    if not local:
        print(f"[WARN] 本机 hugo 版本串不可解析；CI 钉版 {pinned}。跳过版本比对。\n")
        return
    if local.group(1) != pinned:
        print(f"[WARN] 本机 hugo {local.group(1)} != CI 钉版 {pinned}（deploy.yml）")
        print("       0.166+ 的部分写法本地过、CI 红（ADR-0004）；提交前以 CI 钉版为准。\n")

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

# 精选标识（徽标）契约（ADR-0012 决策 2 / 工单 0056）：三面呈现、精选行不加。
# 期望值为独立字面量：fixture 的 slug 与 featured 分布是手写事实，不从实现重算。
POSTS_BADGE_FEATURED = ["fx-post-feat-a", "fx-post-feat-b", "fx-post-feat-c", "fx-post-feat-d"]
POSTS_BADGE_PLAIN = ["fx-post-false", "fx-post-newest"]
# 契约标记（契约定义处：themes/maplemod/layouts/partials/featured-badge.html docstring）；
# 测试构建不带 --minify，属性带引号（同 B9 注释）。
BADGE_SPAN_RE = re.compile(r'<span class="mf-featured" title="精选">')

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
    # 搜索索引投影契约（工单 0043 决议①：投影守自消费字段）。
    # 钉子串取 errorf 消息的前缀子串（前缀 + 条目 id + 字段名；消息后缀
    # 「（投影必填，无缺省）」不钉）——与产品侧钉子串的子串约定同款。
    "search-missing-name": '搜索索引数据："fx-search-missing-name" 缺少 name',
    "search-missing-summary": '搜索索引数据："fx-search-missing-summary" 缺少 summary',
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

# 搜索索引投影契约（工单 0043 决议③④）：每条记录恰为投影六字段；
# fastsearch 默认 keys 是其子集，差集恰为扩展检索字段——对齐由静态断言
# 执法，这是投影 docstring 接口条款（跨站点层投影 × 主题层消费方）唯一的牙。
SEARCH_INDEX_FIELDS = {"title", "permalink", "summary", "content", "tags", "categories"}
SEARCH_FASTSEARCH_KEYS = ["title", "permalink", "summary", "content"]
SEARCH_EXTRA_FIELDS = {"tags", "categories"}
# 产品条目形态期望值（0044 决议③：投影 docstring ③ 的牙）：fixture 五产品的
# (name, summary, scale) 独立字面量——与 tests/fixtures/data/products.yaml 逐字
# 对应（summary 均为「已上架 + 付费」式带空格加号），改 fixture 数据须同步改这里。
# permalink 为根相对形态（.RelPermalink 无域名）。
FIXTURE_PRODUCT_SHAPE = {
    "fx-unlisted-plain": ("夹具·未上架免费（非精选）", "featured: false 对照行——必须不上首页，但在产品页可见。", "1 页"),
    "fx-listed-paid": ("夹具·已上架付费", "已上架 + 付费 → 可点「购买」+ data-price=paid。", "1 个模板"),
    "fx-listed-free": ("夹具·已上架免费", "已上架 + 免费 → 可点「免费获取」+ data-price=free。", "1 页"),
    "fx-unlisted-paid": ("夹具·未上架付费", "未上架 + 付费 → 禁用「即将上架」+ data-price=paid（与价格无关）。", "1 题"),
    "fx-unlisted-free": ("夹具·未上架免费", "未上架 + 免费 → 禁用「即将上架」+ data-price=free（免费同样可以即将上架）。", "1 页"),
}

# 主题层契约（0032 决议）的独立字面量：post_meta 的 title 属性必须是显式时区格式，
# 不是 Go 的 time.Time.String()（后者由构建机时区决定输出字节）。
POST_META_TITLE_RE = re.compile(r"title='\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}'")

# 菜单渲染契约（0032 决议 B9）：hugo.toml 的 9 条 menu.main 全部是顶层项——2026-10-23
# 删除了 4 条不渲染的 parent=categories 死配置（Hugo 的 site.Menus.main 本就不含子项，
# 故子项配置零读取点）。期望值 = 实际渲染的 9 项，按 weight 序；内部链接符合 uglyURLs 形态。
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


def parse_home_featured_block(html):
    """首页「精选文章」区的 ol.mf-rows 块（按标题锚定后的第一个 mf-rows）。

    不取「第一个 mf-rows」——产品精选区同用该 class，0 篇 featured 时第一个
    mf-rows 就是产品区（会把空态断言变成假红）。无「精选文章」标题 → None。
    """
    anchor = re.search(r"精选文章", html)
    if not anchor:
        return None
    return re.search(r'<ol class=["\']?mf-rows["\']?>(.*?)</ol>', html[anchor.start():], re.S)


def parse_home_featured_slugs(html):
    """首页「精选文章」区的 slug 序。"""
    block = parse_home_featured_block(html)
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


def parse_badge_present(html):
    """页面是否渲染精选徽标（契约标记：span.mf-featured[title=精选]）。"""
    return bool(BADGE_SPAN_RE.search(html))


def parse_card_badges(html, article_class):
    """按文章卡片容器切块，返回 {slug: 是否带精选徽标}。

    entry-link 是整卡点击层（既有网格判定同款锚点）；徽标在卡片标题内、
    entry-link 之前，故按 <article> 切块后可同块判定。article_class 传
    "post-entry"（主题层列表卡）或 "mf-post"（站点层首页网格卡）。
    """
    cards = {}
    for block in re.split(r'<article class="' + article_class + r'[\s"]', html)[1:]:
        m = re.search(r'class="entry-link"[^>]*href="([^"]+)"', block)
        if m:
            cards[_post_slug(m.group(1))] = bool(BADGE_SPAN_RE.search(block))
    return cards


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


def assert_search_projection(report, dest):
    """搜索索引投影的接口条款（工单 0043 决议④⑤）：条目字段集 + fastsearch keys 对齐。

    两条独立字面量 + 一条关系断言：
      ① 构建产物每条记录恰为投影六字段（契约定义处：index.json docstring 字段表）；
      ② fastsearch.js 默认 options 块的 keys 为四字段字面量——读主题层源码，
         接口条款横跨两层，断言语境在站点层套件（与 B7-B13 读主题文件同例）；
         该文件是单副本活文件（项目级 assets 覆盖已于 0046 施工期合并删除，
         复活守门见函数末尾）；
      ③ 差集恰为 {tags, categories}（扩展检索预留）——接口条款本身。
    变异检验：改投影字段集 / 改 fastsearch keys，两条各红过才收。
    """
    index = json.loads((dest / "index.json").read_text(encoding="utf-8"))
    bad_shape = [e.get("permalink") for e in index if set(e) != SEARCH_INDEX_FIELDS]
    report.check(f"索引 {len(index)} 条记录均为投影六字段", not bad_shape,
                 f"字段集不符: {bad_shape[:3]}")
    js = (REPO / "themes" / "maplemod" / "assets" / "js" / "fastsearch.js").read_text(encoding="utf-8")
    m = re.search(r"let options = \{(.*?)\n\s*\};", js, re.S)
    km = re.search(r"keys:\s*\[([^\]]*)\]", m.group(1), re.S) if m else None
    keys = re.findall(r"'([^']+)'", km.group(1)) if km else []
    report.check("fastsearch 默认 keys = [title, permalink, summary, content]",
                 keys == SEARCH_FASTSEARCH_KEYS, f"got {keys}")
    report.check("投影字段 - fastsearch keys = {tags, categories}（扩展检索预留）",
                 SEARCH_INDEX_FIELDS - set(keys) == SEARCH_EXTRA_FIELDS,
                 f"got {SEARCH_INDEX_FIELDS - set(keys)}")
    # 产品条目形态（0044 决议③）：title=name / permalink 锚点 / content 三字段拼接。
    # 期望值为 fixture 数据的独立字面量（不从实现重算）。
    fx = {e["permalink"].rsplit("#", 1)[-1]: e for e in index
          if "products.html#" in (e.get("permalink") or "")}
    bad_product = []
    for pid, (name, summary, scale) in FIXTURE_PRODUCT_SHAPE.items():
        e = fx.get(pid, {})
        if not (e.get("title") == name
                and e.get("permalink") == "/products.html#" + pid
                and e.get("content") == f"{name} {summary} {scale}"):
            bad_product.append(pid)
    report.check("产品条目形态（title=name / permalink 锚点 / content 拼接）",
                 not bad_product, f"不符: {bad_product}")
    # 单副本守门（0046 施工期发现）：fastsearch.js 曾有项目级覆盖（assets/js/
    # 覆盖 themes/maplemod/assets/js/，子模块时代的遗产），覆盖与本文件读的主题
    # 路径会静默漂移（0043 施工期的 B3 一度读的是死文件）。合并已入主题层，
    # 项目级副本复活即本断言红。
    report.check("fastsearch.js 单副本（无项目级 assets 覆盖复活）",
                 not (REPO / "assets" / "js" / "fastsearch.js").exists(),
                 "assets/js/fastsearch.js 复活：覆盖层=两份真相，B3 读的可能是死文件")


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
        rel = re.sub(r'^/(mapleFlow/)?', '', m.group(1))
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
    assert_search_projection(report, dest)
    assert_search_artifacts(report, dest)
    assert_search_entry_artifacts(report, dest)
    assert_theme_transition(report, dest)


def assert_theme_transition(report, dest):
    """主题切换过渡（2026-10-24 视觉批 D2）：切换时颜色平滑过渡，不是硬闪。

    纯 CSS 实现（不新增 JS / 动效模块）：body 等大面元素在切换时过渡颜色；
    卡片必须**保留原有 transform 动效**（按下反馈）再追加颜色，否则整份
    transition 被覆盖会把卡片按压动画弄丢。
    三条落地牙：
      ① body 规则含 background-color 过渡（页面底色是切换最显眼的面）；
      ② 卡片规则同时含 transform 与 background-color（保留动效 + 追加颜色）；
      ③ 整段包在 prefers-reduced-motion 守卫内（减弱动效偏好下瞬时切换）。
    只守「规则在场且属性对」，不守时长/曲线具体值（视觉值非契约，
    与 .mf-featured 同款纪律）。期望值为独立字面量：属性名与媒体查询词是
    spec 的直写，不从实现重算。
    """
    css_text = "\n".join(p.read_text(encoding="utf-8") for p in dest.rglob("*.css"))
    report.check("产物 CSS 含 body 背景色过渡（主题切换不硬闪）",
                 re.search(r"body[^{]*\{transition:[^}]*background-color", css_text) is not None,
                 "missing body background-color transition in built CSS")
    # 卡片的动效列表是单一真源（--card-motion 定义在 section 15 的卡片规则里），
    # 16d 用 var() 组合颜色项——这里同时守「变量含 transform（按压反馈）」与
    # 「卡片 transition 由变量 + background-color 组成」（结构即契约：变量存在
    # 是为了消除 15↔16d 的整份抄写，抄回去就红）。
    report.check("卡片动效走 --card-motion 单一真源且追加 background-color",
                 re.search(r"\.post-entry[^{]*\{[^}]*--card-motion:[^}]*transform[^}]*\}",
                           css_text) is not None
                 and re.search(r"\.post-entry[^{]*\{transition:var\(--card-motion\)[^}]*background-color",
                               css_text) is not None,
                 "card motion variable or composed transition missing")
    report.check("主题切换过渡包在 prefers-reduced-motion 守卫内",
                 re.search(r"prefers-reduced-motion:\s*(no-preference|reduce)", css_text) is not None,
                 "missing prefers-reduced-motion guard around theme transition")
    # 行内次级文本与目录标签显式着色 var(--secondary)，不会随 body 的 color
    # 过渡继承——不单独给它们加 color 过渡，切换时会跳色。允许合成一条规则
    # 或分散声明（只要求「每个选择器都有 transition + color」）。
    def _has_color_transition(selector):
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css_text):
            if selector in m.group(1) and "transition:" in m.group(2) and "color" in m.group(2):
                return True
        return False

    missing = [s for s in (".mf-row-sum", ".mf-row-meta", ".post-toc-title")
               if not _has_color_transition(s)]
    report.check("显式着色的次级文本含 color 过渡（切换不跳色）", not missing,
                 f"missing color transition: {missing}")


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


def assert_featured_badge(report):
    """精选标识（徽标）三面契约（ADR-0012 决策 2 / 工单 0056 决议）。

    fixture 独立构建（contentDir 覆盖，与文章精选同套 fixture）：
      ① 文章页（single）：4 篇 featured 有徽标、false/未声明无；
      ② 列表卡片（分类/标签页 + /posts/，同走主题层 list.html）：按卡片判；
      ③ 首页网格卡片（站点层 index.html）：被 limit 截断回落的 feat-a 有徽标；
      ④ 负向：首页精选行（区块标题「精选文章」已表达）无徽标。
    真实构建不锚（ADR-0009「真实精选清单不锚」原则——真实 featured 由项目负责人掌控）。
    期望值为独立字面量；变异检验逐面做过（去条件 / 去调用点 / 精选行误加）。
    """
    dest = TMP / "posts-fixture-badge"
    proc = build(POSTS_FIXTURE_CONFIG, dest)
    report.check("徽标 fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    # ① 文章页（single.html 标题旁）
    bad_has = [s for s in POSTS_BADGE_FEATURED
               if not parse_badge_present((dest / "posts" / f"{s}.html").read_text(encoding="utf-8"))]
    report.check("文章页：4 篇 featured 均带精选徽标", not bad_has, f"缺徽标: {bad_has}")
    bad_plain = [s for s in POSTS_BADGE_PLAIN
                 if parse_badge_present((dest / "posts" / f"{s}.html").read_text(encoding="utf-8"))]
    report.check("文章页：false/未声明文章不带徽标", not bad_plain, f"误带: {bad_plain}")
    # ② 列表卡片（分类/标签页 + /posts/，同走主题层 list.html）
    for label, path in (("分类页", dest / "categories" / "fixture.html"),
                        ("标签页", dest / "tags" / "fixture.html"),
                        ("/posts/ 列表", dest / "posts" / "index.html")):
        cards = parse_card_badges(path.read_text(encoding="utf-8"), "post-entry")
        bad_has = [s for s in POSTS_BADGE_FEATURED if not cards.get(s)]
        report.check(f"{label}：4 篇 featured 卡片带徽标", not bad_has, f"缺徽标: {bad_has}")
        bad_plain = [s for s in POSTS_BADGE_PLAIN if cards.get(s)]
        report.check(f"{label}：false/未声明卡片不带徽标", not bad_plain, f"误带: {bad_plain}")
    # ③ 首页网格卡片（站点层 index.html；被 limit 截断回落的 feat-a 是天然样本）
    home_html = (dest / "index.html").read_text(encoding="utf-8")
    grid = parse_card_badges(home_html, "mf-post")
    report.check("首页网格：截断回落的 featured（fx-post-feat-a）带徽标",
                 grid.get(POSTS_FIXTURE_TRUNCATED) is True, f"got {grid}")
    bad_plain = [s for s in POSTS_BADGE_PLAIN if grid.get(s)]
    report.check("首页网格：false/未声明卡片不带徽标", not bad_plain, f"误带: {bad_plain}")
    # ④ 负向：首页精选行不带徽标（区块标题「精选文章」已表达，0056 决议一）
    block = parse_home_featured_block(home_html)
    report.check("首页精选行不带徽标（区块标题已表达）",
                 block is not None and not BADGE_SPAN_RE.search(block.group(1)),
                 "精选行出现徽标" if block else "找不到精选行区块")
    # ⑤ 视觉层落地牙：契约 class 必须在产物 CSS 里有规则（ADR-0012：视觉值归视觉层，
    #    但 class=mf-featured 无样式 = 裸文本「精选」，是未完成态而非设计选择）
    css_text = "\n".join(p.read_text(encoding="utf-8") for p in dest.rglob("*.css"))
    report.check("产物 CSS 含 .mf-featured 精选标识规则（视觉层落地）",
                 ".mf-featured" in css_text, "missing .mf-featured rule in built CSS")


def assert_post_reading_meta(report):
    """文章页 meta 行的阅读辅助契约（2026-10-24 阅读体验批 A2）。

    契约：文章页 meta 行同时呈现阅读时长（「N 分钟」）与字数（「N 字」）。
    中文串由主题 i18n zh-cn.yaml 的 read_time / words 既有条目承载；本批只开
    site 级参数 ShowReadingTime / ShowWordCount。**site 级是唯一可达路径**：
    SOP 派生文的 front matter 只透传 categories/tags/featured
    （content/posts/_content.gotmpl），页面级参数对派生文不可设。
    本断言守「参数确实开启且渲染到产物」，不守具体数值——读数由正文长度
    决定，非契约。

    期望值为独立字面量：中文单位串「分钟」「字」来自 i18n 契约，不从实现重算。
    锚 fixture 构建（POSTS_FIXTURE_CONFIG，与精选/徽标同套 fixture）。
    """
    dest = TMP / "posts-fixture-reading"
    proc = build(POSTS_FIXTURE_CONFIG, dest)
    report.check("阅读辅助 fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    sample = dest / "posts" / f"{POSTS_BADGE_FEATURED[0]}.html"
    if not sample.is_file():
        report.check("阅读辅助：样本文章页存在", False, f"missing {sample}")
        return
    html = sample.read_text(encoding="utf-8")
    m = re.search(r'<div class="post-meta">(.*?)</div>', html, re.S)
    if not m:
        report.check("阅读辅助：文章页存在 post-meta 区块", False, "no .post-meta block")
        return
    meta = m.group(1)
    report.check("meta 行含阅读时长（N 分钟）", re.search(r"\d+\s*分钟", meta) is not None,
                 f"meta={meta[:160]!r}")
    report.check("meta 行含字数（N 字）", re.search(r"\d+\s*字", meta) is not None,
                 f"meta={meta[:160]!r}")
    # 卡片形态（compact）：只留阅读时长、不留字数——窄卡片上「N 字」会换行成
    # 孤字（首页 335px 卡片实测「571 / 字」断行）。同一 partial 两种形态，
    # 本对断言守「两种形态确实不同」。
    list_html = (dest / "posts" / "index.html").read_text(encoding="utf-8")
    card = re.search(r'<footer class="entry-footer">(.*?)</footer>', list_html, re.S)
    if not card:
        report.check("阅读辅助：列表卡片存在 entry-footer", False, "no card footer in /posts/")
        return
    card_meta = card.group(1)
    report.check("卡片 meta 含阅读时长", re.search(r"\d+\s*分钟", card_meta) is not None,
                 f"card meta={card_meta[:160]!r}")
    report.check("卡片 meta 不含字数（compact 形态，避免窄卡孤字换行）",
                 re.search(r"\d+\s*字", card_meta) is None,
                 f"card meta={card_meta[:160]!r}")


def assert_post_toc(report):
    """文章目录（2026-10-24 阅读体验批 A1）：文内顶部目录，只收 h2。

    契约（三个目的地已定）：
      ① 位置 = 文内顶部（不做常驻侧栏——内容宽 970px，代码块密集）；
      ② 移动端 = 同一标记仅列数变化（桌面两列 / ≤768px 一列，不折叠）；
      ③ 无滚动高亮（顶部目录随内容滚走，高亮只对常驻目录有意义）——
         由「零 JS」实现保证：本批不引入任何脚本，故无高亮可断。
    四条落地牙（本函数锚真实构建，故只在完整套件执行；空态另见
    assert_post_toc_empty——那里 fixture 即可，--quick 也跑）：
      · TOC 条目 == **源笔记的 h2 序列**——期望值取自 docs/sop/ANSIBLE_SOP.md
        的 `## ` 行（内容事实，独立于模板与产物），不是拿页面正文反算自己；
        多收 h3、漏收 h2、顺序漂移都会红；
      · 目录不使用 `<details>` 折叠（② 的「不折叠」落地牙）；
      · 桌面 `columns:2`、≤768px 媒体查询内 `columns:1`（② 的列数落地牙）。
    """
    dest = TMP / "real"
    if not dest.is_dir():
        report.check("目录：真实构建产物存在", False, "missing tests/tmp/real（先跑完整套件）")
        return
    sop_page = dest / "posts" / "sop-ansible-automation-guide.html"
    if not sop_page.is_file():
        report.check("目录：真实 SOP 派生页存在", False, f"missing {sop_page}")
        return
    html = sop_page.read_text(encoding="utf-8")
    toc = re.search(r'<div class="post-toc">(.*?)</div>\s*<div class="post-content">', html, re.S)
    if not toc:
        report.check("SOP 文章页渲染 .post-toc 目录", False, "no .post-toc block")
        return
    toc_html = toc.group(1)
    toc_titles = [x.strip() for x in re.findall(r"<li><a[^>]*>(.*?)</a></li>", toc_html, re.S)]
    # 独立字面量：源笔记的 h2 行（去掉 "## " 前缀），不从产物重算
    note = REPO / "docs" / "sop" / "ANSIBLE_SOP.md"
    note_h2 = [ln[3:].strip() for ln in note.read_text(encoding="utf-8").splitlines()
               if ln.startswith("## ")]
    report.check("TOC 条目 == 源笔记 h2 序列（数量/文本/顺序全等）",
                 toc_titles == note_h2, f"toc={toc_titles} note_h2={note_h2}")
    report.check("目录不使用 details 折叠（移动端同标记展开）",
                 "<details" not in toc_html, "details found in .post-toc")
    css_text = "\n".join(x.read_text(encoding="utf-8") for x in dest.rglob("*.css"))
    report.check("目录桌面两列、≤768px 单列（列数收口）",
                 re.search(r"\.post-toc ul\{[^}]*columns:2", css_text) is not None
                 and re.search(r"@media\(max-width:768px\)\{[^@]*columns:1", css_text) is not None,
                 "column count missing (desktop 2 / mobile 1)")


def assert_post_toc_empty(report):
    """目录空态（A1）：无 h2 的页面整块不渲染（与精选区/网格同一空态纪律）。

    锚 fixture 构建（assert_post_reading_meta 已建；本函数在 --quick 下也执行，
    因为空态不依赖真实数据）。fixture 文章正文只有一句话、无任何标题。
    """
    fixture_dest = TMP / "posts-fixture-reading"
    plain_page = fixture_dest / "posts" / f"{POSTS_BADGE_PLAIN[0]}.html"
    if not plain_page.is_file():
        report.check("目录空态：fixture 文章页存在", False,
                     f"missing {plain_page}（应先用 POSTS_FIXTURE_CONFIG 构建）")
        return
    report.check("无标题文章不渲染目录（空态整块不渲染）",
                 'class="post-toc"' not in plain_page.read_text(encoding="utf-8"),
                 "post-toc rendered on a page without headings")


def assert_search_fixture(report):
    """文章侧投影形态与三类排除规则（工单 0043 决议⑤；0044 字段契约的落面）。

    fixture：tests/fixtures/content-search——2 篇正常文章（alpha 短正文 /
    beta 含 markdown）+ searchHidden / archives layout / search layout 三页。
    复用 hugo.test.posts.toml + --contentDir 既有机制（0039 的 none/all/bad
    变体同款），不新增构建配置；fixture 日期一律过去日（坑点 12：Hugo 不发布
    未来内容）。期望值为独立字面量（fixture 正文是手写事实，不从实现重算）。
    前提记录：fixture 无 products 页（site.GetPage "page" "products" 不成立），
    故索引只应含文章条目——若将来给 fixture 加 products 页，「仅含 2 篇」
    断言须同步改，否则会以「got N 条」误导排除规则的排障方向。
    """
    dest = TMP / "search-fixture"
    proc = build(POSTS_FIXTURE_CONFIG, dest, ["--contentDir", "tests/fixtures/content-search"])
    report.check("搜索投影 fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    index = json.loads((dest / "index.json").read_text(encoding="utf-8"))
    urls = {e["permalink"] for e in index}
    excluded = [u for u in ("fx-hidden", "fx-archives", "fx-search-page") if any(u in p for p in urls)]
    report.check("三类排除全生效（searchHidden / archives / search layout 不进索引）",
                 len(index) == 2 and not excluded, f"got {len(index)} 条, 漏排除: {excluded}")
    alpha = next((e for e in index if "fx-proj-alpha" in (e.get("permalink") or "")), None)
    report.check("alpha：summary == content == 正文（同源变换的直写字面量）",
                 alpha is not None and alpha.get("summary") == "Alpha 投影摘要正文，含要点一与要点二。"
                 and alpha.get("content") == alpha.get("summary"),
                 f"got {alpha}")
    beta = next((e for e in index if "fx-proj-beta" in (e.get("permalink") or "")), None)
    report.check("beta：plainify 剥离 markdown 后的摘要（独立字面量）",
                 beta is not None and beta.get("summary") == "Beta 粗体 与 链接 摘要，验证 plainify 剥离。",
                 f"got {beta}")
    report.check("fixture 文章的 tags/categories 原样投影",
                 alpha is not None and alpha.get("tags") == ["投影", "Alpha"]
                 and alpha.get("categories") == ["投影"]
                 and beta is not None and beta.get("tags") == ["投影", "Beta"],
                 f"got alpha={alpha and alpha.get('tags')}, beta={beta and beta.get('tags')}")


def assert_search_artifacts(report, dest):
    """搜索交付面（工单 0047 决议①：产物断言代替 jsdom 行为套件）。

    0043 docstring ④ 交付面条款的牙——「outputs JSON / search 页引用 search.js /
    fetch 同目录 index.json」三者任一坏掉，搜索静默失效（无报错、无结果）：
      · search.html 引用构建产物 search.*.js 且文件落盘（脚本接线，对位 B2）；
      · 构件里 XHR fetch 路径为同目录 "index.json"、无 "../index.json"
        （子路径部署 /mapleFlow/ 下 ../ 会逃逸到域名根 404；0046 施工期把
        项目级覆盖合并入主题层时同批修正，head.html preload 同步）。
    锚 fixture 构建（--quick 也跑）；构件经 head.html 的 resources.Minify，
    路径串用容忍引号的正则匹配。
    """
    search_html = (dest / "search.html").read_text(encoding="utf-8")
    m = re.search(r'<script[^>]+src=["\']?([^"\'\s>]*search[^"\'\s>]*\.js)', search_html)
    report.check("search 页引用 search.js 构件（脚本接线）", m is not None,
                 "no <script src=...search*.js> in search.html")
    if not m:
        return
    rel = re.sub(r'^/(mapleFlow/)?', '', m.group(1))
    js_path = dest / rel
    report.check(f"search.js 构件落盘（{rel}）", js_path.is_file(), "built file missing")
    if not js_path.is_file():
        return
    js = js_path.read_text(encoding="utf-8")
    report.check('构件 fetch 路径为同目录 "index.json"',
                 re.search(r"""open\(['"]GET['"]\s*,\s*['"]index\.json['"]""", js) is not None
                 and "../index.json" not in js,
                 "fetch path drifted (expected same-dir index.json, no ../)")
    # 0051 决议④：呈现层加深的弱产物断言——构件内含 item.summary 渲染引用，
    # 守「契约宣称的渲染确实在构件里」（契约-代码漂移牙口；变异检验：删渲染
    # 代码即红）。正则覆盖 item.summary 与 item["summary"] 两种属性访问写法
    # （堵「换括号写法绕逃」的边缘口子——弱断言的边界：仍不守渲染结果正确）。
    # 「渲染结果正确」在「不重写引擎」约束下无低成本自动牙（fixture 的 search
    # 页是静态空 ul，渲染只发生在浏览器运行时），记为已知限制入 fastsearch.js
    # docstring 与工单 0053 记录。
    report.check('构件含摘要渲染引用（item.summary；0051 呈现层加深）',
                 re.search(r'item\.summary|item\[[\'"]summary[\'"]\]', js) is not None,
                 "summary rendering reference missing in bundle")
    # 视觉层落地牙（2026-10-24 搜索视觉批 B1）：搜索结果摘要必须有样式规则。
    # 契约：.entry-summary 在结果 li 内是「次级信息」——必须带行数截断，
    # 否则 200 字摘要把每条结果拉成小卡片（0051 已渲染、视觉批补样式）。
    # 只守「规则存在且带截断」，不守字号/颜色具体值（视觉值非契约，
    # 与 .mf-featured 同款纪律）。
    css_text = "\n".join(p.read_text(encoding="utf-8") for p in dest.rglob("*.css"))
    report.check("产物 CSS 含 .entry-summary 摘要规则（含行数截断）",
                 re.search(r"\.entry-summary\{[^}]*line-clamp", css_text) is not None,
                 "missing .entry-summary rule with line-clamp in built CSS")


def assert_search_entry_artifacts(report, dest):
    """搜索入口构件交付面（工单 0050 决议⑧：产物四条之①②）。

    入口脚本经 extend_footer 的第二个 js.Build 全站恒加载（决议⑤：站点层
    assets/js/mf-search-entry.js，iife + minify + fingerprint + defer，
    与 mf-reveal 同款管线）：
      · 每个非跳转页都引用 mf-search-entry*.js 构件（全站面；页面集与 B7
        同款——排除 Hugo 别名/跳转页）；
      · 构件落盘且内含注入的 searchUrl——fixture（dev baseURL）形态为
        "/search.html"（决议⑥：URL 走 Hugo 构建期注入、不写死；生产子路径
        形态 "/mapleFlow/search.html" 由 assert_real 守，见 assert_real）。
    坏掉时的失效形态：入口全站静默缺失（无报错、无结果——静默失效类），
    或 URL 逃逸域名根 404（0046 的 ../index.json 同类事故）。
    """
    pages = [p for p in sorted(dest.rglob("*.html"))
             if 'http-equiv="refresh"' not in p.read_text(encoding="utf-8")]
    missing, refs = [], []
    for p in pages:
        html = p.read_text(encoding="utf-8")
        m = re.search(r'<script[^>]+src=["\']?([^"\'\s>]*mf-search-entry[^"\'\s>]*\.js)', html)
        if not m:
            missing.append(p.relative_to(dest).as_posix())
        else:
            refs.append((p, m.group(1)))
    report.check(f"全站 {len(pages)} 页均引用 mf-search-entry 构件（extend_footer 恒加载）",
                 bool(pages) and not missing, f"缺: {missing[:3]}")
    if not refs:
        return
    # 引用 URL 有两种形态：页面相对（./ 或 ../，dev/fixture 构建实测）与绝对
    # （/mapleFlow/...，生产构建）——按各自页面目录解析，两种都吃
    resolved = [dest / re.sub(r'^/(mapleFlow/)?', '', ref) if ref.startswith('/')
                else (p.parent / ref).resolve() for p, ref in refs]
    off_disk = [r for r in resolved if not r.is_file()]
    report.check("mf-search-entry 构件落盘（按页面目录解析引用）", not off_disk,
                 f"missing: {[str(r) for r in off_disk[:2]]}")
    if off_disk:
        return
    js = resolved[0].read_text(encoding="utf-8")
    report.check('构件内含注入的 searchUrl（fixture 形态 "/search.html"）',
                 '"/search.html"' in js, "injected URL missing in bundle")
    # 反向牙（决议⑧③的 fixture 侧）：fastsearch 构件不得出现在非 search 页——
    # ADR-0010「第二个消费方」触发条件的观测面；fixture 恒跑（--quick 也在），
    # 与 assert_real 的同名检查各守一层（CI 全量 + 本地快速迭代都不缺席）。
    leak = [p.relative_to(dest).as_posix() for p in pages
            if p.name != "search.html"
            and re.search(r'src=["\']?[^"\'\s>]*assets/js/search\.[^"\'\s>]*\.js',
                          p.read_text(encoding="utf-8"))]
    report.check("fastsearch 构件不泄漏到非 search 页（fixture；第二个消费方守门）",
                 not leak, f"泄漏: {leak[:3]}")


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
    assert_search_entry_real(report, dest)
    assert_theme_contract(report, dest)
    # 阅读辅助的真实面（2026-10-24 阅读体验批 A2）：SOP 派生文也必须显示
    # 阅读时长/字数——这是「site 级参数是派生文唯一可达路径」的直接证据
    # （派生文 front matter 只透传 categories/tags/featured）。
    sop_page = dest / "posts" / "sop-ansible-automation-guide.html"
    if not sop_page.is_file():
        report.check("阅读辅助：真实 SOP 派生页存在", False, f"missing {sop_page}")
    else:
        html = sop_page.read_text(encoding="utf-8")
        m = re.search(r'<div class="post-meta">(.*?)</div>', html, re.S)
        sop_meta = m.group(1) if m else ""
        report.check("SOP 派生页 meta 含阅读时长与字数（site 级参数可达派生文）",
                     re.search(r"\d+\s*分钟", sop_meta) is not None
                     and re.search(r"\d+\s*字", sop_meta) is not None,
                     f"meta={sop_meta[:160]!r}")


def assert_search_entry_real(report, dest):
    """搜索入口的真实数据面（工单 0050 决议⑧：产物②③；--quick 跳过）。

    ② 生产子路径 URL：入口构件（extend_footer 的 js.Build + params 注入）
    内 searchUrl 必须是 "/mapleFlow/search.html"——fixture 是 dev baseURL
    （"/search.html"），只有生产构建能验子路径；写死根路径会逃逸域名根 404
    （0046 的 ../index.json 同类事故）。
    ③ 加载面双向：入口构件全站每页在（全站恒加载）；fastsearch 构件仍仅
    search 页引用——后半条是 ADR-0010「第二个消费方」触发条件的观测牙
    （0049 缺口 7：此前无任何断言会提示重写条件已被触发）。
    """
    bundles = sorted((dest / "js").glob("mf-search-entry*.js"))
    report.check("入口构件落盘（真实构建 dest/js/）", bool(bundles),
                 "no mf-search-entry*.js under dest/js")
    if bundles:
        js = bundles[0].read_text(encoding="utf-8")
        report.check('入口构件内 searchUrl 为生产子路径形态 "/mapleFlow/search.html"',
                     '"/mapleFlow/search.html"' in js, "production subpath URL missing in bundle")
    pages = [p for p in sorted(dest.rglob("*.html"))
             if 'http-equiv="refresh"' not in p.read_text(encoding="utf-8")]
    no_entry = [p.relative_to(dest).as_posix() for p in pages
                if "mf-search-entry" not in p.read_text(encoding="utf-8")]
    report.check(f"真实构建全站 {len(pages)} 页均挂入口构件", bool(pages) and not no_entry,
                 f"缺: {no_entry[:3]}")
    leak = []
    for p in pages:
        if p.name == "search.html":
            continue
        if re.search(r'src=["\']?[^"\'\s>]*assets/js/search\.[^"\'\s>]*\.js',
                     p.read_text(encoding="utf-8")):
            leak.append(p.relative_to(dest).as_posix())
    report.check("fastsearch 构件仍仅 search 页引用（不引入第二个消费方）", not leak,
                 f"泄漏到非 search 页: {leak[:3]}")


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

    # B14: 搜索入口菜单文案（工单 0050 决议④）：accesskey=/ 退役（浏览器中介、
    # macOS 实为 Ctrl+Option+/，且零测试），title 后缀 "(Alt + /)" 改 "/"——
    # 菜单广告的快捷键必须与全站 `/` 入口一致，否则提示即误导。
    menu = re.search(r"<ul id=[\"']?menu[\"']?>(.*?)</ul>", post_html, re.S)
    search_anchor = None
    if menu:
        for a in re.findall(r"<a [^>]*>", menu.group(1)):
            if "search.html" in a:
                search_anchor = a
                break
    report.check("B14 搜索菜单项 accesskey 已退役",
                 search_anchor is not None and "accesskey" not in search_anchor,
                 f"anchor={search_anchor}")
    report.check('B14 搜索菜单项 title 提示为 "/"',
                 search_anchor is not None and 'title="搜索 /"' in search_anchor,
                 f"anchor={search_anchor}")

    # B10: 首页 RSS 只收 posts（内容策略，站点 rss.xml 的核心语义）。
    rss_path = dest / "index.xml"
    rss = rss_path.read_text(encoding="utf-8") if rss_path.exists() else ""
    items = re.findall(r"<item>.*?<link>(.*?)</link>", rss, re.S)
    report.check(f"首页 RSS {len(items)} 条 item 全部为 posts", bool(items) and all("/posts/" in link for link in items),
                 f"非 posts 条目: {[l for l in items if '/posts/' not in l][:3]}")

    # B11: search 页 DOM 三挂点（挂点契约的定义处：fastsearch.js 文件头
    # docstring「搜索协议」——0046 决议②；坏了搜索静默失效）。
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

    preflight_hugo_version()

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
    assert_featured_badge(report)
    assert_post_reading_meta(report)
    # 目录空态只依赖 fixture 构建，--quick 也跑（空态是 A1 的明确要求）
    assert_post_toc_empty(report)
    assert_search_fixture(report)
    assert_empty_state(report)
    assert_bad_cases(report)
    assert_bad_caller_limit(report)
    assert_bad_caller_missing_items(report)
    assert_bad_caller_missing_uid(report)
    if not args.quick:
        assert_real(report)
        # 目录正面锚真实构建产物（--quick 不建 real，故跟随 assert_real 一起跳过）
        assert_post_toc(report)

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
