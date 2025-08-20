### 10 Agents 工程实践面试题（Agent Engineering Practices）

- 关注点：Agent 代码规范、可测试性、工具编排工程化、人审/回退、灰度与开关
- 关键参考：`agents/graph/agent/**`, `agents/graph/node/**`, `agents/graph/workflows/**`

#### 基础题
- 你如何在本项目中划分“Agent vs Node vs Workflow”的职责边界？新增 Agent 的最小改动面是什么？
- 为什么工具声明采用 `@tool` + `create_react_agent(..., tools=[...])` 组合，对比直接函数调用的工程收益？
- 人审在环（HITL）如何落地？`interrupt/resume` 相比自研暂停协议的优势与限制？

#### 进阶题
- 工具幂等与副作用防护：哪些工具需要幂等键？如何设计“幂等键生成 + 重放保护 + 补偿事务”？
- Agent 配置热更新：模型、温度、系统提示如何在运行中变更？如何保证变更的可回滚与可观测？
- Prompt 管理：如何避免 Prompt 泄露与“模板地狱”？可复用片段、占位符、版本化如何落地？

#### 实操题
- 将 `content_writing_agent` 的工具列表扩展为“写作→评审→打分→再写作”的循环，写出路由条件与步数上限策略。
- 为 `content_search_agent` 加入“并行搜索 + 汇总合并”的节点设计，给出合并器核心逻辑与阈值。

#### 场景题
- A/B Prompt 实验：如何对同一 Agent 在生产中灰度两套 Prompt，并采集对比指标（转化/稽核过审率）？
- 灰度与开关：如何为高风险 Agent/工具加“开关 + 配额 + 限流”，避免整体服务退化？

#### 追问
- 你如何编写 Agent 级单元测试与集成测试？如何模拟 LLM 响应与工具错误，以提高回归效率？
- 对“易变外部依赖”的工具，你会如何封装重试/熔断/超时/降级？请给出统一拦截器设计要点。

#### 作业
- 写一个“Agent 执行拦截器”伪代码：统计耗时、记录入参出参摘要、遇错分级重试、生成 trace/span ID、输出 metrics。

### 参考答案（示例）
- 职责边界（落地）：
  - Agent：负责“如何用工具”与提示词策略，弱化对 HTTP/DB 等基础能力的直接依赖；
  - Node：封装 Agent 的一次可重放调用，输入/输出与状态字段严格约束；
  - Workflow：只做接线（`add_node/add_edge/add_conditional_edges`）、检查点注入与编译；
  - 收益：单测可对 Node/Agent 各自隔离测试，工作流层只需少量 E2E 校验。
- 工具注入与治理：
  - 统一在 `*_agent.py` 中通过 `create_react_agent(model, tools=[...])` 注入；
  - 新增工具流程：新增 `@tool` 函数→完善 description/示例→在 Agent 列表注册→补充单测/速率限制；
  - 高危工具：强制 IToolExecutor（鉴权/超时/重试/熔断/参数清洗/metrics），必要时加人审确认。
- 人审与恢复：
  - 在关键节点（如产出/发布前）使用 `interrupt`；API 层用 `Command(resume=...)` 恢复；
  - 恢复原则：仅继续执行未完成路径；对外部副作用步骤必须幂等或补偿。
- 幂等/重试/熔断：
  - 幂等键设计：`hash(user|session|op|payload|version)`；
  - 重试：指数退避 + 抖动 + 最大时长；错误分级（可重试：网络/限流/超时；不可重试：4xx 参数/权限）；
  - 熔断：按错误率/延迟阈值触发，设恢复窗口；降级为静态/延迟/近似方案。
- 观测：
  - 统一生成 trace_id 并贯穿日志/指标/追踪；
  - 指标：QPS、P95/99、工具错误率/重试次数、熔断触发、缓存命中、向量检索延迟；
  - 看板按 Agent/工具/版本维度拆分；告警阈值与自愈（降级）联动。
- 伪代码：IToolExecutor 拦截器
```python
def tool_executor(tool_fn):
    def wrapper(*args, **kwargs):
        start = now(); trace_id = get_trace_id();
        try:
            enforce_auth_quota(kwargs)
            payload = sanitize(kwargs)
            return retry_with_backoff(lambda: with_timeout(tool_fn, payload))
        except RetryableError as e:
            mark_retryable(e); raise
        except Exception as e:
            open_circuit_if_needed(e); raise
        finally:
            dur = now()-start
            emit_metrics(tool=tool_fn.__name__, duration_ms=dur, trace_id=trace_id)
            write_audit(tool_fn.__name__, args, kwargs)
    return wrapper
```

#### 附录：代码片段引用
- Agent 工具注入（节选）：
```220:258:agents/graph/agent/content_writing_agent.py
llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=api_base,
    temperature=0.7
)
content_writing_agent = create_react_agent(
    model=llm,
    tools=[plan_content_creation, create_content_variant, review_and_optimize_content, generate_content_package],
    prompt=..., name="content_writing",
)
```

#### 样例回答/评分标准
- 样例回答要点：
  - 清晰阐述 Agent/Node/Workflow 职责与依赖方向；
  - 说明为何工具要 `@tool` + `create_react_agent` 动态注入；
  - 给出幂等/补偿、热更新、Prompt 管理与人审落地方案；
  - 能画出调用链并定位观测与拦截点。
- 评分标准：
  - 优秀：覆盖职责边界/工程治理/稳定性/观测/测试，提供具体代码位点或伪代码；
  - 合格：能说明主要设计决策与至少两项工程化手段；
  - 待提高：仅泛泛而谈，缺少落地与风控方案。

### 常见错误与改进建议
- 错误：Agent/Node/Workflow 职责混淆，逻辑散落多个层次。
  - 改进：严格边界，Agent 专注工具与策略，Node 负责封装与状态处理，Workflow 只做装配与路由。
- 错误：工具直接在 Agent 内部硬编码，难以灰度/替换。
  - 改进：用 `tools=[...]` 动态注入 + IToolExecutor 统一拦截器（鉴权/重试/熔断/观测）。
- 错误：人审流程仅靠文案提示，无法恢复。
  - 改进：使用 `interrupt/resume` + 检查点，定义恢复协议与前端回填格式。
