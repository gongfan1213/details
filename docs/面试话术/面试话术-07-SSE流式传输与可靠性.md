### 面试话术｜SSE 流式传输与可靠性

- 一句话简介：端到端流式响应，包含心跳保活、错误透传与渐进渲染，保障长任务过程可见与连接稳定。

#### 职责（15s）
- 设计后端 SSE 事件格式与心跳；前端 `fetch-event-source` 处理与视图增量更新

#### 实现要点（1min）
- 后端：
  - 控制器：`GenieController#queryAgentStreamIncr` → `SseEmitterUTF8`
  - 打点：`agent/printer/SSEPrinter.java` 统一输出 event/type/data
  - 心跳：定时 `heartbeat`，异常/完成事件闭环
- 前端：
  - `ui/src/utils/querySSE.ts` 基于 `@microsoft/fetch-event-source`
  - 按 `messageType` 更新 Chat/Plan/Task/File（`ActionPanel` 系列渲染器）

#### 问题与解决
- 问题1：长连断开/网关超时
  - 方案：心跳 + 前端重连指数退避；Nginx/网关超时配置
- 问题2：大消息导致阻塞
  - 方案：拆分事件、前端分帧渲染、避免一次性巨块JSON
- 问题3：异常不可见/难复现
  - 方案：SSE 中透传错误事件与 requestId；统一日志与文件留痕
- 问题4：字符集/emoji 乱码
  - 方案：`SseEmitterUTF8` 统一 UTF-8；前端解码兜底

#### 指标
- 平均端到端首包 < 1s（网络环境良好）
- 长链路（>2min）保持率显著提升

#### Q&A
- Q：为什么选 SSE 而非 WebSocket？
  - A：服务端单向推更贴近场景；握手与代理兼容性更好；需要双向时也支持降级切换。

#### 演进
- 支持断点续传/事件重放；消息压缩
