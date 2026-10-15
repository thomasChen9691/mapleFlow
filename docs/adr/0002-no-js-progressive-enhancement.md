# 0002 - 渐进增强以 .no-js 类名为基线，而非 noscript 标签

进场动画（reveal / mf-rise）的初始隐藏只在 JS 确实可用时生效：`<html>` 默认带 `no-js` 类，head 内联脚本立即将其替换为 `js`。选择类名而非 `<noscript>` 标签，因为 noscript 只覆盖「JS 被完全禁用」，覆盖不了「JS 启用但脚本加载失败」——后者会让内容永久隐藏，且影响不执行 JS 的爬虫与社交抓取。代价是 layouts/_default/baseof.html 与 layouts/partials/extend_head.html 两个主题覆盖文件需在 PaperMod 子模块升级时手动同步。
