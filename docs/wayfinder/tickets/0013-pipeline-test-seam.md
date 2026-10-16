---
id: 0013
title: SOP 管线的测试缝形状
type: grilling
mode: HITL
status: closed
blocked_by: [0012]
assignee: agent
claimed: 2026-10-16
closed: 2026-10-16
map: map-sop-source-sync
---

## Question

管线落地后，断言什么、放哪、CI 怎么跑？

候选（可组合）：

- 每条源笔记都有对应渲染产物（防漏生成）；
- 渲染正文与源笔记归一化后相等（防漂移——这是「零同步」痛点的守门转化）；
- 无孤儿文章（有产物无真源，或反向）；
- 日期非零值回归（工单 0007 的 `dates` 陷阱：照抄文档示例会静默全零）；
- `--printPathWarnings` 守门（adapter 页与残留 .md 撞路径）；
- 双构建（fixture + 真实数据）是否必要——参照 ADR-0004「fixture 双构建覆盖全部分支 + 真实数据守线上回归」的既有范式是否需要照搬。

决策依据：ADR-0004 的测试哲学——契约执法在模块内（`errorf`，构建即门禁）+ 存活测试只以构建产物断言；Hugo 生态无模板单测（工单 0001 已证），一切断言只能是 build-then-assert；CI 权威 + 本地 advisory 的运行策略是否沿用。

## 预裁记录（工单 0008/0009 质询，2026-10-15）

测试集已裁（0008 决议第 4 条 + 0009 决议连带裁定）：构建期契约 4 类（死条目 / 无 H1 / 缺 date / 缺 slug）+ 产物断言 6 条（6 篇存在[URL 冻结回归]、标题==H1、日期非零、正文归一化比对、ref 解析、6 slug 无手写残留）+ README↔注册表双向一致 + fixture 双构建。进入 frontier 后只剩正式落档：脚本命名（`tests/assert_sop_pipeline.py`）、fixture 站点组织（临时目录 + dataDir 覆盖，对 ADR-0001 只做加法）、CI 断言步插入点。

## Resolution

2026-10-16 · grilling（用户为决策者）。测试缝形状正式落档——预裁集全部实现（100/100 绿），本题裁一项未决工作流 + 两项正式声明。

**落档的测试缝全貌**（`tests/assert_sop_pipeline.py`，CI 权威 + 本地 advisory，`--quick` 跳真实数据构建）：
- 构建期契约 5 类（`errorf`，失败即阻断）：缺必填字段（slug/note/date/categories，tags 可缺节）/ 死条目 / 笔记首行无 H1 / H1 之后无章节标题行。每类一个 fixture，断言「构建失败且错误含该契约子串」——钉死归因，不许因别的原因失败也绿灯。
- 产物断言（build-then-assert，期望值独立于实现）：6 个冻结 URL 在役；posts/ 页面集合 == 派生 slug + 手写非草稿文章（孤儿笔记零页面）；无手写 .md 残留；标题 == 源笔记 H1；日期非零且 == 注册表 date（独立格式化）；meta description == 注册表（Plumbing 回归）；结构三断言（导语在场 / 章节标题序列 == 笔记 / 笔记末行在场）——新条目不依赖 golden 同样受守。
- 迁移保真：6 个迁移条目的 `<article>`/title/meta 与 golden 逐字节一致（golden 出处与复验见 `tests/fixtures/sop-golden/README.md`）。
- 漂移与投影：README↔注册表双向一致 + MAPLEFLOW_BLOG_SOP 不发布标注；索引文章 ref 解析且目标已构建；搜索索引含全部派生条目。
- draft 行为：`draft: true` 不进生产构建、`-D` 出现。
- CI 守门：deploy.yml build 后跑本脚本，失败阻断部署；断言自身在任（CI wiring 断言）。

**本题新裁：golden 生命周期 = 独立捕获脚本**（工单 0013 质询，选项 A）。`tests/capture_sop_golden.py`（+ 共享抽取模块 `tests/sop_golden.py`，捕获与断言共用防规则漂移）：`--check` 只读校验陈旧、默认重捕获已有 golden、显式 slug 可新建。工作流：笔记合理修订 → 断言红 → 确认有意 → 捕获 → golden diff 进 PR review。**防线在可审的 diff，不在命令缺失**；明确否决「断言脚本内 --recapture」（验证与再生混入口，误跑即把回归洗成期望更新）。已验证幂等：未改动树上 `--check` 零 diff、重捕获零 diff。

**两项正式声明**：
1. **`--printPathWarnings` 不采用**——ADR-0001 固定构建命令只做加法，不给它加 flag；撞路径风险（adapter 页 vs 残留 .md）已由「无残留」断言直接覆盖，再加一道 flag 是重复守门。
2. **无双路径 fixture**——与产品状态模块不同，SOP 管线不设「好数据 fixture」：真实数据（6 篇在役）就是好路径，fixture 只承载坏输入与行为特例（draft）。真实数据构建 + 6 个坏 fixture + 1 个行为 fixture 即全覆盖。

**实施期订正（2026-10-16，CI 首红）**：迁移保真的比对由「逐字节」改为「规范化」（`tests/sop_golden.py: canonical` → 标签/属性/文本 token 序列）。原因：golden 由本机 0.167 渲染捕获，CI 用 0.164——渲染器版本差异（属性引号、空白、代码高亮写法）使逐字节比对在 CI 必红，与「CI 钉 0.164 / 本机 0.167」的既定政策冲突。规范化后仍抓一切真实变化（标签、属性值、文本），且噪声容忍已被受控样例验证。另：断言脚本新增 GitHub 工作流注解输出（`::error`），CI 失败项无需日志权限即可从 run 页读出。

**下游影响**：0014 解除阻塞进入 frontier（收口工单）。golden 捕获脚本已随本次落档实现（`tests/sop_golden.py` + `tests/capture_sop_golden.py`，README 已载明生命周期）。无新工单、无雾区。
