# Jenkins 标准操作规范（SOP）

## 1. 简介

Jenkins 是开源的持续集成/持续部署（CI/CD）服务器，通过任务（Job/Pipeline）执行构建、测试、部署等流水线。

- **典型场景**：代码拉取、编译、单元测试、代码扫描、构建镜像、部署到测试/生产。

---

## 2. 安装与基本配置

### 2.1 使用 Docker 快速启动

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# 首次启动后从日志获取初始密码：
docker logs jenkins
# 访问 http://localhost:8080 输入该密码，安装推荐插件并创建管理员用户
```

### 2.2 常用管理命令（系统级）

```bash
# 以 systemd 为例
sudo systemctl start jenkins
sudo systemctl stop jenkins
sudo systemctl restart jenkins
sudo systemctl status jenkins

# 查看日志
sudo journalctl -u jenkins -f
# 或
sudo tail -f /var/log/jenkins/jenkins.log
```

### 2.3 常用 Jenkins 操作（Web）

- **新建任务**：New Item → 选择 Freestyle 或 Pipeline。
- **配置**：源码（Git）、触发方式（轮询/Webhook）、构建步骤、构建后操作。
- **Pipeline**：使用 Jenkinsfile（Pipeline as Code）。

---

## 3. 常用命令与脚本

### 3.1 Jenkins CLI（可选）

```bash
# 从 Web：Manage Jenkins → Manage CLI 下载 jenkins-cli.jar
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth user:token list-jobs
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth user:token build "JobName"
```

### 3.2 触发构建（API）

```bash
# 使用 API Token（用户设置中生成）
curl -X POST "http://localhost:8080/job/MyJob/build" --user "user:api_token"

# 带参数
curl -X POST "http://localhost:8080/job/MyJob/buildWithParameters?ENV=prod&VERSION=1.0" --user "user:api_token"

# 触发并等待结果（Crumb 需先获取，见官方文档）
curl -X POST "http://localhost:8080/job/MyJob/build" --user "user:api_token" -H "Jenkins-Crumb: xxx"
```

### 3.3 Pipeline 语法（Jenkinsfile 示例）

```groovy
pipeline {
  agent any
  environment {
    REGISTRY = 'myregistry.com'
    IMAGE = 'myapp'
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Build') {
      steps {
        sh 'make build'
      }
    }
    stage('Test') {
      steps {
        sh 'make test'
      }
    }
    stage('Sonar') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh 'sonar-scanner'
        }
      }
    }
    stage('Docker') {
      steps {
        sh "docker build -t ${REGISTRY}/${IMAGE}:${env.BUILD_NUMBER} ."
        sh "docker push ${REGISTRY}/${IMAGE}:${env.BUILD_NUMBER}"
      }
    }
    stage('Deploy Staging') {
      steps {
        sh "./deploy.sh staging ${env.BUILD_NUMBER}"
      }
    }
  }
  post {
    failure {
      mail to: 'team@example.com', subject: "Build Failed: ${env.JOB_NAME}", body: "${env.BUILD_URL}"
    }
  }
}
```

---

## 4. 常用操作速查

### 4.1 凭证与凭据

- **Manage Jenkins → Credentials**：添加 Username/Password、SSH Key、Secret Text（如 API Token）。
- Pipeline 中使用：`credentials('credential-id')` 或 `withCredentials([...])`。

### 4.2 节点与 Agent

- **Manage Jenkins → Nodes**：添加 Agent（物理机/虚拟机/容器），标签如 `docker`、`linux`。
- Pipeline 中：`agent { label 'docker' }` 指定在该节点执行。

### 4.3 常用插件

| 插件 | 用途 |
|------|------|
| Git / GitLab | 拉取代码、MR 状态更新 |
| Pipeline | Pipeline as Code |
| Blue Ocean | 新 UI |
| Docker Pipeline | 在 Pipeline 中 build/push 镜像 |
| SonarQube Scanner | 集成 Sonar 扫描 |
| Credentials Binding | 安全注入密码等 |

---

## 5. 日常操作流程（SOP）

### 5.1 新建 Pipeline 任务

1. New Item → 输入名称 → 选择 Pipeline。
2. Pipeline 定义选择 “Pipeline script from SCM”，选择仓库与 Jenkinsfile 路径。
3. 配置触发（如 GitLab webhook、轮询），保存。

### 5.2 发布/部署流程

1. 确认参数（如 ENV、VERSION）在 “Build with Parameters” 中已配置。
2. 点击 “Build with Parameters”，选择参数后执行。
3. 在 Console Output 中查看日志；失败时根据报错修复代码或流水线。

### 5.3 失败重跑与清理

- **重跑**：进入某次 Build → “Rebuild”。
- **清理工作空间**：进入 Job → “Workspace” → “Wipe out current workspace” 或脚本中 `cleanWs()`。

---

## 6. 故障排查

| 现象 | 排查方法 |
|------|----------|
| 构建一直 Pending | 检查 Agent 是否在线、标签是否匹配、执行器数量 |
| 拉代码失败 | 检查 Credentials、网络、仓库 URL 与权限 |
| 权限/脚本报错 | 检查用户权限、脚本权限（如 `sh` 步骤） |
| 磁盘占满 | 清理工作空间、配置 “Discard old builds” 策略、清理全局缓存 |
| 插件冲突 | 在 Manage Jenkins → Plugins 中禁用/升级插件，必要时备份后重装 |

### 查看构建日志

- 进入具体 Build → Console Output；或通过 API：`/job/JobName/lastBuild/consoleText`。

---

## 7. 参考链接

- [Jenkins 官方文档](https://www.jenkins.io/doc/)
- [Pipeline 语法](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Pipeline 步骤参考](https://www.jenkins.io/doc/pipeline/steps/)
