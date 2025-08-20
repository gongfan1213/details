# SSE流式传输与可靠性

## 功能概述

SSE（Server-Sent Events）流式传输是JoyAgent-JDGenie的核心通信机制，实现前后端实时数据交互。系统支持流式任务执行、实时进度反馈、心跳保活等功能，确保长时间任务的可靠性和用户体验的流畅性。

## 业务功能实现

### 1. SSE协议实现

#### 1.1 后端SSE控制器
```java
@RestController
public class GenieController {
    
    @PostMapping(value = "/web/api/v1/gpt/queryAgentStreamIncr", 
                produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter queryAgentStreamIncr(@RequestBody AgentRequest request) {
        SseEmitter emitter = new SseEmitterUTF8(0L); // 无超时限制
        
        // 启动心跳任务
        ScheduledExecutorService executor = Executors.newScheduledThreadPool(1);
        ScheduledFuture<?> heartbeatTask = executor.scheduleAtFixedRate(() -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("heartbeat")
                    .data("ping"));
            } catch (Exception e) {
                log.error("Heartbeat failed", e);
            }
        }, 0, 15, TimeUnit.SECONDS);
        
        // 处理智能体请求
        CompletableFuture.runAsync(() -> {
            try {
                AgentContext context = buildAgentContext(request);
                AgentHandlerService handler = agentHandlerFactory.getHandler(context, request);
                handler.handle(context, request);
                
                // 发送完成信号
                emitter.send(SseEmitter.event()
                    .name("complete")
                    .data("done"));
                emitter.complete();
            } catch (Exception e) {
                log.error("Agent processing failed", e);
                try {
                    emitter.send(SseEmitter.event()
                        .name("error")
                        .data(e.getMessage()));
                    emitter.complete();
                } catch (IOException ex) {
                    log.error("Error sending error message", ex);
                }
            } finally {
                heartbeatTask.cancel(true);
                executor.shutdown();
            }
        });
        
        return emitter;
    }
}
```

#### 1.2 前端SSE连接
```typescript
import { fetchEventSource } from '@microsoft/fetch-event-source';

export const querySSE = async (options: SSEOptions) => {
  const { 
    sessionId, 
    requestId, 
    query, 
    deepThink, 
    outputStyle, 
    onMessage, 
    onError, 
    onFinish 
  } = options;
  
  await fetchEventSource('/web/api/v1/gpt/queryAgentStreamIncr', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({
      sessionId,
      requestId,
      query,
      deepThink,
      outputStyle
    }),
    onmessage(event) {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error('Failed to parse SSE message:', e);
      }
    },
    onerror(err) {
      console.error('SSE connection error:', err);
      onError(err);
    },
    onclose() {
      console.log('SSE connection closed');
      onFinish();
    },
    onopen(response) {
      if (response.ok && response.status === 200) {
        console.log('SSE connection established');
      } else {
        throw new Error(`SSE connection failed: ${response.status}`);
      }
    }
  });
};
```

### 2. 流式数据处理

#### 2.1 消息类型定义
```typescript
export interface SSEMessage {
  messageType: string;
  message: any;
  requestId: string;
  messageId?: string;
  isFinal?: boolean;
  finish?: boolean;
}

export const MESSAGE_TYPES = {
  TOOL_THOUGHT: 'tool_thought',
  TASK: 'task',
  TASK_SUMMARY: 'task_summary',
  PLAN_THOUGHT: 'plan_thought',
  PLAN: 'plan',
  TOOL_RESULT: 'tool_result',
  RESULT: 'result',
  HEARTBEAT: 'heartbeat',
  ERROR: 'error',
  COMPLETE: 'complete'
} as const;
```

#### 2.2 消息处理机制
```typescript
const handleSSEMessage = (data: SSEMessage) => {
  const { messageType, message, requestId } = data;
  
  switch (messageType) {
    case MESSAGE_TYPES.TOOL_THOUGHT:
      updateToolThought(requestId, message);
      break;
      
    case MESSAGE_TYPES.TASK:
      updateTask(requestId, message);
      break;
      
    case MESSAGE_TYPES.TASK_SUMMARY:
      updateTaskSummary(requestId, message);
      break;
      
    case MESSAGE_TYPES.PLAN_THOUGHT:
      updatePlanThought(requestId, message);
      break;
      
    case MESSAGE_TYPES.PLAN:
      updatePlan(requestId, message);
      break;
      
    case MESSAGE_TYPES.TOOL_RESULT:
      updateToolResult(requestId, message);
      break;
      
    case MESSAGE_TYPES.RESULT:
      updateResult(requestId, message);
      break;
      
    case MESSAGE_TYPES.HEARTBEAT:
      // 心跳保活，无需特殊处理
      break;
      
    case MESSAGE_TYPES.ERROR:
      handleError(requestId, message);
      break;
      
    case MESSAGE_TYPES.COMPLETE:
      handleComplete(requestId);
      break;
      
    default:
      console.warn('Unknown message type:', messageType);
  }
};
```

### 3. 心跳保活机制

#### 3.1 后端心跳实现
```java
public class HeartbeatManager {
    private static final String HEARTBEAT_MESSAGE = "ping";
    private static final int HEARTBEAT_INTERVAL = 15; // 15秒
    
    public static void startHeartbeat(SseEmitter emitter, ScheduledExecutorService executor) {
        executor.scheduleAtFixedRate(() -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("heartbeat")
                    .data(HEARTBEAT_MESSAGE));
            } catch (Exception e) {
                log.error("Failed to send heartbeat", e);
            }
        }, 0, HEARTBEAT_INTERVAL, TimeUnit.SECONDS);
    }
}
```

#### 3.2 前端心跳检测
```typescript
class HeartbeatMonitor {
  private lastHeartbeat: number = Date.now();
  private heartbeatTimeout: number = 30000; // 30秒超时
  private checkInterval: NodeJS.Timeout | null = null;
  
  startMonitoring() {
    this.checkInterval = setInterval(() => {
      const now = Date.now();
      if (now - this.lastHeartbeat > this.heartbeatTimeout) {
        console.warn('Heartbeat timeout, reconnecting...');
        this.reconnect();
      }
    }, 5000); // 每5秒检查一次
  }
  
  updateHeartbeat() {
    this.lastHeartbeat = Date.now();
  }
  
  stopMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }
  
  private reconnect() {
    // 实现重连逻辑
    this.stopMonitoring();
    // 触发重连
  }
}
```

## 技术方案支撑

### 1. 连接管理

#### 1.1 连接池管理
```java
@Component
public class SSEConnectionManager {
    private final Map<String, SseEmitter> connections = new ConcurrentHashMap<>();
    private final Map<String, ScheduledFuture<?>> heartbeatTasks = new ConcurrentHashMap<>();
    
    public SseEmitter createConnection(String requestId) {
        SseEmitter emitter = new SseEmitterUTF8(0L);
        connections.put(requestId, emitter);
        
        // 设置完成回调
        emitter.onCompletion(() -> {
            connections.remove(requestId);
            cancelHeartbeat(requestId);
        });
        
        emitter.onTimeout(() -> {
            connections.remove(requestId);
            cancelHeartbeat(requestId);
        });
        
        emitter.onError((ex) -> {
            connections.remove(requestId);
            cancelHeartbeat(requestId);
        });
        
        return emitter;
    }
    
    public void sendMessage(String requestId, String eventName, Object data) {
        SseEmitter emitter = connections.get(requestId);
        if (emitter != null) {
            try {
                emitter.send(SseEmitter.event()
                    .name(eventName)
                    .data(data));
            } catch (Exception e) {
                log.error("Failed to send message to {}", requestId, e);
                connections.remove(requestId);
                cancelHeartbeat(requestId);
            }
        }
    }
    
    private void cancelHeartbeat(String requestId) {
        ScheduledFuture<?> task = heartbeatTasks.remove(requestId);
        if (task != null) {
            task.cancel(true);
        }
    }
}
```

#### 1.2 重连机制
```typescript
class SSEReconnectionManager {
  private maxRetries: number = 3;
  private retryDelay: number = 1000;
  private currentRetries: number = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  
  async reconnect(options: SSEOptions): Promise<void> {
    if (this.currentRetries >= this.maxRetries) {
      throw new Error('Max reconnection attempts reached');
    }
    
    this.currentRetries++;
    const delay = this.retryDelay * Math.pow(2, this.currentRetries - 1); // 指数退避
    
    return new Promise((resolve, reject) => {
      this.reconnectTimer = setTimeout(async () => {
        try {
          await querySSE(options);
          this.currentRetries = 0; // 重置重试计数
          resolve();
        } catch (error) {
          reject(error);
        }
      }, delay);
    });
  }
  
  cancelReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
```

### 2. 数据序列化

#### 2.1 消息序列化
```java
public class SSEMessageSerializer {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    public static String serialize(Object data) {
        try {
            return objectMapper.writeValueAsString(data);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize message", e);
            return "{}";
        }
    }
    
    public static <T> T deserialize(String json, Class<T> clazz) {
        try {
            return objectMapper.readValue(json, clazz);
        } catch (JsonProcessingException e) {
            log.error("Failed to deserialize message", e);
            return null;
        }
    }
}
```

#### 2.2 流式数据缓冲
```typescript
class StreamBuffer {
  private buffer: string[] = [];
  private maxBufferSize: number = 1000;
  
  add(chunk: string) {
    this.buffer.push(chunk);
    if (this.buffer.length > this.maxBufferSize) {
      this.buffer.shift(); // 移除最旧的数据
    }
  }
  
  getBuffer(): string[] {
    return [...this.buffer];
  }
  
  clear() {
    this.buffer = [];
  }
  
  getLatest(n: number = 10): string[] {
    return this.buffer.slice(-n);
  }
}
```

### 3. 错误处理

#### 3.1 异常处理机制
```java
public class SSEExceptionHandler {
    
    public static void handleException(SseEmitter emitter, Exception e, String requestId) {
        log.error("SSE error for request {}: {}", requestId, e.getMessage());
        
        try {
            ErrorResponse errorResponse = ErrorResponse.builder()
                .requestId(requestId)
                .errorCode("SSE_ERROR")
                .errorMessage(e.getMessage())
                .timestamp(System.currentTimeMillis())
                .build();
            
            emitter.send(SseEmitter.event()
                .name("error")
                .data(SSEMessageSerializer.serialize(errorResponse)));
        } catch (IOException ex) {
            log.error("Failed to send error message", ex);
        } finally {
            try {
                emitter.complete();
            } catch (Exception ex) {
                log.error("Failed to complete emitter", ex);
            }
        }
    }
}
```

#### 3.2 前端错误恢复
```typescript
class SSEErrorHandler {
  private errorCount: number = 0;
  private maxErrors: number = 5;
  private errorWindow: number = 60000; // 1分钟窗口
  private errorTimestamps: number[] = [];
  
  handleError(error: Error, requestId: string): boolean {
    const now = Date.now();
    
    // 清理过期的错误记录
    this.errorTimestamps = this.errorTimestamps.filter(
      timestamp => now - timestamp < this.errorWindow
    );
    
    this.errorTimestamps.push(now);
    this.errorCount = this.errorTimestamps.length;
    
    if (this.errorCount >= this.maxErrors) {
      console.error('Too many errors, stopping reconnection attempts');
      return false; // 停止重连
    }
    
    console.warn(`SSE error (${this.errorCount}/${this.maxErrors}):`, error);
    return true; // 继续重连
  }
  
  reset() {
    this.errorCount = 0;
    this.errorTimestamps = [];
  }
}
```

## 常见问题

### 1. 连接稳定性
**问题**：长时间连接容易断开
**解决方案**：
- 心跳保活机制
- 自动重连策略
- 连接状态监控
- 网络异常检测

### 2. 数据丢失
**问题**：网络异常导致数据丢失
**解决方案**：
- 消息确认机制
- 数据缓冲策略
- 断点续传
- 状态同步

### 3. 性能问题
**问题**：大量并发连接性能下降
**解决方案**：
- 连接池管理
- 资源限制
- 负载均衡
- 异步处理

## 系统设计

### 1. 架构层次
```
SSE服务层
├── SSEConnectionManager    // 连接管理器
├── HeartbeatManager        // 心跳管理器
├── SSEExceptionHandler     // 异常处理器
└── SSEMessageSerializer    // 消息序列化器

协议层
├── SSE协议实现            // Server-Sent Events
├── 消息格式定义           // 统一消息格式
└── 事件类型管理           // 事件类型枚举

传输层
├── HTTP长连接             // 持久连接
├── 流式数据传输           // 实时数据流
└── 网络异常处理           // 网络容错
```

### 2. 配置管理
```yaml
# application.yml
sse:
  heartbeat_interval: 15    # 心跳间隔（秒）
  connection_timeout: 0     # 连接超时（0表示无限制）
  max_connections: 1000     # 最大连接数
  buffer_size: 1000         # 缓冲区大小
  retry_attempts: 3         # 重试次数
  retry_delay: 1000         # 重试延迟（毫秒）
```

### 3. 监控指标
- 连接数量统计
- 消息吞吐量
- 错误率监控
- 响应时间统计
- 心跳成功率

## 可扩展性

### 1. 新消息类型扩展
```typescript
// 扩展消息类型
export const MESSAGE_TYPES = {
  ...DEFAULT_MESSAGE_TYPES,
  CUSTOM_EVENT: 'custom_event'
};

// 添加处理逻辑
const handleCustomEvent = (data: any) => {
  // 自定义事件处理逻辑
};
```

### 2. 协议扩展
- 支持WebSocket协议
- 自定义传输协议
- 协议版本管理

### 3. 功能扩展
- 消息压缩
- 加密传输
- 多路复用

## 高可用性

### 1. 故障转移
```java
public class SSELoadBalancer {
    private final List<String> serverUrls;
    private final AtomicInteger currentIndex = new AtomicInteger(0);
    
    public String getNextServer() {
        int index = currentIndex.getAndIncrement() % serverUrls.size();
        return serverUrls.get(index);
    }
    
    public void markServerDown(String serverUrl) {
        // 标记服务器不可用
        // 实现健康检查逻辑
    }
}
```

### 2. 负载均衡
- 连接分发策略
- 服务器健康检查
- 动态负载调整

### 3. 监控告警
- 连接数监控
- 错误率告警
- 性能指标监控
- 自动恢复机制

## 通用性

### 1. 跨平台支持
- 浏览器兼容性
- 移动端适配
- 桌面应用支持

### 2. 标准化协议
- SSE标准实现
- HTTP/2支持
- 协议版本兼容

### 3. 多语言支持
- JavaScript/TypeScript
- Java后端
- Python工具服务
- 其他语言客户端
