/**
 * fastsearch.js —— 站内搜索检索引擎（搜索协议·行为层；工单 0046 决议①②；
 * 呈现层摘要加深与入口互指分别见候选 12 工单 0051/0052 决议）
 * ============================================================
 * 【检索交互契约的定义处。与 index.json 的投影契约（layouts/_default/index.json
 *   文件头 docstring）分立两个模块：投影管「索引里有什么」，本文件管「检索怎么跑」。
 *   两模块不合并命名（0043 决议④）；reveal 协议管动效交互（ADR-0007），与本协议并列。】
 *
 * 加载（themes/maplemod/layouts/partials/head.html，仅 .Layout == "search" 时）：
 *   与 fuse.basic.min.js、license.js concat 为 assets/js/search.js 后 fingerprint；
 *   js.Build 无 params——fuseOpts 参数位已删（0046 决议③：无消费方的预留位不留）。
 *
 * 指针（候选 12 工单 0052 决议②）：全站 `/` 快捷键入口是并列模块——
 *   assets/js/mf-search-entry.js + mf-search-entry-engine.js（经 extend_footer
 *   全站恒加载，契约定义处在其文件头 docstring）。入口只负责跳转/聚焦到本页，
 *   检索仍归本协议；本协议仅 .Layout == "search" 页加载（head.html 条件），
 *   入口构件全站每页在——两个搜索相关 JS 面、加载条件不同，勿混。
 *
 * DOM 契约（现状快照：本文件是 vendored 上游 PaperMod 代码的第一方化留存，
 *   快照式记录当前行为、非设计目标；重写时本契约随移）：
 *   读  #searchbox > #searchInput    搜索输入（autofocus / maxlength=64 / aria-label=search）
 *       #searchResults               结果列表（aria-label=search results）
 *   写  #searchResults.innerHTML     <li class="post-entry"><header class="entry-header">
 *                                    {title}&nbsp;»</header><div class="entry-summary">
 *                                    {summary}</div><a href="{permalink}"
 *                                    aria-label="{title}"></a></li>——标题+摘要+链接
 *                                    （0051 决议②：摘要是场景乙「正文命中时纯标题
 *                                    无法区分哪篇真含」的低成本半解；不显标签——
 *                                    categories 全站同值、tags 与 summary 信息重叠；
 *                                    不做命中高亮——不动 fuse matches，ADR-0010
 *                                    「只改渲染层」边界；不显精选不变——索引不投影
 *                                    featured，0044）
 *       .focus                       键盘导航当前项（结果项导航时加在 li 上——search.css
 *                                    #searchResults .focus 消费，唯一 CSS 耦合类；
 *                                    焦点回输入框时加在 #searchbox 上，无 CSS 消费方）
 *   键盘（document.onkeydown 全局监听）：Escape 恒可重置（清空输入与结果、焦点回
 *        输入框——位于结果门之前，无结果 / 焦点在框外时也响应）；输入框获焦时先清理
 *        既有 .focus；ArrowDown/ArrowUp/ArrowRight 受「结果可用且焦点在搜索框内」门控
 *        （ArrowRight = 点击当前项）。
 *   点击热区：#searchResults a 绝对定位铺满 li（search.css 消费）；li 的
 *         post-entry / entry-header 类名无外部消费方，仅本模板自用。
 *
 * 检索契约（0046 决议③：调参 = 改代码 + 改契约 + 评审，不再有配置分支）：
 *   Fuse options 为代码显式设定（fuseOpts 分支删除后即默认值）：
 *   distance 100 / threshold 0.4 / ignoreLocation true；
 *   keys = [title, permalink, summary, content]——与投影六字段的差集恰为
 *   tags/categories（扩展检索预留），对齐由 tests/assert_site_contracts.py 的
 *   assert_search_projection 执法（改投影字段须同步 keys）。
 *   索引来源：XHR GET "index.json"（同目录相对——站点在子路径 /mapleFlow/ 下，
 *   上游的 ../index.json 会逃逸到域名根而 404，已实测；head.html 的 preload 同步同目录）。
 *
 * 已知限制（快照记录，不承诺修复——0046 决议④）：
 *   · XHR 失败仅 console.log、JSON.parse 无 try/catch：索引损坏时搜索静默失效
 *     （无结果、无用户可见报错）——容错 UX 待重写或工单 0047 行为测试缝时处理；
 *   · 呈现层「渲染结果正确」无自动断言：引擎为无导出经典脚本，不立 jsdom 套件
 *     （ADR-0010 决策 5）；弱产物断言只守「构件含 item.summary 渲染引用」（契约-
 *     代码不漂移），浏览器运行时的实际渲染由人工验证覆盖（0051 决议④）；
 *   · no-js 下搜索页只剩空壳：客户端搜索的固有属性（ADR-0002 基线只保证内容可读）；
 *   · reduced-motion：无运动面可降级（唯一动效是 search.css 的 li:active 0.1s
 *     按压反馈，非进场动画）。
 *
 * 测试：B11 三挂点 + 摘要渲染引用等产物断言（tests/assert_site_contracts.py）；
 *   jsdom 行为测试未立（ADR-0010 决策 5；0047 决议同旨）。历史：2026-10-22 前
 *   存在项目级 assets/js/fastsearch.js 覆盖（子模块时代为改 XHR 路径而建），
 *   已合并入本文件并删除——单副本由 assert_search_projection 的守门断言执法。
 */

let fuse; // holds our search engine
let resList = document.getElementById('searchResults');
let sInput = document.getElementById('searchInput');
let first, last, current_elem = null
let resultsAvailable = false;

// load our search index
window.onload = function () {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                let data = JSON.parse(xhr.responseText);
                if (data) {
                    // fuse.js options; check fuse.js website for details
                    let options = {
                        distance: 100,
                        threshold: 0.4,
                        ignoreLocation: true,
                        keys: [
                            'title',
                            'permalink',
                            'summary',
                            'content'
                        ]
                    };
                    fuse = new Fuse(data, options); // build the index from the json file
                }
            } else {
                console.log(xhr.responseText);
            }
        }
    };
    // 同目录相对 "index.json"（子路径部署下 ../ 会逃逸到域名根——契约详见文件头 docstring）。
    xhr.open('GET', "index.json");
    xhr.send();
}

function activeToggle(ae) {
    document.querySelectorAll('.focus').forEach(function (element) {
        // rm focus class
        element.classList.remove("focus")
    });
    if (ae) {
        ae.focus()
        document.activeElement = current_elem = ae;
        ae.parentElement.classList.add("focus")
    } else {
        document.activeElement.parentElement.classList.add("focus")
    }
}

function reset() {
    resultsAvailable = false;
    resList.innerHTML = sInput.value = ''; // clear inputbox and searchResults
    sInput.focus(); // shift focus to input box
}

// execute search as each character is typed
sInput.onkeyup = function (e) {
    // run a search query (for "term") every time a letter is typed
    // in the search box
    if (fuse) {
        let results = fuse.search(this.value.trim()); // the actual query being run using fuse.js
        if (results.length !== 0) {
            // build our html if result exists
            let resultSet = ''; // our results bucket

            for (let item in results) {
                resultSet += `<li class="post-entry"><header class="entry-header">${results[item].item.title}&nbsp;»</header>` +
                    `<div class="entry-summary">${results[item].item.summary}</div>` +
                    `<a href="${results[item].item.permalink}" aria-label="${results[item].item.title}"></a></li>`
            }

            resList.innerHTML = resultSet;
            resultsAvailable = true;
            first = resList.firstChild;
            last = resList.lastChild;
        } else {
            resultsAvailable = false;
            resList.innerHTML = '';
        }
    }
}

sInput.addEventListener('search', function (e) {
    // clicked on x
    if (!this.value) reset()
})

// kb bindings
document.onkeydown = function (e) {
    let key = e.key;
    let ae = document.activeElement;

    let inbox = document.getElementById("searchbox").contains(ae)

    if (ae === sInput) {
        let elements = document.getElementsByClassName('focus');
        while (elements.length > 0) {
            elements[0].classList.remove('focus');
        }
    } else if (current_elem) ae = current_elem;

    if (key === "Escape") {
        reset()
    } else if (!resultsAvailable || !inbox) {
        return
    } else if (key === "ArrowDown") {
        e.preventDefault();
        if (ae == sInput) {
            // if the currently focused element is the search input, focus the <a> of first <li>
            activeToggle(resList.firstChild.lastChild);
        } else if (ae.parentElement != last) {
            // if the currently focused element's parent is last, do nothing
            // otherwise select the next search result
            activeToggle(ae.parentElement.nextSibling.lastChild);
        }
    } else if (key === "ArrowUp") {
        e.preventDefault();
        if (ae.parentElement == first) {
            // if the currently focused element is first item, go to input box
            activeToggle(sInput);
        } else if (ae != sInput) {
            // if the currently focused element is input box, do nothing
            // otherwise select the previous search result
            activeToggle(ae.parentElement.previousSibling.lastChild);
        }
    } else if (key === "ArrowRight") {
        ae.click(); // click on active link
    }
}
