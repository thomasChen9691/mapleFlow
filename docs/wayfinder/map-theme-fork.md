---
id: map-theme-fork
title: 主题 fork 图（候选 6）
labels: [wayfinder:map]
status: open
created: 2026-10-20
---

# 主题 fork 图（候选 6）

## Destination

候选 6「主题 fork」的决策集定稿：themes/PaperMod 从外挂 git 子模块转为仓内第一方主题（或经 0029 裁定的其他形态）的全部待决问题——fork 形态与修剪范围、分层契约（四个近逐字覆盖 + 两个语义重写 + net-new 的归属）、子模块退役与构建链触点、主题层「可测试」的缝、命名 / AI 导航契约 / 上游关系与许可。达到「可测试、AI 可导航」的可施工状态即收口。本图只产决策；施工按候选 5 先例，经项目负责人指示后展开。

## Notes

- **边界（开图时与项目负责人钉死）**：候选 6 = 主题层整体处置（fork 形态、修剪、分层、测试、导航、上游关系）。不改搜索 JS（fastsearch）与 index.json 投影细节（归候选 8）；不改视觉/CSS 参数；不动内容填充。
- 领域词汇以根目录 `CONTEXT.md` 为准；讨论敲定的新术语当场写入 `CONTEXT.md`，不攒批。
- 闭卷 ADR：0001（生产构建固定命令）、0002（no-js 渐进增强基线——基线机制不重开，本图只处理其两个覆盖文件的归属与同步义务之关闭；0027 实测同步义务实为 4 个文件）、0004（产品状态模块）、0005（SOP 发布管线）、0006（产品索引双 seam）、0007（reveal 协议）。
- Hugo 0.164 语义编写（CI 钉版）：本机 0.167 与 CI 之间存在不对称 skew，0.166+ 的条件多 return 写法本地过、CI 红，禁止。
- 测试总原则：Hugo 生态无模板单测机制，静态产物只能 build-then-assert；JS 行为测试走 node harness（CI 权威）；fixture 基建单份，拆脚本 = 第二实现必然漂移（ADR-0004/0006 枪毙模式）；变异检验 + 期望值独立字面量两条纪律沿用（ADR-0007 先例）。
- 事实底座：`research/0027`（本地盘点：116 文件 dirty 实锤纯 CRLF、9/25 partial 可达、archives 与 6 短代码不可达、4 个近逐字覆盖、主题行为零断言 9 处、hugo.toml 死配置 8+、构建触点清单）与 `research/0028`（外部：钉住点落后 master 92 提交且上游活跃但 release 停 v8.0、themes/ 下普通目录与子模块构建等价、改名须同步 hugo.toml、MIT 最低义务=保留 LICENSE+版权行且无强制署名、官方无 fork 跟上游专指南）。后续工单的事实争辩以这两份为准，不重新推导。
- 用户是项目负责人：术语敲定与 ADR 是否记录由用户拍板。质询一次一问，先给推荐答案。能查到的**事实**自己查（文件 / 子代理），只有**决策**问用户。HITL 工单必须与用户实时对话解决，agent 不得自答。
- 背景证据：候选枚举源自 2026-10-15 架构评审（临时 HTML 已清理，1/2/4/5 已成图闭环、3 随后端退役消解、7 ratified 未开工）；候选 4/5 地图 Out of scope 均注明「主题 fork 独立成图」；候选 5 地图原注「ADR-0002 的两个覆盖文件同步义务不随本图重开」——本图接管该义务。
- 排图日 2026-10-20：两张研究工单（0027/0028）开图当日并行解决，事实落 `research/`，本图只留 gist。

## Decisions so far

- [主题 fork 事实底座（本地盘点）](tickets/0027-theme-fork-facts.md) — gitlink 干净、116 文件 dirty 实锤纯 CRLF；9/25 partial 可达、16/25 不可达、archives 模板与 6 个短代码不可达、robots.txt 被 static/ 遮蔽、head.html:201 悬空引用 google_analytics；站点 4 个近逐字覆盖（baseof/post_meta/extend_head/extend_footer，opengraph 亦近逐字）+ rss.xml/index.json 语义重写 + index.html/product-* net-new，**ADR-0002 漏列 post_meta 与 opengraph 两个同步义务文件（实为 4 个）**；主题行为零断言 9 处（no-js 全站面、post_meta 时区回退不红、菜单/URL、RSS、404、list/taxonomy、search、dev-vs-prod 双守卫）；hugo.toml 死配置 8+（reorderNavItems 复核确认真不读）；构建触点清单（deploy.yml 1 处、AGENTS.md 5 处、README 5 处、.gitmodules、auto_push.py 无需改）。
- [上游与外部事实](tickets/0028-upstream-external-facts.md) — 钉住点 6c5a8f6（2026-01-09）落后 master 92 提交（上游 2026-10-18 仍活跃，release 停 v8.0/2024-11）；官方明示 theme 名须匹配 themes/ 目录名（改名必须同步 hugo.toml）；项目 layouts 对主题同名文件「项目最左、文件级优先」；themes/ 下普通目录即 vendored 主题、与子模块构建等价；vendor 化机械路径 = `git rm --cached` + 删 .gitmodules + add；actions/checkout 默认不拉子模块，移除后构建不依赖改 deploy.yml；MIT 最低义务=随附 LICENSE+版权行、无强制署名；官方无 fork 跟上游专指南（社区实践=upstream remote 按需 merge）。
- [fork 形态与修剪范围](tickets/0029-fork-form-and-pruning-scope.md) — vendored + 改名第一方：`themes/maplemod`，hugo.toml theme 同步改；删死面档（删 12 不可达 partial + 6 短代码 + archives/robots 模板 + .github + 45 i18n，同删守卫调用点；留 google_analytics 钩子与 cover；assets 不碰）；行尾复用现有 .gitattributes（add 时归一 + 验证）；死配置同批清理独立 commit（对 maplemod 重新 grep 取证，键名错配组明确「从未生效」；socialIcons 因 schema_json 读取而保留，修正 0027 误判）。施工已获指示，同场红绿循环展开。
- [分层契约：覆盖文件归并与站点层剩余](tickets/0030-layering-contract-overrides.md) — 合并入主题层（覆盖层消除，文件唯一）：5 个站点版搬进 maplemod（baseof/extend_head/extend_footer/post_meta/opengraph），rss.xml 与 index.json 留站点（内容策略/站点数据），两个主题死副本删除；站点层最终 7 文件，判据「因什么而变」；验证 = public/ 逐字节 diff 零差异 + 三套件 + 同路径不变量；ADR-0002 义务消失（实际涉 5 文件非 2），指针行由 0034 统一落。
- [子模块退役与构建链触点](tickets/0031-submodule-retirement-build-touchpoints.md) — `.git/modules` 10M 缓存保留（0033 期权，本地状态不进仓库）、历史 gitlink 不 rewrite；CI 删 `submodules: true` + `fetch-depth: 0`（.GitInfo 零使用）；文档触点表（AGENTS 5 处/README 3 处，坑点 6 删+顺延编号+改唯一交叉引用）；边界「0031 清子模块事实 / 0033 管命名导航」；验收 = 本地 5 条（构建+三套件、无子模块指令、无 gitlink 条目、LF 复验、localhost 零残留）+ CI 实证 push 后回填，本地绿即 closed。
- [主题层可测试的缝](tickets/0032-theme-test-seam.md) — 必锚 6 条（B7 no-js 全站 / B8 post_meta 时区 / B9 菜单 13 项与 URL / B10 RSS 仅 posts / B11 search DOM / B12 ogImage 兜底），5/6/9 不锚；落 `assert_product_states.py`（fixture 单份，命名债记账待第三类职责时改名）；golden 不收严（B8 提供牙口）；完整性只加同路径不变量、不建清单快照；逐条变异检验。
- [命名、AI 导航契约与上游关系](tickets/0033-naming-ai-nav-upstream.md) — CONTEXT.md 加概念级「主题层」条；原地重写 themes/maplemod/README.md（fork 点/保留修剪清单/分层契约/历史在旧路径/MIT）；AGENTS 坑点 3 改参数纪律、坑点 5 删+顺延、§7 加主题目录行；上游 **cut cord**（无 remote，删 10M 孤立缓存）；LICENSE 保留 + README 注 provenance、页脚不鸣谢；内部结构不重组、无再同步机制（雾区两条毕业）。

## Not yet specified

<!-- 空：0033 已使两条雾区毕业（内部结构不重组；cut cord 后无再同步机制）。frontier 仅剩 0034（收口：术语/导航/ADR-0008）。 -->

## Out of scope

- **站内搜索 JS（fastsearch）与 index.json 投影契约**：候选 8（0019/0026 已划界）。0027 盘到的 search.html 渲染零断言，其归属在本图 0032 以边界注记处理，细节归候选 8。
- **视觉 / CSS 参数调值**（时长、曲线、降级阈值）：视觉层（候选 5 地图先例）。
- **data/products.yaml 填充、about.md 简历、socialIcons 真实邮箱、脚手架文章删除**：卡用户材料，不随图（候选 5 先例）。
- **候选 7「精选机制」**（文章 featured 字段）：方向已裁决、另行开工。
- **后端重启时的产品数据源替换**：ADR-0006 已定，届时只动 product-items 一处。
- **Hugo 版本钉版（CI 0.164）与 skew 治理**：fork 与 Hugo 版本正交，不随本图升级。
