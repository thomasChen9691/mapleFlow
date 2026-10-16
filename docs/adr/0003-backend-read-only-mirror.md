# 0003 - 后端 API 是 Hugo 内容的只读镜像，解析语义独立

> **状态：适用对象已退役**（2026-10-16，wayfinder 工单 0011 裁决：`backend/` 全套删除）。退役理由：零消费者（两份历史审计早已结论）、SOP 管线适配器化后其输入模型（glob `content/posts/*.md`）对 60% 内容失效。本 ADR 的语义裁决（后端若存在，则是 Hugo 的只读镜像、分歧时后端对齐 Hugo）**不作废**——它对此后任何「Hugo 内容的磁盘镜像」仍然有效；仅为「backend/ 已不存在」留此状态标注，防止未来会话对着不存在的模块重新推导。

backend/（FastAPI）用自建的正则 + tomli 解析 content/posts 的 front matter，不经 Hugo；它不参与部署，也不是内容的真源——Hugo 才是。因此两端解析语义出现分歧时，修正方向是「后端对齐 Hugo」（如 draft 缺省值，2026-10-15 已对齐），而非让 Hugo 适配后端。选择独立解析是因为 Python 生态没有可用的 Hugo front matter 解析器；代价是两套语义需持续核对。
