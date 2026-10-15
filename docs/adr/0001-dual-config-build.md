# 0001 - 双配置构建：开发与生产分离

生产构建固定为 `hugo --gc --minify --cleanDestinationDir --config hugo.toml,config.production.toml`，本地预览只用 `hugo server -D`（仅 hugo.toml）。原因是生产 baseURL 带 `/mapleFlow/` 子路径（GitHub Pages 项目站），而 `hugo server` 在根路径提供服务——若用生产配置起预览，页面内的子路径 CSS/资源链接会全部 404，整页失去样式（已实测踩坑，AGENTS.md 列为禁止命令）。该分离同时保证 CI 与本地构建产物一致。
