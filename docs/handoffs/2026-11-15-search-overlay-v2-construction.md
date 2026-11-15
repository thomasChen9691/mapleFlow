# 交接：搜索浮层 v2 施工（2026-11-15）

> 只写当前状态、下一步、建议 skill。决策与契约不在此重述，按需取：
> `docs/wayfinder/map-search-overlay-v2.md`（已 closed，六票 Decisions so far）、
> 六张工单的 `## Resolution`、`docs/wayfinder/research/0089-search-overlay-v2-facts.md`、
> `CONTEXT.md`、`AGENTS.md`。本文不重复。

## 当前状态

- **决策面已闭环并落库**：第 13 张地图 `map-search-overlay-v2` `status: closed`（2026-11-15），
  六票全 closed、frontier 空；commit `ec01d3d`（`docs: chart search overlay v2 map and resolve
  six decision tickets`）已推 `main`，CI run `43718244728` 的 verify（15 步）+ deploy（7 步）双 job 全绿。
  `gh-pages` 未产生新提交属正常（docs-only、产物无变化）。
- **本图不含施工**：ADR-0017、0010/0011/0013 三笔指针行、CONTEXT 扩写、AGENTS §7 / 坑点 14·18、
  以及本文，全部属**收口批施工**，经项目负责人 2026-11-15 指示后另开批次，不进闭图条件。
- **两处施工期灰点已由 grilling 逼死（仅对话决议，未回写已 closed 的地图与工单）**：
  1. **Enter 语义**：有选中项时 Enter 导航该项、无选中项仍导航首条（MFO-15 原样存活）；
     ArrowDown 到底停、ArrowUp 到顶停，**clamp 不循环**（与 `fastsearch.js:176-198` 一致）；
     焦点恒在 input（`aria-activedescendant` 指选中项，不转移到 `<a>`）；
     **重检索（input 事件）与 close 都清空选中索引**。
  2. **施工序列 = 两笔提交**：① 契约与实现笔 ② 文档资产笔。详见下一步。

## 下一步（两笔提交，严格分开）

### 第 1 笔：契约与实现（本文不与本笔同提交）

范围（docstring / 实现 / 断言**同进同退**，回滚点 = 整笔）：

1. `assets/js/mf-search-overlay-engine.js` 头 docstring：删 `isOpen` 返回形状描述（对齐实现
   `{ open, close }`）；补方向键 / 选中态 / `aria-*` / Enter / clamp / 清空时机条款；容错 UX 段
   去掉「引导去 search 页」的措辞。
2. 同文件实现：选中索引与 `setSelected` / `clearSelection`；`render()` 给 li 写 id / `role=option`
   / `aria-selected`（**用属性选择器做视觉反馈，不新增 `is-*` class，避免 parity 门 RGR-14 正向红**）；
   open/close 时由引擎给 `.mf-search-link` 写 `aria-expanded`；input keydown 处理
   ArrowUp/Down（clamp）与 Enter（选中项优先）；重检索与 close 清空。
3. `tests/assert_search.mjs`：测试头注释删 `isOpen`；`overlaySample()` 的 ul 加 `role=listbox` 镜像骨架；
   新增 MFO-20.. 行为断言（返回形状 / 触发器 aria-expanded / 选中态三属性 / Enter 选中项 /
   clamp 两向 / 重检索清空 / close 清空）。**MFO-15 一字不改**。
4. `themes/maplemod/layouts/partials/search-overlay.html`：ul 加 `role=listbox`；错误文案删
   「或前往搜索页」改为「索引加载失败，请稍后重试。」（继续硬编码中文，不进 i18n）。
5. `assets/css/extended/custom.css`：补 `.mf-search-item[aria-selected="true"]` 的功能性视觉反馈
   （选中态必须可见；不属视觉重设计）。
6. `tests/assert_site_contracts.py`：产物断言守骨架错误文案与 `role=listbox`，源码弱断言守
   docstring / 测试头不再出现 `isOpen`。

**TDD 纪律**：新断言先红（实现未动时跑 `npm test` 与 site 套件，看到可定位的红）→ 实现到绿 →
每条以变异检验证牙（破坏实现→断言红→还原）。MFO-15 全程保持绿。

**门禁计数预期**：`npm test` 新增 MFO-20.. 若干条；`assert_site_contracts.py` 新增 2–3 条
（基线 185/185 → 约 188/188）；`assert_harness.py` 19/19、`assert_sop_pipeline.py` 105/105 不变；
生产构建零 WARN、无 localhost 泄漏。

### 第 2 笔：文档资产（可与本文同提交）

- `docs/adr/0017-search-overlay-v2.md`（一图一 ADR，各条注工单号 0089–0094，含负向边界与重开触发条件）。
- 旧 ADR **指针三笔**：0010 / 0011 / 0013（正文不改）；写明「两面容错不对称是有意的，勿当漏实现补上」。
- `CONTEXT.md` 只扩写既有「搜索浮层」词条；不新增实现机制词（ADR-0015 决策 12）。
- `AGENTS.md` §7 增行、坑点 14 / 18 补注。
- 本文 + 收口 handoff（施工序列、回滚点、验证基线、已知限制、建议 skill）。
- `docs/README.md` 计数（13 张地图 / 94 张工单）归清理批，**不顺手改**。

**回滚点**：第 1 笔整笔回退（docstring / 实现 / 断言同进同退，不许只回退一半导致契约与代码分叉）；
第 2 笔纯文档，可独立回退、不影响运行时。每笔各自跑四道门 + `git push origin main` + 确认 CI 双 job。

## 环境坑（历图传承）

- shell 的 grep 对 `\|` 交替静默失效 —— 内容搜索一律用 Grep 工具，且双向复核。
- `gh` 未安装；查 CI 用 curl + GitHub API（runs / jobs 匿名可读，logs 需管理员 token）。
- **`git add -A && commit && push` 长链会被沙箱升级重跑**：commit 在第一次执行已成功、
  第二次 `staged=0` 令链断在 push 前。一律用「幂等脚本（staged 空则不 commit、仍 push）」，
  不重复提交、不 amend、不 `--force`。
- dev server 运行期间不要跑生产构建（AGENTS 坑点 5c）；跑门前先 `pgrep -fl "hugo server"`。
- 本机 Hugo 0.167 / CI 0.164 的 skew 只有 advisory WARN，不是失败。

## 建议 skill

- **realeng-tdd**：红绿 + 变异检验；纯删除/文档批的变体 = 删完套件原样全绿。
- **realeng-code-review**：收尾双轴评审（Standards / Spec），本项目每批各抓到过真问题。
- **realeng-grilling / realeng-wayfinder**：开下一张地图时用；本图已 closed，勿加票。
