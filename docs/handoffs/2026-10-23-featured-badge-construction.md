# 交接：候选 13 施工批——精选标识三面落地（ADR-0012 决策 2，本地已提交待推）

> 本文只记本批终态与去向。决策全文在 ADR-0012 与工单 0056 Resolution；本图收口交接（决策面）见 `docs/handoffs/2026-10-23-featured-fog-zones-closure.md`。

## 当前状态

- **施工批完成**（项目负责人 2026-10-23 指示展开）：`themes/maplemod/layouts/partials/featured-badge.html`（契约定义处，docstring 四要素：class/title/谓词/调用面清单）+ 三处调用点（主题层 `single.html` 文章页 / 主题层 `list.html` 列表卡片 / 站点层 `index.html` 首页网格，均传页面上下文、单一标记实现、无内联拷贝）；**首页精选行按决议不加**（负向断言守门）。
- **TDD 四轮红绿**（一次一行为，垂直切片）：① 文章页——红（4 篇 featured 缺徽标）→ partial + single 调用 → 绿；② 列表卡片——红（分类页 /`/posts/` 缺）→ list 调用 → 绿；③ 首页网格——红（截断回落的 feat-a 缺）→ index 调用 → 绿（负向守门牙同轮落，天然绿）；④ 变异检验 **5/5 捕获**（M1 去谓词 → 4 条负向检查红；M2/M3/M4 分别去三个调用点 → 各面正向检查红；M5 往精选行误植 → 负向检查红）。
- **code-review 双轴**（固定点 `c57a718`）：**Standards 零硬违规**（3 判断项：index 调用点 trim 标记不一致 / ④ 区块提取与 `parse_home_featured_slugs` 复刻 / docstring 称「分类/标签页」而断言只跑分类页）；**Spec 忠实实现、零缺失、零 scope creep**。三个判断项提交前全部处理：trim 统一为 `{{-`、抽 `parse_home_featured_block` 共享辅助、补标签页断言（实现与 docstring 自此一致）。
- **验证**：三套测试全绿——`assert_site_contracts.py` **99/99**（徽标 11 条：fixture 三面全锚 + 精选行负向；真实构建不锚）、`assert_sop_pipeline.py` 104/104、`npm test` 16+13；生产构建零 WARN、无 localhost 残留；真实站点抽查符合决议：featured 文章页 1 枚、`/posts/` 页 1（六篇中一篇 featured）恰 1 枚、首页网格 0 枚（3 篇 featured 全在精选区、补集无 featured）、精选行 0 枚。
- **提交**：本批与本文同提交（`feat: featured badge on article, list and home grid surfaces (ADR-0012)`），**本地未推**——GitHub 连接器 auth-required；连同既有六批（候选 12 三批 + 候选 13 三批）待负责人恢复后推送过 CI。

## 下一步

1. **推送并过 CI**（负责人恢复连接后）：徽标断言是 fixture 产物断言，不涉 Hugo 版本 skew 面；预期全绿。
2. **视觉层跟进**：`.mf-featured` 当前无任何样式（无样式行内文本「精选」）——ADR-0012 边界明示视觉值归视觉层；DOM 契约（class / title）已齐，视觉批只加样式、不动结构。
3. **backlog 剩余**：第 11 项（fastsearch 重写）长期挂起；内容填充三项（buy_url/listed、about.md、socialIcons）卡用户材料。

## 环境注意（本批新踩）

- 本 shell `sed -i ''` 对含 `|` 分隔符与中文的脚本报「No such file or directory」且**不报错退出**（害出一次假绿）——文件改写用 Python `pathlib` 替代，变异与恢复都走它。
