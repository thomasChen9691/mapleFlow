# 交接：精选类型守卫 PR 与合并（2026-10-26）

> 决策与契约见 `docs/adr/0015-featured-type-guard.md` 与地图 `docs/wayfinder/map-featured-type-guard.md`（已 closed）；本文件只记当前状态、下一步、建议 skill。

## 当前状态

- **GitHub 授权已恢复**（用户 2026-10-26 确认）。两条分支均未推、PR 均未开：
  - `refactor/harness-convergence`：自 main 起 **13 笔**（harness 9 笔 + 基点可视批 4 笔），测试基建收敛（ADR-0014）。
  - `refactor/featured-guard-module`：自 harness 尖起 **5 笔**（`a1202e8` 图 → `c8725e8` 模块 → `7a01618` 四票 Resolution → `2cf3d2a` SOP 缺口 → `7e2e968` 收口），精选类型守卫（ADR-0015）。
- **本地验证基线**：site 159/159 · sop 105/105 · npm 8+23+41 · 生产构建零 WARN · 无 localhost 泄漏。
- 地图 `map-featured-type-guard` 已 closed（7/7 票），frontier 空。

## 下一步

1. **先合 harness 分支**：`git push -u origin refactor/harness-convergence` → 开 PR → 等 verify 绿（注意含 `Assert harness self-test` 步与零 WARN 守门）→ **squash 合并**（规则集仅允许 squash）→ 删远端分支。
2. **本分支 rebase 到 main**：`git rebase --onto origin/main refactor/harness-convergence refactor/featured-guard-module`（只重放 5 笔，不重放已在 main 的 harness 提交）→ `git push -u origin refactor/featured-guard-module` → 开 PR → verify 绿 → squash 合并 → 删远端分支、本地 `git pull`。
3. 合并后 gh-pages 自动推进；两套 PR 的 verify 全绿即收口。

## 建议 skill

- **realeng-handoff**：本文件已用（跨会话接力时优先读它）。
- **realeng-code-review**：若 CI 红，修复后按 Standards / Spec 双轴复审。
- **realeng-tdd**：后续施工照例红绿 + 变异检验。
- **realeng-grilling**：开新地图时用（一次一问、推荐先行、事实自查后问决策）。
