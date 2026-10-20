---
id: 0031
title: 子模块退役与构建链触点
type: grilling
mode: HITL
status: closed
blocked_by: [0029]
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

子模块从「外挂依赖」退为「仓内目录」的机械路径与全部触点的处置边界。事实底坐：0027 §7 触点清单、0028 §3 vendor 化路径与 CI 行为。

待决问题（一次会话内按序过，先给推荐答案）：

1. **gitlink 处置确认**：`git rm --cached themes/PaperMod` + 删 `.gitmodules` + `git add themes/PaperMod` 的 vendor 化路径（0028：官方语义组合的社区通行做法）——历史中的 gitlink 与 `.git/modules/` 缓存不动，是否有异议？若 0029 择改名（B），`git mv`/重命名与 add 的顺序如何定？
2. **CI 触点**：deploy.yml:28 `submodules: true` —— 0028 证实移除后构建不依赖它。删除该行（连带注释）还是暂留？本地/CI 的 Hugo 查找是否需任何其他改动（预期无）？
3. **文档触点范围**（0027 §7 清单）：AGENTS.md 5 处——①「项目概览」子模块描述；② 部署流水线「检出（含子模块）」；③「首次初始化主题子模块」整段；④ 坑点 6（`git checkout main` 联网卡死，整条随子模块消失）；⑤ §7 速查表 post_meta 行「升级时必须回来同步」；README 5 处子模块初始化指引。删除/改写的边界（哪些整删、哪些改写为 fork 后形态）？
4. **验收标准**：触点清完的判据——三套件（`npm test` / `assert_product_states.py` / `assert_sop_pipeline.py`）+ 生产构建 exit=0 + `grep -r "localhost:1313" public/` 零残留（ADR-0001/0005/0007 既有纪律）；是否加「主题目录文件清单快照」类断言（归 0032 决策，本题只确认验收面）。
5. **本地 dirty 状态**：当前工作区 themes/PaperMod 116 文件 CRLF dirty——若 0029 择「入库时转 LF」，本题确认添加时的行尾归一方式（`.gitattributes` vs add 前转换）。

决策记录：本题 Resolution 落触点处置表（每处：删/改/留 + 理由）+ 验收判据，作为施工期（项目负责人指示后展开）的执行清单。

## Resolution

2026-10-20 · grilling（四问全决，用户为决策者；施工待项目负责人指示）：

1. **gitlink 处置**：0029 施工已完成 `git rm --cached` + 删 `.gitmodules` + 文件入库；**历史中的 gitlink 不清理**（不 rewrite，旧提交仍指 themes/PaperMod 是历史事实）。`.git/modules/themes/PaperMod`（10M 上游完整历史缓存）**保留**——它是上游历史唯一本地副本，是 0033 上游关系决议的期权；处置时机挂在 0033（选 cut-cord 后再删）。**写明**：该缓存是本地状态，不进仓库、不进 clone，避免未来会话误以为上游历史在仓库里。
2. **CI 触点 = A（两行都删）**：deploy.yml 删 `submodules: true`（已无子模块）与 `fetch-depth: 0`（全仓 `.GitInfo` 零使用，Hugo 构建不读 git 历史，原注释「避免 Hugo 构建出错」货不对板）——与 0029 的「死配置=谎言」同一纪律。正确性由 push 后 CI 实证，红则回滚（成本一行）。
3. **文档触点处置表 + 边界**（**0031 清「子模块事实」/ 0033 管「命名与导航」**，边界写入两份 Resolution 防重复编辑）：
   - AGENTS §1 L10「themes/PaperMod 是 Git 子模块」→ 改写为 `themes/maplemod` 仓内第一方主题（fork 自 PaperMod v8.0-55，无子模块、无同步义务）；
   - AGENTS §2 L20「检出（含子模块）」→ 删括号；
   - AGENTS §3 L31-33 子模块初始化整段（含 proxy 排障）→ 整段删除；
   - AGENTS §4 坑点 6（checkout 卡死）→ 删除 + **后续坑点顺延编号**（7→6、7b→6b…12→11），同步改 L45「见坑点 7b」→「见坑点 6b」（全仓仅此一处引用，已 grep 实证）；
   - AGENTS §7 post_meta 行「升级 PaperMod 子模块时必须回来同步…」→ 删同步义务子句（路径/命名完整改述归 0033）；
   - README 克隆段（`--recurse-submodules`、子模块补拉、proxy 排障、手动 clone 主题）→ 普通 clone + 整段删排障；README 部署「检出代码（包含 PaperMod 子模块）」→ 删括号；
   - **不动**（归 0033）：README 标题/正文的 PaperMod 命名、AGENTS 坑点 3/5 的 PaperMod 表述、新增主题速查行。
4. **验收 = 本地 5 条 + CI 1 条**：① 生产构建 exit=0 + 三套件（16/39/100）；② 无子模块指令不变量——`grep -n "git submodule\|--recurse-submodules\|submodules:" AGENTS.md README.md deploy.yml` 零命中（不能只 grep「子模块」：改写后「无子模块、无同步义务」是正确表述，判据是「不再有子模块操作」）；③ `.gitmodules` 不存在 + `git ls-files --stage | grep 160000` 零命中；④ `git ls-files --eol themes/maplemod` index 全 i/lf 复验；⑤ `localhost:1313` 零残留；⑥ **CI 实证（push 后）**：Deploy run 全绿——唯一能验证 checkout 改动的地方。**关闭规则：本地 5 条全过即 closed，CI 结果 push 后回填**（CI 若红属新缺陷，另开修复，不卡地图）。
   - 明确不做：主题目录清单快照/结构断言归 0032；坑点 6 删除后**不补写**分支切换注意事项（`git checkout` 回归普通操作，无替代坑）。

**边界确认**：0031 施工顺序应在 0030 合并之后（post_meta 行改写以合并后的路径为准）；0033 在两者之后统一做命名/导航/上游关系。

**施工订正（2026-10-20 双轴评审后）**：① **越界回退**——AGENTS §1「性质」行曾被顺带改为 maplemod，按「命名归 0033」边界**回退为 PaperMod**（与 README 标题一致，等 0033 统一改）；README 克隆段多写的一行排障注记已删（严格按「整段删排障」）。② 坑点 11 的「`extend_head` 的 class swap 是 ADR-0002 **升级同步件**」措辞改为「ADR-0002 **基线的一部分**」——「升级同步件」与同文件「无同步义务」互斥。③ 验收复跑：本地 5 条全过（构建 0 / 16 / 39 / 100、无子模块操作、无 gitlink、LF、localhost 零残留）。
