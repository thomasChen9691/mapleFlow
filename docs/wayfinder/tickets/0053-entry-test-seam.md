---
id: "0053"
title: 入口与呈现层的测试缝
type: grilling
mode: HITL
status: closed
blocked_by: [0052]
assignee: agent
map: map-search-entry.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

新入口 / 呈现层的测试缝（前提：0052 已决，契约定义处已落位）：

1. **行为测试**：入口交互（唤起 / 聚焦 / 键盘 / 浮层 / no-js 降级）与呈现层加深的 jsdom 套件——并入 `tests/assert_reveal.mjs` 还是新建 `tests/assert_search.mjs`；`package.json` 的 test 入口是否调整；样本 DOM 手写镜像契约（ADR-0007 先例：不用构建产物，fingerprint / minify 会使 harness 脆弱）；断言范围与 0052 契约定死范围一致。
2. **产物断言**：入口在首页 / 全站的渲染挂哪个 fixture 构建（现有三套：dataDir fixture / contentDir fixture / 真实数据——第四套 config 键的成本，fixture 基建单份原则）；fastsearch 构件引用面断言（哪些页面必须引用 `search.*.js`——交付面守门，参照 0047 先例）；加载条件改动的回归（search 页仍加载、新页面也加载、其余页面不加载）。
3. **坏用例缝**：若 0052 新增 errorf——进 `tests/fixtures/bad/` + `BAD_CASE_EXPECT` 逐用例钉子串（参照产品索引门禁先例）。
4. **CI 守门**：deploy.yml 的 `Assert site contracts` 步与新断言的关系；`npm test` 入口是否仍单条。

纪律沿用：每条断言变异检验（破坏实现 → 红 → 还原）；期望值独立字面量（非同义反复）；真实内容不锚（字段契约与结构必须锚）。

**已决输入**：ADR-0010 决策 5（不立 jsdom 行为套件的理由与「重写时测试与新契约一起 TDD」的既定路径——本图不是重写，入口交互的测试缝要回答「为什么这次值得立」或按产物断言覆盖）、0047 测试缝先例、0052 契约落位。

## Resolution

2026-10-23 · grilling（HITL，用户为决策者；一开放问题落定，五条记录经用户最终确认共识）。前提盘点：本工单四个子问题中三个半已被 0050/0051 决议与施工回答（记录为既定事实，不重开）。答案五条：

1. **行为测试**：无新决策——0050 决议⑧ + 施工已落地：新建 tests/assert_search.mjs（jsdom、手写样本镜像引擎 docstring、13 条：跳转/焦点门控/修饰键门控/页内聚焦/params 降级），npm test 双套件串联，node 套件「只测源码不经构建」不变式保住。
2. **产物断言**：无新决策——同落地：入口构件交付面、生产子路径 URL、加载面双向（fixture + real）、菜单文案，全挂既有三套构建（无第四套 config，fixture 基建单份原则守住）。
3. **坏用例缝**：无新增——0052 零 errorf（入口无构建失败面；extend_footer 的入口缺失守卫是 reveal 既有模式复制，文件在仓内、fixture 层无法模拟「文件不存在」）。结论记录：无可缝。
4. **CI 守门**：deploy.yml 零改动（npm test 跑双套件、Assert site contracts 跑 Python 套件，顺序内容均无需动）。发现两处注释漂移——Assert site contracts 步仍写「七类…B7-B13」（已八类 + B14）、Install test deps 步写「jsdom 只为 assert_reveal.mjs 服务」（现兼服务 assert_search.mjs）——移交 0054 收口批修。
5. **渲染 harness（唯一新决策）**：**A——保持一次性**（0051 决议④ 原样）。**所有权分层原则**就此立住：我们新写的代码（入口引擎，纯函数 seam）→ 常驻行为测试；我们承诺不重写的遗留引擎（fastsearch，ADR-0010）→ 弱产物断言 + 记录在案的一次性验证。不为 legacy 内部机制（XHR 模式 / onload / 模块级捕获）给 CI 征税——那会拖慢 exactly 我们想鼓励的内部修复。
