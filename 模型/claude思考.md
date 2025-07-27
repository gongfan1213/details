模型差异的关键维度

1. 主动性：

• 主动型模型（如 gemini-2.5-pro、claude-3.7-sonnet）：自信、決策快

•谨慎型模型（如 03、claude-3.5-sonnet）：更多规划和提问

2. 上下文窗口：

某些模型可以处理更大的代码库范围。

模型行 类型

1.思考型模型

•特点：推断意图、提前规划、自主决策

• 适用场景：希望模型自主完成任务、减少引导

•代表模型：claude-3.7-sonnet、gemini-2.5-pro、03

•最佳用途：探索想法、广泛重构、需要独立思考

2.非思考型模型

•特点：等待明确指示、不做过多推断

•适用场景：需要精确控制输出

•代表模型：claude-3.5-sonnet、gpt-4.1

•最佳用途：精确定义的任务、需要可预测行为

如何选择模型

1. 按提示风格选择

•喜欢控制并给明确指示：选择非思考型模型

•喜欢让模型主动发挥：选择思考型模型

2. 按任务类型选择

• 小范围变更：适合非思考型模型

•大型重构：适合思考型模型

• 代码库导航/搜索：大多数模型都可胜任

• 规划或问题解决：思考型模型更佳

•复杂错误或深度推理：03（专为复杂问题设计，但速度较慢）

3. 自动选择

• Auto 选项：从可靠模型池中选择（不包括 03）

• 不根据任务类型路由，但作为不确定时的可靠默认选择

实用建议

•保存有效组合：将特定提示与特定模型的组合保存为“自定义模式”。

？ 这是一个很好的实践！

•日常驱动选择：claude-3.5-sonnet、claude-3.7-sonnet、gemini-

2.5-pro、gpt-4.1 都是强大的日常选择。

•特殊问题选择：03 适合最复杂的问题。

注意：03 模型速度较慢。

• 不确定时：使用 Auto-select 作为安全默认选项。

以上经验不太准确说实话的，
# cluade 3,7相比cluade 3,5更懒一些，3.7相比于3.5容易想太多，只剩有限次数完成任务的时候，最后直接摆烂

claude 3.5 sonnet适合修复bug，和逻辑密集的执行

4o适合产品规划和ui开发计划

gemini 2.5 pro
读取代码库，重构和审计代码查找bug等

写文本

4.5> o3> claude sonnet 3.7 >gemini2.5pro


# claude思考

- HIGHEST 32k
- MIDDLE 10k
- BASIC 4k
- NONE 0

English (英语)
-   HIGHEST: "think harder", "think intensely", "think longer", "think really hard", "think super hard", "think very hard", "ultrathink"
-   MIDDLE: "think about it", "think a lot", "think deeply", "think hard", "think more", "megathink"
-   BASIC: "think"

 Chinese (中文)
-   HIGHEST: "多想一会", "深思", "仔细思考"
-   MIDDLE: "多想想", "好好想"
-   BASIC: "想", "思考"
-   NONE: (无关键词)


