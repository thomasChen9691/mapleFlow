---
id: "0086"
title: CSS 影子契约的 token 清单与 parity 方向
type: grilling
mode: HITL
status: closed
blocked_by: ["0079", "0080", "0085"]
assignee: agent
claimed: 2026-10-27
closed: 2026-10-31
map: map-architecture-deepening.md
created: 2026-10-27
---

## Question

CSS 影子契约的 token 集合怎么定义、parity 检查哪个方向——「门守什么」的问题。落点与强度归 0087，本票只定**集合与判据**。

现状：JS 写入 `is-in` / `is-hidden` / `--mf-progress` / `--mf-i` / `aria-pressed` / `inert` / `hidden`，CSS 侧消费 `.reveal` / `.is-in` / `.is-hidden` / `--mf-progress` / `--mf-i` / `.mf-index` / `.mf-search-overlay`；契约的**定义处是引擎文件头 docstring**（ADR-0007），CSS 只是无门的影子拷贝——JS 改类名、CSS 忘改，两边都不报错，只表现为「动效消失」。

要决策的面：

1. **token 清单来源**：从 JS 源码抽取（正则扫 `classList.*` / `setProperty`）、从 CSS 抽取（扫选择器与自定义属性）、手写单一 registry 文件、还是从 docstring 的契约段解析。四者的漂移风险不同——手写 registry 会变成**第二个契约定义处**（与 ADR-0007 的「docstring 是唯一定义处」冲突），需正面处理。
2. **检查方向**：JS→CSS 单向（JS 写的必须被 CSS 消费——防「写了没人读」）、CSS→JS 反向（CSS 消费的必须有生产者——防「读了没人写」）、还是双向。反向会遇到 markup 拥有的类（`.reveal` 由模板写在元素上）与纯视觉类，需要白名单。
3. **覆盖范围**：只 class，还是含自定义属性（`--mf-*`）、`aria-*`、`data-*`、`hidden` / `inert` 这类属性；构建期生成的类与主题自带类是否排除。
4. **语义漂移能否被发现**：同名但语义不一致（例如 JS 只在 reduce 时加、CSS 当常态样式）parity 只能查存在性——是否接受「只守存在性、语义靠 docstring」这一已知限制并记录。
5. **白名单机制**：白名单写在哪（registry 文件 / 断言内常量 / docstring 标记），谁维护，新引擎加入时如何被引导（是否要求 docstring 用固定格式声明 token，从而可被解析）。

边界（不开票）：ADR-0007 的「docstring 是 DOM 契约定义处」不重开；门放哪、失败强度归 0087；死面删除结果由 0085 提供（本票的 token 集合以删除后的现状为基）。

## Resolution（决议已定，施工未开始）

2026-10-27 · grilling（HITL，两问定案）。

**清单来源 = 源码双向抽取 + 白名单**：JS 侧正则抓 `classList.add/remove/toggle('x')` 字面量、`setProperty('--x')`、以及**传给 helper 的 `'is-*'` 字面量**（`replay(el, 'is-morphing', 520)` 这种参数化写法，规则要覆盖）；CSS 侧抓选择器类名与 `var(--x)`；两侧 diff。**不手写 registry**——它会变成第二个契约定义处（与 ADR-0007 冲突）且改 JS 忘改 registry 就假绿。docstring 仍是唯一定义处。已知代价：动态拼名抓不到，靠白名单兜。

**方向 = 双向；范围 = 只 class 与 CSS 变量**：
- 正向（JS 写 → CSS 必须消费）防「写了没人读」，这是本门的主要动机（动效静默失效）；
- 反向（CSS 消费 → 必须有 JS 或 markup 生产者）防死样式；markup-owned 类（`.reveal`）走反向白名单；
- **`aria-*` / `inert` / `hidden` 不进 parity**：它们的消费方是浏览器与 JS，不是 CSS，纳入会变成永久白名单维护工程。

**已知限制（诚实入档）**：门只守**存在性**，不守**语义漂移**——同名不同义（例如 JS 只在 reduce 时加、CSS 当常态样式）发现不了，语义仍靠 docstring 与 review。

**白名单形态**：位置随 [0087](0087-parity-gate-placement-strength.md) 的落点定（测试期 → 断言内常量；构建期 → 数据文件）。白名单每条必须带理由与归属文件，不设「看着像就放过」。

**施工（2026-10-31，PR② 第二笔 `08f1280`）**：`tests/tokens.mjs` 落地——`collect({js, css, markup})` 出 `{writes, reads, markup}` 三张表，每 token 带 `{file, line}`；`listFiles(dir, ext)` 供断言侧取文件清单；每项可为路径或 `{file, text}`（自测纯函数入口）。

**门首跑抓到真问题**：`is-free` 的生产者写在模板动作**外面**（`class="mf-price{{ if $state.free }} is-free{{ end }}"`），按空白切 class 属性会把 token 粘成 `is-free{{` → 抽取器改为扫描前剥 `{{ … }}`，并把该形态钉进 `assert_harness` 自测。

**白名单为空已兑现**：反向只查 `is-*` 六个，全部有生产者（4 个 JS 写 + `is-current`/`is-free` 模板写）。

**实施细化（2026-10-31 grilling，PR② 开工前）**
- **反向范围收窄到 `is-*` 状态词表**（6 个：`is-bump` / `is-current` / `is-free` / `is-hidden` / `is-in` / `is-morphing`），生产者面 = **模板 class 属性 + JS 写入**（`is-current` 由 `pagination.html`、`is-free` 由 `product-index.html` 生产）。**白名单为空**——`mf-*` 视觉类不进反向检查（它们的死样式归 0085 一次性清理，不开长期门）。这条同时解掉了「双向 ⇒ 等于死面守门」与 0085「不加死面守门」的冲突。
- **抽取器独立成 `tests/tokens.mjs`**（机制层，零期望值）；断言与范围判断留在 `assert_reveal.mjs`；`assert_harness.mjs` 加抽取器自测（已知输入 → 已知 token 集）。
- **接口 = 带定位的词法表**：`collect({js:[路径], css:[路径]}) → {writes:{token:[{file,line}]}, reads:{…}}`，class 与 var 分两类。抽取器不懂方向、不懂 `is-*` 范围、不持白名单。
- **首跑基线已实测**：正向（JS 写 → CSS 读）**0 违规**；反向 6 个 `is-*` 全有生产者 → 门上线即绿，红只会在真漂移时出现。
