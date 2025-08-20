### LLM 适配与工具调用协议设计

#### 配置加载与实例化
`LLM` 从 `application.yml` 读取默认与命名配置，支持多模型并行配置：
```30:54:genie-backend/src/main/java/com/jd/genie/agent/llm/Config.java
private static LLMSettings getDefaultConfig() {
    // 从 application.yml 读取 llm.default.* 与其他属性
    return LLMSettings.builder()
        .model(props.getProperty("llm.default.model", "gpt-4o-0806"))
        .maxTokens(...)
        .temperature(...)
        .baseUrl(...)
        .interfaceUrl(...)
        .apiKey(...)
        .maxInputTokens(...)
        .build();
}
```

#### 消息与工具序列化
`LLM.ask(...)` 负责格式化消息与工具清单，依据模型差异（如 Claude）进行兼容：
```401:432:genie-backend/src/main/java/com/jd/genie/agent/llm/LLM.java
// BaseTool → tools(functions)
for (BaseTool tool : tools.getToolMap().values()) {
    functionMap.put("name", tool.getName());
    functionMap.put("description", tool.getDescription());
    functionMap.put("parameters", tool.toParams());
    formattedTools.add({"type": "function", "function": functionMap});
}
// MCP 工具合并并在 Claude 下转换
if (model.contains("claude")) { formattedTools = gptToClaudeTool(formattedTools); }
```

#### 请求参数与 Function-Call
统一参数包括 `model/messages/max_tokens/temperature/tools/tool_choice/...`：
```203:241:genie-backend/src/main/java/com/jd/genie/agent/llm/LLM.java
public CompletableFuture<String> ask(AgentContext context, List<Message> messages, List<Message> systemMsgs, boolean stream, Double temperature) {
    List<Map<String, Object>> formattedMessages = formatMessages(...);
    Map<String, Object> params = new HashMap<>();
    params.put("model", model);
    params.put("messages", formattedMessages);
    params.put("max_tokens", maxTokens);
    params.put("temperature", temperature != null ? temperature : this.temperature);
    if (Objects.nonNull(extParams)) { params.putAll(extParams); }
    // 非流式与流式分支分别构建请求体
}
```

#### Token 预算与上限
- `max_tokens` 与 `max_input_tokens` 由配置控制，`TokenCounter` 负责输入 token 统计与截断策略（在模型调用前确保不越界）
- `totalInputTokens` 累计记录请求消耗，便于观测与限额控制

#### 关键难点
- 不同厂商 Function-Call 形态差异（OpenAI/Claude 等）：需在工具序列化与 system 消息注入上做兼容
- 工具参数 JSON-Schema 与 Java 类型映射：`BaseTool.toParams()`、MCP 工具 `inputSchema` 透传
- 流式与非流式的统一参数面板：确保上游（编排器）只需切换 `stream` 即可


