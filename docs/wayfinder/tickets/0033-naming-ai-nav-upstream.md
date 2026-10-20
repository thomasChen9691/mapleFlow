---
id: 0033
title: 命名、AI 导航契约与上游关系
type: grilling
mode: HITL
status: open
blocked_by: [0029, 0030, 0028]
assignee:
map: map-theme-fork.md
created: 2026-10-20
---

## Question

「AI 可导航」的契约面 + 命名 + 上游关系与许可落点。事实底坐：0027 覆盖表与可达性两栏、0028 上游差距（92 提交）与 MIT 义务。

待决问题（一次会话内按序过，先给推荐答案）：

1. **主题命名**：跟随 0029 形态——目录名与 `theme` 字段（原名 PaperMod vs 自研名）；CONTEXT.md 是否新增术语条（「主题」/「第一方主题」/「vendored 主题」？——CONTEXT.md 只载领域概念不载文件布局，术语条措辞按此纪律设计）。
2. **主题内导航文档**：AI 代理进仓后如何不看会话历史就理解主题层——主题目录内 README/清单写什么（建议至少：25 partial 可达性两栏、4 覆盖文件→主题文件映射、dev/prod 双守卫说明、CRLF→LF 与 LICENSE  provenance）；放主题目录内还是 docs/ 下（考虑主题目录将来若改名/迁移，文档是否随动）。
3. **AGENTS.md 导航更新**：§7 速查表（主题相关行改述：post_meta「升级同步」改「fork 内文件」等）、坑点 3（reorderNavItems 「当前 PaperMod v8 不读」改述——fork 后可自行决定是否实现）、坑点 6 删除（0031 落地时）；§3 构建命令注释中子模块痕迹。
4. **上游关系**：cut cord（零同步、不接受上游变更）vs 留 upstream remote 按需 merge（社区实践，官方无专指南）——考量 0028 事实：上游活跃但 release 停 v8.0、钉住点已落后 92 提交；若 cut cord，是否在决策中显式记载「已知放弃的上游修复」（如 post_meta ISO 8601 上游修复——本站已自有实现）？
5. **许可落点**：MIT 最低义务=分发时随附 LICENSE+版权行——保留 themes/*/LICENSE 原位即可；是否需要额外 provenance 注记（主题 README 注明 fork 自 adityatelange/hugo-PaperMod @ 6c5a8f6）；无强制署名条款，页脚是否自愿加鸣谢由用户定。

决策记录：本题 Resolution 落命名 + 术语条措辞 + 主题内导航文档形态 + 上游关系策略 + 许可/provenance 落点。
