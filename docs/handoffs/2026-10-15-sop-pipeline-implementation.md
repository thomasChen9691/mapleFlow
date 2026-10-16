# 交接：SOP 发布管线实现（2026-10-15 夜场）

## 当前状态

- 候选 2「SOP 真源与发布管线」的已裁范围继续推进：工单 0010/0011/0012 全部 closed，本地 `main` 现有 13 个 commit（`2597727` → `e4a739e`），**全部未 push**（ahead of origin 53 个；push 仍卡 CJK commit message 重写待批准）。
- 双测试套件全绿：`tests/assert_sop_pipeline.py` 100/100、`tests/assert_product_states.py` 14/14。CI 双断言步在位。
- **backend 已退役**（0011，`e2de031` + 文档补齐 `e4a739e`）：零消费者 + 两份历史审计建议 + 适配器化后 glob 静默 10→4 篇。ADR-0003 加状态标注（语义有效、对象已不在）。AGENTS.md/CLAUDE.md 后端章节已删并重编号（纪律节 9→8 / 7→6）。
- 0012 落档：导语↔定位段复制对接受为设计（双受众双文本），README 已补笔记结构约定 + 「改定位段时 review 导语」约定。
- wayfinder 地图 `map-sop-source-sync`：0007-0012 closed，雾区清空。**当前 frontier = 0013（测试缝形状）与 0014（命名与导航契约，收口）**。

## 下一步

1. **工单 0013（frontier）**：测试缝正式落档——契约断言集、fixture 双构建、CI 权威本地 advisory 策略均已实现（0010 落了 categories 契约），实质是确认性落档。
2. **工单 0014（frontier，收口）**：命名（候选已收敛为「SOP 发布管线」）、CONTEXT.md 术语条目（源笔记定义预计无需改写）、**ADR-0005 是否记录**、以及对实现期提前落地的 AGENTS.md 文档同步做 ratify/adjust（review 曾判越权、方向无害）。0014 关闭 = 目的地到达，地图标记 closed。
3. **遗留地雷（移交 F10）**：`docs/sop/MAPLEFLOW_BLOG_SOP.md` 仍教人启动已删除的 backend——按 0009 决议该文件整体移交 F10，未碰。
4. **push 与历史重写**：仍待用户批准 CJK commit message 重写方案；未批准前所有新 commit 只进本地。
5. **本会话教训（已应验两次）**：Bash 链式命令的显示层会出幽灵（假「no changes added」、`§` 字符损坏）——提交后必须 `git show --stat` 独立验证内容，`2>/dev/null` 会吞掉 staging 失败（`e2de031` 只说没做，靠 `e4a739e` 补）。

## 建议 skill

- **realeng-tdd** — 继续任何新行为（0011 backend 路由若要施工，先红后绿）。
- **realeng-code-review** — 每批结束跑双轴（固定点取上一批首个 commit）。
- **realeng-grilling** — 0010-0014 进 frontier 时一次一问，先给推荐答案。
- **realeng-domain-modeling** — 0014 定名「SOP 发布管线」若 ratified，当场进 CONTEXT.md。
