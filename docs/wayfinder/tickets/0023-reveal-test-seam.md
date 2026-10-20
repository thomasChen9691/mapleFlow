---
id: 0023
title: 可测试的缝：JS 行为测试与产物断言的分工
type: grilling
mode: HITL
status: closed
blocked_by: [0022]
assignee: agent
map: map-reveal-protocol.md
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

目的地要求「可测试」——测试缝落在哪、怎么分：

1. **分工**：哪些行为进 Node DOM harness（真实点击、aria-pressed、计数、空态、减弱动效、同页多实例），哪些只配 build-then-assert 产物断言（class / data-* / aria / 脚本挂点存在性、no-js 降级规则的存在）？判据是什么？
2. **套件与守门**（若引 harness）：测试落点（并入 `tests/assert_product_states.py` 还是新脚本如 `tests/assert_reveal.py`）、样本 HTML 来源、CI 守门（权威 / advisory）、与 Hugo 版本 skew 的关系（harness 消费产物，预期与 Hugo 版本无关——需确认）。
3. **既有缺口**：no-js 基线（html class、head swap 脚本、`.no-js .reveal` CSS 降级）当前零断言，缺口补在哪个缝？

## 施工期注记（2026-10-20，待本工单追认）

0022 决议④的 A/B 分流已按用户指示提前施工（候选 4 先例：施工先于工单，本段登记待追认事实）：

- **A 类行为 harness**：落点 `tests/assert_reveal.mjs`（Node ESM + jsdom），样本 HTML 手写于 harness 内（镜像渲染 seam 的 DOM 契约），未用构建产物；A 类 9 项已全落（RGR-1..8，含 RGR-7c 减弱动效分支）。A6 的 remove→reflow→add 中 reflow 不可观测（jsdom 无布局），断言只锁终态与 timer 行为——评审确认为可观测极限，不测实现细节。
- **B 类产物断言**：并入 `tests/assert_product_states.py`（`assert_reveal_artifacts`，B1–B6），B5 为精确集合比对。
- **依赖供给**：jsdom 经仓外 symlink（`node_modules → managed workspace`）解析，`package.json` 未入仓、CI 无 node 步——harness 目前只在开发机可跑。**这是本题待决的核心**：套件形态已事实定为「独立 .mjs（行为）+ 并入 .py（产物）」，但依赖入仓方式（package.json + npm ci 步 / vendored / CI 不跑仅本地 advisory）与 CI 守门策略未定。
- **C 类逐出已执行**：视觉参数数值未断言（评审曾抓出 520ms 数值被打钉，已删）；搜索 JS 未碰。

## Resolution

2026-10-20 · grilling（用户为决策者），三问落定：

1. **依赖供给与守门 = 入仓 + CI 权威**：`package.json` + `package-lock.json` 入仓（jsdom 为 devDependency）；CI 在 python 两步之前加 `npm ci` + `node tests/assert_reveal.mjs`，失败即阻断部署（ADR-0004「CI 权威 + 本地 advisory」的总原则适用于行为层）。已知代价：Hugo 仓引入 npm 供应链（jsdom 约 20 个传递依赖，锁文件固定）、CI 约 +15–25s——接受。
2. **套件形态 = 两脚本两步**：node harness 与 python 套件各自一个 CI step，与现有「每套件一 step」形态一致；不建单一入口（多一层间接、失败定位变差），不全搬 node（复制 python fixture 基建 = 0019 枪毙过的第二实现）。
3. **样本来源 = 手写 + 产物守契约**：行为 harness 用手写样本（镜像引擎 docstring 契约）；渲染 seam 是否偏离契约由 B 类产物断言（B4 挂点、B5 词表）守。不加「样本 ↔ 产物一致性」断言——那是契约的第二实现，漂移风险自增。
4. **既有缺口追认**：no-js 基线断言落 B 类（B1 html class + swap、B6 CSS 降级规则），施工已落。

**下游影响（施工动作，待用户指示）**：写 `package.json`（private、devDependencies.jsdom、scripts.test 入口）、生成并提交 `package-lock.json`、`.github/workflows/deploy.yml` 加两步（npm ci → node harness）；`tests/assert_reveal.mjs` 头注释去掉「provisional pending 0023」，改为正式 seam 说明；AGENTS.md 补一行测试命令（0026 收口时统一整理导航）。
