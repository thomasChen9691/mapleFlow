+++
title = 'Prometheus 标准操作规范（SOP）'
date = '2026-01-28T20:25:00+08:00'
draft = false
categories = ['运维']
tags = ['Prometheus', '监控', 'PromQL', '告警', 'SOP', '速查']
+++

Prometheus 是开源指标采集、存储与查询系统，采用拉模式（Pull）从 Target 抓取指标，支持 PromQL 查询与告警（Alertmanager）。本文整理安装、配置、常用 API 与日常 SOP，便于在网页上查阅。

---

## 1. 简介

- **典型场景**：机器/容器/应用指标采集、监控大屏（配合 Grafana）、告警。

---

## 2. 安装与基本配置

### 2.1 Docker 快速启动

```bash
# 仅 Prometheus
docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest

# 访问：http://localhost:9090
```

### 2.2 最小 prometheus.yml

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []   # 可选：Alertmanager 地址

rule_files: []          # 可选：告警/记录规则文件

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['192.168.1.10:9100', '192.168.1.11:9100']
    # 若需认证（如 basic_auth / bearer_token），在此配置
```

### 2.3 系统级安装（Linux）

```bash
# 下载并解压
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xzf prometheus-*.tar.gz
cd prometheus-*/

# 启动（前台）
./prometheus --config.file=prometheus.yml --web.enable-lifecycle

# 或使用 systemd 管理（需自行编写 unit 文件）
```

### 2.4 常用启动参数

```bash
--config.file=prometheus.yml    # 配置文件
--storage.tsdb.path=/data       # 存储路径
--web.enable-lifecycle          # 允许 API 重载配置
--web.listen-address=:9090      # 监听地址
```

---

## 3. 常用命令与操作

### 3.1 重载配置（不重启）

```bash
# 需启用 --web.enable-lifecycle
curl -X POST http://localhost:9090/-/reload
```

### 3.2 查询（Web + PromQL）

- 打开 http://localhost:9090 → Graph，输入 PromQL 示例：

```promql
#  CPU 使用率（Node Exporter）
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 某服务 QPS
rate(http_requests_total[5m])
```

### 3.3 常用 API

```bash
# 查询瞬时值
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=up'

# 查询范围
curl -G 'http://localhost:9090/api/v1/query_range' \
  --data-urlencode 'query=up' \
  --data-urlencode 'start=...' --data-urlencode 'end=...' --data-urlencode 'step=15s'

# 查看 Target 状态
curl http://localhost:9090/api/v1/targets

# 重载配置
curl -X POST http://localhost:9090/-/reload
```

### 3.4 Node Exporter（主机指标）

```bash
# 目标机安装并暴露 9100
docker run -d --name node_exporter -p 9100:9100 --net="host" --pid="host" \
  -v "/:/host:ro,rslave" quay.io/prometheus/node-exporter:latest --path.rootfs=/host
```

在 `prometheus.yml` 的 `scrape_configs` 中增加该主机 `ip:9100`。

---

## 4. 告警规则与 Alertmanager

### 4.1 告警规则示例（rules.yml）

```yaml
groups:
  - name: example
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} down"

      - alert: HighCpu
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU on {{ $labels.instance }}"
```

在 `prometheus.yml` 中：

```yaml
rule_files:
  - "rules.yml"
```

### 4.2 Alertmanager 最小配置

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'

receivers:
  - name: 'default'
    # 示例：邮件
    # email_configs:
    #   - to: 'ops@example.com'
    #     send_resolved: true
```

启动 Alertmanager：

```bash
docker run -d --name alertmanager -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager:latest
```

在 `prometheus.yml` 的 `alerting` 中填写 `targets: ['alertmanager:9093']`。

---

## 5. 日常操作流程（SOP）

### 5.1 新增监控目标

1. 在目标机器/容器部署 Exporter（如 node_exporter、应用暴露 /metrics）。
2. 在 `prometheus.yml` 的 `scrape_configs` 中增加 job 与 targets。
3. 执行 `curl -X POST http://localhost:9090/-/reload`（或重启），在 Status → Targets 确认 UP。

### 5.2 新增/修改告警规则

1. 编辑 `rules.yml`（或新建 rule_files）。
2. 若 rule_files 已包含该文件，reload 即可；否则修改 `prometheus.yml` 后 reload。
3. 在 Alerts 页查看是否出现 Pending/Firing，并确认 Alertmanager 收到告警。

### 5.3 容量与保留

- 默认保留 15 天，可通过 `--storage.tsdb.retention.time=30d` 调整。
- 注意磁盘空间；可配合远程写入（如 Thanos、Cortex）做长期存储。

---

## 6. 故障排查

| 现象 | 排查方法 |
|------|----------|
| Target Down | 检查网络、防火墙、Exporter 是否监听、URL 是否正确 |
| 无指标/少指标 | 检查 Exporter 版本、是否启用所需 collector、应用是否暴露 /metrics |
| 查询很慢 | 缩小时间范围、简化 PromQL、检查 tsdb 磁盘与内存 |
| 告警不触发 | 检查 rule 的 expr、for 时间、Alertmanager 是否配置并可达 |
| 配置不生效 | 确认 YAML 语法、是否执行 reload 或重启 |

### 常用检查

```bash
# 检查配置文件语法
promtool check config prometheus.yml

# 检查规则文件
promtool check rules rules.yml

# 查看 TSDB 状态
curl http://localhost:9090/api/v1/status/tsdb
```

---

## 7. 参考链接

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [PromQL 文档](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alertmanager 配置](https://prometheus.io/docs/alerting/latest/configuration/)
- [Exporters 列表](https://prometheus.io/docs/instrumenting/exporters/)
