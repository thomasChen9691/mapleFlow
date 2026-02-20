# Ansible 标准操作规范（SOP）

## 1. 简介

Ansible 是一款开源的自动化运维工具，基于 Python，通过 SSH 对目标主机执行任务，无需在受管节点安装 Agent。

- **特点**：无 Agent、幂等性、YAML 剧本、模块丰富。
- **典型场景**：配置管理、应用部署、批量命令、持续交付。

---

## 2. 安装与基本配置

### 2.1 控制节点安装（Linux/macOS）

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y ansible

# CentOS/RHEL
sudo yum install -y ansible

# macOS
brew install ansible

# 使用 pip 安装（推荐指定版本）
pip install ansible-core
```

### 2.2 查看版本与配置

```bash
ansible --version
ansible-config dump --only-changed   # 查看当前生效配置
```

### 2.3 清单文件（Inventory）

默认清单：`/etc/ansible/hosts` 或项目目录下 `inventory`、`hosts`。

```ini
# 简单示例 inventory/hosts
[web]
192.168.1.10
192.168.1.11

[db]
192.168.1.20

[prod:children]
web
db
```

```yaml
# inventory.yml（YAML 格式）
all:
  children:
    web:
      hosts:
        web1:
          ansible_host: 192.168.1.10
        web2:
          ansible_host: 192.168.1.11
    db:
      hosts:
        db1:
          ansible_host: 192.168.1.20
```

### 2.4 SSH 与权限

```bash
# 使用密钥（推荐）
ssh-keygen -t ed25519 -N "" -f ~/.ssh/ansible
ssh-copy-id user@target_host

# 测试连通性
ansible all -m ping -i inventory
```

---

## 3. 常用命令

### 3.1 临时命令（Ad-hoc）

```bash
# 语法：ansible <pattern> -m <module> -a "<args>" [-i inventory]

# 连通性测试
ansible all -m ping

# 执行 shell 命令
ansible web -m shell -a "uptime"
ansible web -m command -a "df -h"   # 无 shell 解析，更安全

# 复制文件
ansible web -m copy -a "src=/local/file dest=/remote/file mode=0644"

# 安装软件包
ansible web -m apt -a "name=nginx state=present update_cache=yes" --become
ansible db -m yum -a "name=mysql-server state=present" --become

# 管理服务
ansible web -m systemd -a "name=nginx state=started enabled=yes" --become

# 收集主机信息（Facts）
ansible all -m setup
ansible all -m setup -a "filter=ansible_distribution*"
```

### 3.2 剧本（Playbook）执行

```bash
# 执行剧本（干跑不执行）
ansible-playbook playbook.yml --check --diff

# 执行剧本
ansible-playbook playbook.yml -i inventory

# 指定额外变量
ansible-playbook playbook.yml -e "env=prod" -e "version=1.0"

# 从指定 task 开始
ansible-playbook playbook.yml --start-at-task="Install nginx"

# 限制主机
ansible-playbook playbook.yml --limit web
ansible-playbook playbook.yml --limit "web1:&prod"
```

### 3.3 常用模块速查

| 模块 | 用途 | 示例 |
|------|------|------|
| `ping` | 连通性 | `-m ping` |
| `command` / `shell` | 执行命令 | `-a "ls /tmp"` |
| `copy` | 复制文件 | `src=... dest=...` |
| `template` | 模板渲染 | `src=... dest=...` |
| `apt` / `yum` | 包管理 | `name=... state=present` |
| `systemd` | 服务管理 | `name=... state=started` |
| `user` | 用户管理 | `name=... state=present` |
| `file` | 文件/目录 | `path=... state=directory` |
| `lineinfile` / `blockinfile` | 编辑文件 | 修改单行/块 |
| `git` | 克隆仓库 | `repo=... dest=...` |

---

## 4. Playbook 编写规范

### 4.1 最小示例

```yaml
# playbook.yml
---
- name: 确保 Nginx 安装并运行
  hosts: web
  become: yes
  tasks:
    - name: 安装 Nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: 启动并开机自启 Nginx
      systemd:
        name: nginx
        state: started
        enabled: yes
```

### 4.2 使用变量与 Handlers

```yaml
- hosts: web
  vars:
    app_port: 8080
    app_user: www-data
  tasks:
    - name: 部署应用包
      copy:
        src: "app-{{ version }}.tar.gz"
        dest: /opt/app/
      notify: 重启应用

  handlers:
    - name: 重启应用
      systemd:
        name: myapp
        state: restarted
```

### 4.3 目录结构建议

```
project/
├── inventory/
│   ├── hosts
│   └── group_vars/
│       ├── all.yml
│       └── prod.yml
├── roles/
│   └── nginx/
│       ├── tasks/
│       ├── handlers/
│       ├── templates/
│       └── defaults/
├── playbook.yml
└── ansible.cfg
```

---

## 5. 日常操作流程（SOP）

### 5.1 批量执行前检查

1. 确认清单正确：`ansible all -m ping -i inventory`
2. 确认权限与 sudo：`ansible all -m shell -a "whoami" --become`
3. 使用 `--check --diff` 做一次模拟执行

### 5.2 发布应用

1. 备份或打快照（如有需要）。
2. 执行部署剧本：`ansible-playbook deploy.yml -e "version=x.y.z" -i inventory`
3. 检查服务与日志：通过剧本或 Ad-hoc 执行 `systemctl status`、`tail -f log`。

### 5.3 配置变更

1. 修改对应 role 的 task/template 或 group_vars。
2. `ansible-playbook site.yml --check --diff`
3. 确认无误后：`ansible-playbook site.yml`

---

## 6. 故障排查

| 现象 | 排查命令/方法 |
|------|----------------|
| SSH 连接失败 | `ssh -v user@host`、检查防火墙与 `authorized_keys` |
| 权限不足 | 使用 `--become` 或配置 sudo 免密 |
| 模块报错 | `ansible host -m module -a "..." -vvv` 看详细输出 |
| 变量未定义 | `ansible-playbook ... -e "var=value"` 或检查 `group_vars` |
| 剧本某步失败 | 使用 `--start-at-task="Task名"` 从该任务重跑 |

### 常用调试

```bash
# 单主机、详细输出
ansible web1 -m shell -a "id" -vvv

# 列出该主机的所有 facts
ansible web1 -m setup
```

---

## 7. 参考链接

- [Ansible 官方文档](https://docs.ansible.com/)
- [Ansible Module Index](https://docs.ansible.com/ansible/latest/collections/index_module.html)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
