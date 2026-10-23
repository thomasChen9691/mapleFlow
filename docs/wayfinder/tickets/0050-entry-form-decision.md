---
id: "0050"
title: 入口形态定案
type: grilling
mode: HITL
status: closed
blocked_by: [0049]
assignee: agent
map: map-search-entry.md
created: 2026-10-23
claimed: 2026-10-23
closed: 2026-10-23
---

## Question

入口形态定案——新搜索入口是什么形态（前提：0049 事实已落盘，事实争辩以 research/0049 为准）：

1. **候选形态**（可组合、可全部否决）：
   - A. 全站快捷键唤起（键位候选：`/`、`Cmd+K`/`Ctrl+K`、沿用 `Alt+/` 扩展到全站）——唤起后落点：跳转 search 页 / 全站浮层；
   - B. 首页常驻搜索框（实时结果浮层 / 提交后跳 search 页）；
   - C. A+B 组合；
   - D. 维持现状（菜单项 + search 页内 Alt+/）——「不做」需显式确认。
2. **fastsearch 加载面后果**：现 fastsearch 仅 search 页加载；A/B 任一「重形态」（全站浮层 / 首页实时结果）都意味着新增加载页面——按 ADR-0010（2026-10-23 指针）这构成「第二个消费方」，触发「不重写」结论的重评。本工单要定：新入口是否仍基于 fastsearch 引擎（不重写前提下加载面怎么扩：head.html 条件扩展 / extend_footer 恒加载 / 新轻量入口脚本）；重评结论是什么。注意「轻形态」（快捷键或首页框只负责跳转 + focus，检索仍在 search 页）不扩大 fastsearch 加载面，「第二个消费方」问题消解于萌芽——这是 A/B 内部的重要分叉。
3. **发现性 vs 首屏空间的权衡**：菜单已有「搜索」项；快捷键不可发现；首页框占首屏——项目定位（个人技术博客、读者为运维 / SRE 同行、检索场景以查命令与 SOP 为主）下哪个更重要。

**推荐**：A 的轻形态（全站快捷键 → 跳转 search 页并 focus，键位 `Cmd+K`/`Ctrl+K`，`/` 为备选）——理由：不挤首屏、与现状（search 页已是完整检索页、onload focus 已存在）兼容、加载面不扩故不触发重评；若你更重视可发现性，B 的轻形态（首页框提交跳转）次之；浮层 / 实时结果等重形态成本最高且触发 ADR-0010 重评，除非有真实需求否则不建议。一次一问，先给推荐答案，你拍板。

**已决输入**：ADR-0010 快照契约（fastsearch.js docstring）与「不重写」指针；ADR-0002 no-js 基线（任何入口脚本必须遵守渐进增强）；ADR-0008 分层判据（入口脚本落站点层还是主题层归 0052，本工单只选形态）。

## Resolution

2026-10-23 · grilling（HITL，用户为决策者；九问全部落定，终局形状经用户最终确认共识）。事实前提：`research/0049`。答案九条：

1. **真实需求**：P1——从任意页面发起搜索的步骤成本（现状 2 步：菜单 → search 页）。
2. **形态**：A 单独成立（全站快捷键）。B（首页常驻框）不做——它解决的是已被排序在后的 P2，将来有新证据另开工单；D 已否。
3. **轻重**：轻形态——按键跳转 `/search.html`（search 页打开即 autofocus，检索体验完整）；重形态（当前页浮层实时检索）否决（第二个消费方 + 引擎改造 + 新交互契约的成本，对 17 条索引买贵了）。按键在 search 页自身时只聚焦、不刷新。
4. **键位**：`/`；焦点在 input/textarea/select/contenteditable 或按着 Ctrl/Meta/Alt 时不拦截；Firefox quick-find 被遮蔽的取舍已知并接受。菜单 `(Alt + /)` accesskey 退役、提示改 `/`。
5. **seam**：站点层新单文件 `assets/js/mf-search-entry.js`，经 extend_footer 第二个 js.Build（iife + minify + fingerprint + defer）全站恒加载——复刻 reveal 模式、零 resources.Get 遮蔽风险；契约落新文件 docstring，与 fastsearch.js 快照并列互指不合并。
6. **URL 注入**：js.Build params 注入全局 `params.searchUrl` = search 页 RelPermalink（构建期自动带 `/mapleFlow/` 子路径；git 历史 0425f4d 证实本项目 Hugo 0.164 的 params 注入形态即全局 `params` 对象）；`typeof params` 守卫，缺失即静默不启用，菜单链接兜底，绝不猜 URL；同一注入值兼作「当前是否在 search 页」判定。
7. **第二个消费方重评结论**：入口脚本只做跳转/聚焦，与 fastsearch、index.json 零耦合 ⇒ **不构成第二个消费方，不触发 ADR-0010 重评**，「不重写」原样成立。
8. **测试**：新建 `tests/assert_search.mjs`（jsdom 四行为：跳转 / 焦点门控 / 页内聚焦不跳转 / params 缺失静默；npm test 改两条串联）；产物新增四条（入口构件交付面锚 fixture、生产子路径 URL 锚 assert_real、加载面双向钉死锚 fixture+real、菜单文案锚 assert_real）+ 无新坏用例；每条新断言变异检验。
9. **零改动区**：fastsearch.js、index.json、search 页、search.css、mf-reveal、首页 layouts——一个字节不动；无搭车项。

**机械后果**：0051 解除阻塞（frontier 前移）；0052 的契约落位问题被本票大幅预决（落点 / docstring / params 机制已定），剩余面收窄为 extend_footer 双 build 施工形状 + 与 fastsearch 契约互指措辞。施工经项目负责人 2026-10-23 指示展开（TDD 红绿、一次一行为、收尾 realeng-code-review 后单独 commit）。

**施工期补记（2026-10-23，双轴 code-review 后回写）**：

- 决议⑤「新单文件」的 seam 落地为两文件：`assets/js/mf-search-entry.js`（入口，保留决议原名——import '@params' 虚拟模块 + 装配注册）与 `assets/js/mf-search-entry-engine.js`（纯引擎，零 Hugo 依赖，行为契约定义处）。机制原因为排图时未知、施工期实证：Hugo `js.Build` params 的注入形态是 **ESM import（`import * as params from '@params'`）**而非裸全局对象（本机 0.167 实证注入生效；0.162-0.168 发布日志无 params 相关变更，故 CI 钉版 0.164 同款；旧 fastsearch 的裸 `params` 写法在现行 Hugo 下实为死路径）。入口文件因此不可被 Node 直接导入，裂出纯引擎方能满足决议⑧「jsdom 直测源码」——与 mf-reveal 的 app.js + 引擎分层同构。决议意图（URL 走构建期注入、可产物断言、站点层、extend_footer 恒加载）不变。
- 决议⑥「typeof params 守卫」落地为 searchUrl 值守卫：`@params` 模块恒为对象，`typeof` 检查无意义；值守卫（字符串 + 非空）语义等价，fixture 无 search 页时实测走此降级路径。
