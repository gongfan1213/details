# 工具系统与MCP协议

## 功能概述

工具系统是JoyAgent-JDGenie的核心能力支撑，提供统一的工具调用接口和MCP（Model Context Protocol）协议支持。系统支持内置工具（代码执行、报告生成、深度搜索、文件管理）和外部MCP工具的动态集成，实现工具的可插拔和扩展。

## 业务功能实现

### 1. 工具接口设计

#### 1.1 统一工具接口
```java
public interface BaseTool {
    String getName();                    // 工具名称
    String getDescription();             // 工具描述
    Map<String, Object> toParams();      // 工具参数规范
    Object execute(Object input);        // 执行工具
}
```

#### 1.2 工具集合管理
```java
public class ToolCollection {
    private Map<String, BaseTool> toolMap;           // 本地工具映射
    private Map<String, McpToolInfo> mcpToolMap;     // MCP工具映射
    
    public void addTool(BaseTool tool);              // 添加本地工具
    public void addMcpTool(String name, String desc, String parameters, String mcpServerUrl); // 添加MCP工具
    public Object execute(String name, Object toolInput); // 执行工具
}
```

### 2. 内置工具实现

#### 2.1 代码执行工具（CodeInterpreterTool）
**功能**：执行Python代码，支持数据处理、可视化等
**特点**：
- 安全的代码执行环境
- 支持文件上传和结果输出
- 流式执行反馈

```java
public class CodeInterpreterTool implements BaseTool {
    @Override
    public Object execute(Object input) {
        // 调用Python工具服务
        return callCodeAgentStream(request);
    }
}
```

#### 2.2 报告生成工具（ReportTool）
**功能**：生成多种格式的报告（HTML、PPT、Markdown）
**特点**：
- 支持多种输出格式
- 模板化报告生成
- 流式内容生成

#### 2.3 深度搜索工具（DeepSearchTool）
**功能**：执行深度网络搜索和信息检索
**特点**：
- 多搜索引擎支持
- 智能结果聚合
- 实时搜索反馈

#### 2.4 文件管理工具（FileTool）
**功能**：文件上传、下载、预览和管理
**特点**：
- 统一文件接口
- 支持多种文件格式
- 文件元数据管理

### 3. MCP协议支持

#### 3.1 MCP工具信息
```java
@Data
@Builder
public class McpToolInfo {
    private String name;           // 工具名称
    private String desc;           // 工具描述
    private String parameters;     // 参数规范
    private String mcpServerUrl;   // MCP服务器地址
}
```

#### 3.2 MCP工具调用
```java
public class McpTool implements BaseTool {
    public Object callTool(String mcpServerUrl, String toolName, Object toolInput) {
        // 通过MCP客户端调用外部工具
        return mcpClient.callTool(mcpServerUrl, toolName, toolInput);
    }
}
```

## 技术方案支撑

### 1. 工具路由机制

#### 1.1 优先级策略
```java
public Object execute(String name, Object toolInput) {
    // 优先使用本地工具
    if (toolMap.containsKey(name)) {
        return toolMap.get(name).execute(toolInput);
    } 
    // 其次使用MCP工具
    else if (mcpToolMap.containsKey(name)) {
        McpToolInfo toolInfo = mcpToolMap.get(name);
        return new McpTool().callTool(toolInfo.getMcpServerUrl(), name, toolInput);
    }
    return null;
}
```

#### 1.2 动态工具发现
```java
// 启动时动态发现MCP工具
private void discoverMcpTools() {
    for (String mcpServerUrl : genieConfig.getMcpServerUrlArr()) {
        List<McpToolInfo> tools = mcpClient.listTools(mcpServerUrl);
        for (McpToolInfo tool : tools) {
            toolCollection.addMcpTool(tool.getName(), tool.getDesc(), 
                                    tool.getParameters(), mcpServerUrl);
        }
    }
}
```

### 2. 工具调用流程

#### 2.1 本地工具调用
```
智能体 → ToolCollection → BaseTool.execute() → Python工具服务 → 结果返回
```

#### 2.2 MCP工具调用
```
智能体 → ToolCollection → McpTool → MCP客户端 → MCP服务器 → 结果返回
```

### 3. 错误处理机制

#### 3.1 工具异常处理
```java
public Object execute(String name, Object toolInput) {
    try {
        if (toolMap.containsKey(name)) {
            return toolMap.get(name).execute(toolInput);
        }
    } catch (Exception e) {
        log.error("Tool execution error: {}", e.getMessage());
        return createErrorResponse(e);
    }
}
```

#### 3.2 降级策略
- 工具不可用时自动降级
- 支持备用工具切换
- 优雅的错误提示

## 常见问题

### 1. 工具调用超时
**问题**：外部工具响应时间长
**解决方案**：
- 设置合理的超时时间
- 实现异步调用机制
- 添加重试逻辑

### 2. 工具参数验证
**问题**：工具参数格式错误
**解决方案**：
- JSON Schema参数验证
- 参数类型检查
- 默认值处理

### 3. MCP工具连接失败
**问题**：MCP服务器不可用
**解决方案**：
- 连接池管理
- 健康检查机制
- 自动重连策略

## 系统设计

### 1. 架构设计
```
工具管理层
├── ToolCollection        // 工具集合管理
├── BaseTool              // 工具接口定义
└── 工具实现类

MCP协议层
├── McpTool              // MCP工具封装
├── McpToolInfo          // MCP工具信息
└── MCP客户端

服务层
├── Python工具服务       // 本地工具服务
└── MCP服务器           // 外部工具服务
```

### 2. 配置管理
```yaml
# application.yml
mcp_server_url: "http://ip1:port1/sse,http://ip2:port2/sse"
code_interpreter_url: "http://127.0.0.1:1601"
deep_search_url: "http://127.0.0.1:1601"
mcp_client_url: "http://127.0.0.1:8188"
```

### 3. 数据流设计
```
用户请求 → 智能体 → 工具选择 → 工具执行 → 结果处理 → 返回用户
```

## 可扩展性

### 1. 新工具扩展
```java
// 实现BaseTool接口
public class CustomTool implements BaseTool {
    @Override
    public String getName() {
        return "custom_tool";
    }
    
    @Override
    public String getDescription() {
        return "自定义工具描述";
    }
    
    @Override
    public Map<String, Object> toParams() {
        return Map.of("type", "object", "properties", Map.of(
            "param1", Map.of("type", "string", "description", "参数1")
        ));
    }
    
    @Override
    public Object execute(Object input) {
        // 工具执行逻辑
        return result;
    }
}
```

### 2. MCP工具集成
```java
// 在Controller中注册新工具
private ToolCollection buildToolCollection(AgentContext agentContext, AgentRequest request) {
    ToolCollection toolCollection = new ToolCollection();
    
    // 添加自定义工具
    CustomTool customTool = new CustomTool();
    toolCollection.addTool(customTool);
    
    return toolCollection;
}
```

### 3. 工具配置扩展
- 支持工具参数配置
- 动态工具启用/禁用
- 工具权限控制

## 高可用性

### 1. 工具可用性保证
- 工具健康检查
- 自动故障转移
- 负载均衡策略

### 2. 监控告警
- 工具调用成功率监控
- 响应时间监控
- 异常告警机制

### 3. 容错机制
- 工具调用重试
- 降级策略
- 熔断保护

## 通用性

### 1. 标准化接口
- 统一的工具接口规范
- 标准化的参数格式
- 兼容多种协议

### 2. 跨平台支持
- 支持多种操作系统
- 跨语言工具集成
- 云原生部署

### 3. 协议兼容性
- MCP协议标准支持
- 向后兼容性保证
- 协议版本管理
