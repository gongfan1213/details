### 面试题：SSE 与前端渲染

#### Q1：SSE 的优势与适用场景？为什么本项目选用 SSE？
**标准回答**：
- 单向推送、实现简单、浏览器原生支持、HTTP 语义清晰；适合服务端持续输出文本/事件。本项目场景上行极少，SSE 更贴切且更易与反向代理共存。

#### Q2：如何保证 SSE 长连接的稳定性？
**标准回答**：
- 服务端周期性 `heartbeat`，客户端忽略心跳但维持连接活性；禁用代理缓存、设置 UTF-8、合理超时；出现异常时快速 `completeWithError`，客户端兜底重连。

#### Q3：前端如何消费与归并 SSE 事件？
**标准回答**：
- 使用 `fetch-event-source` 建立 POST SSE；`onmessage` 中对 `event.data` 执行 JSON 解析，交由 `combineData/handleTaskData` 将不同 `messageType`（plan/task/content/summary）合并到 `chatList.current`；根据 `isFinal/finished` 收敛加载状态并触发展示（如 Action 面板与文件预览）。

#### Q4：如何处理超长文本/大文件渲染？
**标准回答**：
- 按 token/time 模式批量推送（工具端支持多种 `stream_mode`）；前端增量拼接并使用 `requestAnimationFrame` 降抖；对于 HTML/表格结果，组件级按需渲染并限制首屏大小。

#### Q5：SSE 与代理/网关共存时的注意事项？
**标准回答**：
- 关闭中间缓存与自动超时；确保 `Content-Type: text/event-stream; charset=utf-8`；在断流时由客户端重试，避免服务端无限等待；对跨域需正确配置 CORS 与凭证。


