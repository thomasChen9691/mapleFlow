#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""产品状态模块的产物断言（ADR-0004；wayfinder 工单 0002/0005 定案）。

测试缝（预先商定，勿在未确认的缝上写测试）：
  · 渲染产物 seam —— fixture 构建的 products.html（控件态 / 文案 / data-price）
    与 index.html（「可下载产品」计数）
  · 契约 seam —— tests/fixtures/bad/ 下每个用例的构建必须失败
    （输入契约由模块内 errorf 执法，非零退出 + 错误信息含「产品状态」）
  · 真实数据 seam —— 生产配置构建的 products.html / index.html，线上回归守门

用法：
  python3 tests/assert_product_states.py          # 全套
  python3 tests/assert_product_states.py --quick  # 跳过真实数据构建（本地快速迭代）

Hugo 版本纪律：模块必须保持 0.164 语义（单变量 + 根级单条 return）。本机 hugo
可能为 0.167 而 CI 钉 0.164——0.164 风格代码两端一致，但 0.166+ 的条件多
return 写法本地过、CI 红。本脚本只消费构建产物，与 Hugo 版本无关。

期望值均为独立字面量（决策规则的直写），不是对实现的重算——防止同义反复测试。
"""

import argparse
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
        "control": "link", "label": "购买", "href": "https://example.com/fx-listed-paid",
        "data_price": "paid", "price_text": "¥39",
    },
    "fx-listed-free": {
        "control": "link", "label": "免费获取", "href": "https://example.com/fx-listed-free",
        "data_price": "free", "price_text": "免费",
    },
    "fx-unlisted-paid": {
        "control": "disabled", "label": "即将上架", "href": None,
        "data_price": "paid", "price_text": "¥49",
    },
    "fx-unlisted-free": {
        "control": "disabled", "label": "即将上架", "href": None,
        "data_price": "free", "price_text": "免费",
    },
}
FIXTURE_LISTED_COUNT = 2   # 4 条 fixture 中已上架 2 条
REAL_ROW_COUNT = 5         # data/products.yaml 现有 5 条
REAL_LISTED_COUNT = 0      # 迁移后全部未上架（占位），可下载产品为 0（工单 0004：显示 0）


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
                         "price_text": "", "control": None, "href": None, "label": ""}
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


def build(config, dest):
    return run(["hugo", "--cleanDestinationDir", "--config", config, "-d", str(dest)])


class Report:
    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self):
        return [i for i in self.items if not i[0]]


def assert_search_index(report, dest):
    """产品搜索条目的 tag 必须用标准术语「产品」（CONTEXT.md；资源为禁用词）。"""
    import json
    index = json.loads((dest / "index.json").read_text(encoding="utf-8"))
    product_entries = [e for e in index if "products.html#" in (e.get("permalink") or "")]
    if not product_entries:
        report.check("搜索索引含产品条目", False, "index.json 里没有 products.html# 锚点条目")
        return
    bad = [e for e in product_entries if e.get("tags") != ["产品"]]
    report.check(f"产品搜索条目 tag = [\"产品\"]（{len(product_entries)} 条）", not bad,
                 "" if not bad else "got: " + "; ".join(str(e.get("tags")) for e in bad))


def assert_fixture(report):
    dest = TMP / "fixture"
    proc = build(FIXTURE_CONFIG, dest)
    report.check("fixture 构建成功", proc.returncode == 0, proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    rows = parse_rows(dest / "products.html")
    for pid, exp in FIXTURE_ROWS.items():
        row = rows.get(pid)
        if row is None:
            report.check(f"fixture[{pid}] 渲染出产品行", False, "products.html 中找不到该 id")
            continue
        report.check(f"未上架+免费 → 禁用「即将上架」+ data-price=free" if pid == "fx-unlisted-free"
                     else f"未上架+付费 → 禁用「即将上架」+ data-price=paid" if pid == "fx-unlisted-paid"
                     else f"已上架+免费 → 可点「免费获取」" if pid == "fx-listed-free"
                     else f"已上架+付费 → 可点「购买」",
                     row["control"] == exp["control"] and row["label"] == exp["label"]
                     and row["data_price"] == exp["data_price"] and row["price_text"] == exp["price_text"]
                     and row["href"] == exp["href"],
                     f"got control={row['control']} label={row['label']!r} data-price={row['data_price']} price={row['price_text']!r} href={row['href']!r}")
    count = parse_spec_count((dest / "index.html").read_text(encoding="utf-8"), "可下载产品")
    report.check("fixture 首页计数 = 已上架条数（2）", count == FIXTURE_LISTED_COUNT, f"got {count}")
    assert_search_index(report, dest)


def assert_bad_cases(report):
    """每个坏 fixture 的构建必须失败——契约执法（模块内 errorf）。"""
    bad_root = REPO / "tests" / "fixtures" / "bad"
    cases = sorted(p.name for p in bad_root.iterdir() if p.is_dir()) if bad_root.is_dir() else []
    if not cases:
        report.check("存在契约坏用例", False, "tests/fixtures/bad/ 下没有用例")
        return
    for case in cases:
        cfg = TMP / f"bad-{case}.toml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text('dataDir = "tests/fixtures/bad/%s"\n' % case, encoding="utf-8")
        proc = build("hugo.toml,%s" % cfg.relative_to(REPO), TMP / f"bad-{case}")
        ok = proc.returncode != 0 and "产品状态" in (proc.stderr + proc.stdout)
        report.check(f"契约[{case}] → 构建失败且错误来自产品状态模块", ok,
                     "" if ok else "exit=%d stderr=%s" % (proc.returncode, (proc.stderr or proc.stdout)[-300:]))


def assert_real(report):
    dest = TMP / "real"
    proc = build(REAL_CONFIG, dest)
    report.check("真实数据构建成功（生产配置）", proc.returncode == 0, proc.stderr[-400:] if proc.returncode else "")
    if proc.returncode != 0:
        return
    rows = parse_rows(dest / "products.html")
    all_unlisted = len(rows) == REAL_ROW_COUNT and all(
        r["control"] == "disabled" and r["label"] == "即将上架" for r in rows.values())
    report.check(f"真实数据 {REAL_ROW_COUNT} 条全部「即将上架」", all_unlisted,
                 f"got {len(rows)} rows: " + ", ".join("%s=%s/%s" % (k, v["control"], v["label"]) for k, v in rows.items()))
    count = parse_spec_count((dest / "index.html").read_text(encoding="utf-8"), "可下载产品")
    report.check(f"真实数据可下载产品计数 = {REAL_LISTED_COUNT}", count == REAL_LISTED_COUNT, f"got {count}")


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
    assert_fixture(report)
    assert_bad_cases(report)
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
