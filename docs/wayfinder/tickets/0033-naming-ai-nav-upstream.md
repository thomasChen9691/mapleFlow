---
id: 0033
title: 命名、AI 导航契约与上游关系
type: grilling
mode: HITL
status: closed
blocked_by: [0029, 0030, 0028]
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
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

## Resolution

2026-10-20 · grilling（五问全决，用户为决策者；施工待项目负责人指示）：

1. **命名与术语**：主题名 `maplemod` 沿用 0029 决议；CONTEXT.md 新增**概念级**「主题层」术语条——主题层 = 呈现与行为基线（themes/maplemod），与站点层（内容与数据）相对；不载文件布局（0020 纪律），与「产品索引」「reveal 协议」同级。
2. **主题内导航文档 = 原地重写 `themes/maplemod/README.md`**（现有上游安装/宣传文档已误导）。内容：fork 点与日期、保留/修剪清单与理由、分层契约（主题层 vs 站点层，含「因什么而变」判据）、**五个合并文件的合并前历史在旧站点路径**（0030 施工订正遗留）、MIT 许可。文档跟代码走，进目录即见。
3. **AGENTS 导航**：坑点 3 改写为**前向参数纪律**（每个 hugo.toml 参数必须在 maplemod 有读取点，grep 验证；无读取点即死配置——0029 已清 14 个）；坑点 5（homeInfoParams）是已删功能残留，**整条删除并顺延编号**（6→5、6b→5b、7→6…11→10），同步改唯一交叉引用（§3「见坑点 6b」→「5b」）；§7 速查表新增 `themes/maplemod/` 目录级一行（主题层，导航见其 README，无同步义务）。
4. **上游关系 = cut cord**：不建 upstream remote；fork 点（6c5a8f6 / v8.0-55 / 2026-01-09）记入主题 README；**删除 `.git/modules` 的 10M 孤立缓存**（0031 留的处置时机在此兑现）。理由：0029 已删 70 文件 + 改名 + 合并覆盖，merge 上游必然冲突风暴，跟踪与设计对抗。
5. **许可与 provenance**：`themes/maplemod/LICENSE` 原样保留（两行上游版权）；README 注明 fork 来源、commit、日期、MIT 与修改范围；**页脚不加鸣谢**（MIT 无强制要求，且与「第一方主题」定位矛盾）。
6. **雾区毕业（本题顺带定）**：主题内部结构**不重组**——assets/css 分文件与 partial 目录保持上游布局（无功能收益，且保留与上游的对照性）；fork 后**无再同步机制**（cut cord 的推论），版本钉记只在 README 的 fork 点一行。
