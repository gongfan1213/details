### 面试话术｜工具编排与 Code Interpreter

- 一句话简介：以统一接口编排文件、搜索、报告、代码执行等工具，默认命中本地工具，未命中时透明切到 MCP 外部工具；代码执行在受控沙箱内完成并将结果标准化落盘。

#### 我负责的事情（20s）
- 设计 `ToolCollection` 路由与本地/MCP 工具并存机制
- 实现 `CodeInterpreterTool` 的安全沙箱、流式输出与文件交付

#### 架构与实现要点（1min）
- 统一接口：`BaseTool#getName/getDescription/toParams/execute`
- 工具集合：`ToolCollection` 维护 `toolMap`（本地）与 `mcpToolMap`（外部），`execute(name,input)` 优先本地命中
- 代码执行：
  - Java 侧工具：`genie-backend/.../tool/common/CodeInterpreterTool.java`
  - Python 服务：`genie-tool` 暴露 `/v1/tool/code_interpreter`，支持 SSE & 非流式
  - 受控环境：白名单导入、临时工作目录、超时与内存限制
- 结果交付：统一通过文件服务 `/v1/file_tool/*` 上传、下载、预览

关键代码定位：
- `genie-backend/.../agent/tool/ToolCollection.java`
- `genie-backend/.../agent/tool/common/CodeInterpreterTool.java`
- `genie-tool/genie_tool/tool/code_interpreter.py`（与 API `api/tool.py`）

#### 遇到的问题与解决方案
- 问题1：代码执行安全（高风险）
  - 根因：第三方依赖与运行指令不可控
  - 方案：白名单库、禁用网络/系统危害操作、工作目录隔离、时长/内存限制、输出重定向
  - 效果：0 安全事故，OOM/超时率显著下降

- 问题2：长输出导致 UI 阻塞
  - 根因：一次性大块返回
  - 方案：SSE 增量输出（`EventSourceResponse`），前端按事件类型渐进渲染
  - 效果：主观等待时间降低，用户可见“在做事”

- 问题3：文件路径注入与覆盖
  - 根因：用户输入未经清洗
  - 方案：统一以 `requestId` 建目录，归一化/校验文件名；仅允许工作区相对路径
  - 效果：杜绝越权读写，交付物可追踪

- 问题4：MCP 工具 Schema 不一致
  - 根因：外部工具参数命名/必填项差异
  - 方案：启动期 `McpTool.list` 注入并校验 Schema；运行时参数验证与友好报错
  - 效果：联调成本降低，错误显著减少

#### 量化指标
- 代码执行成功率 95%+
- 受控超时中位数 30-60s（含数据处理/绘图）
- 文件交付 100% 走统一服务，可追踪可审计

#### Q&A 备选
- Q：如何在工具选择上避免“误用工具”？
  - A：`ToolChoice` 与提示词约束，必要时强制 `required` 工具；在计划阶段显式给出工具候选与理由。
- Q：如何保证可观测？
  - A：所有工具调用前后均产生日志与 SSE 事件，关键中间物文件化保存。

#### 演进
- 工具调用代价估计与排程
- 原子工具自动拆装，支持复合工具自动合成
