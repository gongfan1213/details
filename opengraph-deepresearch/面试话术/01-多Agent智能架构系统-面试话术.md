# 多Agent智能架构系统｜技术面试话术

## 一句话定位
- 多智能体协同编排（Supervisor + 专家Agent），以可观测、可恢复、可扩展为核心，覆盖研究、创作的端到端链路。

## 架构要点（对技术面）
- 角色编排：`Supervisor` 统一拆解任务与路由；`Insight/Profile/Hitpoint/Facts/XHSWriting/Tiktok/Wechat` 等专家Agent各司其职。
- 执行形态：Nova3（队列+并发管控）与 Loomi（ReAct式编排+Notes）双形态共存。
- 上下文与记忆：`utils/context_manager.py`、`utils/loomi_context_manager.py` 管理会话级 state 与长期 memory，支持检索注入。
- 可恢复性：`agents/graph/redis_checkpoint.py` 保存最小可恢复检查点，失败可回放、跳步重试。
- 观测与追踪：LangSmith、结构化日志、事件流（SSE）。

## 关键代码指引
- `agents/nova3/*.py`：各子Agent实现与队列协作
- `agents/loomi/*.py`：Concierge/Orchestrator 与 Notes 流
- `apis/routes.py`：SSE 流式事件
- `agents/graph/redis_checkpoint.py`：检查点

## 已解决的典型问题与方案
- 任务漂移/上下文丢失：检查点 + 会话级 Agent 实例（避免全局单例串话）。
- 并发冲突：三层队列（内存/Redis/文件）+ 限流与租约，见 `utils/layered_queue_manager.py`。
- 工具调用不稳定：超时/重试/降级（例如向量检索失败降级关键词检索）。
- 长上下文成本高：上下文裁剪与结果压缩注入。

## 指标与收益（可量化）
- 多Agent并行后端到端时延下降 30%+（典型内容生产任务）。
- 失败重试与回放后，人工介入次数下降 40%+。

## 可扩展 & 高可用
- 新增 Agent 仅需注册能力+上下文拼装；路由基于标签/得分。
- 存储抽象（Redis/文件/DB），单点可替换；核心链路幂等。

## Demo 话术（3 分钟）
- 1 分钟讲编排：如何把“写一篇小红书运营分析”拆成搜索→洞察→打点→写作。
- 1 分钟展流式事件：SSE 展示各 Agent 的阶段输出。
- 1 分钟讲恢复：中断后回放到最近检查点继续执行。

## 追问与答法
- Q：如何避免多个会话串话？
  - A：会话级 Agent 实例 + 上下文 key 隔离 + 检查点命名空间。
- Q：如何定位瓶颈？
  - A：LangSmith trace + 事件时序 + 队列统计三视角联动。
