"""
assert_harness.py —— harness Python 侧自测（工单 0066）
============================================================
测什么：牙临界行为——Report 的记账与 failed 判定、finish 的退出码、
dest 的路径拼装与守卫、reset_tmp 的套件隔离、write_config 的四轴与
路径正规化。间接覆盖判据（0066 Q1）：破坏这些行为时契约套件是否
可定位地红——不达标者（静默假绿类）立自测。

纪律：**独立记账**——刻意不复用被测的 harness.Report（复用即同义
反复：被测物坏掉时自测的记账一起坏）；期望值独立字面量；每条以变异
检验证牙（施工期执行：破坏 harness → 本文件红 → 还原）；本文件禁存
任何被测模块的契约字面量（0061 禁项在自测侧同样生效）。

跑法：python3 tests/assert_harness.py（CI verify 一步，先于契约断言）。
"""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

ITEMS = []


def check(name, ok, detail=""):
    """独立记账（被测物正是 harness.Report，故自建）。"""
    ITEMS.append((bool(ok), name, detail))


# ---- Report 记账与 failed 判定
r = harness.Report()
r.check("a", True)
r.check("b", False)
r.check("c", 1)  # 真值强制：bool(1) is True
check("Report.items 记录全部三条", len(r.items) == 3, f"got {len(r.items)}")
check("Report.failed 只返回未过项", [i[1] for i in r.failed] == ["b"],
      f"got {[i[1] for i in r.failed]}")
check("Report.check 真值强制（bool(1) is True）", r.items[2][0] is True)


# ---- finish 退出码（截 stdout，防污染自测输出）
def finish_code(report):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = harness.finish("selftest", report)
    return code, buf.getvalue()


ok_report = harness.Report()
ok_report.check("x", True)
code, out = finish_code(ok_report)
check("finish 全过返回 0", code == 0, f"got {code}")
check("finish 全过输出 GREEN 与 1/1", "GREEN" in out and "1/1 passed" in out, out[-80:])
bad_report = harness.Report()
bad_report.check("x", False)
code, out = finish_code(bad_report)
check("finish 有失败返回 1", code == 1, f"got {code}")
check("finish 有失败输出 RED 与 0/1", "RED" in out and "0/1 passed" in out, out[-80:])


# ---- dest 拼装与守卫（_suite 由 run() 登记；自测直接设置以观测契约）
harness._suite = "selftest"
check("dest 拼 tmp/<suite>/<purpose>",
      harness.dest("real") == REPO / "tests" / "tmp" / "selftest" / "real",
      f"got {harness.dest('real')}")
harness._suite = None
raised = False
try:
    harness.dest("x")
except RuntimeError:
    raised = True
check("dest 无套件登记时守卫报错（不静默走 None 路径）", raised)


# ---- reset_tmp 套件隔离
harness.reset_tmp("selftest")
root = harness.tmp_root("selftest")
check("reset_tmp 建根", root.is_dir())
(root / "junk.txt").write_text("x", encoding="utf-8")
harness.reset_tmp("selftest")
check("reset_tmp 清场（旧内容不残留）", not (root / "junk.txt").exists())
check("tmp_root 按套件分根", harness.tmp_root("site") == REPO / "tests" / "tmp" / "site")


# ---- write_config 四轴与路径正规化
harness._suite = "selftest"
cfg = harness.write_config("probe",
                           dataDir=REPO / "tests" / "fixtures" / "data",
                           contentDir=REPO / "tests" / "fixtures" / "content-img",
                           sopNotesDir=REPO / "docs" / "sop",
                           refLinksErrorLevel="WARNING")
text = (harness.tmp_root("selftest") / "probe.toml").read_text(encoding="utf-8")
check("write_config dataDir 轴（绝对路径相对化）",
      'dataDir = "tests/fixtures/data"' in text, text)
check("write_config 无反斜杠（as_posix）", "\\" not in text, text)
check("write_config contentDir 轴", 'contentDir = "tests/fixtures/content-img"' in text)
check("write_config sopNotesDir 在 [params] 下",
      "[params]" in text and 'sopNotesDir = "docs/sop"' in text, text)
check("write_config refLinksErrorLevel 轴", 'refLinksErrorLevel = "WARNING"' in text)
check("write_config 返回配置串", cfg == "hugo.toml,tests/tmp/selftest/probe.toml",
      f"got {cfg}")
minimal = harness.write_config("probe-min", dataDir=REPO / "tests" / "fixtures" / "data")
text2 = (harness.tmp_root("selftest") / "probe-min.toml").read_text(encoding="utf-8")
check("write_config 未传的轴不出现（无缺省回落）",
      "contentDir" not in text2 and "sopNotesDir" not in text2
      and "refLinksErrorLevel" not in text2 and "[params]" not in text2, text2)


# ---- 收尾（独立记账的汇总，格式对齐套件惯例）
width = max(len(name) for _, name, _ in ITEMS)
for ok, name, detail in ITEMS:
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name.ljust(width)}" + (f"  {detail}" if detail and not ok else ""))
failed = [i for i in ITEMS if not i[0]]
print(f"\n{len(ITEMS) - len(failed)}/{len(ITEMS)} passed")
if failed:
    print("RED — %d 个行为未满足" % len(failed))
    sys.exit(1)
print("GREEN")
sys.exit(0)
