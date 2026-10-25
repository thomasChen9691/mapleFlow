#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOP 发布管线的产物断言（wayfinder 工单 0008/0009 决议；ADR-0004 测试哲学）。

测试缝（预先商定，勿在未确认的缝上写测试）：
  · 派生 seam —— 生产配置构建的 /posts/sop-*.html：URL 冻结（6 个线上 slug
    必须在役）、标题 == 源笔记 H1（独立交叉核对）、日期非零且 == 注册表 date、
    meta description == 注册表（description 透传 Plumbing 回归）、
    结构断言（导语在场 / 章节标题序列 == 笔记 / 笔记末行在场——派生关系
    不依赖 golden，新条目同样受守）
  · 迁移保真 seam —— 有 golden 的条目（6 个迁移条目）：<article> 全文与
    meta/title 与迁移前线上页面逐字节一致。golden 缺失 = 新条目，走结构
    断言，不红（新增流程：写笔记 + 加注册条目）。
  · 残留 seam —— content/posts/ 下 6 个派生 slug 不得有手写 .md；
    posts/ 页面集合 == 派生 slug + 手写非草稿文章（孤儿笔记零页面）
  · 契约 seam —— tests/fixtures/bad/sop/ 下每个用例的构建必须失败，
    且错误信息含本管线标记与各用例的契约子串
  · draft seam —— tests/fixtures/draft/：draft: true = 已注册的草稿，
    不进生产构建，-D 构建出现（0009 目录契约）
  · 漂移 seam —— docs/sop/README 表格 ↔ 注册表双向一致；
    索引文章 6 个 ref 解析且目标已构建；搜索索引含全部派生条目
  · CI seam —— deploy.yml 必须跑本脚本（守门自身在位）

用法：
  python3 tests/assert_sop_pipeline.py          # 全套
  python3 tests/assert_sop_pipeline.py --quick  # 只跑契约/draft/CI（本地快速迭代）

Hugo 版本纪律：适配器按 0.164 语义编写（dates 嵌套 dict、params 承载
categories/tags、description 顶层）。本机 hugo 可能为 0.167 而 CI 钉
0.164——本脚本只消费构建产物，与 Hugo 版本无关。

期望值独立于实现：标题直读源笔记；日期由注册表 date 独立格式化；golden
为迁移前线上页面的直捕（出处见 tests/fixtures/sop-golden/README.md）。
均非对适配器逻辑的重算，防同义反复测试。
"""

import json
import re
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sop_golden as sg  # golden 抽取与捕获脚本共用，防规则漂移
import harness  # 测试 harness 的 Python 侧（工单 0062）：入口仪式 / Report / tmp 分根

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "data" / "sop.yaml"
BAD_ROOT = REPO / "tests" / "fixtures" / "bad" / "sop"
DRAFT_ROOT = REPO / "tests" / "fixtures" / "draft"
FEATURED_ROOT = REPO / "tests" / "fixtures" / "featured"
NOTES_DIR = REPO / "docs" / "sop"  # 镜像 hugo.toml 的 params.sopNotesDir 缺省值
REAL_CONFIG = "hugo.toml,config.production.toml"
PIPELINE_MARKER = "SOP 发布管线"
ZERO_DATE_TEXT = "January 1, 0001"  # Hugo 对零值日期的渲染形态（独立字面量）

# 6 个迁移条目的线上 URL（工单 0008 硬约束：冻结）——失任一即线上 404。
FROZEN_SLUGS = [
    "sop-ansible-automation-guide",
    "sop-gitlab-cicd-guide",
    "sop-jenkins-cicd-guide",
    "sop-prometheus-metrics-alerting-guide",
    "sop-sonarqube-code-quality-guide",
    "sop-grafana-dashboard-alerting-guide",
]

# 契约坏用例 → 期望错误子串：把每个 fixture 钉到它的契约，防止「因别的原因
# 失败也绿灯」（如 missing-slug 其实死于缺 note）。
BAD_CASE_EXPECT = {
    "sop-dead-entry": "死条目",
    "sop-missing-date": "缺必填字段",
    "sop-missing-slug": "缺必填字段",
    "sop-missing-categories": "缺必填字段",
    "sop-no-h1": "首行无 H1",
    "sop-h1-only": "无章节标题行",
}


def parse_registry(path):
    """解析 data/sop.yaml 的扁平 schema：list of {key: scalar | [inline list]}。

    只用 stdlib——CI 的 python3 不保证有 PyYAML，与 assert_site_contracts.py
    的零依赖纪律一致。schema 由本项目控制：值为标量或行内列表，不含 '#'、
    无多行块值；含冒号的值仅限时间串（partition 取首个冒号）。
    """
    entries, cur = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if cur is not None:
                entries.append(cur)
            cur = {}
            stripped = stripped[2:].strip()
        if cur is None or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            cur[key] = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            cur[key] = value.strip("'\"")
    if cur is not None:
        entries.append(cur)
    return entries


def build(config, dest, flags=None):
    """SOP 套件的构建适配器：绑定 sop-pipeline 档（0063——档位是套件的属性；
    drafts 语义糖已拆，-D 走 flags）。"""
    return harness.build(config, dest, "sop-pipeline", flags)


def note_text(note_file):
    return (NOTES_DIR / note_file).read_text(encoding="utf-8")


def note_h1(note_file):
    """源笔记首行 H1 的标题文本（去 '# ' 前缀）——标题的独立期望值来源。"""
    for line in note_text(note_file).splitlines():
        if line.strip():
            return line[2:].strip() if line.startswith("# ") else None
    return None


def html_to_text(html):
    """渲染产物 → 归一化文本（去标签 / 实体解码 / 空白折叠）。"""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def squash(text):
    """去全部空白——包含性断言专用：行内标签边界会插入源文本没有的空格
    （如 <code> 边界），空白无关比较才稳。"""
    return re.sub(r"\s+", "", text)


def strip_code_blocks(md):
    return re.sub(r"```.*?```", "", md, flags=re.S)


def md_inline(md):
    """剥行内标记（反引号 / 粗体 / 链接），保留全部字符——标题文本用。"""
    text = re.sub(r"`([^`]*)`", r"\1", md)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def md_to_text(md):
    """笔记 markdown → 归一化文本（行内 + 块级标记；包含性断言用）。"""
    text = re.sub(r"^#{1,6}\s*", "", md_inline(md), flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = text.replace("|", " ")
    return re.sub(r"\s+", " ", text).strip()


def note_headings(md):
    """源笔记的章节标题序列（## 起；代码块内的 # 注释不算——先剥代码块）。

    标题文本只剥行内标记：块级剥离会吃掉编号（「## 1. 简介」→「简介」），
    与页面渲染出的「1. 简介」对不上。
    """
    return [md_inline(m.group(1))
            for m in re.finditer(r"^#{2,6}\s+(.+)$", strip_code_blocks(md), re.M)]


def page_headings(inner):
    """渲染页面的章节标题序列（h2-h6；剥标题内 anchor 链接的 # 后缀）。"""
    out = []
    for m in re.finditer(r"<h[2-6][^>]*>(.*?)</h[2-6]>", inner, re.S):
        text = re.sub(r"<a\b[^>]*>.*?</a>", "", m.group(1), flags=re.S)
        out.append(html_to_text(text))
    return out


def hugo_date_text(iso):
    """注册表 date → Hugo 的渲染形态（如 'January 28, 2026'）。

    独立格式化：注册表时间串自带偏移，页面 title 属性显示 Hugo 按该偏移
    渲染（实测 +0800 CST）。日无前导零（Go :date_long 语义），故手拼。
    """
    dt = datetime.fromisoformat(iso)
    return "%s %d, %d" % (dt.strftime("%B"), dt.day, dt.year)


def fixture_config(name, root):
    """SOP fixture 布局约定的 root→轴适配器（0064 裁定：映射留套件——harness
    不懂内容布局，seam 之后只有机制）。

    root 下 data/（纯数据文件）与 notes/（源笔记）平级隔离——.md 混入
    dataDir 即 Hugo unmarshal 崩溃（0064 坑二，完整文档在 harness.write_config）。
    refLinksErrorLevel = WARNING：fixture 注册表不含 6 个真实 slug，
    sop-ops-tools-index 的 ref 会落空——预期内的环境差异，不应掩蔽本模块的
    契约错误（真实构建保持默认 ERROR 级）。
    """
    return harness.write_config(name,
                                dataDir=root / "data",
                                sopNotesDir=root / "notes",
                                refLinksErrorLevel="WARNING")


def assert_derived(report):
    """真实数据：派生 + 迁移保真 + 残留 + 孤儿容忍，一网打尽。"""
    if not REGISTRY.is_file():
        report.check("注册表 data/sop.yaml 存在", False, str(REGISTRY))
        return
    entries = parse_registry(REGISTRY)
    report.check("注册表非空", len(entries) > 0, f"got {len(entries)}")
    dest = harness.dest("real")
    proc = build(REAL_CONFIG, dest)
    report.check("真实数据构建成功（生产配置）", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return

    # URL 冻结：6 个线上 slug 必须在役（失任一即线上 404）
    actual_pages = {p.stem for p in (dest / "posts").glob("*.html") if p.stem != "index"}
    for slug in FROZEN_SLUGS:
        report.check(f"线上 URL 冻结：{slug}.html 在役", slug in actual_pages)

    # 孤儿笔记零页面：posts/ 集合 == 派生 slug + 手写非草稿文章
    handwritten = set()
    for md in (REPO / "content" / "posts").glob("*.md"):
        if re.search(r"^draft\s*=\s*true", md.read_text(encoding="utf-8"), re.M):
            continue
        handwritten.add(md.stem)
    expected_pages = {e.get("slug") for e in entries} | handwritten
    report.check("posts/ 页面集合 == 派生 slug + 手写非草稿文章（孤儿笔记零页面）",
                 actual_pages == expected_pages,
                 f"stray={sorted(actual_pages - expected_pages)} missing={sorted(expected_pages - actual_pages)}")

    for e in entries:
        slug, note = e.get("slug"), e.get("note")
        page = dest / "posts" / f"{slug}.html"
        if not page.is_file():
            report.check(f"[{slug}] 派生页面存在于冻结 URL", False, f"{page} 不存在")
            continue
        html = page.read_text(encoding="utf-8")
        fields = sg.extract(html)
        got_title, got_desc = fields["title"], fields["meta_description"]
        inner = fields["article_html"] or ""
        # 残留：派生 slug 不得有手写 .md（否则与 adapter 页同路径共存）
        residue = REPO / "content" / "posts" / f"{slug}.md"
        report.check(f"[{slug}] 无手写 .md 残留", not residue.exists(), str(residue))
        # 标题：源笔记 H1 是独立期望值（适配器不得自说自话）
        h1 = note_h1(note)
        report.check(f"[{slug}] 标题 == 源笔记 H1", h1 is not None and got_title == f"{h1} | MapleFlow",
                     f"h1={h1!r} got={got_title!r}")
        # 日期：零值陷阱回归 + 与注册表 date 独立核对
        rendered_date = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", inner)
        got_date = rendered_date.group(1) if rendered_date else ""
        want_date = hugo_date_text(e["date"]) if e.get("date") else ""
        report.check(f"[{slug}] 日期非零且 == 注册表 date（dates 嵌套回归）",
                     got_date == want_date and ZERO_DATE_TEXT not in inner,
                     f"got={got_date!r} want={want_date!r}")
        # description 透传：Plumbing 回归（曾因放 params 而 meta 全空）
        report.check(f"[{slug}] meta description == 注册表",
                     bool(got_desc) and got_desc == (e.get("description") or ""),
                     f"got={got_desc!r}")
        # 结构断言：派生关系不依赖 golden（新条目同样受守）
        page_text = html_to_text(inner)
        intro_text = md_to_text(e.get("intro") or "")
        report.check(f"[{slug}] 导语出现在页面",
                     bool(intro_text) and squash(intro_text) in squash(page_text))
        md = strip_code_blocks(note_text(note))
        heads_exp, heads_got = note_headings(md), page_headings(inner)
        report.check(f"[{slug}] 章节标题序列 == 源笔记", heads_exp == heads_got,
                     f"note={heads_exp} page={heads_got}")
        tail_lines = [l for l in md.splitlines() if l.strip()]
        tail = md_to_text(tail_lines[-1]) if tail_lines else ""
        report.check(f"[{slug}] 笔记末行内容出现在页面",
                     bool(tail) and squash(tail) in squash(page_text),
                     f"tail={tail[:60]!r}")
        # 迁移保真：仅迁移条目有 golden；新条目无 golden 是预期（新增流程）
        golden_path = sg.golden_path(slug)
        if golden_path.is_file():
            golden = json.loads(golden_path.read_text(encoding="utf-8"))
            want_tokens = sg.canonical(golden["article_html"])
            got_tokens = sg.canonical(inner)
            report.check(f"[{slug}] <article> == golden（迁移保真·规范化比对）",
                         want_tokens == got_tokens,
                         sg.first_divergence(want_tokens, got_tokens))
            report.check(f"[{slug}] <title> == golden", got_title == golden["title"],
                         f"got={got_title!r} want={golden['title']!r}")
            report.check(f"[{slug}] golden meta description == golden",
                         bool(got_desc) and got_desc == golden["meta_description"],
                         f"got={got_desc!r} want={golden['meta_description']!r}")


def assert_bad_cases(report):
    """契约坏用例：构建必须失败，错误含管线标记 + 该用例的契约子串。

    根卫生（0061 决议）：bad/sop/ 下每个目录必须含 data/sop.yaml——本根只住
    本模块用例，错放别模块用例大声失败，取代旧的「平铺共享 + 按内容标记过滤」。
    """
    if not BAD_ROOT.is_dir():
        report.check("存在契约坏用例", False, "tests/fixtures/bad/sop/ 下没有用例")
        return
    strays = sorted(p.name for p in BAD_ROOT.iterdir()
                    if p.is_dir() and not (p / "data" / "sop.yaml").is_file())
    if strays:
        report.check("坏用例根卫生：bad/sop/ 下每个用例含 data/sop.yaml", False,
                     "错放用例（无 data/sop.yaml）：%s" % strays)
        return
    cases = sorted(p.name for p in BAD_ROOT.iterdir() if p.is_dir())
    if not cases:
        report.check("存在契约坏用例", False, "tests/fixtures/bad/sop/ 下没有用例")
        return
    for case in cases:
        expect = BAD_CASE_EXPECT.get(case)
        if expect is None:
            report.check(f"契约[{case}] 有期望错误子串登记", False, "BAD_CASE_EXPECT 缺该用例")
            continue
        config = fixture_config(f"bad-{case}", BAD_ROOT / case)
        proc = build(config, harness.dest(f"bad-{case}"))
        out = proc.stderr + proc.stdout
        ok = proc.returncode != 0 and PIPELINE_MARKER in out and expect in out
        report.check(f"契约[{case}] → 构建失败且错误指向该契约", ok,
                     "" if ok else "exit=%d expect=%r %s" % (proc.returncode, expect, out[-300:]))


def assert_draft(report):
    """draft: true = 已注册的草稿（0009 目录契约）：不进生产构建，-D 出现。"""
    config = fixture_config("draft", DRAFT_ROOT)
    prod = build(config, harness.dest("draft-prod"))
    report.check("draft fixture 生产构建成功", prod.returncode == 0,
                 prod.stderr[-300:] if prod.returncode else "")
    if prod.returncode == 0:
        live = (harness.dest("draft-prod") / "posts" / "draft-live-entry.html").is_file()
        hidden = (harness.dest("draft-prod") / "posts" / "draft-hidden-entry.html").exists()
        report.check("draft: true 条目不进生产构建（对照组进）", live and not hidden,
                     f"live={live} hidden={hidden}")
    withd = build(config, harness.dest("draft-d"), ["-D"])
    report.check("draft fixture -D 构建成功", withd.returncode == 0,
                 withd.stderr[-300:] if withd.returncode else "")
    if withd.returncode == 0:
        report.check("draft: true 条目在 -D 构建出现",
                     (harness.dest("draft-d") / "posts" / "draft-hidden-entry.html").is_file())


def assert_readme(report):
    """README ↔ 注册表双向一致 + MAPLEFLOW_BLOG_SOP 的不发布标注（0009 决议）。"""
    readme_path = REPO / "docs" / "sop" / "README.md"
    if not readme_path.is_file():
        report.check("docs/sop/README.md 存在", False, str(readme_path))
        return
    readme = readme_path.read_text(encoding="utf-8")
    listed = set(re.findall(r"\]\(([A-Za-z0-9_]+\.md)\)", readme))
    registered = {e.get("note") for e in parse_registry(REGISTRY)}
    report.check("README 表格列出的笔记 == 注册表 note 集合（双向）", listed == registered,
                 f"README-only={sorted(listed - registered)} registry-only={sorted(registered - listed)}")
    report.check("README 标注 MAPLEFLOW_BLOG_SOP 为不发布",
                 any("MAPLEFLOW_BLOG_SOP" in line and "不发布" in line for line in readme.splitlines()))


def assert_featured_passthrough(report):
    """注册表 featured 透传（工单 0040 决议）：featured: true 的派生文进首页精选区。

    观察点是**消费方**（首页精选区），不是内部 params——契约的价值在行为。
    未标 featured 的派生文不得进精选区（缺省即非精选）。

    fixture 同时覆盖 contentDir（tests/fixtures/featured/content，内含适配器
    副本）——否则首页精选区混入真实文章的 featured，本用例能否通过取决于
    真实内容的日期排序（0039-4「真实清单不锚」的翻版）。
    适配器副本与真实 seam 的漂移由下方「副本一致」断言守门。
    """
    seam = REPO / "content" / "posts" / "_content.gotmpl"
    copy = FEATURED_ROOT / "content" / "posts" / "_content.gotmpl"
    report.check("fixture 适配器副本与真实 seam 逐字节一致（防漂移）",
                 copy.is_file() and copy.read_bytes() == seam.read_bytes(),
                 "副本漂移：请重新 cp content/posts/_content.gotmpl 到 fixture")
    config = harness.write_config("featured",
                                  dataDir=FEATURED_ROOT / "data",
                                  contentDir=FEATURED_ROOT / "content",
                                  sopNotesDir=FEATURED_ROOT / "notes",
                                  refLinksErrorLevel="WARNING")
    dest = harness.dest("featured")
    proc = build(config, dest)
    report.check("featured 透传 fixture 构建成功", proc.returncode == 0,
                 proc.stderr[-300:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    html = (dest / "index.html").read_text(encoding="utf-8")
    # 本套件按 CI 生产命令构建（--minify），属性无引号：class=mf-rows 形态。
    block = re.search(r'<ol class=["\']?mf-rows["\']?>(.*?)</ol>', html, re.S)
    slugs = re.findall(r'href=["\']?[^"\' >]*posts/([^"\' >]+)\.html', block.group(1)) if block else []
    report.check("注册表 featured: true → 派生文进首页精选区",
                 "sop-featured-entry" in slugs, f"got {slugs}")
    report.check("未标 featured 的派生文不进精选区（缺省即非精选）",
                 "sop-plain-entry" not in slugs, f"got {slugs}")


def assert_ref_links(report):
    """索引文章的 ref 解析到冻结 URL，且目标页面真实构建（0009 连带裁定）。"""
    page = harness.dest("real") / "posts" / "sop-ops-tools-index.html"
    if not page.is_file():
        report.check("索引文章产物存在", False, str(page))
        return
    html = page.read_text(encoding="utf-8")
    for e in parse_registry(REGISTRY):
        target = "/mapleFlow/posts/%s.html" % e["slug"]
        report.check(f"索引文章 ref → {target}", target in html)
        report.check(f"ref 目标已构建 {e['slug']}.html",
                     (harness.dest("real") / "posts" / f"{e['slug']}.html").is_file())


def assert_search_index(report):
    """搜索索引含全部派生条目（雾区结论的实施期验证：生成页是真页面）。"""
    index_path = harness.dest("real") / "index.json"
    if not index_path.is_file():
        report.check("index.json 产物存在", False, str(index_path))
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for e in parse_registry(REGISTRY):
        needle = "posts/%s.html" % e["slug"]
        report.check(f"搜索索引含 {e['slug']}",
                     any(needle in (x.get("permalink") or "") for x in index))


def assert_ci_wiring(report):
    """CI 守门在位（0013 预裁：CI 权威 + 本地 advisory）——部署流水线里
    必须跑本脚本，否则断言的「失败阻断部署」不存在。

    2026-10-24（DevOps 批）：工作流由 deploy.yml 重建为 ci-cd.yml（verify +
    deploy 双 job、PR 门禁）。自守门改为 **glob 全部工作流**——不再钉文件名，
    流水线再改名/拆分时这条守门照样生效（钉文件名曾是隐性耦合：改名即红，
    而红的原因与 SOP 管线无关）。"""
    workflows = sorted((REPO / ".github" / "workflows").glob("*.yml"))
    if not workflows:
        report.check("CI 工作流文件存在", False, "no *.yml under .github/workflows")
        return
    text = "\n".join(w.read_text(encoding="utf-8") for w in workflows)
    report.check("CI 工作流含 SOP 管线断言步",
                 "tests/assert_sop_pipeline.py" in text,
                 f"checked: {[w.name for w in workflows]}")


def checks(report, quick):
    if not quick:
        assert_derived(report)
        assert_readme(report)
        assert_ref_links(report)
        assert_search_index(report)
    assert_bad_cases(report)
    assert_draft(report)
    assert_featured_passthrough(report)
    assert_ci_wiring(report)


def main():
    return harness.run("sop", checks)


if __name__ == "__main__":
    sys.exit(main())
