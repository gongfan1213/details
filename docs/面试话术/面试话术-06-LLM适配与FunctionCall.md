### 面试话术｜LLM 适配与 Function-Call

- 一句话简介：统一各家大模型（OpenAI/DeepSeek/Claude等）的对话与函数调用协议，保证工具调用稳定、流式解析可靠、上下文可控。

#### 职责（20s）
- 设计 `LLM` 抽象与适配层、Token 计数与消息截断、Function-Call 标准化

#### 实现要点（1-2min）
- 关键类：
  - Java：`genie-backend/.../agent/llm/LLM.java`、`LLMSettings.java`、`TokenCounter.java`
  - Prompt：`genie-backend/.../agent/prompt/ToolCallPrompt.java`
- 功能：
  - 统一 Function-Call 请求体（工具清单、ToolChoice、温度、max_tokens）
  - 多供应商差异化适配（函数字段命名、工具schema、流式格式）
  - 流式解析：增量拼接content与tool_calls；心跳/[DONE]终止
  - Token 控制：计数/截断；区分 system/user/assistant 额外开销

#### 遇到的问题与解决方案（STAR）
- 问题1：厂商 Function-Call 格式差异大
  - 方案：适配器模式统一抽象；入参/出参统一规范（Tool、ToolCall、Usage）
  - 效果：同一编排层可无缝切换模型

- 问题2：流式响应丢片与黏包
  - 方案：基于前缀`data:`严格切片；拼接器幂等判重；`heartbeat`保活
  - 效果：长链路稳定性明显提升

- 问题3：超窗口导致 400/截断幻觉
  - 方案：`TokenCounter` + `MessageTruncator` 智能截断，优先保留 system 与最近消息
  - 效果：失败率下降、回答连贯性提升

- 问题4：工具参数幻觉或越权
  - 方案：严格 schema 校验+默认值/范围校验；无证据不调用；失败降级
  - 效果：工具失败重试率下降

#### 指标
- LLM 调用成功率 > 99%
- 工具调用参数校验覆盖率 100%
- 超窗口失败率显著下降（有截断策略后）

#### Q&A 备选
- Q：如何在不同模型间平滑切换？
  - A：适配器抽象 + 统一工具/消息协议；配置驱动模型选择。
- Q：如何处理流式中途断开？
  - A：心跳+前端重连策略，后端可重放最近片段（可选）。

#### 演进
- 引入代价估计与响应模型选择（路由）
- 更细粒度的对话压缩与记忆策略
