---
id: "0082"
title: 卡片单模块的测试缝与产物守门
type: grilling
mode: HITL
status: closed
blocked_by: ["0081"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-28
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

卡片单模块怎么被 build-then-assert 守住——「可测试」在 Hugo 模板侧的具体形态。现状：`tests/assert_site_contracts.py` 与 `tests/assert_reveal.mjs` 中**零处**引用 `post-entry` / `mf-post` / `entry-header`（排图日粗查），即卡片当前**没有产物契约**；收敛过程中若渲染错位，现有套件不会红。

要决策的面：

1. **断言什么**：结构契约（`article` 类名 + `header` / 摘要 / `footer` / `entry-link` 四段 + 顺序）、字段契约（标题、摘要截断、meta、徽标的有无）、还是**跨面等价**（同一篇文章在首页与列表页渲染出同一骨架）。
2. **用哪套件**：`assert_site_contracts.py` 的哪一类（现有十五类里新增第十六类，还是并入既有类）；是否需要 `assert_sop_pipeline.py` 侧同步（派生文也走卡片）。
3. **fixture**：现有 `content-posts` / `content-posts-all` / `content-posts-none` / `content-posts-bad` 是否够用；是否需要新 fixture 覆盖 `first-entry` 与 `hideMeta` / cover 分支（fixture 基建单份，不新开第四套构建）。
4. **变异口径**：破坏卡片模板的哪个分支 → 哪条断言红；给出可执行的变异清单（对照 ADR-0015 的「禁用类型检查 → 四条同红」）。
5. **等价性断言的强度**：0080 若选「结构等价」，断言钉到类名与段序即可，还是钉到字段集合；会不会与视觉调整频繁冲突（误红成本）。

边界（不开票）：视觉回归（截图 / 像素）不在本图（Hugo 侧无此基建）；搜索与 reveal 的行为断言不动（归 0084）。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，四问定案）。

**测试锚点下沉到语义**：现有 8 条锚类名的断言（`parse_card_badges` 三面 × 2 = 6 条 + 首页 `mf-post` × 2 条）改为锚 `entry-link`（整卡点击层，已是既有锚点）+ 结构（`article > header / entry-content / entry-footer`）；类名只在**一个常量**里出现一次；新增一条「卡片类名 ↔ 产物 CSS 有对应规则」断言，兜住「类名改了、CSS 没跟上」的视觉静默失效（同 `assert_featured_badge` ⑤ 的落地牙写法）。

排图日事实更正：**「现有断言零处引用卡片类名」是错的**（只扫了两个词、没扫 `parse_card_badges` 调用点）。真实情况是 8 条断言直接锚类名，`assert_post_grid_empty` 另锚 `mf-posts` 容器、`assert_theme_transition` 用正则锚 `.post-entry { --card-motion }`。

**断言归属 = 新增一类 `assert_post_card`**：卡片契约独立成类（site 套件第十六类），自带 fixture 构建，与 `assert_featured_badge` 的卡片解析抽公共 helper。代价 = 多一次 hugo 构建（`harness.build()` 无缓存）；换来的是一类一契约、失败定位准、可导航。

**fixture = 新建 `tests/fixtures/content-card/`**：四篇（普通 / featured / 带 cover / `hideMeta`），一套生产构建盖住**三个生产可达分支**。**草稿分支不测**——生产构建排除 draft，该分支只在 `hugo server -D` 下渲染，记为**已知限制**（不值得为本地预览再开一档 `-D` 构建）。不复用 `content-posts`：它被精选链 / 徽标 / 数据条计数多套断言共享，加文章会连锁改期望值。

**验收强度 = 三层**：
1. **结构契约**：`article > header / entry-content / entry-footer / entry-link` 四段 + 类名常量 + 「类名 ↔ 产物 CSS 有对应规则」落地牙；
2. **跨面等价**：同一 slug 在首页网格与 `/posts/` 列表渲染出的骨架逐段一致——**这是「单模块」唯一的直接证据**（首页与列表各自正确 ≠ 同一模块）；
3. **变异清单五条**：删 cover 调用 / 去 `hideMeta` 守卫 / 改类名 / 删 `entry-link` / 回退成两处内联渲染——每条必须至少让一条断言**可定位地红**（ADR-0015 决策 14「变异等价」同款口径）。

**施工（2026-10-28，PR①）**：新增 `assert_post_card`（site 套件第十六类）+ `tests/fixtures/content-card/`（plain / featured / cover / nometa 四篇，复用 posts 档位 + `--contentDir` 覆盖，未新开构建配置）；`parse_cards` 为卡片解析唯一实现，`parse_card_badges` 改为复用（评审指出两套切块并存后合并）；类名只走 `CARD_CLASS` 一个常量（含 `assert_theme_transition` 的正则也由常量构造）。

**断言清单（22 条）**：构建成功 1 · 四面渲染出卡片 4 · 四面类名 4 · 四面历史类名残留 4 · 三面骨架段序 3 · 跨面等价 1 · 徽标 1 · 父容器深度 3 · CSS 落地牙 1。另给 `assert_featured_badge` 补了 4 条「解析到卡片」前置——**反向断言在解析为空时会假绿**（实测 `grid={}` 时「不带徽标」通过），这是本轮抓到的真洞。

**变异检验（五条，全部可定位地红）**：删 cover 调用 → 1 条（cover 骨架）；去 `hideMeta` 守卫 → 1 条（nometa 骨架）；类名漂移 → 7 条；删 `entry-link` → 5 条；首页回退内联旧卡 → 4 条。

**未做**：像素级回归（Hugo 侧无此基建，Out of scope）。
