### SSE 流式传输与可靠性

#### 后端心跳与编码
- 心跳：每 ~10s 发送一次 `heartbeat`
```55:73:genie-backend/src/main/java/com/jd/genie/controller/GenieController.java
private ScheduledFuture<?> startHeartbeat(SseEmitter emitter, String requestId) {
    return executor.scheduleAtFixedRate(() -> {
        emitter.send("heartbeat");
    }, HEARTBEAT_INTERVAL, HEARTBEAT_INTERVAL, TimeUnit.MILLISECONDS);
}
```
- UTF-8：确保 `text/event-stream; charset=utf-8`
```10:20:genie-backend/src/main/java/com/jd/genie/util/SseEmitterUTF8.java
protected void extendResponse(ServerHttpResponse outputMessage) {
    headers.setContentType(new MediaType("text", "event-stream", StandardCharsets.UTF_8));
}
```

#### 中转与事件解包
`/web/api/v1/gpt/queryAgentStreamIncr` 作为 UI 的统一入口：内部消费 `/AutoAgent` 的 `data:` 行并转成前端识别的结构；遇到 `heartbeat` 转为心跳事件；`[DONE]` 终止。
```90:121:genie-backend/src/main/java/com/jd/genie/service/impl/MultiAgentServiceImpl.java
while ((line = reader.readLine()) != null) {
    if (!line.startsWith("data:")) continue;
    String data = line.substring(5);
    if (data.equals("[DONE]")) break;
    if (data.startsWith("heartbeat")) { sseEmitter.send(buildHeartbeatData(...)); continue; }
    AgentResponse agentResponse = JSON.parseObject(data, AgentResponse.class);
    GptProcessResult result = handler.handle(...);
    sseEmitter.send(result);
}
```

#### Python 工具侧的心跳与完结
- 工具服务（FastAPI）使用 `EventSourceResponse`，统一 `ping` 与 `heartbeat`，并在完成时发送 `[DONE]`
```124:131:genie-tool/genie_tool/api/tool.py
if (body.stream) {
  return EventSourceResponse(_stream(), ping_message_factory=lambda: ServerSentEvent(data="heartbeat"), ping=15)
}
```

#### 客户端实现（UI）
- 使用 `@microsoft/fetch-event-source`，onmessage 逐条 JSON 解析并交给渲染管线；onerror/onclose 做降级与重连策略
```25:54:ui/src/utils/querySSE.ts
fetchEventSource(url, {
  method: 'POST', headers: {..., 'Accept': 'text/event-stream'},
  onmessage: (event) => handleMessage(JSON.parse(event.data)),
  onerror: handleError, onclose: handleClose
})
```

#### 可靠性要点
- 心跳间隔权衡：过短增加网络开销，过长易触发网关断连；后端 10s、工具端 15s 为折中
- 编解码一致性：UTF-8、防止代理/网关缓存；确保 `Cache-Control: no-cache`
- 出错与超时：`onError/completeWithError` 及时释放资源；SSEEmitter `onTimeout/onCompletion` 可观测
- 幂等与断点续传：上游可通过 `requestId/sessionId` 做重试关联；前端在 `finished` 后统一收敛状态


