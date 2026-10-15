#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOP 发布管线的产物断言（wayfinder 工单 0008/0009 决议；ADR-0004 测试哲学）。

测试缝（预先商定，勿在未确认的缝上写测试）：
  · 派生 seam —— 生产配置构建的 6 个 /posts/sop-*.html：URL 冻结（存在性）、
    标题 == 源笔记 H1（独立交叉核对）、日期非零值、<article> 全文与 meta
    description == golden（迁移保真：线上页面零变化）
  · 残留 seam —— content/posts/ 下 6 个派生 slug 不得有手写 .md
  （契约 seam 与漂移 seam 由后续红绿循环追加）

用法：
  python3 tests/assert_sop_pipeline.py          # 全套
  python3 tests/assert_sop_pipeline.py --quick  # 跳过真实数据构建

Hugo 版本纪律：适配器按 0.164 语义编写（dates 嵌套 dict、params 承载
categories/tags）。本机 hugo 可能为 0.167 而 CI 钉 0.164——本脚本只消费
构建产物，与 Hugo 版本无关。

期望值独立于实现：golden 为迁移前线上页面的直捕（tests/fixtures/sop-golden/），
标题期望值直读源笔记——都不是对适配器逻辑的重算，防同义反复测试。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp"
REGISTRY = REPO / "data" / "sop.yaml"
GOLDEN = REPO / "tests" / "fixtures" / "sop-golden"
REAL_CONFIG = "hugo.toml,config.production.toml"
BAD_ROOT = REPO / "tests" / "fixtures" / "bad"
DRAFT_ROOT = REPO / "tests" / "fixtures" / "draft"
PIPELINE_MARKER = "SOP 发布管线"

ZERO_DATE_TEXT = "January 1, 0001"  # Hugo 对零值日期的渲染形态（独立字面量）


def parse_registry(path):
    """解析 data/sop.yaml 的扁平 schema：list of {key: scalar | [inline list]}。

    只用 stdlib——CI 的 python3 不保证有 PyYAML，与 assert_product_states.py
    的零依赖纪律一致。schema 由本项目控制：值不含 '#' 与 ': ' 外的冒号结构。
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


def build(config, dest):
    # 与 CI 的生产命令逐字一致（--gc --minify --cleanDestinationDir）：
    # golden 按 minify 后的线上产物捕获，构建条件不一致则逐字节比对无意义。
    return run(["hugo", "--gc", "--minify", "--cleanDestinationDir", "--config", config, "-d", str(dest)])


def note_h1(note_file):
    """源笔记首行 H1 的标题文本（去 '# ' 前缀）——标题的独立期望值来源。"""
    for line in (REPO / "docs" / "sop" / note_file).read_text(encoding="utf-8").splitlines():
        if line.strip():
            if not line.startswith("# "):
                return None
            return line[2:].strip()
    return None


def article_inner(html):
    m = re.search(r"<article[^>]*>", html)
    if not m:
        return None
    end = html.find("</article>", m.end())
    return html[m.end():end] if end >= 0 else None


class Report:
    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self):
        return [i for i in self.items if not i[0]]


def assert_derived(report):
    """真实数据：6 篇 SOP 文全部由管线派生，且与迁移前线上页面逐字节一致。"""
    if not REGISTRY.is_file():
        report.check("注册表 data/sop.yaml 存在", False, str(REGISTRY))
        return
    entries = parse_registry(REGISTRY)
    report.check("注册表含 6 条", len(entries) == 6, f"got {len(entries)}")
    dest = TMP / "real"
    proc = build(REAL_CONFIG, dest)
    report.check("真实数据构建成功（生产配置）", proc.returncode == 0,
                 proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    for e in entries:
        slug, note = e.get("slug"), e.get("note")
        page = dest / "posts" / f"{slug}.html"
        if not page.is_file():
            report.check(f"[{slug}] 派生页面存在于冻结 URL", False, f"{page} 不存在")
            continue
        html = page.read_text(encoding="utf-8")
        # 残留：派生 slug 不得有手写 .md（否则与 adapter 页同路径共存）
        residue = REPO / "content" / "posts" / f"{slug}.md"
        report.check(f"[{slug}] 无手写 .md 残留", not residue.exists(), str(residue))
        # 标题：源笔记 H1 是独立期望值（适配器不得自说自话）
        h1 = note_h1(note)
        title = re.search(r"<title>(.*?)</title>", html)
        got_title = title.group(1) if title else ""
        report.check(f"[{slug}] 标题 == 源笔记 H1", h1 is not None and got_title == f"{h1} | MapleFlow",
                     f"h1={h1!r} got={got_title!r}")
        # 日期：零值陷阱回归（adapter page map 顶层 date 静默失效，0007 事实）
        inner = article_inner(html) or ""
        report.check(f"[{slug}] 日期非零值", ZERO_DATE_TEXT not in inner,
                     "渲染出零值日期——检查 dates 嵌套写法")
        # golden：迁移保真（线上页面零变化）
        golden_path = GOLDEN / f"{slug}.json"
        if not golden_path.is_file():
            report.check(f"[{slug}] golden 存在", False, str(golden_path))
            continue
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        report.check(f"[{slug}] <article> 全文 == golden（迁移保真）", inner == golden["article_html"],
                     "渲染正文与迁移前线上页面不一致")
        desc = re.search(r'<meta name=description content="([^"]*)"', html)
        got_desc = desc.group(1) if desc else ""
        report.check(f"[{slug}] meta description == golden", got_desc == golden["meta_description"],
                     f"got={got_desc!r} want={golden['meta_description']!r}")
        report.check(f"[{slug}] <title> == golden", got_title == golden["title"],
                     f"got={got_title!r} want={golden['title']!r}")


def fixture_config(name, root):
    """坏用例 / 行为 fixture 的构建配置：dataDir 与 sopNotesDir 双覆盖。

    dataDir 只含数据文件（sop.yaml），notes/ 平级隔离——Hugo 数据加载器
    会递归解析 dataDir 下所有文件，.md 混入即「unmarshal of format」崩溃。

    refLinksErrorLevel = WARNING：fixture 注册表不含 6 个真实 slug，
    sop-ops-tools-index 的 ref 会落空——那是预期内的环境差异，
    不应掩蔽本模块的契约错误（真实构建保持默认 ERROR 级）。
    """
    cfg = TMP / f"{name}.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        'dataDir = "%s/data"\nrefLinksErrorLevel = "WARNING"\n[params]\nsopNotesDir = "%s/notes"\n'
        % (root.relative_to(REPO), root.relative_to(REPO)),
        encoding="utf-8")
    return "hugo.toml,%s" % cfg.relative_to(REPO)


def assert_bad_cases(report):
    """契约坏用例：构建必须失败，且错误信息来自 SOP 发布管线（0008 决议第 4 条）。"""
    cases = sorted(p.name for p in BAD_ROOT.iterdir()
                   if p.is_dir() and p.name.startswith("sop-")) if BAD_ROOT.is_dir() else []
    if not cases:
        report.check("存在契约坏用例", False, "tests/fixtures/bad/sop-* 下没有用例")
        return
    for case in cases:
        config = fixture_config(f"bad-{case}", BAD_ROOT / case)
        proc = build(config, TMP / f"bad-{case}")
        ok = proc.returncode != 0 and PIPELINE_MARKER in (proc.stderr + proc.stdout)
        report.check(f"契约[{case}] → 构建失败且错误来自 SOP 发布管线", ok,
                     "" if ok else "exit=%d %s" % (proc.returncode, (proc.stderr or proc.stdout)[-300:]))


def assert_draft(report):
    """draft: true = 注册但未发布（0009 目录契约）：不进生产构建，-D 构建出现。"""
    config = fixture_config("draft", DRAFT_ROOT)
    prod = build(config, TMP / "draft-prod")
    report.check("draft fixture 生产构建成功", prod.returncode == 0,
                 prod.stderr[-300:] if prod.returncode else "")
    if prod.returncode == 0:
        live = (TMP / "draft-prod" / "posts" / "draft-live-entry.html").is_file()
        hidden = (TMP / "draft-prod" / "posts" / "draft-hidden-entry.html").exists()
        report.check("draft: true 条目不进生产构建（对照组进）", live and not hidden,
                     f"live={live} hidden={hidden}")
    withd = run(["hugo", "--gc", "--minify", "--cleanDestinationDir", "-D",
                 "--config", config, "-d", str(TMP / "draft-d")])
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
    """索引文章的 6 个 ref 全部解析到冻结 URL（0009 连带裁定：实施期第一验证点）。"""
    page = TMP / "real" / "posts" / "sop-ops-tools-index.html"
    if not page.is_file():
        report.check("索引文章产物存在", False, str(page))
        return
    html = page.read_text(encoding="utf-8")
    for e in parse_registry(REGISTRY):
        target = "/mapleFlow/posts/%s.html" % e["slug"]
        report.check(f"索引文章 ref → {target}", target in html)


def assert_search_index(report):
    """搜索索引含 6 篇 SOP（雾区结论的实施期验证：生成页是真页面，自动进投影）。"""
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
