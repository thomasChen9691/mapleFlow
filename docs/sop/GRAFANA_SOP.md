# Grafana 标准操作规范（SOP）

## 1. 简介

Grafana 是开源的可视化与告警平台，可对接 Prometheus、InfluxDB、Elasticsearch、MySQL 等多种数据源，用于仪表盘、告警和探索式查询。

- **典型场景**：监控大屏、业务/系统指标看板、告警规则配置与通知（邮件、钉钉、Slack 等）。

---

## 2. 安装与基本配置

### 2.1 Docker 快速启动

```bash
docker run -d --name=grafana -p 3000:3000 grafana/grafana:latest

# 默认访问：http://localhost:3000
# 默认账号/密码：admin / admin（首次登录需修改）
```

### 2.2 持久化与常用环境变量

```bash
docker run -d --name=grafana -p 3000:3000 \
  -v grafana_data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=your_password \
  -e GF_USERS_ALLOW_SIGN_UP=false \
  grafana/grafana:latest
```

### 2.3 系统级安装（Ubuntu）

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update && sudo apt-get install -y grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

---

## 3. 常用操作与命令

### 3.1 数据源（Prometheus 示例）

- **Web**：Configuration → Data sources → Add data source → Prometheus。
- **URL**：如 `http://prometheus:9090`（容器内用服务名），保存 & Test。

### 3.2 仪表盘

- **新建**：+ → Dashboard → Add visualization，选择数据源与查询（如 PromQL）。
- **导入**：+ → Import，输入官方或社区 Dashboard ID（如 1860 Node Exporter），Load 后选择数据源。
- **变量**：Dashboard settings → Variables，可建 instance、job 等变量，在 Panel 的 Query 中使用 `$variable`。

### 3.3 告警

- **Alerting**（新）：
  - Alert rules → New alert rule：选择 Query、条件（如 avg() of A > 1）、评估周期与 Contact point。
  - Contact points：配置通知渠道（Email、钉钉、Slack、Webhook 等）。
- **旧版**：在 Panel 的 Alert 页签配置（逐步迁移到新 Alerting）。

### 3.4 用户与权限

- **Admin**：Configuration → Users 可创建/禁用用户、改密码。
- **Organization**：可多 Org，不同 Org 下数据源与 Dashboard 隔离。
- **Folder**：对 Dashboard 分组，可配置权限（Viewer/Editor/Admin）。

### 3.5 备份与恢复（文件）

```bash
# 备份（默认 SQLite 或你配置的 DB 由 Grafana 自己管理）
# 主要备份：/var/lib/grafana/grafana.db、provisioning、plugins
docker cp grafana:/var/lib/grafana ./grafana_backup

# 恢复：将备份目录挂载或复制回容器内对应路径，重启
```

### 3.6  provisioning（YAML 配置数据源/仪表盘）

```yaml
# provisioning/datasources/ds.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

启动时挂载：`-v ./provisioning:/etc/grafana/provisioning`。

---

## 4. 日常操作流程（SOP）

### 4.1 新数据源接入

1. Configuration → Data sources → Add，选择类型并填写 URL 与认证（如需）。
2. Save & test，确认 “Data source is working”。

### 4.2 新建/克隆仪表盘

1. 新建：+ → Dashboard，添加 Panel，写查询与图类型。
2. 克隆：打开已有 Dashboard → Dashboard settings → Save as，另存为新名称。

### 4.3 配置告警

1. 在对应 Panel 或 Alerting → Alert rules 新建规则。
2. 设置条件、Evaluate 间隔、Contact point。
3. 在 Contact points 中配置接收人/群（邮件、钉钉等），测试通知。

### 4.4 定期检查

- 检查数据源是否正常（Data source 列表里可看到最后查询时间）。
- 检查告警规则是否触发、通知是否收到；必要时调整阈值或静默。

---

## 5. 故障排查

| 现象 | 排查方法 |
|------|----------|
| 无法登录 | 重置 admin 密码（见下）、检查 LDAP/OAuth 配置 |
| 数据源报错 | 检查 URL、网络、认证；在 Explore 里直接跑查询测试 |
| 面板无数据 | 检查时间范围、PromQL/查询语法、数据源是否有该指标 |
| 告警不触发 | 检查规则条件、Evaluate 周期、Contact point 是否保存并启用 |
| 启动失败 | 查看日志、检查端口占用、DB 连接与权限 |

### 重置 admin 密码（CLI）

```bash
# 若使用默认 SQLite
grafana-cli admin reset-admin-password newpassword

# Docker
docker exec -it grafana grafana-cli admin reset-admin-password newpassword
```

### 查看日志

```bash
# Docker
docker logs grafana -f

# 系统安装
sudo journalctl -u grafana-server -f
```

---

## 6. 参考链接

- [Grafana 官方文档](https://grafana.com/docs/grafana/latest/)
- [Prometheus 数据源](https://grafana.com/docs/grafana/latest/datasources/prometheus/)
- [Alerting 文档](https://grafana.com/docs/grafana/latest/alerting/)
