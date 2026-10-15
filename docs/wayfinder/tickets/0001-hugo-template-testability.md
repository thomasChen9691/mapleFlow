---
id: 0001
title: 查清 Hugo 模板可测性事实
type: research
mode: AFK
status: closed
blocked_by: []
assignee: research-subagent
map: map-product-state-convergence
closed: 2026-10-15
---

## Question

Hugo 0.164 下，产品状态推导逻辑（判定已上架 / 即将上架 / 免费 / 可下载产品，含占位例外）若驻留在模板层，有哪些可测试手段？需要的事实：

1. Hugo 官方/社区是否有模板逻辑的单元测试机制（任何形式）？若无，社区惯用替代是什么？
2. partial 之间共享派生数据的惯用法：返回 dict 的 partial、`.Scratch` / `.Store`（site 级与 page 级）各自的能力与限制；`index.json`（输出格式模板）能否调用同一 partial 复用派生结果？
3. `data/` 目录是否支持构建期计算（还是仅静态文件）？
4. 「构建后断言产物」（解析 `public/*.html` 验证按钮态与首页数字）在本仓技术栈（Python 3.13 / Node 22 可用）下的可行形态与代价。
5. Hugo 当前版本 partial 返回值（`return` 指令）的确切语法与版本要求。

## Resolution

2026-10-15 · research 子代理解决，产物：[research/0001-hugo-template-testability.md](../research/0001-hugo-template-testability.md)

1. **无模板单测机制** —— 社区标准为 gold 文件法（build 后对产物断言），可用 `strings.Diff`（v0.125+）辅助；`--renderSegments`（v0.124+）可只渲染部分页面加速。
2. **派生数据共享惯用法** —— return 型 partial（v0.55+）是主流；`.Store` 家族 v0.139+（site 级按文档语义跨模板持续），`.Scratch` 自 v0.138 软弃用；output-format 模板（如 index.json）可调用同一 partial，但勿依赖跨输出格式的 Store 写入顺序（json weight=0 先于 html 渲染）。
3. **data/ 纯静态** —— 构建启动时一次性读入内存，无构建期生成机制；替代为预构建脚本 / module mounts / content adapters（v0.126+）/ resources.GetRemote。
4. **产物断言可行** —— 已实证 public/products.html 按钮态与 public/index.html 数据条可断言；四坑：minify 后正则易碎（用 html.parser/cheerio）、dev 相对 URL vs 生产子路径前缀、`hugo server` 忽略配置 baseURL（须用全量 `hugo` 构建）、**本机 0.167 与 CI 0.164 的 return 语义分叉（已由本会话独立核实）**。
5. **0.164 return 精确约束** —— 单变量 + 根级单条 return；0.166 前条件块内的 return 也会无条件执行；带副作用的 partial 被 partialCached 缓存会丢/重副作用 → 派生 partial 必须纯计算 + return。
