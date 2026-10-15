---
id: 0001
title: 查清 Hugo 模板可测性事实
type: research
mode: AFK
status: open
blocked_by: []
assignee:
map: map-product-state-convergence
---

## Question

Hugo 0.164 下，产品状态推导逻辑（判定已上架 / 即将上架 / 免费 / 可下载产品，含占位例外）若驻留在模板层，有哪些可测试手段？需要的事实：

1. Hugo 官方/社区是否有模板逻辑的单元测试机制（任何形式）？若无，社区惯用替代是什么？
2. partial 之间共享派生数据的惯用法：返回 dict 的 partial、`.Scratch` / `.Store`（site 级与 page 级）各自的能力与限制；`index.json`（输出格式模板）能否调用同一 partial 复用派生结果？
3. `data/` 目录是否支持构建期计算（还是仅静态文件）？
4. 「构建后断言产物」（解析 `public/*.html` 验证按钮态与首页数字）在本仓技术栈（Python 3.13 / Node 22 可用）下的可行形态与代价。
5. Hugo 当前版本 partial 返回值（`return` 指令）的确切语法与版本要求。
