---
id: 0028
title: 上游与外部事实（PaperMod 现状 / Hugo 解析 / 许可）
type: research
mode: AFK
status: closed
blocked_by: []
assignee: agent
map: map-theme-fork.md
created: 2026-10-20
claimed: 2026-10-20
closed: 2026-10-20
---

## Question

候选 6 的外部事实底坐（本工单只产事实、不产决策；外部访问日期 2026-10-20）：

1. **上游现状**：hugo-PaperMod 相对钉住 commit 6c5a8f6 的差距（落后提交数、有无新 release/tag）、活跃度与维护状态——这是「fork 后是否/如何跟上游」的事实面，但不替用户做决策。
2. **Hugo 0.164 主题解析机制**（CI 钉 0.164.0 extended，以 gohugo.io 官方文档为准）：`theme` 名与 themes/ 目录名的绑定关系（fork 改名是否必须同步改 hugo.toml）；项目 layouts/ 对主题同名文件的覆盖优先级官方表述；themes/ 下非子模块普通目录（vendored）与子模块的构建等价性。
3. **子模块退役的 git 机制**：保留工作区文件、把子模块改为普通目录入库的 vendor 化路径（index/gitlink/.gitmodules 各自怎么动）；actions/checkout 对 submodules 的默认行为（移除后 CI 是否必须改 deploy.yml 才能构建成功）。
4. **MIT 许可义务**：fork+修改后的最低义务；PaperMod README/wiki 是否对使用者有强制署名/鸣谢条款。
5. **官方对 fork 后跟随上游的指导**：quick start（子模块）/ theme-components / use-modules / vendoring 的现行说法；Hugo Modules 与子模块在 0.164 时代的取舍事实（是否官方推荐 modules 取代 submodule）。

## Resolution

2026-10-20 · research（agent 驱动，结论落 [research/0028-upstream-and-external-facts.md](../research/0028-upstream-and-external-facts.md)，未执行任何 git 写操作）：

1. **上游现状**：钉住点 6c5a8f6（2026-01-09）**落后 master 92 提交**（compare API 三次一致；v8.0→钉住点=55 与本地 `git describe` 吻合佐证）；master HEAD 2026-10-18（访问前 2 天仍有提交，仓库活跃、未归档）；**release 策略停在 v8.0（2024-11-03）**，之后只滚动 master 不打 tag。钉住后主要变更（未逐条复核）：llms.txt 支持、hiddenInRss、CSS `.post-content`→`.md-content` 重构、audio/video shortcodes、一批 Hugo 上游 tpl 补丁移植。
2. **Hugo 解析**：`themesDir` 默认 `themes`；官方明示 **theme 名必须匹配 themes/ 下目录名**（改名则 hugo.toml theme 字段必须同步改）；项目 layouts 与主题同名文件「项目在最左、文件级合并、最左优先」；**themes/ 下普通目录即 vendored 主题，Hugo 不感知 git/子模块，构建行为等价**（PaperMod wiki 四种安装方式对 Hugo 完全等价的官方表述佐证）。
3. **vendor 化路径**：`git rm --cached themes/PaperMod`（只摘 index gitlink、不动 .gitmodules、工作区原样）→ 删 `.gitmodules` → `git add themes/PaperMod` → commit；actions/checkout **默认 submodules: false 不拉子模块**——移除后主题文件随主检出入库，**构建正确性不依赖改 deploy.yml**（`submodules: true` 留否属清理性决策）。
4. **MIT**：最低义务=分发时随附版权声明与许可声明（仓库保留 LICENSE+原版权行即常规满足；私有部署不触发分发义务）；PaperMod **无强制署名/页脚鸣谢条款**（README/wiki 的 star/sponsor 均为自愿请求）。
5. **上游指导**：官方 quick start 仍教子模块；独立的 theme-management 页已 404；modules 提供版本化可复现路径（go.mod/go.sum、`hugo mod vendor`，且 **themes/ 下目录不参与 vendor**）；官方页未见「modules 取代 submodule」的逐字推荐；**无官方「fork 后如何跟随上游」专指南**（社区实践=留 upstream remote 按需 merge）。

**下游影响**：0029 的形态三选一（vendored 原名/改名/modules 指向 fork 仓）有解析机制事实；0031 的 CI 触点范围明确（构建不依赖 deploy.yml 改动）；0033 的上游关系有 92 提交差距 + 无官方指南事实；许可证落点明确。
