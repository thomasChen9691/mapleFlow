# 0008 - 主题 fork：第一方化、修剪与分层合并

**状态**：已批准（2026-10-20）。决策过程见 wayfinder 地图「主题 fork 图（候选 6）」（docs/wayfinder/map-theme-fork.md，八工单 0027~0034 全 closed）；本 ADR 是决策的耐久化记录——AGENTS.md §8.1 的阅读路由（CONTEXT.md + docs/adr/）不含 wayfinder 目录，决策必须活在 docs/adr/。基线见 ADR-0002（no-js 渐进增强），产品索引接口见 ADR-0006，reveal 协议见 ADR-0007。

## 决策

1. **形态**：PaperMod 从 git 子模块转为仓内第一方主题 `themes/maplemod`（vendored + 改名，`hugo.toml` 的 `theme` 同步改）。无子模块、无 `.gitmodules`、无上游同步义务——**cut cord**：不建 upstream remote，fork 点 `6c5a8f6`（`v8.0-55`，2026-01-09）记入主题 README。
2. **修剪（删死面）**：删 12 个不可达 partial（breadcrumbs/comments/edit_post/post_canonical/post_nav_links/share_icons/toc/translation_list/home_info/index_profile/social_icons/svg）、6 个零引用短代码、`archives.html`、`robots.txt` 模板、上游 `.github/`、45 个非中文 i18n；保留 13 个可达 partial 链、assets 全量、LICENSE/README/theme.toml/go.mod/images。**修剪必须同删调用点**——死 partial 的守卫块不得留在可达模板里（特性地雷）。
3. **分层契约**：站点层（仓库根 `layouts/`，7 文件：`index.html`、`_default/rss.xml`、`_default/index.json`、product-state/items/index 三 seam、`shortcodes/product-index.html`）＝内容与数据；主题层（`themes/maplemod/`）＝呈现与行为基线。判据「因什么而变」：视觉/骨架/交互 → 主题；内容策略/数据结构 → 站点。**两层不得存在同相对路径文件**（B13 断言）。5 个原站点覆盖文件并入主题（baseof/extend_head/extend_footer/post_meta/opengraph），2 个主题死副本删除（rss.xml/index.json 留站点）。
4. **子模块退役触点**：CI 删 `submodules: true` 与 `fetch-depth: 0`（`.GitInfo` 零使用）；AGENTS/README 清子模块指令（坑点 checkout 卡死整条删除、编号顺延）；`.git/modules` 缓存删除；历史 gitlink 不 rewrite。
5. **测试缝**：主题契约断言 B7-B13 并入 `tests/assert_product_states.py`（fixture 基建单份，不新建脚本——命名债记账）；golden 不收严（CI 0.164 / 本机 0.167 的渲染差异容错保留），post_meta 时区回归由 B8 独立断言提供牙口；**每条断言变异检验**（破坏实现→红→还原）。
6. **命名与术语**：主题名 `maplemod`；CONTEXT.md 增概念级「主题层」条（不载文件布局）；AGENTS 参数纪律（每个 hugo.toml 参数必须在 maplemod 有读取点，无读取点即死配置）；README 与 AGENTS 的 PaperMod 提及全部改为 maplemod（渊源表述保留在主题行、主题 README 与 CONTEXT `_Avoid_`）；LICENSE 保留（MIT），页脚不鸣谢。

## Considered Options

- **保留子模块**：导航与可测试性受制于外部仓库，同步义务永续——本图的起点即否定。
- **Hugo Modules 指向 fork 独立仓库**：文件不在仓内，AI 导航仍需另克隆——与目的地直接冲突，排除。
- **机械全量 vendored**：20 个永不执行的文件留在仓内，导航面未减——排除。
- **解散主题层（全部并入站点 `layouts/`）**：抹掉「呈现 vs 内容」的概念边界，且红笔画掉本图前提——排除。
- **保留双份覆盖（不合并）**：ADR-0002 的同步义务延续——排除。
- **golden 收严为单一时区形态**：会造成非行为原因的误红——排除，改用独立断言。

## Consequences

- 改主题 = 改 `themes/maplemod/`（无同步、无上游）；改内容/数据 = 改站点 `layouts/` 的 7 个文件之一。判据与目录导航见主题 README。
- ADR-0002 的「两个覆盖文件升级时同步」义务**随合并消失**；实际涉 **5 个文件**（baseof/extend_head/extend_footer/post_meta/opengraph），0002 原文记 2 个为漏记（正文不改，指针见 0002）。
- 主题行为由 B7-B13 守门：全站 no-js 基线、post_meta 显式时区、菜单渲染序（9 个顶层项）、RSS 只收 posts、search 页挂点、ogImage 兜底、站点/主题单副本不变量。改主题前先跑 `python3 tests/assert_product_states.py`。
- **历史提示**：五个合并文件的合并前历史在旧站点路径（`git log -- layouts/...`）；`git log --follow` 不穿过合并点（`git mv -f` 在目标已存在时不产生 rename）。查「为什么这样写」去旧路径。
- **边界**：搜索 JS（fastsearch）与 index.json 投影契约归候选 8；本图未动，代码里的 0019 边界注释继续有效。
- 菜单事实：hugo.toml 有 13 条 `menu.main`，但 `header.html` 只渲染顶层 9 项（4 个 `parent = "categories"` 子项不渲染）——既有行为，断言按渲染面锚定；子菜单是否渲染属新需求，另开。
- 许可：MIT，LICENSE 与两行上游版权保留；无强制署名，页脚不鸣谢。
- 主题内部结构保持上游布局（assets/css 分文件、partial 目录不重组）——无功能收益且保留与上游的对照性。
