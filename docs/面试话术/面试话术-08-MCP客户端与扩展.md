### 面试话术｜MCP 客户端与扩展

- 一句话简介：通过 MCP 协议动态发现外部工具，并在运行时以统一 schema 调用，实现“即插即用”的生态扩展。

#### 职责（15s）
- 设计 MCP 工具注入与调用链路；Header/Cookie 透传与错误标准化

#### 实现要点（1min）
- 后端：
  - 工具集合：`ToolCollection` 同时维护本地工具与 `mcpToolMap`
  - MCP 工具：`agent/tool/mcp/McpTool.java`，`controller.GenieController#buildToolCollection`
  - 启动期：调用 MCP `list` 注入工具清单；运行期：`call` 转发参数
- 客户端：`genie-client/` 提供 `/v1/tool/list`、`/v1/tool/call` 接口

#### 问题与解决
- 问题1：外部工具参数不一致
  - 方案：list 时做 schema 标准化与校验；运行时严格校验必填/枚举
- 问题2：网络不稳定/超时
  - 方案：重试+超时+熔断；错误转统一结构返回（方便前端/日志）
- 问题3：认证与上下文透传
  - 方案：统一 HeaderEntity 注入鉴权头/业务 Cookie（可配置）

#### 指标
- 工具注册成功率 > 99%
- 外部工具调用 95p 响应 < 2s（取决于对端）

#### Q&A
- Q：如何避免“影子工具”污染？
  - A：只在白名单 server 中注册；schema 校验失败不注册；可手动禁用。

#### 演进
- 工具市场化管理；调用代价与可靠性打分，驱动路由
