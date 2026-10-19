# Research 0021 — reveal 面事实底座与 JS 可测试性事实

工单 0021 的事实底座（候选 5「reveal 协议」图，2026-10-19）。Part A 为仓库内盘点（行号对应当日文件状态）；Part B 为外部事实，全部对照 Hugo 0.164（CI 钉版 0.164.0 extended）核实，higher-version-only 行为已显式标注。未实证的点标「未验证」。

## Part A — reveal 面盘点（文件 × 行为 × 契约 × 测试覆盖）

### A1 契约点总表

| # | 契约点 | 产生者（写） | 消费者（读） | 位置 | 测试覆盖 |
|---|--------|-------------|-------------|------|---------|
| 1 | `<html class="no-js">`（含 dark/light/auto 三分支） | `layouts/_default/baseof.html:20-24` | CSS `.no-js .mf-rise` / `.no-js .reveal`；extend_head 脚本 | 主题覆盖文件（ADR-0002 义务：升级需同步） | **零** |
| 2 | head 内联 swap 脚本（no-js→js） | `layouts/partials/extend_head.html:9-15` | `<html>` classList | 主题覆盖文件 | **零** |
| 3 | `.mf-rise` + d1/d2/d3 延迟类 | `layouts/index.html:21-35`（手写 class） | `custom.css:184-195`（keyframes + delay） | 首页 hero 独有 | **零** |
| 4 | `.reveal` → `is-in` 滚动进场 | 写①：`extend_footer.html` IO 脚本（IntersectionObserver，rootMargin `0px 0px -6% 0px`，threshold 0.06，一次性 unobserve）；写②：`product-index.html:130` 筛选脚本（animate 时对可见条目直写 is-in） | `custom.css:199-207` | 两个写入方（首页/精选页 .reveal：index.html:82,157；产品页行：product-index.html:58） | **零** |
| 5 | 无 IO / 减弱动效降级：IO 缺席时全部直写 is-in | `extend_footer.html:12-15` | 同上 | footer 脚本 | **零** |
| 6 | 筛选按钮 `data-group`/`data-value` + `aria-pressed` | `product-index.html:38-44` | 脚本 `product-index.html:144-155`（点击切 state、同值回 all、组内互斥写 aria-pressed） | 产品页（filters=true） | **零**（仅 `mf-filter` 控件有无被断言，见 A2） |
| 7 | `is-hidden`（过滤隐藏）+ `.mf-row.is-hidden { display:none !important }` | 脚本 `product-index.html:123` | `custom.css:649` | 产品页 | **零** |
| 8 | `--mf-i` stagger 变量（min(shown,8)，CSS `animation-delay: calc(var(--mf-i,0)*22ms)`） | 脚本 `product-index.html:126` | `custom.css:216-219` | 产品页 | **零** |
| 9 | `is-morphing`（list 重播 mf-pop，520ms 后移除）+ `is-bump`（count 脉冲） | 脚本 `product-index.html:106-115,140-141`（replay 函数：remove→reflow→add） | `custom.css:212-226` | 产品页 | **零** |
| 10 | 计数 `.mf-count` 文案「显示 X / Y」+ `aria-live="polite"` | 脚本 `product-index.html:134` | 产品页 HTML | 产品页 | **零** |
| 11 | 空态「没有符合筛选条件的资源」`hidden` 切换 + 「暂无资源」空数据态 | 脚本 `product-index.html:135`；`product-index.html:31` | 产品页 | **零**（整体空态另有 0019 收口断言，不覆盖筛选空态） |
| 12 | `prefers-reduced-motion` 降级（三处）：CSS 媒体查询定格终态 + 两个脚本的 matchMedia 检查（footer 全量 is-in；筛选不播 morph） | `custom.css:228-247`；`extend_footer.html:11`；`product-index.html:100-102,139` | — | 分布三处 | **零** |
| 13 | 产品行 `data-kind` / `data-price`（筛选依据） | `product-index.html:58` | 脚本 `product-index.html:120-121` | 产品页 | 部分间接：`data-price` 产品状态断言覆盖（ADR-0004）；`data-kind` 无 |

### A2 测试覆盖现状（实测）

`tests/assert_product_states.py` 与 `tests/assert_sop_pipeline.py` 全文检索 `reveal / is-in / mf-rise / no-js / mf-count / is-hidden / aria-pressed`：**零命中**。唯一相邻断言是 `mf-filter` 控件有无（`assert_product_states.py:253-262`：产品页出、首页精选区不出——0019 决议的 filters 开关差异）。

结论：整个 reveal 面（除筛选控件存在性外）**没有任何行为或契约断言**；JS 行为发生在 Hugo 构建之外，build-then-assert 天然覆盖不到。

### A3 与已闭卷决策的接壤

- ADR-0002：no-js 基线与两个主题覆盖文件（baseof / extend_head）的义务已定，本图不重开。
- ADR-0006：`filters` 开关与 `uid` 挂点已归产品索引渲染 seam；reveal 图接管 UI 之下的行为层。shortcode  uid = `printf "mf-idx-%d" .Ordinal`（`layouts/shortcodes/product-index.html:15`），模板调用方传字面量（`layouts/index.html:110` 区）。
- 候选 4 地图雾区「客户端筛选脚本的重写边界」随本图毕业。

## Part B — 外部事实（对照 Hugo 0.164）

### B1 js.Build 在 0.164 可用，源码保持可单测形态

- **引入版本：v0.74.0**（2020-07-13 发布）。release notes 原文：「This release comes with native JavaScript bundling (and minifier), with import support (from node_modules etc.), tree shaking, scope hoisting for ES6 modules, transpilation of JSX and newer JS syntax down to ES6」，含提交 `2fc33807` "Add js.Build asset bundling"（实证：GitHub API 查 `tpl/js/js.go` 路径最早提交 2022-07-02。**注：早先记忆的 0.98/0.101/0.103 均被 release notes 实证否定**）。远早于 0.164 → 0.164 可用，无版本风险。
- 官方文档（gohugo.io/functions/js/build/）：esbuild 后端；options：`format`（默认 iife，适合 script 标签）、`targetPath`、`params`（模板传 JSON 给 JS）、`minify`（默认 **false**，独立于全局 --minify）、`sourceMap`、`target`（默认 esnext）、`shims`、`inject`、`externals`、`defines`、`drop`（0.144+）、`loaders`/`platform`/`sourcesContent`（0.140+）、`JSX`/`JSXImportSource`（0.124+）；`importContext`/`Data.Artifacts`（0.165+，0.164 无）、`charset`（0.168+，0.164 无）。0.164 需要的核心能力（bundle/minify/format/params/sourceMap）全部可用。
- 工作方式：`{{ with resources.Get "js/main.js" }}{{ with . | js.Build $opts }}<script src="{{ .RelPermalink }}"></script>{{ end }}{{ end }}`；生产可再 `| fingerprint` 带 integrity。**`assets/js/*.js` 源文件不被构建改写**（Pipes 读源文件、产出独立资源落 resources/_gen 或 publishdir）→ 源码保持「未被 minify 改写、可单独测试」的形态。
- 0.164 下其他官方机制：`resources.Copy`（仅拷贝，不 bundle）。无其他 JS 打包函数。

### B2 --minify 会改写 JS 产物

官方 minify 默认配置（gohugo.io/configuration/minify/）：`disableJS = false` → `--minify` 时 JS 被 tdewolff/minify 处理（`[minify.tdewolff.js] keepVarNames = false, precision = 0, version = 2022`）。即生产产物中的 JS 与源码字节不同（变量名/空白/精度）。对「以产物做 DOM 测试」的影响：脚本语义不变、可正常执行；**行为断言必须执行脚本而非匹配脚本文本**。HTML 侧仓库已知坑（minify 后属性无引号）同样适用。

### B3 Node DOM 行为测试可行（jsdom / happy-dom）

- 本机 Node v22.22.2；npm registry 可达（`registry.npmjs.org` 返回 jsdom 30.1.3 / happy-dom 21.0.3）。**本研究未安装任何包**——可行性结论基于包元数据与两者公开能力。
- jsdom：可加载 HTML 并执行 inline script（`runScripts: "dangerously"` + `resources: "usable"`）；提供 querySelector(All)、classList、dataset、setAttribute、`hidden`、click/dispatchEvent。`matchMedia` 与 `IntersectionObserver` 无有意义实现，需 stub——**本仓库脚本两者都有守卫**：extend_footer 的 `!('IntersectionObserver' in window)` 分支在 jsdom 中天然走「全量直写 is-in」终态路径；`matchMedia` 用 stub 控制即可测减弱动效分支。
- happy-dom：同类方案，自称 API 覆盖更广（含 IntersectionObserver stub，未验证）。
- CI 成本：`.github/workflows/deploy.yml` 为 `runs-on: ubuntu-latest` + peaceiris Hugo 0.164.0 extended + 两个 python3 断言步。GitHub ubuntu-latest 镜像预装 Node.js；增加一个 `node tests/assert_reveal_*.mjs` 步（或 actions/setup-node）是行数级增量。断言消费构建产物 → **与 Hugo 版本 skew 无关**（0.164/0.167 同在构建侧，harness 在产物侧）。

## Sources

- https://github.com/gohugoio/hugo/releases/tag/v0.74.0（js.Build 引入，2022-07-13；"native JavaScript bundling (and minifier)"）
- GitHub API commits?path=tpl/js/js.go（最早提交 2022-07-02 "Add js.Build asset bundling"）
- https://gohugo.io/functions/js/build/（options 与版本标记：0.124/0.140/0.144/0.165/0.168）
- https://gohugo.io/configuration/minify/（disableJS=false 默认；tdewolff js 配置）
- https://registry.npmjs.org/jsdom/latest（30.1.3）、https://registry.npmjs.org/happy-dom/latest（21.0.3）——仅元数据探测，未安装
- 仓库实证：layouts/_default/baseof.html、layouts/partials/extend_head.html、layouts/partials/extend_footer.html、layouts/partials/product-index.html、layouts/index.html、layouts/shortcodes/product-index.html、assets/css/extended/custom.css:178-247,649、tests/assert_product_states.py:253-262、tests/assert_sop_pipeline.py、.github/workflows/deploy.yml
- docs/adr/0002、docs/adr/0006；docs/wayfinder/map-product-index-narrowing.md 雾区

## Implications for the seam decision

- **三个脚本的两种归宿都有官方支撑**：留 inline（现状，零依赖）vs 提取 `assets/js/` + js.Build（0.164 可用，源文件保持可单测形态；脚本本体不依赖 uid 注入的部分可整体搬迁，注入 uid 的部分需参数化）。决策在工单 0022。
- **可测试的缝天然是双层的**：行为（点击/aria/计数/空态/降级）只能在 Node DOM harness 里跑；HTML 契约面（class/data-*/aria/脚本挂点/降级规则存在性）留给 build-then-assert。两层都与 Hugo 版本解耦。决策在工单 0023。
- **无 IO 的 jsdom 恰好覆盖降级路径**：extend_footer 的 `!('IntersectionObserver' in window)` 分支成为可直接断言的行为（全量 is-in），不是测试障碍。
- **minify 改写 JS 但不改写语义**：产物断言不得匹配脚本文本（HTML 侧的引号坑同源）；若引 harness，fixture/样本 HTML 来自构建产物时为 minify 后字节——行为执行不受影响。
- **A2 的零断言面即 0023 的缺口清单**：12+ 个契约点中仅 `mf-filter` 有守门，「可测试」目的地的最小充分集应由该表驱动取舍。
