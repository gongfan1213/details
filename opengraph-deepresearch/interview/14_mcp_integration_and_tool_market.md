### 14 MCP 集成与工具市场面试题（MCP Integration & Tool Marketplace）

- 关注点：MCP 客户端会话/工具声明、与 LangGraph/LangChain 的衔接、工具市场治理
- 关键参考：`langchain_mcp_adapters`, `google-genai` MCP 支持（实验）、`agents/graph/agent/**`

#### 基础题
- MCP 是什么？相对本地工具/HTTP 工具的优势在哪？
- 本项目虽未直接使用 MCP，但如何以最小侵入接入到 `create_react_agent(..., tools=[...])`？

#### 进阶题
- 方案 A：使用 `langchain_mcp_adapters` 将 MCP 工具转为 LangChain 工具；方案 B：使用 `google-genai` 将 `mcp.ClientSession` 直接作为工具；比较各自优劣。
- 工具市场：注册/发现/启停/版本/权限/配额/可观测；如何设计统一“工具目录 + 策略中心”？

#### 实操题
- 画出“工具加载器”架构：本地工具、HTTP 工具、MCP 工具统一抽象为 `IToolDescriptor`，在运行时注入目标 Agent。
- 权限与风控：为高危工具加入“人审/双人复核/账本审计/审计导出”。

#### 场景题
- 供应商不可用时的降级：同类工具回退链路如何定义？如何做自动熔断与恢复？
- 工具版本灰度：按租户/用户灰度新版本与回滚策略。

#### 追问
- 工具选择：如何让模型更可靠地“选对工具”？从描述、示例、代价、成功率、风险等维度增强信号。
- 计费与配额：如何对每次工具调用记账，并在仪表盘维度可视化？

#### 作业
- 写一个“工具市场元数据模型”示意，覆盖：标识、描述、参数签名、风险等级、成本、成功率、版本、可见性、配额策略。

#### 图稿
- 参见：`interview/diagrams/mcp_tool_market.md`。

### 参考答案（示例）
- 接入路线：
  - A：`langchain_mcp_adapters` → MCP 工具转 LangChain 工具 → 注入 `create_react_agent`；
  - B：`google-genai` 实验支持 → 直接将 `mcp.ClientSession` 作为工具传入；
  - 对比：A 与现有栈更契合、依赖稳定；B 在 Gemini 上路线短，但实验属性更强。
- 工具市场：
  - 目录：`Tool Catalog` 描述/参数签名/版本/风险等级/成本/成功率；
  - 策略中心：配额/权限/可见性/灰度；
  - Loader：按租户/用户加载工具集，支持启停与回滚。
- 风控与回退：
  - 对高危工具启用人审/双人复核/账本，失败触发回退链，结合熔断与恢复窗口；
  - 观测：按工具/版本维度统计成功率与成本，驱动灰度扩容或回滚。

#### 接入步骤示例（方案 A：langchain_mcp_adapters）
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async with MultiServerMCPClient() as client:
    await client.add_stdio_server(command="npx", args=["-y", "@philschmid/weather-mcp"])  # 例
    mcp_tools = await client.load_tools()  # -> List[BaseTool]
    agent = create_react_agent(model=llm, tools=[*local_tools, *mcp_tools])
```

#### 工具市场元数据示例（JSON）
```json
{
  "name": "weather.forecast",
  "version": "1.2.0",
  "risk_level": "medium",
  "cost": {"unit": "req", "estimate": 0.002},
  "success_rate": 0.985,
  "visibility": ["tenantA", "beta"],
  "quota": {"tenant_daily": 10000, "user_minute": 30}
}
```

#### 策略中心规则示例
- 启用范围：按租户/用户分配可见性与配额；
- 风险控制：高风险工具强制人审，记录账本（调用参数摘要/输出摘要/操作者）；
- 灰度与回滚：按版本逐步放量，失败指标超阈值自动回滚；
- 计费与报表：按工具/版本/租户聚合成本与成功率，定期输出报表。

### 常见错误与改进建议
- 错误：工具目录无版本与风险等级，灰度不可控。
  - 改进：为工具元数据增加 `version/risk/cost/success_rate/visibility/quota` 字段；
- 错误：不可用供应商引起级联失败。
  - 改进：同类回退链与熔断恢复窗口，结合配额与限流。
