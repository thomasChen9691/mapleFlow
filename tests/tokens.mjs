/**
 * tokens.mjs —— CSS 影子契约的词法抽取器（机制层）
 * ============================================================
 * 【职责边界（0086 / 0087 决议）】只懂词法：读文本、出 token 表、带定位。
 * **不持白名单、不懂 `is-*` 范围、不判方向**——方向（JS 写→CSS 读、CSS 读→谁
 * 生产）与范围归 tests/assert_reveal.mjs 的断言层。这条分工让本文件能被
 * assert_harness 独立自测，而不必懂任何契约期望值（dom.mjs 同款纪律）。
 *
 * 抽取规则（四类，都是「字面量」级）：
 *   JS 写 class   `classList.add|remove|toggle|replace('x')`
 *                 以及传给 helper 的状态类实参 `, 'is-xxx'`
 *                 （`replay(el, 'is-morphing', 520)` 这种参数化写法）
 *   JS 写变量     `setProperty('--x', …)`
 *   CSS 读 class  选择器里的 `.cls`（先剥注释——注释里常提到类名）
 *   CSS 读变量    `var(--x)`
 *   模板生产 class `class="a b c"`（反向检查的生产者面）——扫描前先剥掉
 *                 Go 模板动作 `{{ … }}`：条件类常写成
 *                 `class="mf-price{{ if $free }} is-free{{ end }}"`，
 *                 不剥的话 token 会粘成 `is-free{{`，反向检查误报孤儿。
 *
 * 接口：collect({ js, css, markup }) → { writes:{class,var}, reads:{class,var}, markup:{class} }
 *   每个 token 映射到 [{ file, line }]（1 基行号），失败消息直接可用。
 *   js/css/markup 的每一项可以是**路径字符串**（读盘），也可以是 `{ file, text }`
 *   ——后者是给 assert_harness 自测用的纯函数入口，不必落临时文件。
 */
import fs from 'node:fs';

const RE_CLASS_WRITE = /classList\.(?:add|remove|toggle|replace)\(\s*'([\w-]+)'/g;
const RE_CLASS_HELPER = /,\s*'(is-[\w-]+)'/g;
const RE_VAR_WRITE = /setProperty\(\s*'(--[\w-]+)'/g;
const RE_CSS_CLASS = /\.([A-Za-z_][-\w]*)/g;
const RE_CSS_VAR = /var\(\s*(--[\w-]+)/g;
const RE_MARKUP_CLASS = /class="([^"]*)"/g;

/** 读一项：路径则读盘，`{file,text}` 则直接用（自测入口）。 */
function readItem(item) {
    if (typeof item === 'string') {
        return { file: item, text: fs.readFileSync(item, 'utf8') };
    }
    return { file: item.file, text: item.text };
}

/** 记一条定位：token → [{file,line}]，同文件同行不重复记。 */
function record(table, token, file, line) {
    const list = (table[token] ||= []);
    if (!list.some((hit) => hit.file === file && hit.line === line)) {
        list.push({ file, line });
    }
}

/** 逐行扫一个正则（行号是 1 基，便于直接写进失败消息）。 */
function scanLines(text, regex, onHit) {
    text.split('\n').forEach((line, index) => {
        for (const m of line.matchAll(regex)) {
            onHit(m[1], index + 1);
        }
    });
}

/** 剥掉 CSS 注释：注释里常出现类名，会把「死样式」误读成活消费。 */
function stripCssComments(text) {
    return text.replace(/\/\*[\s\S]*?\*\//g, (block) => block.replace(/[^\n]/g, ' '));
}

export function collect({ js = [], css = [], markup = [] } = {}) {
    const out = {
        writes: { class: {}, var: {} },
        reads: { class: {}, var: {} },
        markup: { class: {} },
    };

    for (const item of js) {
        const { file, text } = readItem(item);
        scanLines(text, RE_CLASS_WRITE, (t, line) => record(out.writes.class, t, file, line));
        scanLines(text, RE_CLASS_HELPER, (t, line) => record(out.writes.class, t, file, line));
        scanLines(text, RE_VAR_WRITE, (t, line) => record(out.writes.var, t, file, line));
    }

    for (const item of css) {
        const { file, text } = readItem(item);
        const clean = stripCssComments(text);
        scanLines(clean, RE_CSS_CLASS, (t, line) => record(out.reads.class, t, file, line));
        scanLines(clean, RE_CSS_VAR, (t, line) => record(out.reads.var, t, file, line));
    }

    for (const item of markup) {
        const { file, text } = readItem(item);
        // 剥模板动作：条件类的字面量在动作外面（`…{{ if x }} is-free{{ end }}`），
        // 动作本身是 Go 代码，不是类名。
        const clean = text.replace(/\{\{[\s\S]*?\}\}/g, ' ');
        for (const m of clean.matchAll(RE_MARKUP_CLASS)) {
            for (const token of m[1].split(/\s+/).filter(Boolean)) {
                record(out.markup.class, token, file, 1);
            }
        }
    }

    return out;
}

/** 递归列出目录下指定后缀的文件（相对路径，排序后稳定）。 */
export function listFiles(dir, ext) {
    const found = [];
    const walk = (current) => {
        for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
            const full = `${current}/${entry.name}`;
            if (entry.isDirectory()) { walk(full); continue; }
            if (entry.name.endsWith(ext)) { found.push(full); }
        }
    };
    walk(dir.replace(/\/$/, ''));
    return found.sort();
}
