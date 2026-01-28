+++
title = 'Docker 常见命令与用法速查'
date = '2026-01-25T23:30:00+08:00'
draft = false
categories = ['docker']
tags = ['docker', '容器', '运维', '速查']
+++

本文整理了一些日常开发与运维中最常用的 Docker 命令，按“镜像”“容器”“日志与排错”“数据卷与网络”几个维度快速速查，适合日常翻阅。

## 一、镜像相关

### 1.1 查看、搜索、拉取镜像

```bash
# 查看本地镜像
docker images

# 在远程仓库搜索镜像
docker search nginx

# 拉取镜像（最新版）
docker pull nginx

# 拉取指定版本
docker pull nginx:1.25
```

### 1.2 删除镜像

```bash
# 删除指定镜像
docker rmi nginx:1.25

# 强制删除（比如镜像正在被容器使用）
docker rmi -f nginx:1.25

# 删除所有未被使用的镜像
docker image prune -a
```

### 1.3 构建镜像

```bash
# 在当前目录根据 Dockerfile 构建镜像
docker build -t myapp:latest .

# 指定 Dockerfile 路径
docker build -f ./deploy/Dockerfile -t myapp:1.0.0 .
```

## 二、容器生命周期

### 2.1 启动容器

```bash
# 启动一个临时容器，退出后自动删除
docker run --rm -it alpine:latest /bin/sh

# 后台启动一个命名容器并映射端口
docker run -d --name my-nginx -p 8080:80 nginx:latest

# 挂载本地目录到容器（开发常用）
docker run -d --name my-web \
  -p 3000:3000 \
  -v $(pwd):/app \
  node:18 \
  node server.js
```

### 2.2 查看、停止、删除容器

```bash
# 查看正在运行的容器
docker ps

# 查看所有容器（包含已停止）
docker ps -a

# 停止容器
docker stop my-nginx

# 启动已停止的容器
docker start my-nginx

# 删除容器（需先停止）
docker rm my-nginx

# 强制删除正在运行的容器
docker rm -f my-nginx
```

### 2.3 进入容器 / 执行命令

```bash
# 进入容器交互式 Shell
docker exec -it my-nginx /bin/bash

# 在容器中执行一次性命令
docker exec my-nginx nginx -t
```

## 三、日志与排错

```bash
# 查看容器日志（默认从头）
docker logs my-nginx

# 实时查看日志（类似 tail -f）
docker logs -f my-nginx

# 只看最后 100 行日志
docker logs --tail=100 my-nginx
```

遇到容器异常时，常规排查步骤：

1. `docker ps -a` 看容器状态和退出码  
2. `docker logs <容器名>` 看应用日志  
3. `docker inspect <容器名>` 看挂载、网络、环境变量配置是否正确  
4. `docker exec -it <容器名> /bin/sh` 进入容器排查

## 四、数据卷与持久化

### 4.1 数据卷基础

```bash
# 创建数据卷
docker volume create my-data

# 查看数据卷
docker volume ls

# 删除数据卷
docker volume rm my-data
```

### 4.2 在容器中挂载数据卷

```bash
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -v my-data:/var/lib/mysql \
  mysql:8
```

### 4.3 直接挂载主机目录

```bash
docker run -d --name my-nginx \
  -p 8080:80 \
  -v /data/nginx/html:/usr/share/nginx/html \
  nginx:latest
```

## 五、网络常用命令

```bash
# 查看网络
docker network ls

# 创建 bridge 网络
docker network create my-net

# 运行容器并加入指定网络
docker run -d --name app --network my-net myapp:latest
docker run -d --name redis --network my-net redis:latest
```

在同一自定义网络 `my-net` 下，容器可以通过“容器名”互相访问，例如：`redis:6379`。

---

后续可以在本分类下继续补充：

- 容器资源限制（CPU / 内存 / 限流）  
- 多阶段构建优化镜像体积  
- 使用 docker compose 管理多容器应用 等等。

