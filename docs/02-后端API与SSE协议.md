### 后端 API 与 SSE 协议说明

#### 健康检查
- **GET** `/web/health`
  - 返回：`ok`

---

#### 多智能体流式接口（UI 主用）
- **POST** `/web/api/v1/gpt/queryAgentStreamIncr`
  - Header：`Accept: text/event-stream`
  - Body（示例）：
    ```json
    {
      "sessionId": "<任意 UUID>",
      "requestId": "<任意 UUID>",
      "query": "帮我生成一份出行计划并做成网页报告",
      "deepThink": 0,
      "outputStyle": "html"
    }
    ```
  - 返回：SSE 事件流（`data:` 为 JSON 串），含周期性 `heartbeat`
  - 事件数据字段（常见）：
    - `resultMap.eventData`：阶段产物（计划、任务、增量文本、文件信息等）
    - `packageType`：事件类型；`heartbeat` 为心跳包
    - `finished`：是否结束

---

#### 智能体编排入口（内部/高级用）
- **POST** `/AutoAgent`（SSE）
  - Body（`AgentRequest`）：
    ```json
    {
      "requestId": "<UUID>",
      "erp": "userId",
      "query": "任务目标描述",
      "agentType": 1,
      "basePrompt": "",
      "sopPrompt": "",
      "isStream": true,
      "outputStyle": "html",
      "messages": [
        {"role": "user", "content": "上下文", "files": []}
      ]
    }
    ```
  - 返回：SSE（心跳 + 过程事件 + 结果）

---

#### SSE 客户端注意事项
- 建议使用 `@microsoft/fetch-event-source` 或原生 `EventSource`/`fetch + ReadableStream`
- Header 示例：
  ```http
  Content-Type: application/json
  Cache-Control: no-cache
  Connection: keep-alive
  Accept: text/event-stream
  ```
- 心跳：后端每 ~10s 发送 `heartbeat`，客户端需忽略或做保活
- 连接关闭：收到 `[DONE]` 或 `finished=true` 后可断开

---

#### 本地联调建议
- UI 通过 Vite 代理将以 `/web` 开头的请求代理到 `SERVICE_BASE_URL`
- 在 `ui/.env` 设置：`SERVICE_BASE_URL=http://localhost:8080`
- 浏览器 Network 面板应能看到与 `/web/api/v1/gpt/queryAgentStreamIncr` 的持续连接


