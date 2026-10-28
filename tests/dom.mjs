/**
 * dom.mjs —— 测试 harness 的 Node 侧（工单 0062 决议）
 * ============================================================
 * 「harness」是一个概念：Python 侧 tests/harness.py（Report / 入口仪式 /
 * tmp 分根 / build 旗标档位 / fixture 配置写入四轴）+ 本文件（jsdom 页面
 * 装配 / check / 汇总退出）——按职责命名，语言边界强制两个文件，概念是
 * 一个模块。sop_golden.py 是并列的第三个共享模块（内容 fixture 工具），
 * 不并入本概念——防未来的合并冲动，详见 harness.py docstring。
 *
 * seam 纪律（0061 裁定，0062 确认）：seam 之后只有机制——本文件不持有
 * 任何契约期望值；样本 HTML 与断言字面量留在各套件（三层文档契约的
 * 第三层），harness 只提供装配与记账。
 *
 * 导出契约（本 docstring 是唯一定义处，随切片逐条落）：
 *   check(name, cond, detail)  记录一条断言并向 stdout 留痕；与两套件
 *                              原逐字拷贝的同名函数同型（ok / FAIL）
 *   finish()                   汇总（N/M passed + GREEN / RED）并以退出码
 *                              收束（有失败 = 1）；格式与 Python 侧对齐
 *   installDom(html)           装配 jsdom 并把 window / document 绑到全局——
 *                              引擎以全局为宿主的套件用（reveal 模式）
 *   installPage({ html, href, pathname })
 *                              装配「真 document + 注入 location 桩」的 env
 *                              对象——入口引擎纯函数缝的套件用（search 模式）；
 *                              location 是注入桩（env 契约要求可替换），
 *                              不是 dom.window.location
 *   loadFresh(rel)             cache-bust 重新求值引擎模块（ESM 缓存会让
 *                              import 副作用只跑一次，测试间必须重新求值）
 *
 * 消费方：tests/assert_reveal.mjs / tests/assert_search.mjs（npm test）。
 */
import { JSDOM } from 'jsdom';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let passed = 0;
let failed = 0;
let bust = 0;

/** 记录一条断言：cond 为真记通过（ok），否则记失败（FAIL）并带 detail 留痕。 */
export function check(name, cond, detail) {
    if (cond) {
        passed++;
        console.log(`  ok  ${name}`);
    } else {
        failed++;
        console.log(`FAIL  ${name}${detail ? `\n      ${detail}` : ''}`);
    }
}

/** 汇总并退出：有失败即非零退出码（CI 守门的语义来源）。 */
export function finish() {
    console.log(`\n${passed}/${passed + failed} passed`);
    if (failed) {
        console.log('RED — %d 个行为未满足', failed);
        process.exit(1);
    }
    console.log('GREEN');
    process.exit(0);
}

/** 装配 jsdom 并把 window / document 绑到全局（引擎以全局为宿主的模式）。 */
export function installDom(html) {
    const dom = new JSDOM(html, { url: 'http://localhost/' });
    globalThis.window = dom.window;
    globalThis.document = dom.window.document;
    return dom;
}

/** cache-bust 重新求值引擎模块：ESM 缓存会让 import 副作用只跑一次。 */
export function loadFresh(rel) {
    const url = pathToFileURL(path.join(REPO, rel)).href + `?t=${++bust}`;
    return import(url);
}

/**
 * 加载并挂载（0084 决议）：cache-bust 重求值后调用挂载函数，返回模块。
 * 引擎去自注册（0083 决议）后「加载」与「挂载」是两步——本 helper
 * 把两步绑成一次调用，各用例不必各写两行，也让「加载了但忘了挂」这种
 * 假绿难以发生（忘了挂时断言会红，而不是静默空跑）。
 * 注意：mount 收到模块对象；少数用例还要读 computeProgress 之类，故返回模块。
 */
export async function loadMounted(rel, mount) {
    const mod = await loadFresh(rel);
    mount(mod);
    return mod;
}

/**
 * 装配「真 document + 注入 location 桩」的 env 对象（入口引擎纯函数缝的模式）。
 * location 是注入桩——env 契约要求可替换，不是 dom.window.location。
 */
export function installPage({ html, href, pathname }) {
    const dom = new JSDOM(html, { url: href });
    return {
        document: dom.window.document,
        location: { href, pathname },
    };
}
