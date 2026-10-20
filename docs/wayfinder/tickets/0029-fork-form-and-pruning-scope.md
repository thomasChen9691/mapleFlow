---
id: 0029
title: fork 形态与修剪范围
type: grilling
mode: HITL
status: closed
blocked_by: [0027, 0028]
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

候选 6 的主干决策：fork 的**形态**与**修剪范围**。0027/0028 的事实底坐已齐（研究结论见两工单 Resolution）。

待决问题（一次会话内按序过，先给推荐答案）：

1. **形态三选一**：
   - A. vendored 到原目录 `themes/PaperMod`（`theme = "PaperMod"` 不变，构建零配置改动）；
   - B. vendored + 改名自研目录（如 `themes/maplemod`，hugo.toml theme 字段同步改——0028 证实官方要求名目录绑定）；
   - C. Hugo Modules 指向 fork 仓库（`module.imports`，go.mod/go.sum 版本化，themes/ 不留文件）。
   考量：AI 可导航（文件在仓内即可导航——A/B 等价，C 仍需网络拉取）、本地/CI 构建链路改动面、未来升级机制。
2. **修剪范围**：
   - A. 机械全量（116 文件原样入库：含 16 个不可达 partial、6 个零引用短代码、archives 模板、悬空 google_analytics 引用、全量 i18n）；
   - B. 按可达性修剪（只留 9 个可达 partial 链 + 站点实际经过的模板，其余删）；
   - C. 中间态（文件全留，但在主题内 README/注释标注不可达面，留待后续工单处理）。
   考量：与上游跟随意愿的耦合（0028：上游领先 92 提交——修剪越大，将来若想 merge 越难）、删除的即时收益（导航面缩小）vs 风险（误删只在特定配置下可达的面）。
3. **CRLF 行尾治理**：当前子模块 116 文件 dirty 全是 CRLF（0027 实锤）。fork 入库是天然的行尾治理窗口——随本次统一转 LF，还是维持原样只做 gitlink 摘除？
4. **死配置清理是否随图**：0027 盘点出 8+ 个主题零读取参数（avatar/stickyNav/reorderNavItems/showTableOfContents 等）。随 fork 一并清理（改 hugo.toml），还是留作独立小改不在本图决策？

决策记录：本题 Resolution 落形态选择（A/B/C）+ 修剪档位 + 行尾策略 + 死配置归属，并写明对 0030（分层）与 0033（上游关系）的约束。

## Resolution

2026-10-20 · grilling（五问全决，用户为决策者；施工已获项目负责人指示展开，按 realeng-tdd 红绿循环实施，一次一行为一 commit）：

1. **形态**：vendored + 改名第一方（A 原名 / C Modules 均排除——C 需 fork 独立仓库 + 网络拉取，与目的地「仓内文件、AI 可导航」直接冲突）。目录 **`themes/maplemod`**，`hugo.toml` 改 `theme = "maplemod"`（0028：官方要求 theme 名与目录名绑定，机械成本一行配置）。
2. **修剪：删死面档**。入库：`_default/` 的 baseof/single/list/terms/search/404/index.json/rss.xml + `_markup/render-image` + 13 个可达 partial（head/header/footer/extend_head/extend_footer/post_meta/author/anchored_headings/cover/templates/opengraph/twitter_cards/schema_json/_funcs/get-page-images）+ assets 全量（视觉层不碰）+ `i18n/zh.yaml`（单语言站；可达模板引用的 6 个键全覆盖）+ LICENSE/README/theme.toml/go.mod/images。删除：12 个不可达 partial（breadcrumbs/comments/edit_post/post_canonical/post_nav_links/share_icons/toc/translation_list/home_info/index_profile/social_icons/svg）、6 个零引用短代码、`archives.html`、`robots.txt` 模板、`.github/`、39 个非 zh i18n。明确保留：head.html 的 google_analytics 调用（CI 0.164 绿色实证容忍，零成本钩子）与 cover.html（可达、front matter 可激活）。**修剪必须同删调用点**（死 partial 的守卫块留在可达模板里是特性地雷）。
3. **行尾**：复用现有 `.gitattributes`（`* text=auto eol=lf`，2026-10-10 已立）——fork add 时 CRLF 自动归一为落入 index；不新增规则；施工验证 = add 后 index 无整目录行尾 diff + status 干净（子模块 CRLF 噪音的根因就是子模块不受主仓 .gitattributes 管辖，fork 天然消灭该类问题）。
4. **死配置**：随 fork 同批清理、**独立 commit**——删 0027 §5 清单（施工时对 maplemod 重新 grep 取证，修剪后读取点只会更死不会复活）；键名错配组（showTableOfContents/showPrevNextPost 等）按删除处理并明确「这些功能从未生效」；不借机开任何功能。
5. **深化后模块形状**：站点层（layouts/：product-* 三 seam + shortcode + index.html，覆盖文件去留归 0030）压 maplemod 之上；hugo.toml 只留 maplemod 真实读取的参数。隐性契约（归 0030-0033 处置）：dev/prod 双生产守卫是设计非 bug；extend_head/extend_footer 的上游用户钩子模式在 fork 后关系重定义；i18n 收缩到 zh.yaml 后单语言成为显式契约；fork 首提交是全量上游快照，删除物可从 git 历史恢复。
6. **测试存活面**：三套件与 CI 对主题名零引用（grep 实证），机制上全部存活（npm test 不经 Hugo；两 python 套件经 hugo.toml 构建、golden 用生产命令）；「存活」不等于「验过」——验收判据（三套件 + 生产构建 + localhost 零残留）归 0031。0032 的 9 处零断言锚点不因本决定改变。

**对下游的约束**：0030 分层边界已固定（近逐字覆盖 4+1 个、语义重写 2 个）；0031 触点清单已固定（deploy.yml `submodules: true` 可删、构建命令不改、验收含 LF 归一验证）；0033 已被修剪决策收窄（删了 20 个文件后跟上游意愿实质降低，是其强输入）。

**本题关闭。** 施工（fork 导入 / 改名 / 修剪 / 死配置清理）按项目负责人指示于同场展开，红绿记录见 git log。

**施工订正（2026-10-20 双轴评审后）**：① 非 zh i18n 实际 **45 个**（上游 46 − zh.yaml；决议所记 39 为排图期误计，删除范围不变）；② 6 个零引用短代码在首轮施工漏删，经双轴评审（Standards/Spec 同锤）于评审修复提交补齐——修剪承诺以「文件系统实际状态」为准，不以 commit message 记账为准。
