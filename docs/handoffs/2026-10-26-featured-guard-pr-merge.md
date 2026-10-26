# 交接：精选类型守卫 PR 与合并（2026-10-26）

> 决策与契约见 `docs/adr/0015-featured-type-guard.md` 与地图 `docs/wayfinder/map-featured-type-guard.md`（已 closed）；本文件只记当前状态、下一步、建议 skill。

## 当前状态

- **GitHub 授权已恢复**（用户 2026-10-26 确认），SSH push 可用。
- `refactor/harness-convergence`：**已推**到 origin（尖 `4665c33`，自 main 起 13 笔——harness 9 笔 + 基点可视批 4 笔），**PR 待开**。
- `refactor/featured-guard-module`：**未推**，自 harness 尖起的提交链：`a1202e8` 图 → `c8725e8` 模块 → `7a01618` 四票 Resolution → `2cf3d2a` SOP 缺口 → `7e2e968` 收口 → `25599e0` / `14576f9` 本交接（**笔数以 `git log --oneline refactor/harness-convergence..HEAD` 为准**，不写死）。
- **PR 创建/合并的工具面缺口（本会话实测）**：GitHub 连接器状态 connected 但 **MCP 工具未在会话注册**（`mcp__github__*` 全部 not found，`reconnect_plugin` 无变化）；`gh` / `hub` CLI 未安装；无 `GITHUB_TOKEN` / `GH_TOKEN`；`credential.helper = osxkeychain`（remote 走 SSH，无 API 凭据）。**PR 必须经网页或安装 gh 后创建。**
- **本地验证基线**：site 159/159 · sop 105/105 · npm 8+23+41 · 生产构建零 WARN · 无 localhost 泄漏。
- 地图 `map-featured-type-guard` 已 closed（7/7 票），frontier 空。

## 下一步

1. **先合 harness 分支**：打开 `https://github.com/thomasChen9691/mapleFlow/compare/main...refactor/harness-convergence?expand=1` 开 PR → 等 verify 绿（含 `Assert harness self-test` 步与零 WARN 守门）→ **Squash and merge** → 删远端分支。
2. **本分支 rebase 到 main**：`git fetch origin && git rebase --onto origin/main refactor/harness-convergence refactor/featured-guard-module`（只重放本分支自有提交，不重放已在 main 的 harness 提交）→ `git push -u origin refactor/featured-guard-module` → 开 PR（compare URL 同式）→ verify 绿 → squash 合并 → 删远端分支、本地 `git pull`。
3. 若希望全流程由 agent 执行：`brew install gh && gh auth login` 后，agent 可完成开 PR / 看门禁 / squash 合并。

## 建议 skill

- **realeng-handoff**：本文件已用（跨会话接力时优先读它）。
- **realeng-code-review**：若 CI 红，修复后按 Standards / Spec 双轴复审。
- **realeng-tdd**：后续施工照例红绿 + 变异检验。
- **realeng-grilling**：开新地图时用（一次一问、推荐先行、事实自查后问决策）。
