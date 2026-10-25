"""
harness.py —— 测试 harness 的 Python 侧（工单 0062 决议）
============================================================
「harness」是一个概念：本文件（Report / 入口仪式 / tmp 管理）+ Node 侧
tests/dom.mjs（check / jsdom 页面装配 / 汇总退出）——按职责命名，语言
边界强制两个文件，概念是一个模块。消费方：assert_site_contracts.py 与
assert_sop_pipeline.py 两个入口套件（另 capture_sop_golden.py 用其
tmp 根）。

seam 纪律（0061 裁定，0062 确认）：**seam 之后只有机制**——
  · 承诺（0062 五承诺中本文件先落三件）：收报告（Report 记账 / 汇总 /
    退出码）、入口仪式（--quick 参数 / hugo 检查 / tmp 重置）、tmp 按
    套件分根（0065：tmp/<suite>/，所有权从约定变为结构）
  · 禁止：知道任何被测模块的词表 / 持有任何契约期望值 / 持有 fixture
    数据。四套件的契约字面量（BAD_CASE_EXPECT 等）与样本留在各套件——
    三层文档契约的第三层（ADR-0007），independent 是承重设计
  · 待接入的两件承诺：跑构建（旗标档位归工单 0063）、写 fixture 配置
    （参数面归工单 0064）——未决前由套件各自持有

tmp 残留清点（0065 Q4，记录在案、不加锁不分家）：tests/__pycache__
（跟着被导入模块的文件位置走、按 mtime 自失效）与 resources/_gen
（Hugo 资源缓存，今日已被两套件共享）是既有共享状态，缓存语义，
分根不改变它们。

与 sop_golden.py 的关系：**并列的第三个共享模块**（内容 fixture 工具：
golden 抽取 / 规范化 / 生产构建捕获），不并入本 harness——分类裁定见
工单 0061，结构关系归工单 0070；提及于此以防未来的合并冲动。

纳入判据（0062）：≥2 消费者 + deletion test；无消费者预期的入口不留
（ADR-0006 决策 2 同款）。harness 自身如何被测归工单 0066。
"""
import argparse
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class Report:
    """断言记账：check 记录一条，failed 给未过项；汇总与退出见 finish。"""

    def __init__(self):
        self.items = []

    def check(self, name, ok, detail=""):
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self):
        return [i for i in self.items if not i[0]]


def tmp_root(suite):
    """套件 tmp 根（0065：按套件分根——site / sop / capture 各有其根）。"""
    return REPO / "tests" / "tmp" / suite


_suite = None  # run() 登记当前套件；dest() 据此拼根（仅 run() 之后的套件代码调用）


def dest(purpose):
    """构建目标目录（0065 Q3：dest 归 harness 生成——套件传用途名，本函数拼
    tmp/<suite>/<purpose>；「real」这类魔法字符串不进调用点，跨套件不相撞）。"""
    if _suite is None:
        raise RuntimeError("dest() 仅在 harness.run() 之后的套件代码中调用")
    return tmp_root(_suite) / purpose


def reset_tmp(suite):
    """入口仪式之一：清空并重建本套件的 tmp 根（0065：按套件分根）。"""
    root = tmp_root(suite)
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)


def run(suite, checks):
    """入口仪式：参数 → hugo 检查 → tmp 重置 → Report → checks → 汇总退出。

    checks(report, quick) 是套件的断言清单（0062：入口只剩参数 + 有序
    断言清单，编排顺序是套件知识不是基建）。
    """
    global _suite
    _suite = suite
    parser = argparse.ArgumentParser(description=f"{suite} 套件产物断言")
    parser.add_argument("--quick", action="store_true", help="跳过真实数据构建")
    args = parser.parse_args()

    if shutil.which("hugo") is None:
        print("ERROR: hugo 不在 PATH（CI 由 peaceiris/actions-hugo 提供）")
        return 2

    reset_tmp(suite)
    report = Report()
    checks(report, args.quick)
    return finish(suite, report)


def finish(suite, report):
    """汇总留痕 + GitHub Actions 注解 + 退出码（有失败 = 1）。"""
    width = max((len(name) for _, name, _ in report.items), default=0)
    for ok, name, detail in report.items:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name.ljust(width)}" + (f"  {detail}" if detail and not ok else ""))
    failed = report.failed
    # CI 日志需认证才能取，注解在 run 页直接可见（2026-10-16 首红时的教训）。
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for _, name, detail in failed:
            print(f"::error title={suite} assertion::{name} - {detail}")
    print(f"\n{len(report.items) - len(failed)}/{len(report.items)} passed")
    if failed:
        print("RED — %d 个行为未满足" % len(failed))
        return 1
    print("GREEN")
    return 0
