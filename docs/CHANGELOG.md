# 更新日志

## 2026-01-29

### 新增功能
- ✅ 创建 FastAPI 后端服务，支持获取博客内容
- ✅ 实现博客文章解析器，支持 Hugo front matter 格式
- ✅ 添加搜索功能，支持按标题、内容、标签、分类搜索
- ✅ 创建跨平台 Python 测试脚本 (`test_api.py`)

### 修复问题
- ✅ **修复中文编码问题**
  - 添加自定义 `UTF8JSONResponse` 类
  - JSON 序列化时设置 `ensure_ascii=False`
  - 确保所有响应使用 UTF-8 编码
  - 文件读取使用 UTF-8 编码
  
- ✅ **跨平台支持**
  - 移除 PowerShell 脚本，改用 Python 脚本
  - 测试脚本支持 Linux/macOS/Windows
  - 自动处理不同平台的编码问题

### 文档更新
- ✅ 创建 `docs/` 文件夹统一管理文档
- ✅ 更新后端使用文档 (`docs/README_BACKEND.md`)
- ✅ 添加 API 测试说明 (`docs/API_TEST_SUMMARY.md`)
- ✅ 添加更新日志 (`docs/CHANGELOG.md`)

### 技术改进
- ✅ 使用 uv 进行包管理
- ✅ Python 3.13 支持
- ✅ 虚拟环境配置
- ✅ 环境变量管理 (`.env` 文件)

## 已知问题

### 终端编码问题（Windows）
在 Windows PowerShell 中直接使用 `curl` 或 Python 单行命令时，可能遇到中文乱码。这是 Windows 终端编码设置的问题，不是 API 的问题。

**解决方案：**
1. 使用 `python test_api.py` 脚本（推荐）
2. 使用浏览器访问 http://localhost:8000/docs
3. 设置 PowerShell 编码：`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`

### API 响应编码
API 本身已正确配置 UTF-8 编码，所有 JSON 响应都使用 `ensure_ascii=False`，确保中文内容正确传输。
