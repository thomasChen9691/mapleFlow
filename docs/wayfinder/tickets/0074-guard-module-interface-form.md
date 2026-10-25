---
id: "0074"
title: 守卫模块的形态与接口：入参形态、未声明归属、返回语义
type: grilling
mode: HITL
status: open
blocked_by: ["0072", "0073"]
assignee: ""
map: map-featured-type-guard.md
created: 2026-10-25
---

## Question

守卫模块的形态与接口——Hugo 无函数抽象，partial 是唯一载体；接口形态决定三处拷贝如何改写、「未声明」与「非 bool」的区分归谁、测试怎么驱动。候选（以 0073 裁定的职责边界为前提）：

- **(a) 值语义**：`partial "…guard.html" (dict "value" X "origin" Y)`——调用方保留 `isset`，模块只校验 + 回传；
- **(b) 条目语义**：`(dict "item" M "key" "featured" "origin" Y)`——模块内 `isset` + 校验，调用方最薄；
- **(c) 整批语义**：传入 slice + 键名 + origin，模块内遍历校验（现状模式原样搬家）。

要决策的面：

1. **形态选哪个**；三处数据源（Page.Params / 产品 map / 注册条目 map）在所选形态下如何统一适配（`.Params.featured` 可直接取值；产品与注册条目是 map，需 `index` 或直接传值）。
2. **「未声明」（跳过）与「显式非 bool」（errorf）的区分归调用方还是模块内**（条目语义天然容纳、值语义要求调用方保留 `isset`）——两者对调用点代码量与漏检风险的影响。
3. **返回语义**：校验通过后回传什么（原值 / bool / 无返回只执法）；若 0073 含过滤，(c) 是否返回过滤后的 slice。
4. **0072 事实中 Page.Params 键小写化与数据 map 键原样的差异，对 (b) 的「键」参数是否构成约束**（键名传 `"featured"` 是否三种源都安全）。

边界（不开票）：职责边界（管不管谓词）归 0073；落点归 0075；消息文案归 0076；测试归 0077。
