# 后续待完成清单（2026-10-23）

> **范围**：技术 / 文档 / 流程侧可动项。卡外部输入的内容填充按要求**暂不纳入**（见文末「暂不纳入」一行）。
> **进度（2026-10-23）**：第 1-10、14、15 项**已完成**；第 11 项**已决「不重写」**（仅渲染层按需改）；第 12 项**已完成**（候选 12 收口：`docs/wayfinder/map-search-entry.md` 六票全 closed，决策耐久化于 ADR-0011，施工三批落地，当前实测三套 87/29/104 全绿）；第 13 项挂起，16、17 项为风险登记（无需动作）。候选 12 三批提交（`261b17b` / `3f1aee3` / 收口批）在本地 main **未推**（GitHub 连接器 auth-required，待负责人恢复后推送并过 CI）；本图交接见 `docs/handoffs/2026-10-23-search-entry.md`，backlog 清理批交接（九笔已推、CI run 39881178618 全绿）见 `docs/handoffs/2026-10-23-backlog-cleanup.md`。验收：三套测试 76/76 / 104/104 / 16/16、构建零 WARN、导航 9 项不变。本批交接见 `docs/handoffs/2026-10-23-backlog-cleanup.md`。
> **基线（本清单生成时实测）**：`assert_site_contracts.py` 76/76 · `assert_sop_pipeline.py` 104/104 · `npm test` 16/16 · 生产构建 exit=0（3 条 Hugo 弃用警告）。
> **来源**：候选 8 两份交接（`docs/handoffs/2026-10-22-*.md`）、ADR-0001~0010 的边界段、七张地图的 Out of scope，以及本次对仓库的实测复核。

编号连续，可直接按号下指令。

---

## 一、立即（安全 / 隐私，1 项）

### 1. [已完成] `.workbuddy-ai/` 未进 .gitignore，而提交脚本用 `git add .`

- **证据**：`.gitignore:60-61` 忽略了 `.workbuddy/` 与 `.codebuddy/`，**没有** `.workbuddy-ai/`；`git status` 显示 `?? .workbuddy-ai/`；`auto_push.py:26` 是 `git add .`。
- **风险**：`.workbuddy-ai/memory/*.md` 是逐日工作笔记（含内部推理、环境坑点、后续计划）。仓库是公开的 GitHub Pages 源站，一次 `python3 auto_push.py` 就会把它们带进提交历史——**提交后清理需要改写历史**，成本远高于现在加一行。
- **动作**：`.gitignore` 在 `.workbuddy/` 旁加 `.workbuddy-ai/`。
- **验收**：`git status --short` 不再出现该项；`git check-ignore -v .workbuddy-ai` 有输出。

---

## 二、机械清理（低风险，可一批提交，4 项）

### 2. [已完成] 删脚手架文章 `content/posts/my-first-post1.md`

- **证据**：`draft = true`、`categories = ['随笔']`、`tags = ['Hugo','测试']`，是 2026-01 的显示验证文，从未上线。
- **动作**：`git rm` 该文件（非 SOP 文，不涉注册表）。
- **注意**：它不在生产构建里，但本地 `hugo server -D` 会生成 `categories/随笔/` 等草稿专属页——正是坑点 5b 的孤儿文件来源，删掉可消除一个踩坑入口。

### 3. [已完成] `deploy.yml` 注释两处失实

- **证据**：
  - `.github/workflows/deploy.yml:60` 枚举「产品状态 / 产品索引 / 主题契约 / reveal 产物 / 文章精选」**五类**，而套件头注释与 AGENTS.md §3 已是**七类**（+ 搜索索引投影 + 搜索交付面）。
  - 同文件 `:67` 写「golden **逐字节**比对」，而 ADR-0005 决策 7 明确是「按标签/属性/文本的 **token 序列**，以容忍 CI 0.164 / 本机 0.167 渲染差异」。
- **动作**：改注释，两处；不动流水线逻辑。交接文档已把它列为「下批顺手改，不单独烧 CI」。

### 4. [已完成] 清 3 条 Hugo 弃用警告（5 处调用点）

当前构建输出：

```
WARN deprecated: .Language.LanguageDirection … Use .Language.Direction instead   (v0.158.0 起)
WARN deprecated: .Language.LanguageCode      … Use .Language.Locale instead      (v0.158.0 起)
WARN deprecated: .Site.Data                  … Use hugo.Data instead             (v0.156.0 起)
```

- **调用点**：
  | 文件:行 | 现状 | 目标 |
  |---|---|---|
  | `themes/maplemod/layouts/_default/baseof.html:19,21,23` | `.Language.LanguageDirection` | `.Language.Direction` |
  | `themes/maplemod/layouts/partials/templates/opengraph.html:15` | `site.Language.LanguageCode` | `site.Language.Locale` |
  | `layouts/_default/rss.xml:30` | `site.Language.LanguageCode` | `site.Language.Locale` |
  | `layouts/_default/index.json:76` | `site.Data.products` | `hugo.Data.products` |
  | `layouts/index.html:58` | `site.Data.products` | `hugo.Data.products` |
- **连带**：`index.json` 文件头 docstring 的 26 行与 71 行写着「直读 site.Data.products」，该 docstring 是投影契约的**定义处**（ADR-0010），必须同步改，否则契约与代码分叉。
- **可行性**：三个替代 API 分别在 0.156 / 0.158 引入，CI 钉的 0.164 均可用；但仍需在 CI 上复验一次。
- **验收**：构建输出零 WARN；三套测试全绿。

### 5. [已完成] 删本地 `backend/__pycache__` 残留（可选）

- **证据**：`backend/` 已按 ADR-0003 退役且整目录在 `.gitignore` 内（`git status --ignored` 显示 `!! backend/`），但磁盘上仍有 `backend/__pycache__/blog_parser.cpython-313.pyc`。
- **动作**：删目录即可，不影响 git、不影响构建。纯卫生。

---

## 三、文档卫生（4 项，其中 2 项需先定口径）

### 6. [已完成] `docs/README.md` 整体失实，需重写

- **证据**：该索引仍以「后端 API 文档」为主体，指向 `BACKEND_DOCS.md`（**文件已不存在**）、`test_api.py`（**已删除**）、`../backend/`（**已退役**）；同时**完全没有** `adr/`、`wayfinder/`、`handoffs/`、SOP 管线——而这几处才是现在的决策与导航真源。按它走的读者（人或 AI）会直接掉进死路径。
- **动作**：重写为真实索引（adr / wayfinder / handoffs / sop / CHANGELOG 去留），删掉全部后端段落。
- **验收**：文内每个相对链接都能打开。

### 7. [已完成] `页面改版落地说明.md`（根目录，287 行）描述的是已废弃的行为

- **证据**：文中称「精选文章 = 最新 3 篇」「资源数 = `len site.Data.products`」「当前实测 10 篇 / 4 分类 / 5 资源」——三条都与现状冲突：精选已改由 `featured` 驱动（ADR-0009），资源数改为**可下载产品**计数（ADR-0004，当前 0 而非 5），首页两区已互斥。文件还放在仓库根目录，与 `docs/` 体系割裂。
- **动作**：二选一——删除；或移入 `docs/archive/` 并在文件头标注「历史记录，现行行为见 ADR-0004/0009」。**建议删除**：它记录的每一条现行版本都已由 ADR 覆盖，留档价值低于误导成本。
- **注**：候选 8 的 code review 已抓到「文档记着已删机制」，指的就是这份。

### 8. [已完成] `docs/CHANGELOG.md` 停更 7 天，且含一处失实（停维护）

- **证据**：最后条目是 2026-10-16，候选 7（精选机制）与候选 8（搜索契约）均未记录；10-16 条目里写「页面与迁移前**逐字节**一致（golden 断言）」，与 ADR-0005 的 token 序列比对不符。
- **需决策**：CHANGELOG 还维不维护？
  - 维护 → 补 10-17~10-22 三条（可按 handoff 摘要压缩），并改掉「逐字节」措辞；
  - 停维护 → 文件头加一行「本文件已冻结于 2026-10-16，此后变更见 `docs/handoffs/` 与 `docs/adr/`」，同时把 `docs/README.md` 与 `openspec` 提案里「更新 CHANGELOG」的约定一并撤掉。
- **判断依据**：现在的变更记录实际由 handoff + ADR 承担，CHANGELOG 是第三份重复账本——重复账本必然漂移（ADR-0004 枪毙「第二实现」的同一逻辑）。**我倾向停维护**。

### 9. [已完成] `openspec/` 是否退役（已退役）

- **证据**：`openspec/config.yaml` 是未填写的空模板；唯一的 change `summarize-today-updates/proposal.md` 是 2026-01-29 的产物，通篇讲已退役的 FastAPI 后端、已删除的 `BACKEND_DOCS.md`、以及「用 OpenSpec 管理项目」的旧工作流。全仓对 openspec 的引用只出现在这几份失实文档里，AGENTS.md 完全未提。
- **需决策**：项目追踪已由 `docs/wayfinder/`（地图 + 工单 + frontier）承接，OpenSpec 事实上已被取代。
  - 退役 → 删 `openspec/` 与 `docs/OPENSPEC_GUIDE.md`，清理引用；
  - 保留 → 说明它现在负责什么，否则就是第二个「静默腐化源」。

---

## 四、需决策的功能项（各需一张新图 / 一条 ADR，5 项）

### 10. [已完成] 菜单 4 个 `parent = "categories"` 子项配置了但不渲染（判定为死配置，已删）

- **证据**：`hugo.toml` 有 14 条 `[[menu.main]]`，其中 `ops`/`k8s`/`docker`/`aiops` 四条带 `parent = "categories"`；`themes/maplemod/layouts/partials/header.html:85` 直接 `range site.Menus.main`，构建产物导航实为 9 项（首页/文章/分类/标签/关于/搜索/产品/GitHub/Email），四个子项不出现。
- **性质**：这是**功能决定**（做下拉菜单？还是把分类入口移到分类页？），ADR-0008 明确「要渲染是功能决定，另开图」。当前配置是死的，容易让后来者误以为有下拉。

### 11. [已决：不重写] fastsearch 重写（三块面，ADR-0010 已划出）

- **范围**：① 结果呈现深化（摘要 / 标签 / 命中高亮）；② 引擎形态（ESM 模块化，fuse 与 license 依存）；③ 索引加载失败的容错 UX（现状是 XHR / JSON.parse 静默失效）。
- **前置输入**：ADR-0010 的快照契约（`themes/maplemod/assets/js/fastsearch.js` 文件头 docstring）就是新引擎的接口基线；新测试与新契约一起 TDD 出生（ADR-0010 决策 5 已否掉为遗留快照立 jsdom 套件）。
- **注意**：重写时「改投影字段 = 三处同步」的锚点会随移，投影 docstring 里的 fastsearch 接口条款要一起改。

### 12. [已完成] 搜索入口形态（新功能，项目负责人 2026-10-23 提出）

- **候选**：快捷键唤起（现在只有 search 页内的 Alt + /）、首页常驻搜索框。地图明确列为「新功能方向，不属现状治理」。
- **闭环**：候选 12 排图于 `docs/wayfinder/map-search-entry.md`（工单 0049-0054 全 closed），决策耐久化于 **ADR-0011**：全站 `/` 快捷键轻形态（跳转 search 页 + 聚焦，入口只路由、不构成第二个消费方）+ 结果摘要渲染（`item.summary`）+ 三协议并列互指 + 测试缝（assert_search.mjs 13 行为 + 产物断言 + 所有权分层原则）。施工三批：入口（`261b17b`）/ 呈现与契约（`3f1aee3`）/ 收口（本批）。遗留三条雾区（移动端 / aria / 浮层空间）随地图挂起，触发条件见地图注记。

### 13. [排图中] 精选机制三条雾区（ADR-0009 未决）

- ①「精选」徽标在内容层是否呈现（文章页 / 列表页 / 卡片视觉区分）；
- ② 首页数据条是否区分精选（「N 篇技术文章」是否另加「精选 N 篇」）；
- ③ 分类页 / 标签页是否消费精选（排序是否 featured 优先）。
- **性质**：① 紧邻视觉层（视觉调值本身 out of scope）；②③ 是编排策略。三者都要先定目的地再动工。
- **排图（2026-10-23）**：地图 `docs/wayfinder/map-featured-fog-zones.md` 已开，工单 0055-0060 已建；事实底座工单 0055 已决（`research/0055-featured-fog-facts.md`，缺口 8 条）。
- **质询（2026-10-23，项目负责人七问全决）**：**0056 做**——精选标识进三面（文章页 / 列表卡片 / 首页网格，精选行不加），契约 = 主题层新 partial `featured-badge.html`（docstring 定义处、三处调用、复刻 post_meta 先例），fixture 三面全锚 + 变异检验、真实不锚；**0057 不做**（负向：数据条维持站点总量口径，抽象层不分层 / 信息冗余 / 断言经济学）；**0058 不做**（负向：分类/标签/posts 维持日期倒序）+ seam 边界 docstring 收紧（落地归 0059）。
- **当前 frontier**：0059（收口：术语/导航/ADR 耐久化 + 0058 转入的 docstring 收紧）/ 0060（meta 层是否投影精选，0056 毕业后新开）。施工（partial + 三处调用 + 断言）待项目负责人指示后展开。

### 14. [已完成] 「后端重启」口径待澄清（ADR-0003 与 ADR-0006 冲突）——已加指针行

- **证据**：ADR-0003（2026-10-16）判定 `backend/` **全套退役**；ADR-0006（2026-10-19）的 Consequences 却写「后端重启（项目负责人 2026-10-19 计划）时，产品数据源替换只动数据准备 seam 一处」。两份 ADR 对「后端还要不要回来」给出相反暗示，且 10-19 的「计划」没有任何 ADR 承载。
- **动作**：二选一——若重启计划仍有效，补一条 ADR 说明边界（产品域是否进后端、部署形态）；若已放弃，给 ADR-0006 加一行指针（ADR 正文不改，加指针是本项目既有做法）。
- **影响面**：只影响「产品数据源替换」这一条未来路径，不影响当前任何代码。

---

## 五、风险登记（不是待办，但需要盯，3 项）

### 15. [已完成] Hugo 版本 skew：CI 0.164.0 / 本机 0.167.0

- **证据**：`deploy.yml:31` 钉 `0.164.0`；本机 `hugo v0.167.0`。ADR-0004 已记录过实际后果——「0.166+ 的条件多 return 写法**本地过、CI 红**」。
- **风险类别**：本地全绿 ≠ CI 全绿，且失败出现在部署前最后一步。
- **选项**：（a）本机钉 0.164（`.hugo-version` / mise），保持与 CI 同版；（b）CI 升到 0.167 并重跑全套 + golden 复验。**建议 (a)**：CI 是权威，本机应服从，升级是独立议题。

### 16. `goldmark.renderer.unsafe = true`

- **状态**：当前无风险（评论系统全注释）。**前置条件已明确**：将来启用评论，必须先关闭 `unsafe` 或对用户内容做净化，否则构成 XSS 入口。

### 17. 搜索的已知静默失效面

- **状态**：ADR-0010 已把能加牙的都加了（坏产品字段 errorf、keys 对齐断言、交付面产物断言、单副本守门），**XHR 失败 / JSON.parse 失败仍静默**，记录为已知限制、不承诺修复——处理时点绑定第 11 项（重写）。

---

## 建议执行顺序

1. **第 1 项**（一行改动，防隐私外泄）→ 单独提交。
2. **第 2-5 项**（机械清理）→ 合成一批提交，跑三套测试 + 构建零 WARN 验收。
3. **第 6-9 项**（文档卫生）→ 先定 8、9 两个口径，再一次性重写/归档，避免改两遍。
4. **第 10-14 项**（功能决策）→ 每项先排地图（realeng-wayfinder：目的地先行、工单是待决策问题、一会话一工单），不要直接动手。
5. **第 15 项**（版本 skew）→ 与下一批施工同批处理，本机钉版即可。

---

## 暂不纳入（按要求搁置）

卡外部输入的内容填充，**本轮不排期**：`data/products.yaml` 的 `buy_url` 填空 + `listed` 翻 true（需面包多真实商品页）、`content/about.md` 真实简历、`hugo.toml` 的 `socialIcons` 邮箱（现为 `test@example.com`）。三项都已由 ADR-0009/0010 与七张地图的 Out of scope 明确记为「卡用户材料，不随图」，不会丢。
