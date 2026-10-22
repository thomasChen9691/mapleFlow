---
id: "0039"
title: 精选机制的测试缝与断言集
type: grilling
mode: HITL
status: closed
blocked_by: ["0035", "0037", "0038"]
assignee: agent
map: map-featured-mechanism.md
created: 2026-10-21
claimed: 2026-10-21
closed: 2026-10-21
---

## Question

精选机制的**测试缝**——文章侧精选用什么夹具造、断言落在哪个脚本、必锚哪些行为。事实底座：`tests/hugo.test.toml` 只覆盖 `dataDir`（research/0035 §4），文章 fixture 需新增 `contentDir` 覆盖，且 fixture 构建里 `hugo.Data.sop` 为空、派生文 0 篇。

待决：

1. **落点**：并入 `tests/assert_product_states.py`（fixture 基建单份纪律，ADR-0004/0006 枪毙第二实现），还是新脚本？该脚本名已偏离实际职责（0032 记过「命名债」），文章精选并入会让偏离更远——是**改名**、**继续记账**、还是**按职责新开脚本但共用 fixture 构建函数**（需论证不构成第二实现）。
2. **文章 fixture 的造法**：`contentDir` 覆盖到 `tests/fixtures/content`（真实 `content/` 不再参与 fixture 构建，SOP 派生文本就为 0，但需确认 fixture 里要不要复制 `_content.gotmpl` 与最小 `posts`）；或维持真实 `content/` 而在断言里硬编码真实文章的 featured 期望（**与真实内容耦合，内容一变断言就红**——须明确排除或接受）。两条路的取舍是本题核心。
3. **必锚断言清单**（参照 0032「必锚 6 条」的体例，逐条要能用变异检验证明有牙）：① featured 文章进首页、非 featured 不进；② 条数上限与截断（第 N+1 条 featured 不上首页）；③ 与「最近更新」网格的去重（若 0037 定为剔除）；④ 0 篇时的空态/隐藏行为；⑤ 缺省未声明 = 非精选；⑥ 坏值（若 0036 定为 errorf，则断言构建失败并钉错误子串；若定为静默，则断言按非精选渲染）。
4. **真实数据回归**：现有 5 篇手写 + 6 篇派生文里**谁标 featured**——这既是内容决策也是断言期望值的来源（独立字面量要求），须与项目负责人当场定，否则断言无处落地。
5. **跨类一致性断言**：是否给产品侧既有断言补一条「文章与产品同名同义」的守门（防止未来两侧语义漂移），还是仅在文档层约定。

## Resolution

2026-10-21 · grilling（HITL，用户为决策者；随 0037/0038 同场钉死）：

1. **fixture = 新增独立构建**：第三个配置文件（只设 `contentDir = "tests/fixtures/content-posts"`），与现有 `hugo.toml,tests/hugo.test.toml` 叠加使用，**只服务文章精选断言**。理由：现有 48 条断言（产品 + 主题契约 B7-B13）全部建立在「真实 content + fixture dataDir」上，全局改 `contentDir` 会动摇它们的构建环境；独立构建多花约 1s，换零回归风险。已接受的既有事实：该 fixture 内 `hugo.Data.sop` 为空 → 派生文 0 篇（不新造 SOP 注册表 fixture）。
2. **必锚四条**（用户全选）：
   - ① 过滤 + 缺省语义：featured true 上首页、未声明不上；
   - ② 截断：fixture 放 4 篇 featured、limit 3 → 第 4 篇不上首页、精选区恰 3 行；
   - ③ **两片互斥无遗漏**：精选 ∪ 网格 = 全量、精选 ∩ 网格 = ∅（0037「剔除」决策唯一的牙口）；
   - ④ 空态 + 坏值：0 篇 featured → 区块不渲染；featured 写成字符串/整数 → 构建失败并钉错误子串（bad-case fixture）。
3. **落点 = 并入现有脚本并改名**：`tests/assert_product_states.py` → `tests/assert_site_contracts.py`（如名字最终另定，须满足「一脚本管站点契约」语义）。触发条件已到——0032 记账的「第三类职责时改名」现已超额（产品状态 / 产品索引 / 主题契约 B7-B13 / reveal 产物 / 精选）。
   **改名成本已实测（2026-10-21 复核，修正初判的「4-5 处」）**：活引用 **12 处**——`AGENTS.md` 7（坑点 9/10 + §7 速查 5 行）、`themes/maplemod/README.md` 2、`tests/assert_sop_pipeline.py` 注释 2、`.github/workflows/deploy.yml` 1；另有脚本自身 usage 2 处。**历史引用约 25 处**（6 处 ADR、4 份 handoff、15 处 wayfinder 工单）按「ADR 是历史记录、正文不改」先例**不改**，只在 `AGENTS.md` 加一行旧名指针。
   **节奏 = 搭施工批次的车**：与断言扩展同 commit，CI 只跑一次；不单独做改名提交（单独改名等于为纯重命名付一次部署与一轮文档失真）。
4. **真实数据不锚精选清单**（同 0038 第 6 条）：只保留生产构建冒烟。
5. **纪律沿用**：每条断言变异检验（破坏实现→红→还原）+ 期望值独立字面量（不重算实现）；坏值用例走 `tests/fixtures/bad/` 的「构建必须失败 + 钉错误子串」既有机制。

**施工补记（2026-10-22 落地）**：① 坏值用例按本题④点名补齐两类——字符串与整数各一例（前者过、后者初版因 fixture 日期写成 2099 被 Hugo 的「未来内容不发布」规则整篇排除而假绿，已修正）。② 新增「全部入选 → 网格整块不渲染」断言（0037 第 1 条的边界，评审补上）。③ 解析函数按标题锚定精选区块，不取「第一个 mf-rows」——产品精选区同用该 class，0 篇 featured 时会把空态断言变成假红。④ 每条新断言均过变异检验。
