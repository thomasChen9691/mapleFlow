+++
title = 'SonarQube 标准操作规范（SOP）'
date = '2026-01-28T20:10:00+08:00'
draft = false
categories = ['运维']
tags = ['SonarQube', '代码质量', '安全扫描', 'SOP', '速查']
+++

SonarQube 是代码质量和安全分析平台，支持多语言，可集成到 CI/CD 中自动扫描。本文整理安装、Scanner 配置、质量门禁与日常 SOP，便于在网页上查阅。

---

## 1. 简介

- **典型能力**：代码异味、Bug、漏洞、安全热点、重复代码、覆盖率（需配合测试报告）。
- **典型场景**：MR 质量门禁、每日全量扫描、安全合规检查。

---

## 2. 安装与基本配置

### 2.1 使用 Docker 快速启动

```bash
# 需先有 PostgreSQL（或使用 SonarQube 内置 H2，仅适合试用）
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community

# 默认访问：http://localhost:9000
# 默认账号/密码：admin / admin（首次登录需修改）
```

### 2.2 与 PostgreSQL 一起运行

```bash
docker run -d --name sonar-db -e POSTGRES_USER=sonar -e POSTGRES_PASSWORD=sonar postgres:14
docker run -d --name sonarqube -p 9000:9000 \
  -e SONAR_JDBC_URL=jdbc:postgresql://sonar-db:5432/sonar \
  -e SONAR_JDBC_USERNAME=sonar -e SONAR_JDBC_PASSWORD=sonar \
  --link sonar-db sonarqube:lts-community
```

### 2.3 命令行扫描器（Scanner）

- **SonarScanner CLI**：通用扫描，适合任意语言。
- **Maven/Gradle 插件**：Java 项目常用。
- **Scanner 与 SonarQube 版本尽量与服务器大版本一致。**

```bash
# 下载 SonarScanner（以 Linux 为例）
# https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
unzip sonar-scanner-cli-*.zip
export PATH=$PATH:$(pwd)/sonar-scanner-*/bin
sonar-scanner --version
```

---

## 3. 常用命令与操作

### 3.1 项目配置（sonar-project.properties）

在项目根目录创建或编辑：

```properties
# 项目唯一标识，与 SonarQube 中创建的项目 Key 一致
sonar.projectKey=my-project
sonar.projectName=My Project

# 源码路径（相对项目根）
sonar.sources=src
sonar.exclusions=**/node_modules/**,**/dist/**,**/vendor/**

# 测试与覆盖率（可选）
sonar.tests=test
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.python.coverage.reportPaths=coverage.xml

# SonarQube 服务地址（也可用环境变量 SONAR_HOST_URL）
sonar.host.url=http://localhost:9000
# 认证 Token（推荐用 Token 代替密码）
sonar.login=your_token
```

### 3.2 执行扫描

```bash
# 使用配置文件
sonar-scanner

# 命令行覆盖部分参数
sonar-scanner -Dsonar.projectKey=my-project -Dsonar.host.url=http://sonar.company.com -Dsonar.login=token
```

### 3.3 Maven 项目

```bash
mvn clean verify sonar:sonar \
  -Dsonar.projectKey=my-project \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=your_token
```

### 3.4 生成 Token（Web）

1. 登录 SonarQube → 右上角用户 → My Account → Security。
2. 生成 Token，复制保存（只显示一次）。

---

## 4. 质量门禁与质量配置

### 4.1 质量门（Quality Gate）

- 在 Quality Gates 中可新建或复制默认门禁。
- 常见条件：Bugs=0、Vulnerabilities=0、Coverage≥80%、Duplications≤3% 等。
- 项目可绑定指定 Quality Gate；未通过时 Pipeline 可配置为失败。

### 4.2 质量配置（Quality Profile）

- 每语言一个活跃 Profile，可自定义规则开关与严重级别。
- 可基于内置 Profile 复制后调整，再设为默认。

---

## 5. 日常操作流程（SOP）

### 5.1 新项目接入

1. 在 SonarQube 中创建项目（或由首次扫描自动创建），记下 Project Key。
2. 在代码库根目录添加 `sonar-project.properties`（或 CI 中注入参数）。
3. 在 CI（Jenkins/GitLab CI 等）中增加扫描步骤，传入 `sonar.login`（Token 放 CI 变量）。
4. 跑一次 Pipeline，在 SonarQube 中确认结果并设置 Quality Gate。

### 5.2 每日/MR 扫描

- **MR**：在 CI 中配置 Sonar 扫描，并可选 Sonar 的 “Branch Analysis” 或 “Pull Request Decoration”。
- **每日**：定时任务或夜间 Pipeline 对 main 分支执行 `sonar-scanner`，关注趋势与门禁。

### 5.3 处理“失败”与误报

1. 在 SonarQube 中打开对应 Issue，确认是否为误报或可接受。
2. 确认为误报：可加注释标记（如 `// NOSONAR`）或在该规则中排除。
3. 确认为需修复：按规则说明修改代码后重新扫描。

---

## 6. 故障排查

| 现象 | 排查方法 |
|------|----------|
| 扫描报 401 | 检查 `sonar.login` Token 是否有效、是否有项目权限 |
| 扫描报 404 | 检查 `sonar.host.url`、项目 Key 是否在服务端存在 |
| 无覆盖率 | 确认测试报告路径、格式（如 lcov、cobertura）与语言一致 |
| 内存不足 | 调大 Scanner JVM：`SONAR_SCANNER_OPTS=-Xmx1024m` |
| 服务启动失败 | 查看日志、检查 JDK 版本（需 11+）、数据库连接与磁盘空间 |

### 查看服务日志（Docker）

```bash
docker logs sonarqube
docker logs sonarqube --tail 200 -f
```

---

## 7. 参考链接

- [SonarQube 官方文档](https://docs.sonarqube.org/latest/)
- [SonarScanner 文档](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/)
- [Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
