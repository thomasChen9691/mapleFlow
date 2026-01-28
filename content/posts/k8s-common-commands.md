+++
title = 'Kubernetes 常见命令与日常用法'
date = '2026-01-26T23:45:00+08:00'
draft = false
categories = ['k8s']
tags = ['kubernetes', 'k8s', '容器编排', '运维']
+++

Kubernetes（K8s）已经成为容器编排的事实标准，日常开发和运维中最常用的就是 `kubectl` 命令。
本文从「集群信息」「工作负载」「配置与排错」几个维度整理常用命令，方便快速查阅。

---

## 一、基础与集群信息

### 1.1 查看集群与上下文

```bash
# 查看当前 kubectl 使用的上下文（集群 + 用户 + 命名空间）
kubectl config current-context

# 查看所有上下文
kubectl config get-contexts

# 切换上下文
kubectl config use-context your-context-name
```

### 1.2 查看集群组件与节点

```bash
# 查看集群信息概览
kubectl cluster-info

# 查看所有节点
kubectl get nodes

# 查看节点详情（含标签与状态）
kubectl describe node <node-name>
```

---

## 二、命名空间与资源概览

### 2.1 命名空间

```bash
# 查看所有命名空间
kubectl get ns

# 创建命名空间
kubectl create namespace dev

# 删除命名空间
kubectl delete namespace dev
```

### 2.2 按命名空间查看资源

```bash
# 查看指定命名空间下的 Pod
kubectl get pods -n dev

# 查看所有命名空间下的 Pod
kubectl get pods -A

# 查看命名空间下所有常见资源
kubectl get all -n dev
```

---

## 三、Pod 与 Deployment 管理

### 3.1 查看与过滤 Pod

```bash
# 查看当前命名空间 Pod
kubectl get pods

# 按标签选择 Pod
kubectl get pods -l app=myapp

# 以 wide 模式显示更多信息（节点、IP 等）
kubectl get pods -o wide
```

### 3.2 Deployment 常用操作

```bash
# 查看 Deployment
kubectl get deploy
kubectl get deploy -n dev

# 查看 Deployment 详情
kubectl describe deploy myapp-deployment

# 伸缩副本数
kubectl scale deploy myapp-deployment --replicas=5

# 滚动更新镜像
kubectl set image deploy/myapp-deployment myapp-container=myrepo/myapp:1.1.0
```

### 3.3 快速创建 Deployment

```bash
# 使用命令行快速创建一个 Deployment 和 Service
kubectl create deploy nginx-deploy --image=nginx:1.25
kubectl expose deploy nginx-deploy --port=80 --target-port=80 --type=ClusterIP
```

---

## 四、Service 与 Ingress

### 4.1 Service

```bash
# 查看所有 Service
kubectl get svc

# 查看 Service 详情
kubectl describe svc my-service
```

常见类型：

- `ClusterIP`：集群内访问（默认）
- `NodePort`：对外暴露一个节点端口
- `LoadBalancer`：云厂商负载均衡

### 4.2 Ingress（如集群已安装 Ingress Controller）

```bash
# 查看 Ingress
kubectl get ingress -A

# 查看 Ingress 详情
kubectl describe ingress my-ingress -n dev
```

---

## 五、排错：日志、事件、进入容器

### 5.1 查看 Pod 日志

```bash
# 查看指定 Pod 日志
kubectl logs my-pod

# Pod 有多个容器时指定容器
kubectl logs my-pod -c sidecar

# 实时查看日志（类似 tail -f）
kubectl logs -f my-pod

# 只看最近 100 行
kubectl logs --tail=100 my-pod
```

### 5.2 进入容器执行命令

```bash
# 进入容器交互式 Shell
kubectl exec -it my-pod -- /bin/bash

# 容器是精简镜像（如 alpine），用 sh
kubectl exec -it my-pod -- /bin/sh
```

### 5.3 查看事件与描述资源

```bash
# 查看最近的事件（排查调度失败、镜像拉取失败等）
kubectl get events --sort-by=.lastTimestamp

# describe 是排错的利器
kubectl describe pod my-pod
kubectl describe deploy myapp-deployment
kubectl describe node my-node
```

---

## 六、配置管理：ConfigMap 与 Secret

### 6.1 ConfigMap

```bash
# 从字面量创建 ConfigMap
kubectl create configmap app-config \
  --from-literal=ENV=prod \
  --from-literal=LOG_LEVEL=info

# 从文件创建 ConfigMap
kubectl create configmap app-config-file \
  --from-file=config.yaml

# 查看 ConfigMap
kubectl get configmap
kubectl describe configmap app-config
```

### 6.2 Secret

```bash
# 从字面量创建 Secret（会自动做 base64 编码）
kubectl create secret generic db-secret \
  --from-literal=USER=root \
  --from-literal=PASSWORD=123456

# 查看 Secret（内容是 base64）
kubectl get secret
kubectl describe secret db-secret
```

---

## 七、YAML 与 dry-run

日常推荐使用 YAML 文件来管理资源，配合 `--dry-run` 和 `-o yaml` 可以快速生成模板。

```bash
# 生成 Deployment YAML 模板而不真正创建
kubectl create deploy myapp \
  --image=myrepo/myapp:latest \
  --dry-run=client -o yaml > myapp-deploy.yaml

# 应用/更新 YAML
kubectl apply -f myapp-deploy.yaml

# 删除 YAML 中定义的资源
kubectl delete -f myapp-deploy.yaml
```

---

## 八、日常排错小套路总结

1. **先看 Pod 状态**：`kubectl get pods -o wide`  
2. **看事件和 describe**：`kubectl describe pod <name>`  
3. **看日志**：`kubectl logs -f <pod>`  
4. **进容器排查**：`kubectl exec -it <pod> -- /bin/sh`  
5. **检查 Deployment / Service / Ingress 是否匹配**：端口、标签、选择器是否一致。  

后续你可以在 `k8s` 分类下继续补充：

- HPA（自动扩缩容）  
- StatefulSet / DaemonSet 使用场景  
- 使用 `kubectl top` 查看资源使用情况 等等。

