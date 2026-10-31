# 交接：架构深化收口 + 单人直推切换（2026-10-31）

> 只写当前状态、下一步、建议 skill。决策与契约见 `docs/adr/0016-architecture-deepening.md`，术语见 `CONTEXT.md`，工单链见 `docs/wayfinder/map-architecture-deepening.md`（已 closed）——本文不重复。

## 当前状态

- **代码已全部就位，卡在最后一步推送**：本地 `main` 已 fast-forward 到 `bacc527`（含架构深化 27 笔），但 `git push origin main` 被服务端规则集拒绝：`Changes must be made through a pull request`。远端 `main` 仍停在 `89c3d50`。
- **工作流已改**：`AGENTS.md` §2 换成「单人直推」；旧的 PR + 按序 squash 流程整段注释保留在文末（含恢复步骤）。改这一条的提交就是 `bacc527`。
- **架构深化已收口**：地图 10/10 票 closed，决策落 ADR-0016（四章 20 条）。四件落地——卡片单模块、注册缝下沉、死面删除（−196 行、零断言改动）、parity 门（RGR-14）。
- **门禁基线**：npm **13+31+41** · site **185/185** · sop **105/105** · 生产构建 **0 WARN** · 无 localhost 泄漏。
- **三条 refactor/\* 分支已在远端**（`harness-convergence` / `featured-guard-module` / `card-registration`，叠罗汉关系）。它们的提交已全部包含在本地 `main` 里，**已成历史包袱**。

## 下一步

1. **解开规则集**（唯一阻塞项）：GitHub 仓库 Settings → Rules → Rulesets → `main-protection` → Disable；或保留规则集、把当前账号加进 **Bypass list**（更小的改动，仍允许直推）。**不要 `--force`**。
2. 解禁后 `git push origin main`；确认 CI 的 verify + deploy 两个 job 绿、站点已更新。
3. **清理**：远端与本地删掉三条 `refactor/*` 分支（`git push origin --delete <b>` + `git branch -d <b>`）；`main` 跟踪改回 `origin/main`。
4. 此后每项工作按 `AGENTS.md` §2 的新流程：改 → 本地跑四道门 → commit → `git push origin main`。

## 建议 skill

- **realeng-tdd**：红绿 + 变异；纯删除类改动的「测试」= 删完套件原样全绿。
- **realeng-code-review**：每批收尾双轴评审（本项目两批各抓到真问题，值得保留）。
- **realeng-grilling**：开下一张地图前先质询（一次一问、推荐先行、事实自查后问决策）。
- **realeng-wayfinder**：下一张图用；本图已 closed，**勿往已闭图加票**。
