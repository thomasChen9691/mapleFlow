---
id: "0092"
title: 移动端与小屏的 a11y 契约
type: grilling
mode: HITL
status: closed
blocked_by: ["0089"]
assignee: agent
map: map-search-overlay-v2.md
created: 2026-11-15
claimed: 2026-11-15
closed: 2026-11-15
---

## Question

候选 12 收口时挂起的三条雾区，其触发条件「将来出现浮层形态」已被 ADR-0013 兑现。本图要决定它们如何毕业——哪些进 v2、哪些继续挂起、哪些判为越界：

1. **触屏替代入口**：触屏设备没有 `/` 键时，是否只复用 `.mf-search-link`（它已是浮层触发器、no-js 下是普通链接），还是另立触发面（常驻框 / 手势）？「实际出现触屏流量」这一触发条件是否已被 10-24 F 批的触屏入口兑现？
2. **aria 契约细节**：`role="dialog"` / `aria-modal` / `aria-expanded` / `aria-activedescendant`、打开入焦与关闭还焦、Tab 困排的 inert 分支与手写兜底、锁滚后的 scrollTo 回位——这些是否已被 ADR-0013 决策 8 与引擎 docstring 足够承载，还是需要扩写契约？扩写的话「哪个文件是唯一定义处」如何保持。
3. **小屏空间关系**：浮层与 hero / 精选区的遮挡或让位要不要进 v2 的决策面？还是按历图先例把像素级空间关系留给视觉层？若要进，判据是「行为契约」还是「视觉调值」。
4. **毕业形态**：三条里未被本图消化的，是写进本图 Not yet specified 并附新的触发条件，还是判为 Out of scope？判据参照 `map-search-entry.md` 收口注记「诚实保存、不进 backlog、不宣布 out of scope」的先例。

边界（不开票）：不重写 fastsearch、不改投影字段；方向键 / 高亮归「方向键导航与命中高亮的取舍」；视觉调值 Out of scope。事实以「搜索浮层 v2 现状事实底座（盘点）」为准。

## Resolution

2026-11-15 · HITL grilling（项目负责人实时对话定案）。候选 12 三条挂起雾区按「已兑现 / 扩写 / 越界」分别毕业：

1. **触屏入口判已兑现**：复用 `.mf-search-link`（已是浮层触发器、no-js 下是普通链接），只补断言、**不新立触发面**；「实际出现触屏流量」不再作为等待条件。
2. **aria 契约扩写**进 `mf-search-overlay-engine.js` 头 docstring（唯一定义处）：`aria-expanded`、`aria-activedescendant`、`aria-selected` 三属性。其中 **`aria-expanded` 由引擎在开关时写到触发器节点**——触发器在主题层 `header.html`，但不新增主题层脚本，避免破 ADR-0008 分层判据。按 0090 分层判据配行为 + 产物断言；与 0091 的方向键选中态共用同一处契约。
3. **小屏首屏空间关系判视觉层 Out of scope**：现状只有 `custom.css` 定位、无契约无断言，本图不决策，也不重开地图 Out of scope 条款。

未选「三条全进 v2」（会把 CSS / 布局拉进决策面、与地图 Out of scope 冲突）与「三条全挂起」（会丢掉「浮层形态」已兑现的触发条件）。事实依据见 0089 研究产物第 4 节：① 部分兑现、② 部分兑现、③ 未触及。
