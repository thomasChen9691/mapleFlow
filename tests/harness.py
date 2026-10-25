"""
harness.py —— 测试 harness 的 Python 侧（工单 0062 决议）
============================================================
「harness」是一个概念：本文件（Report / 入口仪式 / tmp 管理）+ Node 侧
tests/dom.mjs（check / jsdom 页面装配 / 汇总退出）——按职责命名，语言
边界强制两个文件，概念是一个模块。消费方：assert_site_contracts.py 与
assert_sop_pipeline.py 两个入口套件（另 capture_sop_golden.py 用其
tmp 根）。

seam 纪律（0061 裁定，0062 确认）：**seam 之后只有机制**——
  · 承诺（0062 五承诺本文件全落）：收报告（Report 记账 / 汇总 / 退出码）、
    入口仪式（--quick 参数 / hugo 检查 / tmp 重置）、tmp 按套件分根
    （0065）、跑构建（旗标档位归 0063，两档 + 逐调用 extras）、写 fixture
    配置（参数面归 0064，四轴全显式）
  · 禁止：知道任何被测模块的词表 / 持有任何契约期望值 / 持有 fixture
    数据。四套件的契约字面量（BAD_CASE_EXPECT 等）与样本留在各套件——
    三层文档契约的第三层（ADR-0007），independent 是承重设计

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
import subprocess
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


def sh(cmd):
    """子调用的统一包装（两套件原各持一份逐字相同的 run——第三处副本，随 build 吸收）。"""
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


# 构建旗标档位（0063）：档位封装基底旗标集与「为什么是这组旗标」的理由；
# 新档位须过 0062 双门槛（≥2 消费者 + deletion test），档位表不得无纪律膨胀。
_PROFILES = {
    # site-contracts：断言解析带引号属性与未压缩 HTML，故意不 minify。
    # real 构建用生产配置但同样不 minify——minify 形态归 CI 零 WARN 守门；
    # 此不对称为承重设计，防将来有人把测试构建「统一」成生产旗标。
    "site-contracts": ["--cleanDestinationDir"],
    # sop-pipeline：与 CI 生产命令逐字一致——golden 按 minify 后的线上产物
    # 捕获，构建条件不一致则逐字节比对无意义。
    "sop-pipeline": ["--gc", "--minify", "--cleanDestinationDir"],
}


def build(config, dest, profile, flags=None):
    """按档位构建（0063）：档位给基底旗标，flags 给逐调用差异
    （--contentDir / --layoutDir / -D 等）；档位是套件的属性，由套件级
    适配器绑定，不在调用点重复。"""
    if profile not in _PROFILES:
        raise ValueError("未知构建档位：%r（现存：%s）" % (profile, sorted(_PROFILES)))
    cmd = (["hugo"] + list(_PROFILES[profile])
           + ["--config", config, "-d", str(dest)] + list(flags or []))
    return sh(cmd)


def _toml_path(value):
    """TOML 内路径正规化（0064 坑一内聚）：绝对路径相对化 + as_posix。

    Windows 上 relative_to 产反斜杠，嵌进 TOML 会被当转义序列解析，
    坏用例将因路径失败而非契约失败（假红）——全仓写入者经本函数共享此坑。
    """
    p = Path(value)
    if p.is_absolute():
        p = p.relative_to(REPO)
    return p.as_posix()


def write_config(name, dataDir, *, contentDir=None, sopNotesDir=None, refLinksErrorLevel=None):
    """fixture 配置写入入口（0064）：一个入口、四轴、全显式、无缺省。

    轴 = dataDir / contentDir / sopNotesDir / refLinksErrorLevel；未传的轴
    不出现（调用方显式选择），不为任何轴备缺省值（ADR-0006 决策 2：缺省
    回落是静默失效类）。宽度上限 = 四轴；新轴须带新消费者并过 deletion
    test（0062 双门槛），入口不得为假想变体撑宽。

    坑二（随入口内聚）：dataDir 只含数据文件——.md 混入即 Hugo
    「unmarshal of format」崩溃（notes 平级隔离的原因，SOP fixture 布局
    约定；套件侧的 root→轴映射归各套件，harness 不懂内容布局）。
    坑一（路径正规化）的内聚处是 _toml_path——本入口的所有路径经它
    相对化 + as_posix，调用方不各自处理。

    返回 "hugo.toml,<cfg>" 配置串（build 的 config 参数）；cfg 落本套件
    tmp 根（0065）。
    """
    if _suite is None:
        raise RuntimeError("write_config() 仅在 harness.run() 之后的套件代码中调用")
    lines = ['dataDir = "%s"' % _toml_path(dataDir)]
    if contentDir is not None:
        lines.append('contentDir = "%s"' % _toml_path(contentDir))
    if refLinksErrorLevel is not None:
        lines.append('refLinksErrorLevel = "%s"' % refLinksErrorLevel)
    if sopNotesDir is not None:
        lines.append('[params]')
        lines.append('sopNotesDir = "%s"' % _toml_path(sopNotesDir))
    cfg = tmp_root(_suite) / f"{name}.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "hugo.toml,%s" % cfg.relative_to(REPO).as_posix()


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
