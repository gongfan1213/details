# LLM适配与FunctionCall

## 功能概述

LLM适配与FunctionCall是JoyAgent-JDGenie的核心智能引擎，负责与大语言模型的交互和工具调用。系统支持多种LLM模型（OpenAI、Claude、DeepSeek等），实现了统一的Function-Call协议，支持流式响应和工具调用，为智能体提供强大的推理和执行能力。

## 业务功能实现

### 1. LLM抽象层设计

#### 1.1 统一LLM接口
```java
public class LLM {
    private String model;           // 模型名称
    private String apiKey;          // API密钥
    private String baseUrl;         // 基础URL
    private String functionCallType; // Function-Call类型
    private TokenCounter tokenCounter; // Token计数器
    
    // 核心方法
    public CompletableFuture<ToolCallResponse> askTool(
        AgentContext context,
        List<Message> messages,
        Message systemMessage,
        List<BaseTool> availableTools,
        ToolChoice toolChoice,
        String digitalEmployee,
        boolean isStream,
        int timeout
    );
}
```

#### 1.2 模型配置管理
```java
@Data
public class LLMSettings {
    private String modelName;       // 模型名称
    private String apiKey;          // API密钥
    private String baseUrl;         // 基础URL
    private int maxTokens;          // 最大Token数
    private double temperature;     // 温度参数
    private String functionCallType; // Function-Call类型
}
```

### 2. Function-Call协议实现

#### 2.1 工具调用请求
```java
public class ToolCallRequest {
    private String model;           // 模型名称
    private List<Message> messages; // 消息列表
    private List<Tool> tools;       // 可用工具列表
    private ToolChoice toolChoice;  // 工具选择策略
    private boolean stream;         // 是否流式
    private int maxTokens;          // 最大Token数
    private double temperature;     // 温度参数
}
```

#### 2.2 工具定义格式
```java
public class Tool {
    private String type = "function";
    private Function function;
    
    @Data
    public static class Function {
        private String name;        // 工具名称
        private String description; // 工具描述
        private Object parameters;  // 参数Schema
    }
}
```

#### 2.3 工具调用响应
```java
@Data
public class ToolCallResponse {
    private String content;         // 响应内容
    private List<ToolCall> toolCalls; // 工具调用列表
    private String finishReason;    // 结束原因
    private Usage usage;            // Token使用情况
    
    @Data
    public static class ToolCall {
        private String id;          // 调用ID
        private String type;        // 调用类型
        private Function function;  // 函数信息
        
        @Data
        public static class Function {
            private String name;    // 函数名称
            private String arguments; // 参数JSON
        }
    }
}
```

### 3. 多模型适配

#### 3.1 OpenAI适配器
```java
@Component
public class OpenAIAdapter implements LLMAdapter {
    @Override
    public CompletableFuture<ToolCallResponse> callLLM(ToolCallRequest request) {
        // OpenAI API调用实现
        return openAIClient.chatCompletions(request);
    }
    
    @Override
    public List<Tool> convertTools(List<BaseTool> tools) {
        // 转换为OpenAI工具格式
        return tools.stream()
            .map(this::convertToOpenAITool)
            .collect(Collectors.toList());
    }
}
```

#### 3.2 Claude适配器
```java
@Component
public class ClaudeAdapter implements LLMAdapter {
    @Override
    public CompletableFuture<ToolCallResponse> callLLM(ToolCallRequest request) {
        // Claude API调用实现
        return claudeClient.messages(request);
    }
    
    @Override
    public List<Tool> convertTools(List<BaseTool> tools) {
        // 转换为Claude工具格式
        return tools.stream()
            .map(this::convertToClaudeTool)
            .collect(Collectors.toList());
    }
}
```

#### 3.3 DeepSeek适配器
```java
@Component
public class DeepSeekAdapter implements LLMAdapter {
    @Override
    public CompletableFuture<ToolCallResponse> callLLM(ToolCallRequest request) {
        // DeepSeek API调用实现
        return deepSeekClient.chatCompletions(request);
    }
    
    @Override
    public List<Tool> convertTools(List<BaseTool> tools) {
        // 转换为DeepSeek工具格式
        return tools.stream()
            .map(this::convertToDeepSeekTool)
            .collect(Collectors.toList());
    }
}
```

## 技术方案支撑

### 1. 适配器模式

#### 1.1 适配器接口
```java
public interface LLMAdapter {
    CompletableFuture<ToolCallResponse> callLLM(ToolCallRequest request);
    List<Tool> convertTools(List<BaseTool> tools);
    boolean supports(String modelName);
}
```

#### 1.2 适配器工厂
```java
@Component
public class LLMAdapterFactory {
    private final Map<String, LLMAdapter> adapters = new HashMap<>();
    
    @Autowired
    public LLMAdapterFactory(List<LLMAdapter> adapterList) {
        for (LLMAdapter adapter : adapterList) {
            // 注册适配器
            registerAdapter(adapter);
        }
    }
    
    public LLMAdapter getAdapter(String modelName) {
        return adapters.values().stream()
            .filter(adapter -> adapter.supports(modelName))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException("Unsupported model: " + modelName));
    }
}
```

### 2. 流式响应处理

#### 2.1 流式响应解析
```java
public class StreamResponseParser {
    public static CompletableFuture<ToolCallResponse> parseStream(
        Flux<String> stream,
        String modelName
    ) {
        return stream.collectList()
            .thenApply(chunks -> {
                StringBuilder content = new StringBuilder();
                List<ToolCall> toolCalls = new ArrayList<>();
                
                for (String chunk : chunks) {
                    if (chunk.startsWith("data: ")) {
                        String data = chunk.substring(6);
                        if ("[DONE]".equals(data)) {
                            break;
                        }
                        
                        // 解析JSON数据
                        JsonNode jsonNode = parseJson(data);
                        if (jsonNode.has("choices")) {
                            JsonNode choice = jsonNode.get("choices").get(0);
                            if (choice.has("delta")) {
                                JsonNode delta = choice.get("delta");
                                if (delta.has("content")) {
                                    content.append(delta.get("content").asText());
                                }
                                if (delta.has("tool_calls")) {
                                    // 解析工具调用
                                    parseToolCalls(delta.get("tool_calls"), toolCalls);
                                }
                            }
                        }
                    }
                }
                
                return new ToolCallResponse(content.toString(), toolCalls);
            });
    }
}
```

#### 2.2 心跳保活机制
```java
public class HeartbeatManager {
    private static final String HEARTBEAT_MESSAGE = "data: {\"type\":\"heartbeat\"}\n\n";
    
    public static Flux<String> addHeartbeat(Flux<String> stream) {
        return Flux.merge(
            stream,
            Flux.interval(Duration.ofSeconds(15))
                .map(tick -> HEARTBEAT_MESSAGE)
        );
    }
}
```

### 3. Token管理

#### 3.1 Token计数器
```java
public class TokenCounter {
    private final Map<String, Integer> tokenCounts = new ConcurrentHashMap<>();
    
    public int countTokens(String text) {
        // 使用tiktoken库计算Token数
        return tiktoken.countTokens(text);
    }
    
    public int countMessageTokens(Message message) {
        int tokens = countTokens(message.getContent());
        if (message.getRole() == RoleType.ASSISTANT) {
            tokens += 4; // 助手消息额外Token
        } else if (message.getRole() == RoleType.USER) {
            tokens += 4; // 用户消息额外Token
        }
        return tokens;
    }
    
    public boolean isWithinLimit(List<Message> messages, int maxTokens) {
        int totalTokens = messages.stream()
            .mapToInt(this::countMessageTokens)
            .sum();
        return totalTokens <= maxTokens;
    }
}
```

#### 3.2 消息截断策略
```java
public class MessageTruncator {
    public static List<Message> truncateMessages(
        List<Message> messages,
        int maxTokens,
        TokenCounter tokenCounter
    ) {
        List<Message> truncated = new ArrayList<>();
        int currentTokens = 0;
        
        // 从最新消息开始，保留系统消息
        for (int i = messages.size() - 1; i >= 0; i--) {
            Message message = messages.get(i);
            int messageTokens = tokenCounter.countMessageTokens(message);
            
            if (currentTokens + messageTokens <= maxTokens || 
                message.getRole() == RoleType.SYSTEM) {
                truncated.add(0, message);
                currentTokens += messageTokens;
            } else {
                break;
            }
        }
        
        return truncated;
    }
}
```

## 常见问题

### 1. 模型兼容性
**问题**：不同模型的Function-Call格式差异
**解决方案**：
- 统一的适配器接口
- 模型特定的格式转换
- 向后兼容性保证
- 配置驱动的模型选择

### 2. 流式响应处理
**问题**：流式数据解析复杂
**解决方案**：
- 标准化的解析器
- 错误恢复机制
- 超时处理
- 内存优化

### 3. Token限制
**问题**：超出Token限制导致请求失败
**解决方案**：
- 智能消息截断
- Token使用监控
- 自动重试机制
- 降级策略

## 系统设计

### 1. 架构层次
```
LLM服务层
├── LLMAdapterFactory     // 适配器工厂
├── LLMAdapter            // 适配器接口
├── OpenAIAdapter         // OpenAI适配器
├── ClaudeAdapter         // Claude适配器
└── DeepSeekAdapter       // DeepSeek适配器

协议层
├── ToolCallRequest       // 工具调用请求
├── ToolCallResponse      // 工具调用响应
├── Tool                  // 工具定义
└── Message               // 消息格式

工具层
├── TokenCounter          // Token计数器
├── StreamResponseParser  // 流式响应解析器
└── MessageTruncator      // 消息截断器
```

### 2. 配置管理
```yaml
# application.yml
llm:
  default_model: "gpt-4"
  models:
    gpt-4:
      adapter: "openai"
      api_key: "${OPENAI_API_KEY}"
      base_url: "https://api.openai.com/v1"
      max_tokens: 4096
      temperature: 0.7
      function_call_type: "auto"
    
    claude-3:
      adapter: "claude"
      api_key: "${CLAUDE_API_KEY}"
      base_url: "https://api.anthropic.com"
      max_tokens: 4096
      temperature: 0.7
      function_call_type: "auto"
    
    deepseek-chat:
      adapter: "deepseek"
      api_key: "${DEEPSEEK_API_KEY}"
      base_url: "https://api.deepseek.com"
      max_tokens: 8192
      temperature: 0.7
      function_call_type: "auto"
```

### 3. 数据流设计
```
智能体请求 → LLM适配器 → 模型API → 流式响应 → 解析处理 → 工具调用 → 结果返回
```

## 可扩展性

### 1. 新模型适配
```java
// 实现LLMAdapter接口
@Component
public class CustomModelAdapter implements LLMAdapter {
    @Override
    public CompletableFuture<ToolCallResponse> callLLM(ToolCallRequest request) {
        // 自定义模型API调用
        return customModelClient.call(request);
    }
    
    @Override
    public List<Tool> convertTools(List<BaseTool> tools) {
        // 转换为自定义模型格式
        return tools.stream()
            .map(this::convertToCustomFormat)
            .collect(Collectors.toList());
    }
    
    @Override
    public boolean supports(String modelName) {
        return modelName.startsWith("custom-");
    }
}
```

### 2. 新协议支持
- 支持新的Function-Call协议
- 自定义消息格式
- 扩展工具定义

### 3. 配置扩展
- 动态模型配置
- 运行时模型切换
- 模型性能监控

## 高可用性

### 1. 故障转移
```java
public class LLMFailoverManager {
    private final List<LLMAdapter> adapters;
    private final AtomicInteger currentIndex = new AtomicInteger(0);
    
    public CompletableFuture<ToolCallResponse> callWithFailover(ToolCallRequest request) {
        for (int i = 0; i < adapters.size(); i++) {
            try {
                LLMAdapter adapter = adapters.get(currentIndex.get());
                return adapter.callLLM(request);
            } catch (Exception e) {
                currentIndex.incrementAndGet();
                if (currentIndex.get() >= adapters.size()) {
                    currentIndex.set(0);
                }
            }
        }
        throw new RuntimeException("All adapters failed");
    }
}
```

### 2. 重试机制
- 指数退避重试
- 熔断保护
- 超时控制

### 3. 监控告警
- API调用成功率
- 响应时间监控
- Token使用统计
- 错误率告警

## 通用性

### 1. 标准化接口
- 统一的LLM接口
- 标准化的工具格式
- 兼容多种协议

### 2. 跨平台支持
- 支持多种云服务
- 本地模型部署
- 混合云架构

### 3. 协议兼容性
- Function-Call标准
- 向后兼容性
- 协议版本管理
