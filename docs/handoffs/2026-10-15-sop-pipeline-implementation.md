# 交接：SOP 发布管线实现（2026-10-15 夜场）

## 当前状态

- 候选 2「SOP 真源与发布管线」的**已裁范围全部施工完毕**：6 个红绿循环 + 评审修复，共 6 个 commit 在本地 `main`（`2597727` → `38f205e`），**全部未 push**（本地 ahead of origin 38+6=44 个 commit；push 仍卡在上一场的 CJK commit message 重写待批准）。
- 双测试套件全绿：`tests/assert_sop_pipeline.py` 99/99、`tests/assert_product_states.py` 14/14。CI 已接线（deploy.yml build 后跑两套断言，失败阻断部署）。
- 管线形态：seam = `content/posts/_content.gotmpl`（注册表驱动 + errorf 契约四类 + draft 透传）；数据 = `data/sop.yaml`（6 条目）+ `docs/sop/*.md` 源笔记；正文变换三规则（剥 H1 / 剥单行定位段 / 前置导语）。6 篇线上页面与迁移前**逐字节一致**（golden 断言）。
- realeng-code-review 双轴已跑（固定点 2597727）并全部修复（`38f205e`）。最重两条：`os.ReadFile` 对缺失文件静默返回空串（死条目契约失效，已改显式 `os.FileExists`）；golden 缺失硬红会阻塞新增 SOP 流程（已改为迁移条目专用 + 新条目走结构断言）。
- wayfinder 地图 `map-sop-source-sync`：0007-0009 closed；**当前 frontier = 0010**（0011←0010；0012←0008+0010；0013←0012；0014←0013）。0010-0014 的 body 均有「预裁记录」——进 frontier 后是正式落档，不是重新决策。

## 下一步

1. **工单 0010（frontier）**：SOP 文派生机制的正式落档——核心已在 0008 质询裁完（adapters + URL 冻结 + 注册表 + H1 提取），剩余只是文档化 + 确认（slug 唯一由注册表给、正文变换顺序、categories/tags 缺省、ref 尖峰结论）。
2. **0014 的越界裁定**：AGENTS.md 坑点 10 + 速查表三行是实现期提前落地的（review 判越权、方向无害），0014 进 frontier 时做 ratify/adjust；ADR-0005 是否记录也在 0014。
3. **0011 之前不动 backend**：两份历史审计已判 backend 死代码，但删除/改道是 0011 的决策，此前只观察。
4. **push 与历史重写**：仍待用户批准 CJK commit message 重写方案（backup + cherry-pick replay + 树哈希双验）；未批准前所有新 commit 只进本地。

## 建议 skill

- **realeng-tdd** — 继续任何新行为（0011 backend 路由若要施工，先红后绿）。
- **realeng-code-review** — 每批结束跑双轴（固定点取上一批首个 commit）。
- **realeng-grilling** — 0010-0014 进 frontier 时一次一问，先给推荐答案。
- **realeng-domain-modeling** — 0014 定名「SOP 发布管线」若 ratified，当场进 CONTEXT.md。
