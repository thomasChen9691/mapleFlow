+++
title = 'GitLab 标准操作规范（SOP）'
date = '2026-01-28T20:05:00+08:00'
draft = false
categories = ['运维']
tags = ['GitLab', 'CI/CD', 'DevOps', 'SOP', '速查']
+++

GitLab 是集代码托管、CI/CD、制品仓库、Wiki、Issue 等于一体的 DevOps 平台。本文整理安装、常用 Git/MR 操作、`.gitlab-ci.yml` 示例与日常 SOP，便于在网页上查阅。

---

## 1. 简介

- **典型场景**：代码仓库、MR/Code Review、CI/CD Pipeline、容器镜像仓库、项目管理。

---

## 2. 安装与访问

### 2.1 快速安装（Linux）

```bash
# 使用官方脚本（Omnibus，含 Nginx/PostgreSQL/Redis）
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | sudo bash
sudo EXTERNAL_URL="https://gitlab.example.com" apt install gitlab-ee

# 或 Docker
docker run -d --hostname gitlab.example.com -p 443:443 -p 80:80 -p 22:22 --name gitlab gitlab/gitlab-ee:latest
```

### 2.2 常用管理命令

```bash
# 重新配置
sudo gitlab-ctl reconfigure

# 服务状态
sudo gitlab-ctl status

# 启动/停止/重启
sudo gitlab-ctl start
sudo gitlab-ctl stop
sudo gitlab-ctl restart

# 查看日志
sudo gitlab-ctl tail          # 所有服务
sudo gitlab-ctl tail nginx    # 指定服务
```

### 2.3 首次登录

- 默认账号：`root`
- 首次登录会要求修改密码；或通过 `sudo gitlab-rake "gitlab:password:reset[root]"` 重置。

---

## 3. 常用 Git 与 GitLab 操作

### 3.1 Git 基础命令

```bash
# 克隆
git clone https://gitlab.example.com/group/project.git
git clone git@gitlab.example.com:group/project.git

# 分支与提交
git checkout -b feature/xxx
git add .
git commit -m "feat: xxx"
git push -u origin feature/xxx
```

### 3.2 合并请求（Merge Request）

1. 在 GitLab 网页上基于分支创建 MR。
2. 或使用 CLI（需安装 [gitlab-cli](https://gitlab.com/gitlab-org/cli)）：

```bash
# 创建 MR
glab mr create -t "标题" -d "描述" -b main

# 列表与查看
glab mr list
glab mr view 123

# 合并
glab mr merge 123
```

### 3.3 标签与发布

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

在 GitLab：Project → Deploy → Releases 可基于 Tag 创建 Release。

---

## 4. CI/CD（.gitlab-ci.yml）

### 4.1 最小 Pipeline 示例

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - echo "Building..."
    - make build
  only:
    - main
    - tags

test:
  stage: test
  script:
    - make test
  only:
    - main
    - merge_requests

deploy_staging:
  stage: deploy
  script:
    - echo "Deploy to staging"
    - ./deploy.sh staging
  environment: staging
  only:
    - main
  when: manual
```

### 4.2 常用全局配置

```yaml
default:
  image: alpine:latest
  before_script:
    - apk add --no-cache git
  after_script:
    - echo "Job finished"

variables:
  DEPLOY_ENV: staging
  DOCKER_DRIVER: overlay2
```

### 4.3 常用 Job 关键字

| 关键字 | 说明 |
|--------|------|
| `stage` | 所属阶段 |
| `script` | 要执行的命令 |
| `only` / `except` | 触发分支/条件 |
| `rules` | 更细的触发规则 |
| `when` | on_success / on_failure / manual / always |
| `artifacts` | 产物保存与传递 |
| `cache` | 缓存目录 |
| `environment` | 环境（staging/production） |
| `needs` | 依赖的 job，可跳过阶段 |

---

## 5. 日常操作流程（SOP）

### 5.1 新建项目并推送

1. 在 GitLab 创建新项目（含或不含 README）。
2. 本地：`git remote add origin <url>`，`git push -u origin main`。

### 5.2 功能开发与 MR

1. 从 `main` 拉取最新：`git checkout main && git pull`
2. 新建分支：`git checkout -b feature/xxx`
3. 开发、提交、推送：`git push -u origin feature/xxx`
4. 在 GitLab 创建 MR，指定 Reviewer，通过后合并。

### 5.3 发布与打 Tag

1. 合并到 `main` 后打 tag：`git tag -a v1.0.0 -m "Release 1.0.0"`，`git push origin v1.0.0`
2. 在 GitLab Releases 中基于该 Tag 创建 Release，填写说明与附件。

### 5.4 Pipeline 失败处理

1. 在 Project → CI/CD → Pipelines 打开失败 Pipeline。
2. 点击失败 Job 查看日志，根据报错修复代码或 CI 配置。
3. 重新运行 Job 或推送新提交触发新 Pipeline。

---

## 6. 故障排查

| 现象 | 排查方法 |
|------|----------|
| 无法克隆/推送 | 检查 SSH 密钥或 Token、网络、仓库权限 |
| Pipeline 一直 Pending | 检查 Runner 是否在线、是否被该项目使用 |
| Job 报错找不到命令 | 确认 `image` 或 `before_script` 中已安装依赖 |
| 权限不足 | 检查 Project/Group 的 Member 与 Role |
| 磁盘占满 | `sudo gitlab-ctl reconfigure`，清理 build cache、旧镜像 |

### 常用管理命令

```bash
# 进入 Rails 控制台
sudo gitlab-rails console

# 重置 root 密码
sudo gitlab-rake "gitlab:password:reset[root]"

# 检查仓库完整性
sudo gitlab-rake gitlab:check
```

---

## 7. 参考链接

- [GitLab 官方文档](https://docs.gitlab.com/)
- [GitLab CI/CD 文档](https://docs.gitlab.com/ee/ci/)
- [.gitlab-ci.yml 参考](https://docs.gitlab.com/ee/ci/yaml/)
