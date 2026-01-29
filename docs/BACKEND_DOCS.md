# MapleFlow Backend API 完整文档

本文档整合了所有后端 API 相关文档，便于 OpenSpec 管理。

---

## 目录

1. [快速开始](#快速开始)
2. [环境要求与安装](#环境要求与安装)
3. [API 端点](#api-端点)
4. [测试 API](#测试-api)
5. [中文编码支持](#中文编码支持)
6. [常见问题](#常见问题)
7. [更新日志](#更新日志)

---

## 快速开始

### 1. 启动服务

```bash
# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\Activate.ps1

# 启动服务
python run_backend.py
```

### 2. 运行测试脚本

在另一个终端运行：

```bash
# Linux/macOS/Windows
python test_api.py
```

测试脚本会自动检查所有 API 端点，并正确显示中文内容。

### 3. 验证编码

```bash
python verify_encoding.py
```

### 4. 使用浏览器测试

访问 http://localhost:8000/docs 查看交互式 API 文档。

---

## 环境要求与安装

### 环境要求

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - 快速 Python 包管理器

### 安装依赖

使用 uv 安装项目依赖：

```bash
# 安装 uv (如果还没有安装)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 创建虚拟环境（Python 3.13）
uv venv --python 3.13

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\Activate.ps1

# 安装项目依赖
uv pip install -e .
```

或者使用 uv 的同步功能：

```bash
uv sync
```

### 配置环境变量

1. 复制 `.env.example` 为 `.env`：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API keys：
```env
QWEN_API_KEY=your_actual_qwen_api_key
DEEPSEEK_API_KEY=your_actual_deepseek_api_key
MCP_API_KEY=your_actual_mcp_api_key
MCP_BASE_URL=https://api.mcp.example.com
```

---

## API 端点

### GET `/`
根端点，返回 API 信息。

**响应示例：**
```json
{
  "message": "MapleFlow Blog API",
  "version": "0.1.0",
  "endpoints": {
    "posts": "/api/posts",
    "post_by_slug": "/api/posts/{slug}",
    "health": "/health"
  }
}
```

### GET `/health`
健康检查端点。

**响应示例：**
```json
{
  "status": "healthy"
}
```

### GET `/api/posts`
获取所有博客文章列表。

**查询参数：**
- `include_drafts` (bool, 默认: false): 是否包含草稿文章
- `limit` (int, 可选): 限制返回数量
- `offset` (int, 默认: 0): 分页偏移量

**示例：**
```bash
curl http://localhost:8000/api/posts?include_drafts=false&limit=10
```

**响应示例：**
```json
{
  "posts": [
    {
      "front_matter": {
        "title": "文章标题",
        "date": "2026-01-27T00:00:00+08:00",
        "draft": false,
        "categories": ["分类"],
        "tags": ["标签1", "标签2"]
      },
      "content": "文章内容...",
      "filename": "post.md",
      "slug": "post-slug"
    }
  ],
  "total": 1
}
```

### GET `/api/posts/{slug}`
根据 slug 获取单篇文章。

**示例：**
```bash
curl http://localhost:8000/api/posts/aiops-state-and-tools
```

**响应示例：**
```json
{
  "front_matter": {
    "title": "文章标题",
    "date": "2026-01-27T00:00:00+08:00",
    "draft": false,
    "categories": ["分类"],
    "tags": ["标签"]
  },
  "content": "完整的文章内容...",
  "filename": "aiops-state-and-tools.md",
  "slug": "aiops-state-and-tools"
}
```

### GET `/api/posts/search?q={query}`
搜索博客文章（标题、内容、标签、分类）。

**查询参数：**
- `q` (string, 必需): 搜索关键词
- `include_drafts` (bool, 默认: false): 是否包含草稿文章

**示例：**
```bash
curl "http://localhost:8000/api/posts/search?q=docker"
```

**响应示例：**
```json
{
  "posts": [
    {
      "front_matter": {
        "title": "匹配的文章标题",
        ...
      },
      ...
    }
  ],
  "total": 1
}
```

---

## 测试 API

### 使用 Python 测试脚本（推荐）

```bash
# 确保服务正在运行
python run_backend.py

# 在另一个终端运行测试
python test_api.py
```

测试脚本会检查：
1. ✅ 健康检查端点
2. ✅ 获取所有文章
3. ✅ 获取单篇文章
4. ✅ 搜索功能
5. ✅ 环境变量配置

### 使用 curl 测试（Linux/macOS）

```bash
# 设置 UTF-8 环境变量
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 测试 API
curl http://localhost:8000/api/posts | python -m json.tool
```

**注意**: 直接使用 `curl` 可能在终端显示乱码，建议：
1. 使用 `python test_api.py` 脚本（推荐）
2. 通过 `python -m json.tool` 管道输出
3. 在浏览器中访问 API 文档页面

### 使用 Python requests

```python
import requests
import json

# 获取所有文章
response = requests.get("http://localhost:8000/api/posts")
response.encoding = 'utf-8'
data = response.json()

print(f"总数: {data['total']}")
for post in data['posts']:
    print(f"- {post['front_matter']['title']}")
```

---

## 中文编码支持

### 问题
使用 `curl` 直接获取数据时可能出现中文乱码。

### 原因
- 终端编码设置不正确
- curl 默认输出可能不是 UTF-8
- JSON 响应中的中文字符需要正确的编码处理

### 解决方案

1. **使用 Python 测试脚本**（最佳方案）
   ```bash
   python test_api.py
   ```
   脚本会自动处理 UTF-8 编码，正确显示中文。

2. **使用浏览器访问**
   - 访问 http://localhost:8000/docs
   - 浏览器会自动处理编码

3. **curl + json.tool**
   ```bash
   curl http://localhost:8000/api/posts | python -m json.tool
   ```

4. **设置终端编码**（Linux/macOS）
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   curl http://localhost:8000/api/posts
   ```

### API 端已做的改进

- ✅ 使用自定义 `UTF8JSONResponse` 类
- ✅ JSON 序列化时设置 `ensure_ascii=False`
- ✅ 响应头包含正确的字符集信息
- ✅ 文件读取使用 UTF-8 编码

---

## 常见问题

### Q: curl 返回的中文是乱码？

**A:** 这是终端编码问题，不是 API 问题。API 已正确配置 UTF-8 编码。

**解决方案：**
1. 使用 `python test_api.py`（推荐）
2. 使用浏览器访问 API 文档
3. 通过 `python -m json.tool` 管道输出

### Q: Windows PowerShell 显示乱码？

**A:** 设置 PowerShell 编码：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

或直接使用 `python test_api.py` 脚本。

### Q: 如何确认 API 编码正确？

**A:** 运行验证脚本：
```bash
python verify_encoding.py
```

脚本会检查：
- 响应头编码
- JSON 中的中文内容
- JSON 序列化是否正确

### Q: 如何添加新的 API 端点？

**A:** 在 `backend/main.py` 中添加新的路由函数。

### Q: 如何修改配置？

**A:** 编辑 `backend/config.py` 中的 `Settings` 类，添加新的配置项。

---

## 项目结构

```
backend/
├── __init__.py          # 包初始化文件
├── main.py              # FastAPI 应用主文件
├── config.py            # 配置管理（从 .env 加载）
├── models.py            # Pydantic 数据模型
├── blog_parser.py       # 博客文章解析器
└── requirements.txt     # 依赖列表（参考用）

docs/                    # 文档目录
├── BACKEND_DOCS.md     # 本文档（整合版）
├── README_BACKEND.md   # 后端使用文档（详细版）
├── API_TEST_SUMMARY.md # API 测试说明
├── QUICKSTART.md       # 快速开始指南
└── CHANGELOG.md        # 更新日志

.env                     # 环境变量（不提交到 Git）
.env.example            # 环境变量模板
pyproject.toml          # uv 项目配置
test_api.py             # Python 测试脚本
verify_encoding.py      # 编码验证脚本
run_backend.py          # 启动脚本
```

---

## 更新日志

### 2026-01-29

#### 新增功能
- ✅ 创建 FastAPI 后端服务，支持获取博客内容
- ✅ 实现博客文章解析器，支持 Hugo front matter 格式
- ✅ 添加搜索功能，支持按标题、内容、标签、分类搜索
- ✅ 创建跨平台 Python 测试脚本 (`test_api.py`)

#### 修复问题
- ✅ **修复中文编码问题**
  - 添加自定义 `UTF8JSONResponse` 类
  - JSON 序列化时设置 `ensure_ascii=False`
  - 确保所有响应使用 UTF-8 编码
  - 文件读取使用 UTF-8 编码
  
- ✅ **跨平台支持**
  - 移除 PowerShell 脚本，改用 Python 脚本
  - 测试脚本支持 Linux/macOS/Windows
  - 自动处理不同平台的编码问题

#### 文档更新
- ✅ 创建 `docs/` 文件夹统一管理文档
- ✅ 更新后端使用文档
- ✅ 添加 API 测试说明
- ✅ 添加更新日志

#### 技术改进
- ✅ 使用 uv 进行包管理
- ✅ Python 3.13 支持
- ✅ 虚拟环境配置
- ✅ 环境变量管理 (`.env` 文件)

---

## 注意事项

- `.env` 文件包含敏感信息，不要提交到 Git
- 确保 `content/posts/` 目录存在且包含 Markdown 文件
- 博客文章需要符合 Hugo 的 front matter 格式（TOML 或 YAML）
- API 响应使用 UTF-8 编码，支持中文内容
- 使用 `test_api.py` 进行跨平台测试（Linux/macOS/Windows）

---

## 相关文档

- [快速开始指南](QUICKSTART.md)
- [API 测试说明](API_TEST_SUMMARY.md)
- [更新日志](CHANGELOG.md)
