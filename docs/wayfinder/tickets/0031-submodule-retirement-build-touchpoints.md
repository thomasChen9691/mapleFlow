---
id: 0031
title: 子模块退役与构建链触点
type: grilling
mode: HITL
status: open
blocked_by: [0029]
assignee:
map: map-theme-fork.md
created: 2026-10-20
---

## Question

子模块从「外挂依赖」退为「仓内目录」的机械路径与全部触点的处置边界。事实底坐：0027 §7 触点清单、0028 §3 vendor 化路径与 CI 行为。

待决问题（一次会话内按序过，先给推荐答案）：

1. **gitlink 处置确认**：`git rm --cached themes/PaperMod` + 删 `.gitmodules` + `git add themes/PaperMod` 的 vendor 化路径（0028：官方语义组合的社区通行做法）——历史中的 gitlink 与 `.git/modules/` 缓存不动，是否有异议？若 0029 择改名（B），`git mv`/重命名与 add 的顺序如何定？
2. **CI 触点**：deploy.yml:28 `submodules: true` —— 0028 证实移除后构建不依赖它。删除该行（连带注释）还是暂留？本地/CI 的 Hugo 查找是否需任何其他改动（预期无）？
3. **文档触点范围**（0027 §7 清单）：AGENTS.md 5 处——①「项目概览」子模块描述；② 部署流水线「检出（含子模块）」；③「首次初始化主题子模块」整段；④ 坑点 6（`git checkout main` 联网卡死，整条随子模块消失）；⑤ §7 速查表 post_meta 行「升级时必须回来同步」；README 5 处子模块初始化指引。删除/改写的边界（哪些整删、哪些改写为 fork 后形态）？
4. **验收标准**：触点清完的判据——三套件（`npm test` / `assert_product_states.py` / `assert_sop_pipeline.py`）+ 生产构建 exit=0 + `grep -r "localhost:1313" public/` 零残留（ADR-0001/0005/0007 既有纪律）；是否加「主题目录文件清单快照」类断言（归 0032 决策，本题只确认验收面）。
5. **本地 dirty 状态**：当前工作区 themes/PaperMod 116 文件 CRLF dirty——若 0029 择「入库时转 LF」，本题确认添加时的行尾归一方式（`.gitattributes` vs add 前转换）。

决策记录：本题 Resolution 落触点处置表（每处：删/改/留 + 理由）+ 验收判据，作为施工期（项目负责人指示后展开）的执行清单。
