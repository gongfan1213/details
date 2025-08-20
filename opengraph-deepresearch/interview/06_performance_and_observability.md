### 06 性能与系统监控（参考答案）

- 关键参考: `config/performance_optimization.py`, `LANGSMITH_TRACING_GUIDE.md`, `utils/langfuse_llm_client.py`, `check_context_cache_*.py`

### 一、性能分解
- 路径分解：排队时间（队列/并发限流）→ LLM 推理时延 → 工具调用时延（网络/下游）→ 序列化/传输（SSE/JSON）→ 前端渲染；
- 观测建议：在 apis/agents/tool 入口加埋点，记录开始/结束时间，生成端到端 trace。

### 二、Token 成本治理
- 约束：最大步数、最大输入/输出 tokens；
- 压缩：检索→Rerank→Compress（摘录摘要/句级选择）；
- 提示复用：模板化少样本、KV Memory 快取常用片段。

### 三、缓存与检索优化
- 上下文缓存：对同 session 的重复查询做短 TTL 缓存（防抖）；
- 结果缓存：以 `Prompt+Tools+Model+Params+User` 的哈希为键，缓存高代价调用结果；
- 向量检索：
  - 分区：按领域/时间/租户分区，减少搜索空间；
  - 索引：HNSW/IVF 参数调优，权衡召回与延迟；
  - 过滤：先粗后精，合并 rerank，提高精准率。

### 四、Tracing 与可观测性
- Langfuse/Langsmith：对 LLM 调用与工具链路打点；
- 采样：按环境/租户/接口设置采样率；
- 脱敏：对 PII/密钥做掩码；
- 指标：QPS、P95/P99、错误率、重试次数、外部依赖可用性、缓存命中率。

### 五、最小侵入的监控落地
- Prometheus/Grafana 尚未接入，可通过：
  1) 引入 `prometheus_client` 暴露 `/metrics`（计数器/直方图/仪表盘）；
  2) 使用 `prometheus-fastapi-instrumentator` 自动收集 HTTP 指标；
  3) Grafana 导入通用 FastAPI/LLM 工具看板模板。

### 六、实操建议
- 识别最慢 Top-2 工具，加入缓存（键规范+TTL）与并发/速率限制，评估：
  - 时延下降比例、错误率变化、缓存命中率、下游调用量下降；
  - 回滚策略（命中异常/陈旧率过高）。

### 附录：Mermaid 指标全景

```mermaid
flowchart LR
  A[FastAPI] --> B[Agents/Graph]
  B --> C[Tools]
  C --> D[External APIs]
  A --> E[Tracing]\n(Langfuse/Langsmith)
  A --> F[Metrics /metrics]
  B --> F
  C --> F
  F --> G[Grafana Dashboards]
```

Prometheus 最小落地：暴露 `/metrics`，采集 HTTP 请求、工具调用直方图、缓存命中计数器。

### 样例回答/评分标准
- 样例回答要点：
  - 端到端延迟分解与关键观测位点（apis/agents/tools）；
  - Token 成本治理（步数上限、压缩、少样本复用、RAG 裁剪）；
  - 缓存策略（键规范、TTL、并发防抖）与检索调优（分区/索引/过滤）；
  - Tracing 与指标（QPS、P95/99、错误率、重试/熔断）与告警阈值。
- 评分标准：
  - 优秀：给出具体改造位点与度量指标并能落地到代码/配置；
  - 合格：覆盖主要手段并给出观察指标；
  - 待提高：只停留在“加缓存/加监控”的表述。

### 最小可运行示例
- 健康检查（验证服务与 checkpoint 类型）：
```bash
curl -s http://localhost:8000/graph/health | jq .
```

### 参考答案（示例）
- 路径分解：入站排队→LLM→工具→序列化→SSE；在 apis/agents/tools 入口加计时埋点，形成端到端 trace；
- 成本治理：限制最大步数/tokens；通过压缩/裁剪/少样本复用/RAG 代替长上下文；
- 缓存：Prompt+Tools+Model+Params+User 哈希为键，短 TTL + 并发抖动保护；
- 检索调优：分区减少搜索空间、HNSW/IVF 参数调优、先粗后精过滤；
- 观测与告警：QPS、P95/99、错误/重试/熔断、缓存命中率、下游可用性，阈值联动降级/告警。

### 常见错误与改进建议
- 错误：只观察平均值，掩盖长尾问题。
  - 改进：以 P95/99 为主，辅以直方图与 TopN 慢调用定位。
- 错误：缓存键不含版本，升级后污染命中。
  - 改进：把模型/Prompt/工具版本纳入键；升级后提升 version。
- 错误：Tracing 与 Metrics 各自为政。
  - 改进：统一 trace_id 贯穿日志/指标/追踪，提供端到端排障能力。

- 补充图稿：`interview/diagrams/observability_overview.md`。