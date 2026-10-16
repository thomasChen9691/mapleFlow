#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOP golden 捕获（wayfinder 工单 0013 裁决 A：独立捕获脚本）。

用法：
  python3 tests/capture_sop_golden.py              # 重捕获全部已有 golden
  python3 tests/capture_sop_golden.py <slug>...    # 捕获指定 slug（新建或更新）
  python3 tests/capture_sop_golden.py --check      # 只读校验：任一 golden 陈旧即非零退出

工作流（golden 的生命周期）：
  · 笔记合理修订 → 断言红（迁移保真）→ 确认变更是有意的 → 跑本脚本 → golden diff
    进 PR review。期望值的更新永远是一个可审的文件变更，不是一条静默命令。
  · 新增 SOP 条目 → 写笔记 + 注册条目 →（可选）跑本脚本为其建 golden，字节级
    守门强于仅结构断言；不建则由结构断言守，两者都是合法状态。
  · 未改动树上跑本脚本或 --check 必须零 diff（幂等自检）。

为什么不是断言脚本里的 --recapture：验证与再生混一个入口，误跑一下就把
「页面回归」洗成「期望更新」——同义反复测试的反模式。
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sop_golden as sg

TMP = sg.REPO / "tests" / "tmp" / "capture"


def main():
    args = [a for a in sys.argv[1:]]
    check = "--check" in args
    slugs = [a for a in args if not a.startswith("--")]
    if not slugs:
        slugs = sg.existing_slugs()
    if not slugs:
        print("没有 golden 可捕获（tests/fixtures/sop-golden/ 为空且未指定 slug）")
        return 2

    if shutil.which("hugo") is None:
        print("ERROR: hugo 不在 PATH")
        return 2
    shutil.rmtree(TMP, ignore_errors=True)
    proc = sg.build_real(TMP)
    if proc.returncode != 0:
        print("ERROR: 生产构建失败——golden 只能从成功构建捕获\n" + proc.stderr[-500:])
        return 1

    changed = []
    for slug in slugs:
        page = TMP / "posts" / f"{slug}.html"
        if not page.is_file():
            print(f"ERROR: {page} 不存在（slug 拼错或未注册？）")
            return 1
        data = sg.extract(page.read_text(encoding="utf-8"))
        path = sg.golden_path(slug)
        if path.is_file():
            old = json.loads(path.read_text(encoding="utf-8"))
            if old == data:
                print(f"[same] {slug}")
                continue
        if check:
            changed.append(slug)
            print(f"[stale] {slug}")
        else:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
            print(f"[{'update' if path.is_file() else 'create'}] {slug}")

    if check and changed:
        print(f"\n{len(changed)} 个 golden 陈旧：{', '.join(changed)}")
        print("若页面变更是有意的，跑 python3 tests/capture_sop_golden.py 重捕获，"
              "并把 golden diff 一并 review。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
