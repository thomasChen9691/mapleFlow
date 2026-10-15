# 运维工具 SOP 文档索引

本目录包含 Ansible、GitLab、SonarQube、Jenkins、Grafana、Prometheus 的标准操作规范（SOP）文档，用于学习与日常运维参考。

**发布机制（SOP 发布管线，wayfinder 工单 0008/0009 决议）**：本目录是 6 篇工具 SOP 的**唯一真源**。发布声明登记在 `data/sop.yaml` 注册表（slug / 日期 / 分类 / 标签 / 描述 / 导语），构建期由 `content/posts/_content.gotmpl` 从源笔记派生文章——磁盘上没有第二份 .md。新增一篇的流程：写笔记 → 加注册条目；没有注册条目的笔记 = 尚未发布的稿件。下表所列笔记与注册表由 `tests/assert_sop_pipeline.py` 双向守护，漏改即 CI 红。

**不发布**：`MAPLEFLOW_BLOG_SOP.md` 是本博客的人类向维护 SOP（与 AGENTS.md 同域），不在发布管线内，注册表不收。

## 文档列表（本目录 Markdown）

| 工具 | 文档 | 说明 |
|------|------|------|
| Ansible | [ANSIBLE_SOP.md](ANSIBLE_SOP.md) | 自动化配置管理与批量操作 |
| GitLab | [GITLAB_SOP.md](GITLAB_SOP.md) | 代码仓库与 CI/CD 平台 |
| SonarQube | [SONARQUBE_SOP.md](SONARQUBE_SOP.md) | 代码质量与安全扫描 |
| Jenkins | [JENKINS_SOP.md](JENKINS_SOP.md) | 持续集成与持续部署 |
| Grafana | [GRAFANA_SOP.md](GRAFANA_SOP.md) | 监控可视化与告警 |
| Prometheus | [PROMETHEUS_SOP.md](PROMETHEUS_SOP.md) | 指标采集与存储 |

## 使用说明

- 每份 SOP 包含：简介、安装/配置、常用命令、日常操作流程、故障排查、参考链接。
- 建议按学习顺序：GitLab → Jenkins/SonarQube → Ansible → Prometheus → Grafana。
- 线上阅读：本站「运维」分类，或通过运维工具 SOP 文档索引一文（`/posts/sop-ops-tools-index.html`）跳转各篇。
