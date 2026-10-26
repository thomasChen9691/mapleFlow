# 交接：精选类型守卫收尾与 PR 暂缓（2026-10-26）

> 决策与契约见 `docs/adr/0015-featured-type-guard.md` 与地图 `docs/wayfinder/map-featured-type-guard.md`（已 closed）；本文件只记当前状态、下一步、建议 skill。

## 当前状态

- **工作已全部落地并验证**：地图 7/7 票 closed、ADR-0015（15 条决策）、收口 handoff 齐备；本地验证基线 = site 159/159 · sop 105/105 · npm 8+23+41 · 生产构建零 WARN · 无 localhost 泄漏。
- **`refactor/harness-convergence`**：已推 origin（尖 `4665c33`，自 main 起 13 笔——harness 9 笔 + 基点可视批 4 笔），PR 未开。
- **`refactor/featured-guard-module`**：**未推**；提交链 `a1202e8` 图 → `c8725e8` 模块 → `7a01618` 四票 Resolution → `2cf3d2a` SOP 缺口 → `7e2e968` 收口 → `25599e0` / `14576f9` / `b7c9afb` 交接（**笔数以 `git log --oneline refactor/harness-convergence..HEAD` 为准**）。
- **PR 创建与合并按用户决定暂缓（2026-10-26）**——主动推迟，非未解决的阻塞。
- **工具面缺口（实测，恢复合并前需先解决）**：GitHub 连接器 status=connected 但 `mcp__github__*` 未在会话注册（ToolSearch / 直接调用均 not found，`reconnect_plugin` 无变化）；`gh` / `hub` 未安装；无 `GITHUB_TOKEN` / `GH_TOKEN`；remote 走 SSH（`credential.helper=osxkeychain` 对 API 无用）。**PR 必须经网页或装 gh 后创建。**

## 下一步（恢复合并时按序执行）

1. **先合 harness 分支**：打开 `https://github.com/thomasChen9691/mapleFlow/compare/main...refactor/harness-convergence?expand=1` 开 PR → 等 verify 绿（含 `Assert harness self-test` 步与零 WARN 守门）→ **Squash and merge** → 删远端分支。
2. **本分支 rebase 到 main**：`git fetch origin && git rebase --onto origin/main refactor/harness-convergence refactor/featured-guard-module`（只重放本分支自有提交，不重放已在 main 的 harness 提交）→ `git push -u origin refactor/featured-guard-module` → 开 PR（compare URL 同式）→ verify 绿 → squash 合并 → 删远端分支、本地 `git pull`。
3. 若希望全流程由 agent 执行：`brew install gh && gh auth login` 后说一声，agent 可完成开 PR / 看门禁 / squash 合并 / rebase。

## 建议 skill

- **realeng-handoff**：本文件已用（跨会话接力时优先读它）。
- **realeng-code-review**：若 CI 红，修复后按 Standards / Spec 双轴复审。
- **realeng-tdd**：后续施工照例红绿 + 变异检验。
- **realeng-grilling**：开新地图时用（一次一问、推荐先行、事实自查后问决策）。
