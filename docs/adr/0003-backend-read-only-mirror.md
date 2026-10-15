# 0003 - 后端 API 是 Hugo 内容的只读镜像，解析语义独立

backend/（FastAPI）用自建的正则 + tomli 解析 content/posts 的 front matter，不经 Hugo；它不参与部署，也不是内容的真源——Hugo 才是。因此两端解析语义出现分歧时，修正方向是「后端对齐 Hugo」（如 draft 缺省值，2026-10-15 已对齐），而非让 Hugo 适配后端。选择独立解析是因为 Python 生态没有可用的 Hugo front matter 解析器；代价是两套语义需持续核对。
