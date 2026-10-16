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
  · 契约 seam —— tests/fixtures/bad/sop-*/ 每个用例的构建必须失败，
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

tests/tmp 为本脚本独占（启动即清空）；与 assert_product_states.py 共享
该目录，两脚本须顺序运行（CI 即顺序），勿并发。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sop_golden as sg  # golden 抽取与捕获脚本共用，防规则漂移

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp"
REGISTRY = REPO / "data" / "sop.yaml"
BAD_ROOT = REPO / "tests" / "fixtures" / "bad"
DRAFT_ROOT = REPO / "tests" / "fixtures" / "draft"
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

    只用 stdlib——CI 的 python3 不保证有 PyYAML，与 assert_product_states.py
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


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def build(config, dest, drafts=False):
    # 与 CI 的生产命令逐字一致（--gc --minify --cleanDestinationDir）：
    # golden 按 minify 后的线上产物捕获，构建条件不一致则逐字节比对无意义。
    cmd = ["hugo", "--gc", "--minify", "--cleanDestinationDir"]
    if drafts:
        cmd.append("-D")
    cmd += ["--config", config, "-d", str(dest)]
    return run(cmd)


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


class Report:
    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self):
        return [i for i in self.items if not i[0]]


def fixture_config(name, root):
    """坏用例 / 行为 fixture 的构建配置：dataDir 与 sopNotesDir 双覆盖。

    dataDir 只含数据文件（sop.yaml），notes/ 平级隔离——Hugo 数据加载器
    会递归解析 dataDir 下所有文件，.md 混入即「unmarshal of format」崩溃。
    路径用 as_posix：Windows 上 relative_to 产反斜杠，嵌进 TOML 会被当
    转义序列解析，坏用例将因路径失败而非契约失败（假红）。

    refLinksErrorLevel = WARNING：fixture 注册表不含 6 个真实 slug，
    sop-ops-tools-index 的 ref 会落空——那是预期内的环境差异，
    不应掩蔽本模块的契约错误（真实构建保持默认 ERROR 级）。
    """
    cfg = TMP / f"{name}.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        'dataDir = "%s/data"\nrefLinksErrorLevel = "WARNING"\n[params]\nsopNotesDir = "%s/notes"\n'
        % (root.relative_to(REPO).as_posix(), root.relative_to(REPO).as_posix()),
        encoding="utf-8")
    return "hugo.toml,%s" % cfg.relative_to(REPO).as_posix()


def assert_derived(report):
    """真实数据：派生 + 迁移保真 + 残留 + 孤儿容忍，一网打尽。"""
    if not REGISTRY.is_file():
        report.check("注册表 data/sop.yaml 存在", False, str(REGISTRY))
        return
    entries = parse_registry(REGISTRY)
    report.check("注册表非空", len(entries) > 0, f"got {len(entries)}")
    dest = TMP / "real"
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
            report.check(f"[{slug}] <article> 全文 == golden（迁移保真）",
                         inner == golden["article_html"], "渲染正文与迁移前线上页面不一致")
            report.check(f"[{slug}] <title> == golden", got_title == golden["title"],
                         f"got={got_title!r} want={golden['title']!r}")
            report.check(f"[{slug}] golden meta description == golden",
                         bool(got_desc) and got_desc == golden["meta_description"],
                         f"got={got_desc!r} want={golden['meta_description']!r}")


def assert_bad_cases(report):
    """契约坏用例：构建必须失败，错误含管线标记 + 该用例的契约子串。"""
    cases = sorted(p.name for p in BAD_ROOT.iterdir()
                   if p.is_dir() and (p / "data" / "sop.yaml").is_file()) if BAD_ROOT.is_dir() else []
    if not cases:
        report.check("存在契约坏用例", False, "tests/fixtures/bad/sop-*/data 下没有用例")
        return
    for case in cases:
        expect = BAD_CASE_EXPECT.get(case)
        if expect is None:
            report.check(f"契约[{case}] 有期望错误子串登记", False, "BAD_CASE_EXPECT 缺该用例")
            continue
        config = fixture_config(f"bad-{case}", BAD_ROOT / case)
        proc = build(config, TMP / f"bad-{case}")
        out = proc.stderr + proc.stdout
        ok = proc.returncode != 0 and PIPELINE_MARKER in out and expect in out
        report.check(f"契约[{case}] → 构建失败且错误指向该契约", ok,
                     "" if ok else "exit=%d expect=%r %s" % (proc.returncode, expect, out[-300:]))


def assert_draft(report):
    """draft: true = 已注册的草稿（0009 目录契约）：不进生产构建，-D 出现。"""
    config = fixture_config("draft", DRAFT_ROOT)
    prod = build(config, TMP / "draft-prod")
    report.check("draft fixture 生产构建成功", prod.returncode == 0,
                 prod.stderr[-300:] if prod.returncode else "")
    if prod.returncode == 0:
        live = (TMP / "draft-prod" / "posts" / "draft-live-entry.html").is_file()
        hidden = (TMP / "draft-prod" / "posts" / "draft-hidden-entry.html").exists()
        report.check("draft: true 条目不进生产构建（对照组进）", live and not hidden,
                     f"live={live} hidden={hidden}")
    withd = build(config, TMP / "draft-d", drafts=True)
    report.check("draft fixture -D 构建成功", withd.returncode == 0,
                 withd.stderr[-300:] if withd.returncode else "")
    if withd.returncode == 0:
        report.check("draft: true 条目在 -D 构建出现",
                     (TMP / "draft-d" / "posts" / "draft-hidden-entry.html").is_file())


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


def assert_ref_links(report):
    """索引文章的 ref 解析到冻结 URL，且目标页面真实构建（0009 连带裁定）。"""
    page = TMP / "real" / "posts" / "sop-ops-tools-index.html"
    if not page.is_file():
        report.check("索引文章产物存在", False, str(page))
        return
    html = page.read_text(encoding="utf-8")
    for e in parse_registry(REGISTRY):
        target = "/mapleFlow/posts/%s.html" % e["slug"]
        report.check(f"索引文章 ref → {target}", target in html)
        report.check(f"ref 目标已构建 {e['slug']}.html",
                     (TMP / "real" / "posts" / f"{e['slug']}.html").is_file())


def assert_search_index(report):
    """搜索索引含全部派生条目（雾区结论的实施期验证：生成页是真页面）。"""
    index_path = TMP / "real" / "index.json"
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
    必须跑本脚本，否则断言的「失败阻断部署」不存在。"""
    workflow = REPO / ".github" / "workflows" / "deploy.yml"
    if not workflow.is_file():
        report.check("deploy.yml 存在", False, str(workflow))
        return
    text = workflow.read_text(encoding="utf-8")
    report.check("deploy.yml 含 SOP 管线断言步", "tests/assert_sop_pipeline.py" in text)


def main():
    parser = argparse.ArgumentParser(description="SOP 发布管线产物断言")
    parser.add_argument("--quick", action="store_true", help="跳过真实数据构建")
    args = parser.parse_args()

    if shutil.which("hugo") is None:
        print("ERROR: hugo 不在 PATH（CI 由 peaceiris/actions-hugo 提供）")
        return 2

    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)

    report = Report()
    if not args.quick:
        assert_derived(report)
        assert_readme(report)
        assert_ref_links(report)
        assert_search_index(report)
    assert_bad_cases(report)
    assert_draft(report)
    assert_ci_wiring(report)

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
