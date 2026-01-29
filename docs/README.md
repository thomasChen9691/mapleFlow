# 文档目录

本目录包含 MapleFlow 项目的所有文档。

## 📚 文档列表

### 后端 API 文档

- **[BACKEND_DOCS.md](BACKEND_DOCS.md)** ⭐ **主要文档**
  - 完整的后端 API 文档（整合版）
  - 包含快速开始、API 端点、测试方法、常见问题等
  - **推荐在 OpenSpec 中引用此文档**

### OpenSpec 相关

- **[OPENSPEC_GUIDE.md](OPENSPEC_GUIDE.md)** ⭐ **OpenSpec 使用指南**
  - 如何在 Cursor 中使用 OpenSpec
  - 命令说明和工作流程
  - **首次使用 OpenSpec 必读**

### 其他文档

- **[CHANGELOG.md](CHANGELOG.md)**
  - 更新日志
  - 记录所有变更和改进

### 压缩文件

- **[backend_docs.zip](backend_docs.zip)**
  - 所有 Markdown 文档的压缩包
  - 便于备份和分享

## 🚀 快速开始

### 使用 OpenSpec 管理项目

1. **阅读 OpenSpec 指南**
   ```
   查看 docs/OPENSPEC_GUIDE.md
   ```

2. **在 Cursor 中使用 OpenSpec**
   ```
   在 Cursor 聊天框中输入：/opsx:onboard
   ```

3. **创建新变更**
   ```
   在 Cursor 聊天框中输入：/opsx:new <your-feature-name>
   ```

### 查看后端 API 文档

1. **完整文档**
   ```
   查看 docs/BACKEND_DOCS.md
   ```

2. **测试 API**
   ```bash
   python test_api.py
   ```

## 📖 文档使用建议

### 对于 OpenSpec 用户

- 在创建 Proposal 或 Specs 时，引用 `BACKEND_DOCS.md` 作为参考
- 使用 `OPENSPEC_GUIDE.md` 了解如何使用 OpenSpec
- 压缩文件 `backend_docs.zip` 可以用于备份

### 对于开发者

- 查看 `BACKEND_DOCS.md` 了解完整的 API 文档
- 文档中包含快速开始指南和测试说明

### 对于维护者

- 更新 `CHANGELOG.md` 记录所有变更
- 保持 `BACKEND_DOCS.md` 与代码同步
- 定期更新压缩文件

## 🔗 相关链接

- [项目主 README](../README.md)
- [OpenSpec 配置](../openspec/config.yaml)
- [后端代码](../backend/)

## 📝 文档更新

所有文档更新都应该：
1. 更新相应的 Markdown 文件
2. 更新 `CHANGELOG.md`
3. 重新生成压缩文件（如需要）

---

**提示**: 在 Cursor IDE 中使用 OpenSpec 时，所有命令都是在聊天界面中输入，不是在终端中执行。
