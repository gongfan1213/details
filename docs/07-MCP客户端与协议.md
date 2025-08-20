# MCP客户端与协议

## 功能概述

MCP（Model Context Protocol）客户端是JoyAgent-JDGenie的外部工具集成层，负责与外部MCP服务器通信，实现工具的动态发现和调用。系统支持多种MCP工具（如地图、票务、天气等），通过标准化的协议实现工具的即插即用和扩展。

## 业务功能实现

### 1. MCP协议实现

#### 1.1 协议核心概念
```python
# MCP协议定义
class MCPProtocol:
    # 工具列表请求
    LIST_TOOLS = "tools/list"
    
    # 工具调用请求
    CALL_TOOL = "tools/call"
    
    # 资源读取请求
    READ_RESOURCE = "resources/read"
    
    # 资源列表请求
    LIST_RESOURCES = "resources/list"
```

#### 1.2 工具信息结构
```python
class MCPToolInfo:
    def __init__(self):
        self.name: str = ""           # 工具名称
        self.description: str = ""    # 工具描述
        self.inputSchema: dict = {}   # 输入参数Schema
        self.outputSchema: dict = {}  # 输出结果Schema
        self.serverUrl: str = ""      # MCP服务器地址
```

### 2. MCP客户端实现

#### 2.1 客户端核心类
```python
class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = aiohttp.ClientSession()
        self.tools_cache = {}
        self.connection_pool = {}
    
    async def list_tools(self) -> List[MCPToolInfo]:
        """获取MCP服务器提供的工具列表"""
        try:
            async with self.session.post(
                f"{self.server_url}/tools/list",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    tools = []
                    for tool_data in data.get("tools", []):
                        tool = MCPToolInfo()
                        tool.name = tool_data["name"]
                        tool.description = tool_data["description"]
                        tool.inputSchema = tool_data.get("inputSchema", {})
                        tool.outputSchema = tool_data.get("outputSchema", {})
                        tool.serverUrl = self.server_url
                        tools.append(tool)
                    return tools
                else:
                    raise Exception(f"Failed to list tools: {response.status}")
        except Exception as e:
            logger.error(f"Error listing tools from {self.server_url}: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用MCP工具"""
        try:
            payload = {
                "name": tool_name,
                "arguments": arguments
            }
            
            async with self.session.post(
                f"{self.server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("content", {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Tool call failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
```

#### 2.2 工具注册机制
```python
class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, MCPToolInfo] = {}
        self.clients: Dict[str, MCPClient] = {}
    
    async def register_server(self, server_url: str):
        """注册MCP服务器"""
        try:
            client = MCPClient(server_url)
            tools = await client.list_tools()
            
            for tool in tools:
                self.tools[tool.name] = tool
                self.clients[tool.name] = client
            
            logger.info(f"Registered {len(tools)} tools from {server_url}")
        except Exception as e:
            logger.error(f"Failed to register server {server_url}: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolInfo]:
        """获取工具信息"""
        return self.tools.get(tool_name)
    
    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """执行工具调用"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        client = self.clients.get(tool_name)
        if not client:
            raise ValueError(f"Client for tool {tool_name} not found")
        
        return await client.call_tool(tool_name, arguments)
```

### 3. 工具集成示例

#### 3.1 12306票务工具
```python
# 12306 MCP工具示例
class TrainTicketTool:
    def __init__(self):
        self.name = "train_ticket_search"
        self.description = "查询火车票信息"
        self.inputSchema = {
            "type": "object",
            "properties": {
                "from_station": {"type": "string", "description": "出发站"},
                "to_station": {"type": "string", "description": "到达站"},
                "date": {"type": "string", "description": "出发日期"},
                "passenger_type": {"type": "string", "description": "乘客类型"}
            },
            "required": ["from_station", "to_station", "date"]
        }
    
    async def execute(self, arguments: dict) -> dict:
        # 调用12306 API
        from_station = arguments["from_station"]
        to_station = arguments["to_station"]
        date = arguments["date"]
        
        # 实际API调用逻辑
        result = await self.search_tickets(from_station, to_station, date)
        return {
            "tickets": result,
            "summary": f"找到{len(result)}趟列车"
        }
```

#### 3.2 地图导航工具
```python
# 地图导航工具示例
class MapNavigationTool:
    def __init__(self):
        self.name = "map_navigation"
        self.description = "提供地图导航服务"
        self.inputSchema = {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "起点"},
                "destination": {"type": "string", "description": "终点"},
                "transport_mode": {"type": "string", "description": "交通方式"}
            },
            "required": ["origin", "destination"]
        }
    
    async def execute(self, arguments: dict) -> dict:
        origin = arguments["origin"]
        destination = arguments["destination"]
        transport_mode = arguments.get("transport_mode", "driving")
        
        # 调用地图API
        route = await self.get_route(origin, destination, transport_mode)
        return {
            "route": route,
            "distance": route["distance"],
            "duration": route["duration"]
        }
```

## 技术方案支撑

### 1. 连接管理

#### 1.1 连接池管理
```python
class MCPConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = {}
        self.connection_semaphore = asyncio.Semaphore(max_connections)
    
    async def get_connection(self, server_url: str) -> aiohttp.ClientSession:
        """获取连接"""
        async with self.connection_semaphore:
            if server_url not in self.active_connections:
                session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    connector=aiohttp.TCPConnector(limit=100)
                )
                self.active_connections[server_url] = session
            return self.active_connections[server_url]
    
    async def close_connection(self, server_url: str):
        """关闭连接"""
        if server_url in self.active_connections:
            session = self.active_connections[server_url]
            await session.close()
            del self.active_connections[server_url]
    
    async def close_all(self):
        """关闭所有连接"""
        for session in self.active_connections.values():
            await session.close()
        self.active_connections.clear()
```

#### 1.2 健康检查
```python
class MCPHealthChecker:
    def __init__(self):
        self.health_status = {}
        self.check_interval = 60  # 60秒检查一次
    
    async def start_health_check(self):
        """启动健康检查"""
        while True:
            await self.check_all_servers()
            await asyncio.sleep(self.check_interval)
    
    async def check_all_servers(self):
        """检查所有服务器健康状态"""
        for server_url in self.health_status.keys():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{server_url}/health") as response:
                        self.health_status[server_url] = response.status == 200
            except Exception as e:
                logger.warning(f"Health check failed for {server_url}: {e}")
                self.health_status[server_url] = False
    
    def is_healthy(self, server_url: str) -> bool:
        """检查服务器是否健康"""
        return self.health_status.get(server_url, False)
```

### 2. 错误处理

#### 2.1 重试机制
```python
class MCPRetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """带重试的执行"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)  # 指数退避
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_exception
```

#### 2.2 熔断器模式
```python
class MCPCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """通过熔断器调用函数"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """成功回调"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### 3. 缓存机制

#### 3.1 工具信息缓存
```python
class MCPToolCache:
    def __init__(self, cache_ttl: int = 300):  # 5分钟缓存
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
```

## 常见问题

### 1. 网络连接问题
**问题**：MCP服务器连接不稳定
**解决方案**：
- 连接池管理
- 自动重连机制
- 健康检查
- 熔断器保护

### 2. 工具调用超时
**问题**：外部工具响应时间长
**解决方案**：
- 超时控制
- 异步调用
- 并发限制
- 降级策略

### 3. 工具版本兼容性
**问题**：不同版本工具协议不兼容
**解决方案**：
- 协议版本管理
- 向后兼容性
- 版本检测
- 自动适配

## 系统设计

### 1. 架构层次
```
MCP服务层
├── MCPClient              // MCP客户端
├── MCPToolRegistry        // 工具注册器
├── MCPConnectionPool      // 连接池
└── MCPHealthChecker       // 健康检查

协议层
├── MCP协议实现           // 标准MCP协议
├── 工具定义格式          // 工具Schema
└── 消息序列化           // JSON序列化

传输层
├── HTTP客户端            // aiohttp客户端
├── 连接管理             // 连接池管理
└── 错误处理             // 异常处理
```

### 2. 配置管理
```yaml
# mcp_config.yml
mcp:
  servers:
    - url: "https://mcp.api-inference.modelscope.net/1784ac5c6d0044/sse"
      name: "modelscope"
      enabled: true
    
    - url: "http://localhost:8081"
      name: "local_tools"
      enabled: true
  
  connection:
    max_connections: 10
    timeout: 30
    retry_attempts: 3
    retry_delay: 1.0
  
  health_check:
    enabled: true
    interval: 60
    timeout: 10
```

### 3. 监控指标
- 工具调用成功率
- 响应时间统计
- 连接池使用率
- 错误率监控
- 缓存命中率

## 可扩展性

### 1. 新工具集成
```python
# 自定义MCP工具
class CustomMCPTool:
    def __init__(self):
        self.name = "custom_tool"
        self.description = "自定义工具"
        self.inputSchema = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    
    async def execute(self, arguments: dict) -> dict:
        # 工具执行逻辑
        return {"result": "success"}

# 注册工具
registry = MCPToolRegistry()
await registry.register_tool(CustomMCPTool())
```

### 2. 协议扩展
- 支持新的MCP协议版本
- 自定义协议扩展
- 协议转换器

### 3. 功能扩展
- 工具权限控制
- 调用频率限制
- 结果缓存策略

## 高可用性

### 1. 故障转移
```python
class MCPFailoverManager:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current_index = 0
    
    async def execute_with_failover(self, func, *args, **kwargs):
        """故障转移执行"""
        for i in range(len(self.servers)):
            try:
                server_url = self.servers[self.current_index]
                return await func(server_url, *args, **kwargs)
            except Exception as e:
                logger.warning(f"Server {server_url} failed: {e}")
                self.current_index = (self.current_index + 1) % len(self.servers)
        
        raise Exception("All servers failed")
```

### 2. 负载均衡
- 轮询负载均衡
- 权重负载均衡
- 健康状态感知

### 3. 监控告警
- 服务器状态监控
- 性能指标收集
- 异常告警机制

## 通用性

### 1. 标准化协议
- MCP标准实现
- 协议版本兼容
- 跨平台支持

### 2. 工具生态
- 丰富的工具库
- 社区贡献
- 开源工具集成

### 3. 部署灵活性
- 本地部署
- 云服务部署
- 混合部署模式
