# OpenSpec 使用指南

## 什么是 OpenSpec？

OpenSpec 是一个用于管理项目变更和规范的框架，通过结构化的方式管理从提案到实现的完整流程。

## 如何在 Cursor 中使用 OpenSpec

### ⚠️ 重要提示

OpenSpec 的命令**不是在终端中执行**，而是在 **Cursor IDE 的聊天界面中使用斜杠命令**。

### 基本命令

在 Cursor 的聊天框中输入以下命令：

#### 1. `/opsx:new` - 创建新变更

创建一个新的变更（feature、fix 等）：

```
/opsx:new add-user-authentication
```

或者描述你想要做什么：

```
/opsx:new 添加用户认证功能
```

#### 2. `/opsx:continue` - 继续创建下一个工件

在创建变更后，使用此命令创建下一个工件（proposal → specs → design → tasks）：

```
/opsx:continue
```

#### 3. `/opsx:apply` - 实施任务

当任务创建完成后，使用此命令开始实施：

```
/opsx:apply
```

#### 4. `/opsx:sync` - 同步规范

将变更中的 delta specs 同步到主规范：

```
/opsx:sync <change-name>
```

#### 5. `/opsx:verify` - 验证变更

验证变更是否完成：

```
/opsx:verify <change-name>
```

#### 6. `/opsx:onboard` - 入门指南

如果你是第一次使用 OpenSpec，运行此命令获取完整指导：

```
/opsx:onboard
```

#### 7. `/opsx:explore` - 探索变更

查看现有变更的状态：

```
/opsx:explore
```

#### 8. `/opsx:ff` - Fast-forward 变更

快速完成变更（跳过某些步骤）：

```
/opsx:ff <change-name>
```

## 工作流程

OpenSpec 使用以下工作流程：

1. **Proposal（提案）** - 描述你想要做什么
2. **Specs（规范）** - 详细的需求和规范
3. **Design（设计）** - 技术设计和架构
4. **Tasks（任务）** - 具体的实施任务

### 示例流程

```
1. /opsx:new add-api-endpoint
   → 创建变更目录和初始文件

2. /opsx:continue
   → 创建 Proposal

3. /opsx:continue
   → 创建 Specs

4. /opsx:continue
   → 创建 Design

5. /opsx:continue
   → 创建 Tasks

6. /opsx:apply
   → 开始实施任务
```

## 项目结构

OpenSpec 会在项目中创建以下结构：

```
openspec/
├── config.yaml              # OpenSpec 配置
├── changes/                 # 所有变更
│   └── <change-name>/       # 单个变更
│       ├── proposal.md      # 提案
│       ├── specs/           # 规范
│       ├── design/          # 设计
│       └── tasks/           # 任务
└── specs/                   # 主规范（合并后的规范）
```

## 使用文档管理

### 文档压缩

为了便于 OpenSpec 管理，所有后端文档已整合到：

- `docs/BACKEND_DOCS.md` - 完整的后端文档（整合版）

### 在 OpenSpec 中引用文档

在创建 Proposal 或 Specs 时，可以引用文档：

```markdown
参考文档：docs/BACKEND_DOCS.md

根据文档中的 API 端点说明，我们需要...
```

## 常见问题

### Q: 为什么 `/opsx:new` 在终端中不工作？

**A:** OpenSpec 的命令是在 Cursor IDE 的聊天界面中使用，不是在终端中。在 Cursor 的聊天框中输入命令即可。

### Q: 如何查看所有可用的 OpenSpec 命令？

**A:** 在 Cursor 聊天框中输入 `/opsx` 然后按 Tab 键，或者查看 `.cursor/commands/` 目录。

### Q: 如何开始使用 OpenSpec？

**A:** 运行 `/opsx:onboard` 命令，它会引导你完成第一个完整的变更流程。

### Q: 如何管理文档？

**A:** 
1. 将相关文档放在 `docs/` 目录
2. 在创建变更时引用这些文档
3. 使用 `docs/BACKEND_DOCS.md` 作为主要参考文档

## 下一步

1. 运行 `/opsx:onboard` 开始学习
2. 运行 `/opsx:new <your-feature>` 创建你的第一个变更
3. 参考 `docs/BACKEND_DOCS.md` 了解后端 API 详情
