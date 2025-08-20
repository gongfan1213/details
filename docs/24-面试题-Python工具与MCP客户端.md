### 面试题：Python 工具与 MCP 客户端

#### Q1：Python 工具服务提供了哪些能力？
**标准回答**：
- 工具：`/v1/tool/code_interpreter`（代码执行）、`/v1/tool/report`（报告生成）、`/v1/tool/deepsearch`（深度搜索，需 `SERPER_SEARCH_API_KEY`）。
- 文件：`/v1/file_tool/*`（内容上传、二进制上传、列表、下载与预览）。
- 流式返回采用 `EventSourceResponse`，`ping=15` 并携带 `heartbeat`，结束时 `[DONE]`。

#### Q2：Code Interpreter 的安全与可控性如何保证？
**标准回答**：
- 使用 `smolagents` 的 `PythonInterpreterTool` 执行受限代码；白名单化的 `additional_authorized_imports`（如 pandas/numpy/matplotlib）；临时工作目录与输出目录隔离；对上传文件先落盘，再做抽取摘要以控成本；最终产物通过文件服务统一上传，避免直接返回大结果。

#### Q3：如何通过 MCP 扩展外部工具？
**标准回答**：
- MCP 客户端暴露 `/v1/tool/list` 与 `/v1/tool/call`，后端在启动时调用 `list` 注入工具清单，并在运行期通过 `call` 转发带参数的工具调用；请求头与 Cookie 透传由 `HeaderEntity` 统一处理；异常转换为统一结构返回。

#### Q4：如何做联调与排错？
**标准回答**：
- 访问 `http://localhost:1601`/`http://localhost:8188/docs` 验证 API；抓取工具端日志与任务的 `request_id` 路径下的输出文件；遇到参数不合法/网络异常时回放最近一次工具输入；优先在非流式模式下复现问题并对比流式差异。


